import json
from datetime import datetime, timedelta

with open("docs/indian_candidates_raw.json", "r") as f:
    candidates = json.load(f)

with open("docs/company_ids.json", "r") as f:
    frontier_labs = json.load(f)

with open("docs/candidate_companies_data.json", "r") as f:
    companies_data = json.load(f)

FRONTIER_LAB_IDS = set(int(v) for v in frontier_labs.values())
COMPANY_HEADCOUNTS = {
    int(cid): c.get("headcount", {}).get("total")
    for cid, c in companies_data.get("companies", {}).items()
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


def compute_score(candidate: dict) -> dict:
    score = 0
    reasons = []

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
            if is_senior_title(role.get("title")):
                frontier_senior = True

    if frontier_senior:
        score += 3
        reasons.append("Senior+ at frontier lab (+3)")

    if default_role:
        start_date = parse_date(default_role.get("start_date"))
        loc = default_role.get("location")
        if is_india_location(loc) and start_date and start_date >= TWELVE_MONTHS_AGO:
            score += 3
            reasons.append("Current India role started <12mo (+3)")

    if default_role:
        company_id = default_role.get("crustdata_company_id")
        headcount = COMPANY_HEADCOUNTS.get(company_id)
        if headcount is not None and headcount < 50 and is_india_location(default_role.get("location")):
            score += 3
            reasons.append(f"India startup <50 headcount ({headcount}) (+3)")

    if default_role and is_founder_title(default_role.get("title")):
        score += 4
        reasons.append("Founder/Co-founder/CEO (+4)")

    if len(frontier_labs_worked) > 1:
        score += 2
        reasons.append(f"Multiple frontier labs ({len(frontier_labs_worked)}) (+2)")

    for role in past_roles:
        company_id = role.get("crustdata_company_id")
        if company_id and company_id in FRONTIER_LAB_IDS:
            if is_intern_title(role.get("title")):
                continue
            end_date = parse_date(role.get("end_date"))
            if end_date and end_date >= SIX_MONTHS_AGO:
                score += 2
                reasons.append("Recent frontier lab departure <6mo (+2)")
                break

    return {
        "crustdata_person_id": candidate.get("crustdata_person_id"),
        "name": candidate.get("basic_profile", {}).get("name"),
        "headline": candidate.get("basic_profile", {}).get("headline"),
        "location": candidate.get("basic_profile", {}).get("location", {}).get("raw"),
        "current_title": candidate.get("basic_profile", {}).get("current_title"),
        "linkedin_url": candidate.get("social_handles", {}).get("professional_network_identifier", {}).get("profile_url"),
        "score": score,
        "reasons": reasons,
        "frontier_labs_count": len(frontier_labs_worked),
        "had_short_frontier_stint": had_short_frontier_stint,
    }


def main():
    print(f"Using cached headcount data for {len(COMPANY_HEADCOUNTS)} companies\n")

    results = []
    excluded_interns = 0
    for candidate in candidates:
        result = compute_score(candidate)
        if result["had_short_frontier_stint"]:
            excluded_interns += 1
            continue
        results.append(result)

    results.sort(key=lambda x: x["score"], reverse=True)
    print(f"Excluded {excluded_interns} candidates (interns or <3mo stints at frontier labs)")

    print(f"Total candidates processed: {len(candidates)}")
    print(f"Top 10 candidates by score:\n")

    for i, r in enumerate(results[:10], 1):
        print(f"{i}. {r['name']} (Score: {r['score']})")
        print(f"   Title: {r['current_title']}")
        print(f"   Location: {r['location']}")
        print(f"   LinkedIn: {r['linkedin_url']}")
        if r['reasons']:
            print(f"   Reasons: {', '.join(r['reasons'])}")
        print()

    with open("docs/all_candidate_scores.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved all {len(results)} candidates to docs/all_candidate_scores.json")


if __name__ == "__main__":
    main()
