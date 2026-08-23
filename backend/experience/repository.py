"""Read trusted local and curated experience data."""

import json
from pathlib import Path
from typing import Any


SHOWCASE_PATH = Path(__file__).resolve().parents[2] / "data" / "showcase_experiences.json"


def load_showcase_experiences() -> dict[int, dict[str, Any]]:
    data = json.loads(SHOWCASE_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("showcase_experiences.json must be an object keyed by artifact ID")
    return {int(artifact_id): value for artifact_id, value in data.items()}
