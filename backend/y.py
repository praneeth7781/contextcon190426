import asyncio
import json
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

with open("docs/indian_candidates_raw.json", "r") as f:
    candidates = json.load(f)

CRUSTDATA_API_KEY = os.environ.get("CRUSTDATA_API_KEY", "")
CRUSTDATA_BASE_URL = "https://api.crustdata.com"


def extract_company_ids(candidates: list[dict]) -> list[int]:
    company_ids = set()
    for candidate in candidates:
        emp = candidate.get("experience", {}).get("employment_details", {})
        for role in emp.get("current", []) or []:
            if role.get("crustdata_company_id"):
                company_ids.add(role["crustdata_company_id"])
        for role in emp.get("past", []) or []:
            if role.get("crustdata_company_id"):
                company_ids.add(role["crustdata_company_id"])
    return list(company_ids)


async def fetch_companies(company_ids: list[int]) -> list[dict]:
    if not company_ids or not CRUSTDATA_API_KEY:
        print("Missing company IDs or API key")
        return []

    companies = []
    batch_size = 100

    async with httpx.AsyncClient() as client:
        for i in range(0, len(company_ids), batch_size):
            batch = company_ids[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(company_ids) + batch_size - 1) // batch_size
            print(f"Fetching batch {batch_num}/{total_batches} ({len(batch)} companies)...")

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
                    "limit": batch_size,
                },
                timeout=60.0,
            )

            if response.status_code == 200:
                data = response.json()
                batch_companies = data.get("companies", [])
                companies.extend(batch_companies)
                print(f"  Got {len(batch_companies)} companies")
            else:
                print(f"  API error: {response.status_code}")
                print(f"  {response.text[:200]}")

    return companies


async def main():
    company_ids = extract_company_ids(candidates)
    print(f"Found {len(company_ids)} unique companies from {len(candidates)} candidates\n")

    companies = await fetch_companies(company_ids)

    company_lookup = {c["crustdata_company_id"]: c for c in companies}

    output = {
        "fetched_at": "2026-04-19",
        "total_candidates": len(candidates),
        "unique_companies_found": len(company_ids),
        "companies_fetched": len(companies),
        "companies": company_lookup,
    }

    output_path = "docs/candidate_companies_data.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved {len(companies)} companies to {output_path}")

    if companies:
        sample = companies[0]
        print(f"\nSample fields available ({len(sample)} fields):")
        for key in sorted(sample.keys())[:20]:
            print(f"  - {key}")
        if len(sample) > 20:
            print(f"  ... and {len(sample) - 20} more fields")


if __name__ == "__main__":
    asyncio.run(main())
