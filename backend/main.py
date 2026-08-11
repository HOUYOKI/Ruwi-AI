"""Ruwi backend — FastAPI service for the artifact explorer MVP."""
import json
import logging
from pathlib import Path
from typing import Optional

import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

import config
from prompts import SYSTEM_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ruwi")

BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_JSON_PATH = (BASE_DIR / config.ARTIFACTS_JSON_PATH).resolve()
ASSETS_DIR = (BASE_DIR / config.ASSETS_DIR).resolve()

# Structural fields: without these the artifact can't be displayed or served at
# all, so a gap here means the file is genuinely malformed and startup must fail.
REQUIRED_ARTIFACT_FIELDS = {"id", "name", "clean_image_path"}

# Descriptive fields: a handful of source records are missing these (curatorial
# data-entry gaps, not file corruption). Default them instead of refusing to
# start the whole 102-artifact catalog over a few incomplete entries.
OPTIONAL_TEXT_FIELDS = {
    "age": "Not available",
    "location": "Not available",
    "material": "Not available",
    "description": "No description is available for this artifact yet.",
}


def load_artifacts() -> dict[int, dict]:
    """Load and validate artifacts.json once at startup. Raises on any problem
    so the process fails fast instead of serving from a broken/empty store."""
    if not ARTIFACTS_JSON_PATH.is_file():
        raise RuntimeError(f"artifacts.json not found at {ARTIFACTS_JSON_PATH}")

    try:
        raw_text = ARTIFACTS_JSON_PATH.read_text(encoding="utf-8")
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"artifacts.json is not valid JSON: {exc}") from exc

    if not isinstance(data, list) or len(data) == 0:
        raise RuntimeError("artifacts.json must be a non-empty JSON array")

    by_id: dict[int, dict] = {}
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            raise RuntimeError(f"artifacts.json entry #{i} is not an object")
        missing = REQUIRED_ARTIFACT_FIELDS - entry.keys()
        if missing:
            raise RuntimeError(f"artifacts.json entry #{i} (id={entry.get('id')}) missing fields: {missing}")
        artifact_id = entry["id"]
        if not isinstance(artifact_id, int):
            raise RuntimeError(f"artifacts.json entry #{i} has non-integer id: {artifact_id!r}")
        if artifact_id in by_id:
            raise RuntimeError(f"artifacts.json has duplicate id: {artifact_id}")

        for field, default in OPTIONAL_TEXT_FIELDS.items():
            if not entry.get(field):
                entry[field] = default

        by_id[artifact_id] = entry

    return by_id


ARTIFACTS_BY_ID = load_artifacts()
logger.info("Loaded %d artifacts from %s", len(ARTIFACTS_BY_ID), ARTIFACTS_JSON_PATH)

if not config.ANTHROPIC_API_KEY:
    raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")

claude_client = anthropic.Anthropic(
    api_key=config.ANTHROPIC_API_KEY,
    timeout=config.CLAUDE_REQUEST_TIMEOUT_SECONDS,
    max_retries=config.CLAUDE_MAX_RETRIES,
)

app = FastAPI(title="Ruwi API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def to_summary(artifact: dict) -> dict:
    return {
        "id": artifact["id"],
        "name": artifact["name"],
        "age": artifact["age"],
        "location": artifact["location"],
        "material": artifact["material"],
        "image_url": f"/images/{artifact['id']}.png",
    }


def to_detail(artifact: dict) -> dict:
    return {
        **to_summary(artifact),
        "description": artifact["description"],
    }


@app.get("/artifacts")
def list_artifacts():
    return [to_summary(a) for a in ARTIFACTS_BY_ID.values()]


@app.get("/artifacts/{artifact_id}")
def get_artifact(artifact_id: int):
    artifact = ARTIFACTS_BY_ID.get(artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return to_detail(artifact)


@app.get("/images/{artifact_id}.png")
def get_artifact_image(artifact_id: int):
    artifact = ARTIFACTS_BY_ID.get(artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")

    image_path = (BASE_DIR / ".." / artifact["clean_image_path"]).resolve()

    # Defense in depth: even though artifact_id was validated against known ids
    # above, confirm the resolved file still lives inside ASSETS_DIR before
    # touching the filesystem.
    if ASSETS_DIR not in image_path.parents or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Artifact image not found")

    return FileResponse(image_path, media_type="image/png")


class ChatRequest(BaseModel):
    artifact_id: int
    question: str = Field(max_length=config.CHAT_QUESTION_MAX_LENGTH)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("question must not be empty")
        return stripped


class ChatResponse(BaseModel):
    answer: str


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    artifact = ARTIFACTS_BY_ID.get(payload.artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")

    has_placeholder_field = any(
        artifact[field] == default for field, default in OPTIONAL_TEXT_FIELDS.items()
    )
    ocr_arabic = artifact.get("ocr_arabic")

    context_lines = [
        "<artifact_context>",
        f"Name: {artifact['name']}",
        f"Age: {artifact['age']}",
        f"Location: {artifact['location']}",
        f"Material: {artifact['material']}",
        f"Description: {artifact['description']}",
    ]
    if has_placeholder_field and ocr_arabic:
        context_lines.append(
            "Raw Arabic museum label (use this to fill in any fields above marked "
            '"Not available" — translate and extract the relevant facts, don\'t '
            f"just repeat the raw text): {ocr_arabic}"
        )
    context_lines.append("</artifact_context>")
    artifact_context_block = "\n".join(context_lines)

    try:
        response = claude_client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": artifact_context_block},
                        {"type": "text", "text": payload.question},
                    ],
                }
            ],
        )
    except anthropic.APIError as exc:
        logger.error("Claude API call failed for artifact %s: %s", payload.artifact_id, exc)
        raise HTTPException(status_code=502, detail="Ruwi is temporarily unavailable. Please try again.") from exc
    except Exception as exc:  # noqa: BLE001 — last-resort guard so no stack trace leaks to the client
        logger.exception("Unexpected error calling Claude for artifact %s", payload.artifact_id)
        raise HTTPException(status_code=502, detail="Ruwi is temporarily unavailable. Please try again.") from exc

    answer_text = "".join(block.text for block in response.content if block.type == "text")
    return ChatResponse(answer=answer_text)
