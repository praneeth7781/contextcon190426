import json
import os
from datetime import datetime

import httpx

BASE_URL = "http://localhost:9000"
TEMP_FILE = "person_search_temp.json"


def search_all_persons(filters: dict, limit: int = 100) -> list[dict]:
    """Fetch all persons matching filters, handling pagination automatically."""
    all_results = []
    cursor = None
    page = 0

    print(f"Starting search with limit={limit}")
    print(f"Target URL: {BASE_URL}/person/search")
    print(f"Temp file: {TEMP_FILE}")

    with httpx.Client(timeout=60.0) as client:
        while True:
            page += 1
            payload = {"filters": filters, "limit": limit, "sorts": [{"field": "professional_network.connections", "order": "desc"}]}
            if cursor:
                payload["cursor"] = cursor

            print(f"\n--- Page {page} ---")
            print(f"Sending request...")

            response = client.post(f"{BASE_URL}/person/search", json=payload)
            print(f"Response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()

            print(f"Response keys: {data.keys() if isinstance(data, dict) else type(data)}")
            print(f"Total count: {data.get('total_count', 'N/A')}")
            results = data.get("profiles", [])
            all_results.extend(results)
            print(f"Fetched {len(results)} results (total: {len(all_results)})")

            with open(TEMP_FILE, "w") as f:
                json.dump(all_results, f, indent=2)
            print(f"Saved to {TEMP_FILE}")

            cursor = data.get("next_cursor")
            if cursor:
                print(f"Next cursor: {cursor[:20]}...")
            else:
                print("No more pages")
                break

    print(f"\nPagination complete. Total pages: {page}")
    return all_results


if __name__ == "__main__":
    filters = {
        "op": "and",
        "conditions": [
            {
                "field": "experience.employment_details.past.company_id",
                "type": "in",
                "value": [
                    "635252",
                    "631466",
                    "1034291",
                    "812301",
                    "6036351",
                    "629012",
                    "662966",
                    "811069",
                    "780194",
                    "780131",
                    "780568",
                    "632824",
                    "710952",
                    "4372218",
                    "952346",
                    "17046658"
                ],
            },
            {
                "field": "experience.employment_details.current.company_id",
                "type": "not_in",
                "value": [
                    "635252",
                    "631466",
                    "1034291",
                    "812301",
                    "6036351",
                    "629012",
                    "662966",
                    "811069",
                    "780194",
                    "780131",
                    "780568",
                    "632824",
                    "710952",
                    "4372218",
                    "952346",
                    "17046658"
                ],
            },
            # {
            #     "field": "recently_changed_jobs",
            #     "type": "=",
            #     "value": True,
            # },
            {
                "field": "basic_profile.location.country",
                "type": "=",
                "value": "India"
            }
        ],
    }

    print("=" * 50)
    print("Person Search - Paginated")
    print("=" * 50)
    print(f"Filter conditions: {len(filters['conditions'])}")

    results = search_all_persons(filters, limit=100)
    print(f"\n{'=' * 50}")
    print(f"Total results: {len(results)}")

    filename = f"person_search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {filename}")

    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)
        print(f"Cleaned up {TEMP_FILE}")
