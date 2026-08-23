"""Read trusted local and curated experience data."""

import json
from pathlib import Path
from typing import Any


SHOWCASE_PATH = Path(__file__).resolve().parents[2] / "data" / "showcase_experiences.json"
SHOWCASE_AR_PATH = Path(__file__).resolve().parents[2] / "data" / "showcase_experiences_ar.json"


def load_showcase_experiences(lang: str = "en") -> dict[int, dict[str, Any]]:
    data = json.loads(SHOWCASE_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("showcase_experiences.json must be an object keyed by artifact ID")
    experiences = {int(artifact_id): value for artifact_id, value in data.items()}
    if lang != "ar":
        return experiences

    translations = json.loads(SHOWCASE_AR_PATH.read_text(encoding="utf-8"))
    for artifact_id, translated in translations.items():
        key = int(artifact_id)
        if key in experiences:
            experiences[key] = {**experiences[key], **translated, "language": "ar"}
    return experiences
