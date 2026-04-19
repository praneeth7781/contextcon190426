import json
import requests
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

CRUSTDATA_API_URL = "https://api.crustdata.com/web/search/live"
CRUSTDATA_API_KEY = os.environ.get("CRUSTDATA_API_KEY")

JSON_FILE_PATH = os.path.join(os.path.dirname(__file__), "../docs/all_candidate_scores_v2.json")


def search_candidate(name: str, current_company: str) -> list[dict]:
    """Search for candidate using Crustdata API."""
    headers = {
        "Authorization": f"Bearer {CRUSTDATA_API_KEY}",
        "Content-Type": "application/json",
        "x-api-version": "2025-11-01",
    }
    payload = {"query": f"{name} India {current_company}"}

    response = requests.post(CRUSTDATA_API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    data = response.json()
    return data.get("results", [])[:5]


def generate_synthesis(candidate: dict, snippets: list[dict]) -> str:
    """Generate synthesis using Groq API."""
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    candidate_data = {k: v for k, v in candidate.items() if k != "synthesis"}

    snippets_text = "\n".join(
        f"- {s.get('title', '')}: {s.get('snippet', '')}" for s in snippets
    )

    prompt = f"""You are helping VCs quickly evaluate potential founders and technical talent returning from top AI labs to India.

Based on the candidate profile and web search results below, write a 2-3 sentence synthesis highlighting:
- Their AI lab experience and seniority
- What they're building now and why it's interesting
- Any signals of founder/technical quality (previous exits, notable projects, team background)

Candidate Profile:
{json.dumps(candidate_data, indent=2)}

Web Search Results:
{snippets_text}

Write a VC-focused synthesis:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()


def main():
    with open(JSON_FILE_PATH, "r") as f:
        data = json.load(f)

    candidates = data["candidates"][:15]

    for i, candidate in enumerate(candidates):
        name = candidate.get("name", "")
        current_company = candidate.get("current_company", "")

        print(f"[{i+1}/15] Processing {name}...")

        try:
            snippets = search_candidate(name, current_company)
            print(f"  Found {len(snippets)} search results")

            synthesis = generate_synthesis(candidate, snippets)
            candidate["synthesis"] = synthesis
            print(f"  Generated synthesis: {synthesis[:80]}...")

        except Exception as e:
            print(f"  Error processing {name}: {e}")
            continue

    with open(JSON_FILE_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print("\nDone! Updated synthesis for first 15 candidates.")


if __name__ == "__main__":
    main()
