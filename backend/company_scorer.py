import json
import os
import time
from datetime import datetime

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.crustdata.com"
API_KEY = os.getenv("CRUSTDATA_API_KEY", "")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(SCRIPT_DIR, "..", "docs")

print("[INIT] Loading data files...")
print(f"  - DOCS_DIR: {DOCS_DIR}")
print(f"  - API_KEY set: {'Yes' if API_KEY else 'NO - MISSING!'}")

with open(os.path.join(DOCS_DIR, "all_candidate_scores_v2.json"), "r") as f:
    candidates_data = json.load(f)
print(f"  - Loaded {len(candidates_data.get('candidates', []))} candidates")

with open(os.path.join(DOCS_DIR, "candidate_companies_data.json"), "r") as f:
    companies_raw = json.load(f)
print(f"  - Loaded {len(companies_raw.get('companies', {}))} companies metadata")

with open(os.path.join(DOCS_DIR, "company_ids.json"), "r") as f:
    frontier_labs = json.load(f)
print(f"  - Loaded {len(frontier_labs)} frontier lab IDs: {', '.join(frontier_labs.keys())}")

FRONTIER_LAB_IDS = set(int(v) for v in frontier_labs.values())
FRONTIER_LAB_NAMES = {int(v): k for k, v in frontier_labs.items()}

COMPANIES_METADATA = {}
for cid, c in companies_raw.get("companies", {}).items():
    if c is None:
        continue
    basic_info = c.get("basic_info") or {}
    headcount_data = c.get("headcount") or {}
    funding_data = c.get("funding") or {}
    COMPANIES_METADATA[int(cid)] = {
        "name": basic_info.get("name") or "Unknown",
        "headcount": headcount_data.get("total"),
        "funding_total": funding_data.get("total_investment_usd"),
        "last_round": funding_data.get("last_round_type"),
        "linkedin_url": basic_info.get("professional_network_url"),
    }


def compute_seniority_score(title: str | None) -> int:
    if not title:
        return 5
    title_lower = title.lower()
    if any(t in title_lower for t in ["director", "vp", "vice president", "head of", "chief"]):
        return 10
    if any(t in title_lower for t in ["staff", "principal"]):
        return 9
    if any(t in title_lower for t in ["lead", "manager"]):
        return 8
    if "senior" in title_lower:
        return 7
    if any(t in title_lower for t in ["associate", "junior", "entry"]):
        return 3
    if any(t in title_lower for t in ["intern", "fellow", "trainee"]):
        return 2
    return 5


def is_founder_title(title: str | None) -> bool:
    if not title:
        return False
    title_lower = title.lower()
    return any(t in title_lower for t in ["founder", "co-founder", "cofounder", "ceo", "cto", "coo"])


def get_ex_lab_info(person: dict) -> dict | None:
    past_roles = person.get("experience", {}).get("employment_details", {}).get("past", [])
    for role in past_roles:
        company_id = role.get("crustdata_company_id")
        if company_id and company_id in FRONTIER_LAB_IDS:
            return {
                "name": person.get("name", "Unknown"),
                "title": role.get("title", ""),
                "former_lab": FRONTIER_LAB_NAMES.get(company_id, "Unknown"),
            }
    return None


def fetch_team_roster(company_id: int, client: httpx.Client) -> list[dict]:
    all_results = []
    cursor = None
    page = 0

    while True:
        page += 1
        payload = {
            "filters": {
                "field": "experience.employment_details.current.company_id",
                "type": "=",
                "value": company_id,
            },
            "limit": 100,
        }
        if cursor:
            payload["cursor"] = cursor

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "x-api-version": "2025-11-01",
        }

        print(f"    [API] Page {page}: POST /person/search (company_id={company_id})")
        response = client.post(f"{BASE_URL}/person/search", json=payload, headers=headers)
        print(f"    [API] Response: {response.status_code}")
        response.raise_for_status()
        data = response.json()

        results = data.get("profiles", [])
        total_count = data.get("total_count", "?")
        all_results.extend(results)
        print(f"    [API] Got {len(results)} profiles (total available: {total_count})")

        cursor = data.get("next_cursor")
        if not cursor:
            print(f"    [API] No more pages")
            break

        print(f"    [API] More pages available, waiting 4s...")
        time.sleep(1)

    return all_results


def score_company(company_id: int, team: list[dict], metadata: dict) -> dict:
    print(f"  [SCORE] Analyzing {len(team)} team members...")
    ex_lab_members = []
    seniority_scores = []

    for person in team:
        name = person.get("name", "Unknown")
        title = person.get("current_title") or ""
        seniority = compute_seniority_score(title)
        seniority_scores.append(seniority)

        ex_lab_info = get_ex_lab_info(person)
        if ex_lab_info:
            ex_lab_members.append(ex_lab_info)
            print(f"    [FOUND] Ex-lab: {name} - {ex_lab_info['former_lab']} ({ex_lab_info['title']})")

    ex_lab_count = len(ex_lab_members)
    avg_seniority = sum(seniority_scores) / len(seniority_scores) if seniority_scores else 5.0
    has_founder = any(is_founder_title(m.get("title")) for m in ex_lab_members)
    headcount = metadata.get("headcount") or len(team)

    headcount_bonus = 0
    if headcount and headcount < 50:
        headcount_bonus = 3
    elif headcount and headcount < 200:
        headcount_bonus = 1

    raw_score = (ex_lab_count * 3) + (avg_seniority * 0.5) + (5 if has_founder else 0) + headcount_bonus
    score = min(10.0, raw_score / 3)

    print(f"  [SCORE] Breakdown: ex_lab={ex_lab_count}*3 + seniority={avg_seniority:.1f}*0.5 + founder={5 if has_founder else 0} + headcount_bonus={headcount_bonus}")
    print(f"  [SCORE] Raw={raw_score:.1f} -> Final={score:.1f}")

    if score >= 7.0:
        tier = "HIGH"
    elif score >= 5.0:
        tier = "MED"
    else:
        tier = "LOW"

    return {
        "id": str(company_id),
        "name": metadata.get("name", "Unknown"),
        "score": round(score, 1),
        "score_tier": tier,
        "headcount": headcount,
        "ex_lab_count": ex_lab_count,
        "avg_seniority": round(avg_seniority, 1),
        "has_founder_from_lab": has_founder,
        "funding_total": metadata.get("funding_total"),
        "last_round": metadata.get("last_round"),
        "team_highlights": ex_lab_members[:5],
        "linkedin_url": metadata.get("linkedin_url"),
    }


MAX_HEADCOUNT = 100  # VC-friendly: early-stage startups only


def main():
    print("\n" + "=" * 60)
    print("  COMPANY SCORER - Phase F (VC Mode)")
    print(f"  Filtering: headcount <= {MAX_HEADCOUNT}")
    print("=" * 60)

    candidates = candidates_data.get("candidates", [])
    sorted_candidates = sorted(candidates, key=lambda c: c.get("score", 0), reverse=True)

    print(f"\n[CANDIDATES] Processing all {len(sorted_candidates)} candidates...")

    unique_company_ids = {}  # company_id -> list of candidates at that company
    skipped_no_company = 0
    skipped_too_large = 0

    for c in sorted_candidates:
        cid = c.get("current_company_id")
        if not cid:
            skipped_no_company += 1
            continue

        cid = int(cid)
        metadata = COMPANIES_METADATA.get(cid, {})
        headcount = metadata.get("headcount")

        # Filter out large companies (>100 employees)
        if headcount and headcount > MAX_HEADCOUNT:
            if cid not in unique_company_ids:  # Only log first time we see this company
                print(f"  [SKIP] {metadata.get('name', 'Unknown')} - headcount {headcount} > {MAX_HEADCOUNT}")
                skipped_too_large += 1
            continue

        if cid not in unique_company_ids:
            unique_company_ids[cid] = []
            company_name = c.get('current_company') or metadata.get('name', 'Unknown')
            print(f"  [ADD] {company_name} (id={cid}, headcount={headcount or '?'})")
        unique_company_ids[cid].append(c['name'])

    print(f"\n[FILTER SUMMARY]")
    print(f"  - Total candidates: {len(sorted_candidates)}")
    print(f"  - No current company: {skipped_no_company}")
    print(f"  - Company too large (>{MAX_HEADCOUNT}): {skipped_too_large}")
    print(f"  - VC-friendly companies found: {len(unique_company_ids)}")

    # Show which ex-lab talent is at each company
    print(f"\n[COMPANY TALENT MAP]")
    for cid, talent in unique_company_ids.items():
        metadata = COMPANIES_METADATA.get(cid, {})
        print(f"  {metadata.get('name', 'Unknown')}: {', '.join(talent[:3])}{' +' + str(len(talent)-3) + ' more' if len(talent) > 3 else ''}")

    scored_companies = []
    start_time = time.time()
    company_ids_list = list(unique_company_ids.keys())

    print(f"\n[FETCH] Starting API calls for {len(company_ids_list)} companies...")
    with httpx.Client(timeout=60.0) as client:
        for i, company_id in enumerate(company_ids_list):
            metadata = COMPANIES_METADATA.get(company_id, {"name": "Unknown"})
            print(f"\n{'─' * 60}")
            print(f"[{i+1}/{len(company_ids_list)}] {metadata.get('name', 'Unknown')} (id={company_id})")
            print(f"  Metadata: headcount={metadata.get('headcount')}, funding=${metadata.get('funding_total') or 0:,.0f}")
            print(f"  Known ex-lab talent: {', '.join(unique_company_ids[company_id])}")

            try:
                team = fetch_team_roster(company_id, client)
                print(f"  [RESULT] Found {len(team)} team members")

                scored = score_company(company_id, team, metadata)
                scored_companies.append(scored)
                print(f"  [RESULT] Final: {scored['score']} ({scored['score_tier']}), {scored['ex_lab_count']} ex-lab members")

            except httpx.HTTPStatusError as e:
                print(f"  [ERROR] HTTP {e.response.status_code}: {e.response.text[:200]}")
            except Exception as e:
                print(f"  [ERROR] {type(e).__name__}: {e}")

            if i < len(company_ids_list) - 1:
                print(f"  [WAIT] Sleeping 4s for rate limit...")
                time.sleep(4)

    elapsed = time.time() - start_time
    scored_companies.sort(key=lambda c: c["score"], reverse=True)

    output = {
        "meta": {
            "total_companies": len(scored_companies),
            "last_updated": datetime.now().isoformat(),
            "source_candidates": len(sorted_candidates),
            "max_headcount_filter": MAX_HEADCOUNT,
            "companies_skipped_too_large": skipped_too_large,
        },
        "companies": scored_companies,
    }

    output_path = os.path.join(DOCS_DIR, "companies_scored.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"  COMPLETE - VC Investment Targets")
    print(f"{'=' * 60}")
    print(f"  Time elapsed: {elapsed:.1f}s")
    print(f"  Companies scored: {len(scored_companies)} (headcount <= {MAX_HEADCOUNT})")
    print(f"  Output: {output_path}")

    # Categorize by tier
    high_tier = [c for c in scored_companies if c['score_tier'] == 'HIGH']
    med_tier = [c for c in scored_companies if c['score_tier'] == 'MED']
    with_founders = [c for c in scored_companies if c['has_founder_from_lab']]

    print(f"\n  [INVESTMENT SUMMARY]")
    print(f"    HIGH tier: {len(high_tier)} companies")
    print(f"    MED tier: {len(med_tier)} companies")
    print(f"    With lab founders: {len(with_founders)} companies")

    print(f"\n  [TOP 10 VC TARGETS]")
    for i, c in enumerate(scored_companies[:10]):
        founder_badge = "🔥 FOUNDER" if c['has_founder_from_lab'] else ""
        print(f"    {i+1}. {c['name']}")
        print(f"       Score: {c['score']} ({c['score_tier']}) | Headcount: {c['headcount']} | Ex-lab: {c['ex_lab_count']} {founder_badge}")
        if c['team_highlights']:
            highlights = ", ".join([f"{h['name']} (ex-{h['former_lab']})" for h in c['team_highlights'][:2]])
            print(f"       Team: {highlights}")


if __name__ == "__main__":
    main()
