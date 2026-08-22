"""
Lists every voice your ELEVENLABS_API_KEY can actually use — more
reliable than browsing the dashboard UI, since free-tier API access
doesn't always match what the UI shows as available.

    Set ELEVENLABS_API_KEY in your .env first, then:
    python list_voices.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("ELEVENLABS_API_KEY")


def main() -> None:
    if not API_KEY:
        print("ELEVENLABS_API_KEY not set — add your real key to .env first.")
        return

    response = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": API_KEY},
        timeout=15,
    )

    if response.status_code != 200:
        print(f"Request failed: {response.status_code} — {response.text}")
        return

    voices = response.json().get("voices", [])
    if not voices:
        print("No voices returned — your key may not have Voices access yet.")
        return

    print(f"{len(voices)} voice(s) accessible with this key:\n")
    for v in voices:
        labels = v.get("labels", {})
        print(f"  name: {v.get('name')}")
        print(f"  voice_id: {v.get('voice_id')}")
        print(f"  labels: {labels}")
        print()

    print("Look at the 'labels' field (accent, description, use_case) to")
    print("identify which voice is actually Arabic-capable — the name alone")
    print("often doesn't say. Copy the real voice_id values into .env.")


if __name__ == "__main__":
    main()