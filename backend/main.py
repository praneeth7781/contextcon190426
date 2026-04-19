import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API",
    version="0.1.0",
)

CRUSTDATA_API_KEY = os.environ.get("CRUSTDATA_API_KEY", "")
CRUSTDATA_BASE_URL = "https://api.crustdata.com"


class Condition(BaseModel):
    field: str
    type: str
    value: Any


class Filters(BaseModel):
    op: str
    conditions: list[Condition]


class PersonSearchRequest(BaseModel):
    filters: Filters
    limit: int = 10
    cursor: str | None = None


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


TODAY = datetime(2026, 4, 19)
TWELVE_MONTHS_AGO = TODAY - timedelta(days=365)
SIX_MONTHS_AGO = TODAY - timedelta(days=180)

SENIOR_TITLES = ["senior", "staff", "principal", "lead", "director", "vp", "head", "chief", "manager", "architect"]
FOUNDER_TITLES = ["founder", "co-founder", "cofounder", "ceo"]

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
with open(os.path.join(DOCS_DIR, "company_ids.json"), "r") as f:
    frontier_labs = json.load(f)
FRONTIER_LAB_IDS = set(int(v) for v in frontier_labs.values())


def parse_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("T00:00:00", ""))
    except Exception:
        return None


def is_senior_title(title: str | None) -> bool:
    if not title:
        return False
    title_lower = title.lower()
    return any(s in title_lower for s in SENIOR_TITLES)


def is_founder_title(title: str | None) -> bool:
    if not title:
        return False
    title_lower = title.lower()
    return any(f in title_lower for f in FOUNDER_TITLES)


def is_india_location(location: dict | str | None) -> bool:
    if not location:
        return False
    if isinstance(location, dict):
        raw = location.get("raw", "")
    else:
        raw = location
    return "india" in raw.lower()


def compute_score(candidate: dict, company_headcounts: dict[int, int | None]) -> dict:
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
    for role in unique_roles:
        company_id = role.get("crustdata_company_id")
        if company_id and company_id in FRONTIER_LAB_IDS:
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
        headcount = company_headcounts.get(company_id)
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
    }


async def fetch_company_headcounts(company_ids: list[int]) -> dict[int, int | None]:
    if not company_ids or not CRUSTDATA_API_KEY:
        return {}

    headcounts = {}
    batch_size = 100

    async with httpx.AsyncClient() as client:
        for i in range(0, len(company_ids), batch_size):
            batch = company_ids[i:i + batch_size]
            response = await client.post(
                f"{CRUSTDATA_BASE_URL}/company/search",
                headers={
                    "Authorization": f"Bearer {CRUSTDATA_API_KEY}",
                    "Content-Type": "application/json",
                    "x-api-version": "2025-11-01",
                },
                json={
                    "filters": {
                        "field": "crustdata_company_id",
                        "type": "in",
                        "value": batch,
                    },
                    "fields": ["crustdata_company_id", "headcount.total", "locations"],
                    "limit": batch_size,
                },
                timeout=30.0,
            )
            if response.status_code == 200:
                data = response.json()
                for company in data.get("companies", []):
                    cid = company.get("crustdata_company_id")
                    total = company.get("headcount", {}).get("total")
                    if cid:
                        headcounts[cid] = total

    return headcounts


@app.get("/candidates/score")
async def score_candidates():
    logger.info("Loading candidates and computing scores with company data")

    with open(os.path.join(DOCS_DIR, "indian_candidates_raw.json"), "r") as f:
        candidates = json.load(f)

    current_company_ids = set()
    for candidate in candidates:
        emp = candidate.get("experience", {}).get("employment_details", {})
        for role in emp.get("current", []) or []:
            if role.get("is_default") and role.get("crustdata_company_id"):
                current_company_ids.add(role["crustdata_company_id"])

    logger.info(f"Fetching headcount for {len(current_company_ids)} companies")
    company_headcounts = await fetch_company_headcounts(list(current_company_ids))
    logger.info(f"Got headcount data for {len(company_headcounts)} companies")

    results = []
    for candidate in candidates:
        result = compute_score(candidate, company_headcounts)
        results.append(result)

    results.sort(key=lambda x: x["score"], reverse=True)
    top_50 = results[:50]

    return {
        "total_candidates": len(candidates),
        "companies_fetched": len(company_headcounts),
        "top_candidates": top_50,
    }


@app.post("/person/search")
async def person_search(request: PersonSearchRequest):
    logger.info("Received person search request")
    logger.info(f"Filters: {request.filters.op} with {len(request.filters.conditions)} conditions")
    logger.info(f"Limit: {request.limit}, Cursor: {request.cursor}")

    if not CRUSTDATA_API_KEY:
        logger.error("CRUSTDATA_API_KEY not configured")
        raise HTTPException(status_code=500, detail="CRUSTDATA_API_KEY not configured")

    logger.info(f"Calling Crustdata API: {CRUSTDATA_BASE_URL}/person/search")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CRUSTDATA_BASE_URL}/person/search",
            headers={
                "Authorization": f"Bearer {CRUSTDATA_API_KEY}",
                "Content-Type": "application/json",
                "x-api-version": "2025-11-01",
            },
            json=request.model_dump(),
            timeout=30.0,
        )

    logger.info(f"Crustdata response status: {response.status_code}")

    if response.status_code != 200:
        logger.error(f"Crustdata API error: {response.text}")
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    result_count = len(data.get("data", []))
    has_next = "next_cursor" in data and data["next_cursor"] is not None
    logger.info(f"Returning {result_count} results, has_next_cursor: {has_next}")

    return data
