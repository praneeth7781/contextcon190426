import json
import re
from datetime import datetime, timedelta

with open("docs/indian_candidates_raw.json", "r") as f:
    candidates = json.load(f)

with open("docs/company_ids.json", "r") as f:
    frontier_labs = json.load(f)

with open("docs/candidate_companies_data.json", "r") as f:
    companies_data = json.load(f)

FRONTIER_LAB_IDS = set(int(v) for v in frontier_labs.values())
FRONTIER_LAB_NAMES = {int(v): k for k, v in frontier_labs.items()}

TIER1_LABS = {"Anthropic", "OpenAI", "Google DeepMind"}

EMPLOYEE_RANGE_TO_MIDPOINT = {
    "1-10": 5,
    "11-50": 30,
    "51-200": 125,
    "201-500": 350,
    "501-1000": 750,
    "1001-5000": 3000,
    "5001-10000": 7500,
    "10001+": 15000,
}

def get_best_headcount(basic_info: dict, headcount_data: dict) -> int | None:
    range_str = basic_info.get("employee_count_range")
    linkedin_count = EMPLOYEE_RANGE_TO_MIDPOINT.get(range_str)
    crustdata_count = headcount_data.get("total")
    if linkedin_count and crustdata_count:
        return max(linkedin_count, crustdata_count)
    return linkedin_count or crustdata_count

COMPANIES = {}
for cid, c in companies_data.get("companies", {}).items():
    if c is None:
        continue
    basic_info = c.get("basic_info") or {}
    headcount_data = c.get("headcount") or {}
    funding_data = c.get("funding") or {}
    COMPANIES[int(cid)] = {
        "name": basic_info.get("name") or c.get("name", "Unknown"),
        "headcount": get_best_headcount(basic_info, headcount_data),
        "headcount_raw": headcount_data.get("total"),
        "employee_range": basic_info.get("employee_count_range"),
        "funding_total": funding_data.get("total_investment_usd"),
        "last_round": funding_data.get("last_round_type"),
        "investors": funding_data.get("investors") or [],
        "year_founded": basic_info.get("year_founded"),
    }

TIER1_INVESTORS = {
    "a16z", "andreessen horowitz", "sequoia", "sequoia capital", "accel",
    "y combinator", "yc", "benchmark", "greylock", "index ventures",
    "lightspeed", "tiger global", "coatue", "insight partners", "general catalyst"
}

TIER1_GLOBAL_SCHOOLS = {
    "stanford", "mit", "massachusetts institute of technology", "cmu",
    "carnegie mellon", "berkeley", "uc berkeley", "harvard", "oxford",
    "cambridge", "caltech", "princeton", "yale", "columbia"
}

TIER1_INDIA_SCHOOLS = {
    "iit bombay", "iit delhi", "iit madras", "iit kanpur", "iit kharagpur",
    "iisc", "indian institute of science", "iim ahmedabad", "iim bangalore",
    "iim calcutta", "iim a", "iim b", "iim c"
}

TIER2_INDIA_SCHOOLS = {
    "iit", "nit", "bits", "bits pilani", "iiit", "iiit hyderabad", "iiit-h",
    "iim", "isr", "ism dhanbad"
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
MIN_ROLE_DURATION = timedelta(days=90)

WEIGHTS = {
    "lab_experience": 0.20,
    "seniority": 0.20,
    "recency": 0.25,
    "startup_fit": 0.15,
    "education": 0.10,
    "company_quality": 0.10,
}


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


def is_india_location(location: dict | str | None) -> bool:
    if not location:
        return False
    raw = location.get("raw", "") if isinstance(location, dict) else location
    return "india" in raw.lower()


def extract_city(location: dict | str | None) -> str | None:
    if not location:
        return None
    raw = location.get("raw", "") if isinstance(location, dict) else location
    raw_lower = raw.lower()
    for key, city_data in CITY_COORDS.items():
        if key in raw_lower:
            return city_data["name"]
    return None


def is_intern_title(title: str | None) -> bool:
    if not title:
        return False
    title_lower = title.lower()
    return any(t in title_lower for t in ["intern", "internship", "trainee", "apprentice", "co-op"])


def compute_seniority_score(title: str | None) -> tuple[int, str]:
    if not title:
        return 5, "Unknown"
    title_lower = title.lower()

    if any(t in title_lower for t in ["director", "vp", "vice president", "head of", "chief"]):
        return 10, "Director/VP+"
    if any(t in title_lower for t in ["staff", "principal"]):
        return 9, "Staff/Principal"
    if "senior" in title_lower:
        return 7, "Senior"
    if any(t in title_lower for t in ["lead", "manager"]):
        return 8, "Lead/Manager"
    if any(t in title_lower for t in ["associate", "junior", "entry"]):
        return 3, "Associate/Junior"
    if any(t in title_lower for t in ["intern", "fellow", "trainee"]):
        return 2, "Intern/Fellow"
    return 5, "Mid-level"


def compute_lab_experience_score(frontier_roles: list, frontier_labs_count: int) -> tuple[int, str]:
    if not frontier_roles:
        return 0, "No frontier lab experience"

    total_tenure_days = 0
    best_lab = None
    for role in frontier_roles:
        duration = get_role_duration(role)
        if duration:
            total_tenure_days += duration.days
        company_id = role.get("crustdata_company_id")
        lab_name = FRONTIER_LAB_NAMES.get(company_id)
        if lab_name and lab_name in TIER1_LABS:
            best_lab = lab_name
        elif not best_lab and lab_name:
            best_lab = lab_name

    tenure_years = total_tenure_days / 365.25

    if tenure_years >= 3:
        base = 10
    elif tenure_years >= 2:
        base = 8
    elif tenure_years >= 1:
        base = 6
    elif tenure_years >= 0.5:
        base = 4
    else:
        base = 2

    if frontier_labs_count > 1:
        base = min(10, base + 2)
    if best_lab in TIER1_LABS:
        base = min(10, base + 1)

    breakdown = f"{tenure_years:.1f}yr"
    if best_lab:
        breakdown += f" at {best_lab}"
    if frontier_labs_count > 1:
        breakdown += f" (+{frontier_labs_count - 1} more labs)"

    return base, breakdown


def compute_recency_score(frontier_roles: list, current_role: dict | None) -> tuple[int, str]:
    if not frontier_roles:
        return 0, "No frontier experience"

    most_recent_end = None
    for role in frontier_roles:
        end = parse_date(role.get("end_date"))
        if end and (most_recent_end is None or end > most_recent_end):
            most_recent_end = end

    if most_recent_end is None:
        return 5, "Unknown departure date"

    days_since = (TODAY - most_recent_end).days

    if days_since <= 90:
        base = 10
        breakdown = f"Left {days_since // 30}mo ago"
    elif days_since <= 180:
        base = 8
        breakdown = f"Left {days_since // 30}mo ago"
    elif days_since <= 365:
        base = 6
        breakdown = f"Left {days_since // 30}mo ago"
    elif days_since <= 730:
        base = 4
        breakdown = f"Left {days_since // 365:.1f}yr ago"
    elif days_since <= 1095:
        base = 2
        breakdown = f"Left {days_since // 365:.1f}yr ago"
    else:
        base = 1
        breakdown = f"Left {days_since // 365:.1f}yr ago"

    if current_role:
        start = parse_date(current_role.get("start_date"))
        if start and is_india_location(current_role.get("location")):
            days_in_india = (TODAY - start).days
            if days_in_india < 180:
                base = min(10, base + 2)
                breakdown += f", returned {days_in_india // 30}mo ago"

    return base, breakdown


def compute_startup_fit_score(current_role: dict | None) -> tuple[int, str]:
    if not current_role:
        return 5, "No current role"

    score = 0
    parts = []

    company_id = current_role.get("crustdata_company_id")
    company = COMPANIES.get(company_id, {})

    last_round = company.get("last_round", "")
    if last_round in ["pre_seed", "seed", "angel"]:
        score += 4
        parts.append("Seed stage")
    elif last_round == "series_a":
        score += 3
        parts.append("Series A")
    elif last_round == "series_b":
        score += 2
        parts.append("Series B")

    headcount = company.get("headcount")
    if headcount:
        if headcount < 10:
            score += 3
            parts.append(f"{headcount} people")
        elif headcount < 50:
            score += 2
            parts.append(f"{headcount} people")
        elif headcount < 200:
            score += 1
            parts.append(f"{headcount} people")

    title = current_role.get("title", "").lower()
    if any(t in title for t in ["founder", "co-founder", "cofounder"]) and "founder's office" not in title:
        score += 3
        parts.append("Founder")
    elif "founding" in title:
        score += 2
        parts.append("Founding member")
    elif "ceo" in title:
        score += 3
        parts.append("CEO")

    return min(10, score), ", ".join(parts) if parts else "Corporate"


def compute_education_score(education: dict | None) -> tuple[int, str]:
    if not education:
        return 5, "Unknown"

    schools = education.get("schools", [])
    if not schools:
        return 5, "No education data"

    best_score = 5
    best_school = "Other"
    has_phd = False
    has_masters = False

    for school in schools:
        school_name = (school.get("school") or "").lower()
        degree = (school.get("degree") or "").lower()

        if "phd" in degree or "doctor" in degree:
            has_phd = True
        if "master" in degree or "mtech" in degree or "mba" in degree or "m.tech" in degree:
            has_masters = True

        for tier1 in TIER1_GLOBAL_SCHOOLS:
            if tier1 in school_name:
                if best_score < 10:
                    best_score = 10
                    best_school = school.get("school", tier1.title())
                break

        for tier1 in TIER1_INDIA_SCHOOLS:
            if tier1 in school_name:
                if best_score < 9:
                    best_score = 9
                    best_school = school.get("school", tier1.upper())
                break

        for tier2 in TIER2_INDIA_SCHOOLS:
            if tier2 in school_name and best_score < 7:
                best_score = 7
                best_school = school.get("school", tier2.upper())
                break

    if has_phd:
        best_score = min(10, best_score + 2)
    elif has_masters:
        best_score = min(10, best_score + 1)

    degree_suffix = ""
    if has_phd:
        degree_suffix = " (PhD)"
    elif has_masters:
        degree_suffix = " (Masters)"

    return best_score, f"{best_school[:30]}{degree_suffix}"


def compute_company_quality_score(current_role: dict | None, is_at_frontier: bool) -> tuple[int, str]:
    if is_at_frontier:
        return 10, "At frontier lab"

    if not current_role:
        return 5, "No current role"

    company_id = current_role.get("crustdata_company_id")
    company = COMPANIES.get(company_id, {})

    if not company:
        return 5, "Unknown company"

    score = 0
    parts = []

    funding = company.get("funding_total")
    if funding:
        if funding >= 100_000_000:
            score += 3
            parts.append(f"${funding / 1_000_000:.0f}M raised")
        elif funding >= 10_000_000:
            score += 2
            parts.append(f"${funding / 1_000_000:.0f}M raised")
        elif funding >= 1_000_000:
            score += 1
            parts.append(f"${funding / 1_000_000:.1f}M raised")

    investors = company.get("investors", []) or []
    has_tier1 = False
    for inv in investors:
        if any(t1 in inv.lower() for t1 in TIER1_INVESTORS):
            has_tier1 = True
            break
    if has_tier1:
        score += 2
        parts.append("Tier-1 investors")

    year_founded = company.get("year_founded")
    headcount = company.get("headcount")
    if year_founded and headcount:
        try:
            age = 2026 - int(year_founded)
            if age < 3 and headcount > 50:
                score += 2
                parts.append("Fast growth")
            elif age < 5 and headcount > 100:
                score += 1
                parts.append("Growing")
        except (ValueError, TypeError):
            pass

    return min(10, score), ", ".join(parts) if parts else "Early stage"


def get_score_tier(composite: float) -> str:
    if composite >= 7.0:
        return "HIGH"
    elif composite >= 5.0:
        return "MED"
    return "LOW"


def compute_scores(candidate: dict) -> dict:
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

    frontier_roles = []
    frontier_labs_worked = set()
    best_frontier_role = None
    had_short_stint = False

    for role in unique_roles:
        company_id = role.get("crustdata_company_id")
        if company_id and company_id in FRONTIER_LAB_IDS:
            if is_intern_title(role.get("title")):
                had_short_stint = True
                continue
            duration = get_role_duration(role)
            if duration is not None and duration < MIN_ROLE_DURATION:
                had_short_stint = True
                continue
            frontier_roles.append(role)
            frontier_labs_worked.add(company_id)
            if best_frontier_role is None or (duration and duration > (get_role_duration(best_frontier_role) or timedelta(0))):
                best_frontier_role = role

    is_at_frontier = False
    if default_role:
        is_at_frontier = default_role.get("crustdata_company_id") in FRONTIER_LAB_IDS

    lab_exp_score, lab_exp_breakdown = compute_lab_experience_score(frontier_roles, len(frontier_labs_worked))

    seniority_score, seniority_breakdown = 0, "N/A"
    if best_frontier_role:
        seniority_score, seniority_breakdown = compute_seniority_score(best_frontier_role.get("title"))

    recency_score, recency_breakdown = compute_recency_score(frontier_roles, default_role)
    startup_fit_score, startup_fit_breakdown = compute_startup_fit_score(default_role)
    education_score, education_breakdown = compute_education_score(candidate.get("education"))
    company_quality_score, company_quality_breakdown = compute_company_quality_score(default_role, is_at_frontier)

    composite = (
        lab_exp_score * WEIGHTS["lab_experience"] +
        seniority_score * WEIGHTS["seniority"] +
        recency_score * WEIGHTS["recency"] +
        startup_fit_score * WEIGHTS["startup_fit"] +
        education_score * WEIGHTS["education"] +
        company_quality_score * WEIGHTS["company_quality"]
    )
    composite = round(composite, 1)

    signals = []
    if seniority_score >= 7:
        signals.append({"type": "senior", "label": seniority_breakdown})
    if startup_fit_score >= 6 and "Founder" in startup_fit_breakdown:
        signals.append({"type": "founder", "label": "Founder"})
    if recency_score >= 8:
        signals.append({"type": "recent_return", "label": recency_breakdown.split(",")[0]})

    current_headcount = None
    current_headcount_range = None
    if default_role:
        company_id = default_role.get("crustdata_company_id")
        company = COMPANIES.get(company_id, {})
        current_headcount = company.get("headcount")
        current_headcount_range = company.get("employee_range")
        if current_headcount and current_headcount < 50:
            if current_headcount < 10:
                signals.append({"type": "tiny_company", "label": "Sub-10 team"})
            elif current_headcount < 20:
                signals.append({"type": "tiny_company", "label": "Sub-20 team"})
            else:
                signals.append({"type": "tiny_company", "label": "Sub-50 team"})
        elif current_headcount and current_headcount >= 1000:
            signals.append({"type": "large_company", "label": "At big tech"})

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
        end = parse_date(best_frontier_role.get("end_date"))
        if end:
            former_end_date = end.strftime("%Y-%m-%d")

    current_role_title = None
    current_company = None
    current_company_id = None
    current_city = None
    days_since_return = None

    if default_role:
        current_role_title = default_role.get("title")
        current_company_id = default_role.get("crustdata_company_id")
        current_company = default_role.get("name") or COMPANIES.get(current_company_id, {}).get("name")
        current_city = extract_city(default_role.get("location"))
        start = parse_date(default_role.get("start_date"))
        if start and is_india_location(default_role.get("location")):
            days_since_return = (TODAY - start).days

    name = candidate.get("basic_profile", {}).get("name", "Unknown")
    synthesis = f"{name} worked at {former_lab or 'a frontier lab'}"
    if former_tenure_years:
        synthesis += f" for {former_tenure_years} years"
    if current_company:
        synthesis += f". Now at {current_company}"
        if current_role_title:
            synthesis += f" as {current_role_title}"
    synthesis += "."

    return {
        "crustdata_person_id": candidate.get("crustdata_person_id"),
        "name": name,
        "headline": candidate.get("basic_profile", {}).get("headline"),
        "scores": {
            "lab_experience": lab_exp_score,
            "seniority": seniority_score,
            "recency": recency_score,
            "startup_fit": startup_fit_score,
            "education": education_score,
            "company_quality": company_quality_score,
            "composite": composite,
        },
        "score_breakdown": {
            "lab_experience": lab_exp_breakdown,
            "seniority": seniority_breakdown,
            "recency": recency_breakdown,
            "startup_fit": startup_fit_breakdown,
            "education": education_breakdown,
            "company_quality": company_quality_breakdown,
        },
        "score": composite,
        "score_tier": get_score_tier(composite),
        "former_lab": former_lab,
        "former_title": former_title,
        "former_tenure_years": former_tenure_years,
        "former_end_date": former_end_date,
        "current_role": current_role_title,
        "current_company": current_company,
        "current_company_id": current_company_id,
        "current_company_headcount": current_headcount_range or current_headcount,
        "current_city": current_city,
        "days_since_return": days_since_return,
        "signals": signals,
        "synthesis": synthesis,
        "linkedin_url": candidate.get("social_handles", {}).get("professional_network_identifier", {}).get("profile_url"),
        "frontier_labs_count": len(frontier_labs_worked),
        "had_short_frontier_stint": had_short_stint,
    }


def main():
    print(f"Processing {len(candidates)} candidates with 6-dimensional scoring\n")

    results = []
    excluded = 0
    for candidate in candidates:
        result = compute_scores(candidate)
        if result["had_short_frontier_stint"] and result["frontier_labs_count"] == 0:
            excluded += 1
            continue
        results.append(result)

    results.sort(key=lambda x: x["scores"]["composite"], reverse=True)

    print(f"Excluded {excluded} candidates (interns or <3mo stints only)")
    print(f"Total in output: {len(results)}\n")

    print("Score distribution by dimension:")
    for dim in ["lab_experience", "seniority", "recency", "startup_fit", "education", "company_quality"]:
        scores = [r["scores"][dim] for r in results]
        avg = sum(scores) / len(scores) if scores else 0
        zeros = sum(1 for s in scores if s == 0)
        print(f"  {dim:18} avg={avg:.1f}  zeros={zeros}")

    composites = [r["scores"]["composite"] for r in results]
    print(f"\nComposite: avg={sum(composites)/len(composites):.1f}  "
          f"min={min(composites):.1f}  max={max(composites):.1f}")

    high = sum(1 for r in results if r["score_tier"] == "HIGH")
    med = sum(1 for r in results if r["score_tier"] == "MED")
    low = sum(1 for r in results if r["score_tier"] == "LOW")
    print(f"Tiers: HIGH={high}  MED={med}  LOW={low}\n")

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
            "scores": r["scores"],
            "score_breakdown": r["score_breakdown"],
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
            "scoring_version": "v2_multidimensional",
            "dimensions": list(WEIGHTS.keys()),
            "weights": WEIGHTS,
            "tier_thresholds": {"HIGH": 7.0, "MED": 5.0},
            "last_updated": TODAY.strftime("%Y-%m-%dT13:00:00Z"),
            "cities": cities_meta
        },
        "candidates": output_candidates
    }

    print("Top 10 candidates:\n")
    for i, r in enumerate(results[:10], 1):
        print(f"{i}. {r['name']} (Composite: {r['scores']['composite']})")
        print(f"   Scores: exp={r['scores']['lab_experience']} sen={r['scores']['seniority']} "
              f"rec={r['scores']['recency']} fit={r['scores']['startup_fit']} "
              f"edu={r['scores']['education']} co={r['scores']['company_quality']}")
        print(f"   {r['former_title']} @ {r['former_lab']} → {r['current_role']} @ {r['current_company']}")
        print()

    with open("docs/all_candidate_scores_v2.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Saved to docs/all_candidate_scores_v2.json")


if __name__ == "__main__":
    main()
