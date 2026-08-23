"""Ruwi backend — FastAPI service for the artifact explorer MVP."""
import json
import logging
import uuid
from pathlib import Path
from typing import Optional

import openai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

import config
from agents.narrator.narrator import run_narrator_turn
from prompts import OPTIONAL_TEXT_FIELDS
from tts.speak_text import speak_text
from experience.routes import create_experience_router
from experience.repository import load_showcase_experiences
from vision.routes import create_vision_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ruwi")

BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_JSON_PATH = (BASE_DIR / config.ARTIFACTS_JSON_PATH).resolve()
ASSETS_DIR = (BASE_DIR / config.ASSETS_DIR).resolve()
AUDIO_DIR = (BASE_DIR / "static" / "audio").resolve()
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Structural fields: without these the artifact can't be displayed or served at
# all, so a gap here means the file is genuinely malformed and startup must fail.
REQUIRED_ARTIFACT_FIELDS = {"id", "name", "clean_image_path"}

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
SHOWCASE_IDS = set(load_showcase_experiences())
logger.info("Loaded %d artifacts from %s", len(ARTIFACTS_BY_ID), ARTIFACTS_JSON_PATH)

if not config.narrator_is_configured():
    logger.warning("Narrator is not configured; collection and curated experiences remain available")
if not config.vision_is_configured():
    logger.warning("Vision is not configured; /identify will return a controlled configuration error")

app = FastAPI(title="Ruwi API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class ImmutableStaticFiles(StaticFiles):
    """Generated TTS filenames are uuid4-based and never reused or
    overwritten, so unlike artifact images these are safe to cache
    aggressively and permanently."""

    def file_response(self, *args, **kwargs) -> FileResponse:
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


app.mount("/static/audio", ImmutableStaticFiles(directory=AUDIO_DIR), name="audio")
app.include_router(create_experience_router(ARTIFACTS_BY_ID))
app.include_router(create_vision_router(ARTIFACTS_BY_ID))


def localized(artifact: dict, field: str, lang: str) -> str:
    """Picks the `{field}_ar` value when lang is "ar" and it's non-empty,
    else falls back to the English `{field}` — same defensive-fallback
    style as the OPTIONAL_TEXT_FIELDS backfill in load_artifacts()."""
    if lang == "ar":
        ar_value = artifact.get(f"{field}_ar")
        if ar_value:
            return ar_value
    return artifact[field]


def to_summary(artifact: dict, lang: str) -> dict:
    return {
        "id": artifact["id"],
        "name": localized(artifact, "name", lang),
        "age": localized(artifact, "age", lang),
        "location": localized(artifact, "location", lang),
        "material": localized(artifact, "material", lang),
        "image_url": f"/images/{artifact['id']}.png",
        "featured": artifact["id"] in SHOWCASE_IDS,
    }


def to_detail(artifact: dict, lang: str) -> dict:
    return {
        **to_summary(artifact, lang),
        "description": localized(artifact, "description", lang),
    }


@app.get("/artifacts")
def list_artifacts(lang: str = "en"):
    return [to_summary(a, lang) for a in ARTIFACTS_BY_ID.values()]


@app.get("/health/config")
def configuration_preflight():
    return config.provider_preflight()


@app.get("/artifacts/{artifact_id}")
def get_artifact(artifact_id: int, lang: str = "en"):
    artifact = ARTIFACTS_BY_ID.get(artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return to_detail(artifact, lang)


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

    # Moderate, not "immutable" — this MVP's images can still be replaced in
    # place under the same id during active curation, unlike generated audio
    # filenames (uuid4, never reused) which get the aggressive cache below.
    return FileResponse(image_path, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})


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
    hit_iteration_cap: bool = False
    audio_url: str | None = None


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    artifact = ARTIFACTS_BY_ID.get(payload.artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    if not config.narrator_is_configured():
        raise HTTPException(
            status_code=503,
            detail="Ask Ruwi is not configured. The artifact experience remains available.",
        )

    try:
        result = run_narrator_turn(
            question=payload.question,
            current_artifact=artifact,
            artifacts_by_id=ARTIFACTS_BY_ID,
            conversation_history=None,
        )
    except openai.OpenAIError as exc:
        logger.error("Narrator API call failed for artifact %s: %s", payload.artifact_id, exc)
        raise HTTPException(status_code=502, detail="Ruwi is temporarily unavailable. Please try again.") from exc
    except Exception as exc:  # noqa: BLE001 — last-resort guard so no stack trace leaks to the client
        logger.exception("Unexpected error running Narrator for artifact %s", payload.artifact_id)
        raise HTTPException(status_code=502, detail="Ruwi is temporarily unavailable. Please try again.") from exc

    audio_url = None
    if config.tts_configuration_status()["configured"]:
        try:
            audio_bytes = speak_text(result.text)
            filename = f"{uuid.uuid4().hex}.mp3"
            audio_path = (AUDIO_DIR / filename).resolve()
            if AUDIO_DIR not in audio_path.parents:
                raise RuntimeError("resolved audio path escaped AUDIO_DIR")
            audio_path.write_bytes(audio_bytes)
            audio_url = f"/static/audio/{filename}"
        except Exception:  # noqa: BLE001 — TTS failure must never break the text response
            logger.exception("TTS generation failed for artifact %s; returning text-only response", payload.artifact_id)

    logger.debug("Narrator transcript for artifact %s: %s", payload.artifact_id, result.transcript)
    return ChatResponse(answer=result.text, hit_iteration_cap=result.hit_iteration_cap, audio_url=audio_url)
