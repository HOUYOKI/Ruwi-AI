"""
Standalone test harness for the Layer 1 Narrator loop.

Provider-agnostic — set the three env vars below to whichever backend
you're testing. No provider is hardcoded or defaulted in this project.


Example: GLM via Z.ai (direct)
    export GLM_BASE_URL="https://api.z.ai/api/paas/v4"
    export GLM_API_KEY="sk-..."
    export NARRATOR_MODEL="z-ai/glm-5.2"
    python test_run.py

Example: Kimi (Moonshot, direct)
    export LLM_BASE_URL="https://api.moonshot.ai/v1"
    export LLM_API_KEY="sk-..."
    export NARRATOR_MODEL="kimi-k2.6"
    python test_run.py
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from .narrator import run_narrator_turn


# adjust this if your data/ folder sits somewhere else relative to
# backend/agents/narrator/test_run.py — this assumes repo_root/data/artifacts.json
ARTIFACTS_PATH = Path(__file__).resolve().parents[3] / "data" / "artifacts.json"

with open(ARTIFACTS_PATH, encoding="utf-8") as f:
    _raw_artifacts = json.load(f)

# keyed by STRING id, matching what the model will actually send in a
# get_artifact tool call — this is the fix for the int/str mismatch above
MOCK_ARTIFACTS = {str(a["id"]): a for a in _raw_artifacts}

"""MOCK_ARTIFACTS = {
    "art_001": {
        "id": "art_001",
        "name": "Meteorite Fragment",
        "age": "Pre-Islamic era",
        "location": "Najran region",
        "material": "Iron-nickel meteorite",
        "description": "A fragment believed to be part of a larger meteorite "
                        "that fell in the region, later worked by local smiths.",
    },
    "art_002": {
        "id": "art_002",
        "name": "Bronze Incense Burner",
        "age": "1st century BCE",
        "location": "Najran region",
        "material": "Bronze",
        "description": "An incense burner used in trade-route rituals along "
                        "the ancient incense road.",
    },
}"""

def looks_like_decline(text: str) -> bool:
    markers = [
        "don't have", "do not have", "don't have information",
        "I'm not able to", "not verified", "can't tell you confidently",
        "no verified connection",
    ]
    return any(m.lower() in text.lower() for m in markers)

def main() -> None:
    provider = os.environ.get("NARRATOR_PROVIDER")
    model = os.environ.get("NARRATOR_MODEL")
 
    if not provider or not model:
        print(
            "Missing NARRATOR_PROVIDER and/or NARRATOR_MODEL.\n\n"
            "This module doesn't default to any provider — set both, plus "
            "that provider's two env vars ({PROVIDER}_BASE_URL and "
            "{PROVIDER}_API_KEY), before running. Example for GLM:\n\n"
            "  export NARRATOR_PROVIDER=glm\n"
            "  export NARRATOR_MODEL=glm-4.7\n"
            "  export GLM_BASE_URL=https://api.z.ai/api/paas/v4\n"
            "  export GLM_API_KEY=sk-...\n"
        )
        return
 
    prefix = provider.upper()
    missing = [v for v in (f"{prefix}_BASE_URL", f"{prefix}_API_KEY") if not os.environ.get(v)]
    if missing:
        print(f"NARRATOR_PROVIDER is '{provider}' but missing: {', '.join(missing)}")
        return
 

    
    print(f"--- Testing against {os.environ['NARRATOR_MODEL']} @ {os.environ['GLM_BASE_URL']} ---\n")

    """ print("--- Test 1: direct-answer question (no tool call expected) ---")
    result = run_narrator_turn(
        question="What is this made of?",
        current_artifact=MOCK_ARTIFACTS["100"],
        artifacts_by_id=MOCK_ARTIFACTS,
    )
    print(f"Text: {result.text}")
    print(f"Tool calls made: {result.tool_calls_made}")
    print(f"Declined: {result.declined}\n")

    print("--- Test 2: cross-reference question (get_artifact expected) ---")
    result = run_narrator_turn(
        question="Is this related to that bronze incense burner I saw earlier (art_002)?",
        current_artifact=MOCK_ARTIFACTS["1"],
        artifacts_by_id=MOCK_ARTIFACTS,
    )
    print(f"Text: {result.text}")
    print(f"Tool calls made: {result.tool_calls_made}")
    print(f"Declined: {result.declined}\n")

    print("--- Test 2b: cross-reference question (get_artifact expected) ---")
    result = run_narrator_turn(
        question="Is this related to that decorated pottery cup I saw earlier (80)?",
        current_artifact=MOCK_ARTIFACTS["79"],
        artifacts_by_id=MOCK_ARTIFACTS,
    )
    print(f"Text: {result.text}")
    print(f"Tool calls made: {result.tool_calls_made}")
    print(f"Declined: {result.declined}\n")"""

    print("--- Test 3: cross-cultural connection question (should decline gracefully) ---")
    result = run_narrator_turn(
        question="What other civilizations used meteorite iron like this?",
        current_artifact=MOCK_ARTIFACTS["16"],
        artifacts_by_id=MOCK_ARTIFACTS,
    )
    print(f"Text: {result.text}")
    print(f"Tool calls made: {result.tool_calls_made}")
    print(f"Hit iteration cap: {result.hit_iteration_cap}\n")
    print(f"Looks like a decline (heuristic, verify manually): {looks_like_decline(result.text)}")

    

if __name__ == "__main__":
    main()