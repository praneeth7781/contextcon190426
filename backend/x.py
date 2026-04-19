import json
from datetime import datetime, timedelta

with open("docs/indian_candidates_raw.json", "r") as f:
    candidates = json.load(f)

with open("docs/company_ids.json", "r") as f:
    frontier_labs = json.load(f)

with open("docs/candidate_companies_data.json", "r") as f:
    companies_data = json.load(f)

FRONTIER_LAB_IDS = set(int(v) for v in frontier_labs.values())
FRONTIER_LAB_NAMES = {int(v): k for k, v in frontier_labs.items()}
COMPANY_HEADCOUNTS = {
    int(cid): c.get("headcount", {}).get("total")
    for cid, c in companies_data.get("companies", {}).items()
}
COMPANY_NAMES = {
    int(cid): c.get("name", "Unknown")
    for cid, c in companies_data.get("companies", {}).items()
}

CITY_COORDS = {
    "bangalore": {"name": "Bangalore", "lat": 12.9716, "lng": 77.5946},
    "bengaluru": {"name": "Bangalore", "lat": 12.9716, "lng": 77.5946},
    "delhi": {"name": "Delhi NCR", "lat": 28.6139, "lng": 77.2090},
    "gurgaon": {"name": "Delhi NCR", "lat": 28.6139, "lng": 77.2090},
    "gurugram": {"name": "Delhi NCR", "lat": 28.6139, "lng": 77.2090},
    "noida": {"name": "Delhi NCR", "lat": 28.6139, "lng": 77.2090},
    "mumbai": {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777},
    "hyderabad": {"name": "Hyderabad", "lat": 17.3850, "lng": 78.4867},
    "chennai": {"name": "Chennai", "lat": 13.0827, "lng": 80.2707},
    "pune": {"name": "Pune", "lat": 18.5204, "lng": 73.8567},
    "kolkata": {"name": "Kolkata", "lat": 22.5726, "lng": 88.3639},
}

TODAY = datetime(2026, 4, 19)
TWELVE_MONTHS_AGO = TODAY - timedelta(days=365)
SIX_MONTHS_AGO = TODAY - timedelta(days=180)
MIN_ROLE_DURATION = timedelta(days=90)

SENIOR_TITLES = [
    "senior", "staff", "principal", "lead", "director", "vp", "head",
    "chief", "manager", "architect"
]

FOUNDER_TITLES = ["founder", "co-founder", "cofounder", "ceo"]

INTERN_TITLES = ["intern", "internship", "trainee", "apprentice", "co-op", "campus partner"]


def parse_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("T00:00:00", ""))
    except Exception:
        return None


def get_role_duration(role: dict) -> timedelta | None:
    start = parse_date(role.get("start_date"))
    if not start:
        return None
    end = parse_date(role.get("end_date")) or TODAY
    return end - start


def is_senior_title(title: str | None) -> bool:
    if not title:
        return False
    title_lower = title.lower()
    return any(s in title_lower for s in SENIOR_TITLES)


def is_founder_title(title: str | None) -> bool:
    if not title:
        return False
    title_lower = title.lower()
    if "founder's office" in title_lower or "founders office" in title_lower:
        return False
    return any(f in title_lower for f in FOUNDER_TITLES)


def is_intern_title(title: str | None) -> bool:
    if not title:
        return False
    title_lower = title.lower()
    return any(i in title_lower for i in INTERN_TITLES)


def is_india_location(location: dict | str | None) -> bool:
    if not location:
        return False
    if isinstance(location, dict):
        raw = location.get("raw", "")
    else:
        raw = location
    return "india" in raw.lower()


def extract_city(location: dict | str | None) -> str | None:
    if not location:
        return None
    if isinstance(location, dict):
        raw = location.get("raw", "")
    else:
        raw = location
    raw_lower = raw.lower()
    for key, city_data in CITY_COORDS.items():
        if key in raw_lower:
            return city_data["name"]
    return None


def get_score_tier(score: float) -> str:
    if score >= 8.0:
        return "HIGH"
    elif score >= 6.5:
        return "MED"
    return "LOW"


def compute_score(candidate: dict) -> dict:
    score = 0
    signals = []

    emp = candidate.get("experience", {}).get("employment_details", {})
    current_roles = emp.get("current", []) or []
    past_roles = emp.get("past", []) or []
    all_roles = current_roles + past_roles

    seen = set()
    unique_roles = []
    for role in all_roles:
        key = (role.get("crustdata_company_id"), role.get("title"))
        if key not in seen:
            seen.add(key)
            unique_roles.append(role)

    default_role = None
    for role in current_roles:
        if role.get("is_default"):
            default_role = role
            break

    frontier_senior = False
    frontier_labs_worked = set()
    had_short_frontier_stint = False
    best_frontier_role = None

    for role in unique_roles:
        company_id = role.get("crustdata_company_id")
        if company_id and company_id in FRONTIER_LAB_IDS:
            if is_intern_title(role.get("title")):
                had_short_frontier_stint = True
                continue
            duration = get_role_duration(role)
            if duration is not None and duration < MIN_ROLE_DURATION:
                had_short_frontier_stint = True
                continue
            frontier_labs_worked.add(company_id)
            if best_frontier_role is None or (duration and duration > (get_role_duration(best_frontier_role) or timedelta(0))):
                best_frontier_role = role
            if is_senior_title(role.get("title")):
                frontier_senior = True

    if frontier_senior:
        score += 3
        signals.append({"type": "senior", "label": "Senior+ at lab"})

    days_since_return = None
    returned_last_12mo = False
    if default_role:
        start_date = parse_date(default_role.get("start_date"))
        loc = default_role.get("location")
        if is_india_location(loc) and start_date:
            days_since_return = (TODAY - start_date).days
            if start_date >= TWELVE_MONTHS_AGO:
                returned_last_12mo = True
                score += 3
                months = days_since_return // 30
                signals.append({"type": "recent_return", "label": f"Returned {months}mo ago"})

    current_headcount = None
    at_sub_50 = False
    if default_role:
        company_id = default_role.get("crustdata_company_id")
        current_headcount = COMPANY_HEADCOUNTS.get(company_id)
        if current_headcount is not None and current_headcount < 50 and is_india_location(default_role.get("location")):
            at_sub_50 = True
            score += 3
            if current_headcount < 10:
                signals.append({"type": "tiny_company", "label": "Sub-10 team"})
            elif current_headcount < 20:
                signals.append({"type": "tiny_company", "label": "Sub-20 team"})
            else:
                signals.append({"type": "tiny_company", "label": "Sub-50 team"})

    is_founder = False
    if default_role and is_founder_title(default_role.get("title")):
        is_founder = True
        score += 4
        title = default_role.get("title", "").lower()
        if "co-founder" in title or "cofounder" in title:
            signals.append({"type": "founder", "label": "Co-founder"})
        elif "ceo" in title:
            signals.append({"type": "founder", "label": "Founder/CEO"})
        else:
            signals.append({"type": "founder", "label": "Founder"})

    if len(frontier_labs_worked) > 1:
        score += 2

    for role in past_roles:
        company_id = role.get("crustdata_company_id")
        if company_id and company_id in FRONTIER_LAB_IDS:
            if is_intern_title(role.get("title")):
                continue
            end_date = parse_date(role.get("end_date"))
            if end_date and end_date >= SIX_MONTHS_AGO:
                score += 2
                break

    if current_headcount is not None and current_headcount >= 1000:
        signals.append({"type": "large_company", "label": "At big tech"})
    elif current_headcount is not None and current_headcount >= 200:
        signals.append({"type": "large_company", "label": "At scale-up"})

    former_lab = None
    former_title = None
    former_tenure_years = None
    former_end_date = None
    if best_frontier_role:
        company_id = best_frontier_role.get("crustdata_company_id")
        former_lab = FRONTIER_LAB_NAMES.get(company_id)
        former_title = best_frontier_role.get("title")
        duration = get_role_duration(best_frontier_role)
        if duration:
            former_tenure_years = round(duration.days / 365.25, 1)
        end_date = parse_date(best_frontier_role.get("end_date"))
        if end_date:
            former_end_date = end_date.strftime("%Y-%m-%d")

    current_role = None
    current_company = None
    current_company_id = None
    current_city = None
    if default_role:
        current_role = default_role.get("title")
        current_company_id = default_role.get("crustdata_company_id")
        current_company = default_role.get("name") or COMPANY_NAMES.get(current_company_id)
        current_city = extract_city(default_role.get("location"))

    name = candidate.get("basic_profile", {}).get("name", "Unknown")
    synthesis = f"{name} worked at {former_lab or 'a frontier lab'}"
    if former_tenure_years:
        synthesis += f" for {former_tenure_years} years"
    if current_company:
        synthesis += f". Now at {current_company}"
        if current_role:
            synthesis += f" as {current_role}"
    synthesis += "."

    return {
        "crustdata_person_id": candidate.get("crustdata_person_id"),
        "name": name,
        "headline": candidate.get("basic_profile", {}).get("headline"),
        "score": score,
        "score_tier": get_score_tier(score),
        "former_lab": former_lab,
        "former_title": former_title,
        "former_tenure_years": former_tenure_years,
        "former_end_date": former_end_date,
        "current_role": current_role,
        "current_company": current_company,
        "current_company_id": current_company_id,
        "current_company_headcount": current_headcount,
        "current_city": current_city,
        "days_since_return": days_since_return,
        "signals": signals,
        "synthesis": synthesis,
        "linkedin_url": candidate.get("social_handles", {}).get("professional_network_identifier", {}).get("profile_url"),
        "frontier_labs_count": len(frontier_labs_worked),
        "had_short_frontier_stint": had_short_frontier_stint,
        "returned_last_12mo": returned_last_12mo,
        "at_sub_50": at_sub_50,
        "is_founder": is_founder,
    }


def main():
    print(f"Using cached headcount data for {len(COMPANY_HEADCOUNTS)} companies\n")

    results = []
    excluded_interns = 0
    for candidate in candidates:
        result = compute_score(candidate)
        if result["had_short_frontier_stint"] and result["frontier_labs_count"] == 0:
            excluded_interns += 1
            continue
        results.append(result)

    results.sort(key=lambda x: x["score"], reverse=True)
    print(f"Excluded {excluded_interns} candidates (interns or <3mo stints at frontier labs)")

    returned_last_12mo = sum(1 for r in results if r.get("returned_last_12mo"))
    at_sub_50 = sum(1 for r in results if r.get("at_sub_50"))
    founders = sum(1 for r in results if r.get("is_founder"))

    city_counts = {}
    for r in results:
        city = r.get("current_city")
        if city:
            city_counts[city] = city_counts.get(city, 0) + 1

    cities_meta = []
    for city_name, count in sorted(city_counts.items(), key=lambda x: -x[1]):
        for data in CITY_COORDS.values():
            if data["name"] == city_name:
                cities_meta.append({
                    "name": city_name,
                    "lat": data["lat"],
                    "lng": data["lng"],
                    "count": count
                })
                break

    output_candidates = []
    for i, r in enumerate(results, 1):
        output_candidates.append({
            "id": str(i),
            "name": r["name"],
            "headline": r["headline"],
            "score": r["score"],
            "score_tier": r["score_tier"],
            "former_lab": r["former_lab"],
            "former_title": r["former_title"],
            "former_tenure_years": r["former_tenure_years"],
            "former_end_date": r["former_end_date"],
            "current_role": r["current_role"],
            "current_company": r["current_company"],
            "current_company_id": r["current_company_id"],
            "current_company_headcount": r["current_company_headcount"],
            "current_city": r["current_city"],
            "days_since_return": r["days_since_return"],
            "signals": r["signals"],
            "synthesis": r["synthesis"],
            "linkedin_url": r["linkedin_url"],
        })

    output = {
        "meta": {
            "total_candidates": len(results),
            "returned_last_12_months": returned_last_12mo,
            "at_sub_50_startups": at_sub_50,
            "founders_or_cofounders": founders,
            "last_updated": TODAY.strftime("%Y-%m-%dT%H:%M:%SZ").replace("00:00:00", "13:00:00"),
            "cities": cities_meta
        },
        "candidates": output_candidates
    }

    print(f"Total candidates processed: {len(candidates)}")
    print(f"Total in output: {len(results)}")
    print(f"Returned last 12 months: {returned_last_12mo}")
    print(f"At sub-50 startups: {at_sub_50}")
    print(f"Founders: {founders}")
    print(f"\nTop 10 candidates by score:\n")

    for i, r in enumerate(results[:10], 1):
        print(f"{i}. {r['name']} (Score: {r['score']}, Tier: {r['score_tier']})")
        print(f"   Former: {r['former_title']} @ {r['former_lab']}")
        print(f"   Current: {r['current_role']} @ {r['current_company']} ({r['current_city']})")
        print(f"   LinkedIn: {r['linkedin_url']}")
        if r['signals']:
            labels = [s['label'] for s in r['signals']]
            print(f"   Signals: {', '.join(labels)}")
        print()

    with open("docs/all_candidate_scores_new.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Saved output to docs/all_candidate_scores_new.json")


if __name__ == "__main__":
    main()
