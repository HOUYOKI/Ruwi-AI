"""Multimodal provider call and conservative artifact-match normalization."""

import base64
import json
from collections.abc import Callable
from typing import Any

from openai import OpenAI

import config
from experience.repository import load_showcase_experiences
from .schemas import IdentificationResponse, MatchCandidate, ProviderIdentification

MATCHED_THRESHOLD = 0.80
PARTIAL_THRESHOLD = 0.45


class VisionConfigurationError(RuntimeError):
    pass


class VisionProviderError(RuntimeError):
    pass


class VisionResponseError(RuntimeError):
    pass


def get_showcase_candidates(artifacts_by_id: dict[int, dict]) -> list[dict[str, Any]]:
    """Build the only allowed candidate set from the curated showcase overlay."""
    showcase = load_showcase_experiences()
    candidates = []
    for artifact_id in showcase:
        artifact = artifacts_by_id.get(artifact_id)
        if artifact is None:
            continue
        candidates.append({
            "artifact_id": artifact_id,
            "name": artifact["name"],
            "description": artifact["description"],
            "material": artifact["material"],
            "age": artifact["age"],
            "location": artifact["location"],
        })
    return candidates


def identify_artifact(
    image_bytes: bytes,
    mime_type: str,
    artifacts_by_id: dict[int, dict],
    provider_call: Callable[[bytes, str, list[dict[str, Any]]], dict] | None = None,
) -> IdentificationResponse:
    candidates = get_showcase_candidates(artifacts_by_id)
    if not candidates:
        return IdentificationResponse(
            status="unsupported",
            artifact_id=None,
            artifact_name=None,
            confidence=0,
            reason="No showcase artifacts are currently available for matching.",
            alternatives=[],
        )
    call = provider_call or call_vision_provider
    try:
        raw = call(image_bytes, mime_type, candidates)
    except VisionConfigurationError:
        raise
    except Exception as exc:
        raise VisionProviderError("The vision provider is temporarily unavailable.") from exc
    return normalize_provider_result(raw, candidates)


def normalize_provider_result(raw: dict, candidates: list[dict[str, Any]]) -> IdentificationResponse:
    try:
        provider_result = ProviderIdentification.model_validate(raw)
    except Exception as exc:
        raise VisionResponseError("The vision provider returned an invalid response.") from exc

    allowed = {candidate["artifact_id"]: candidate for candidate in candidates}
    if provider_result.artifact_id is not None and provider_result.artifact_id not in allowed:
        raise VisionResponseError("The vision provider returned an artifact outside the allowed candidate set.")
    if any(alternative.artifact_id not in allowed for alternative in provider_result.alternatives):
        raise VisionResponseError("The vision provider returned an invalid alternative artifact.")

    confidence = max(0.0, min(1.0, provider_result.confidence))
    chosen = allowed.get(provider_result.artifact_id)
    alternatives = _normalize_alternatives(provider_result, allowed)

    if chosen is not None and confidence >= MATCHED_THRESHOLD:
        status = "matched"
    elif confidence >= PARTIAL_THRESHOLD:
        status = "partial"
        if chosen is not None and all(item.artifact_id != provider_result.artifact_id for item in alternatives):
            alternatives.insert(0, MatchCandidate(
                artifact_id=provider_result.artifact_id,
                artifact_name=chosen["name"],
                confidence=confidence,
            ))
            alternatives = alternatives[:3]
    else:
        status = "unsupported"

    if status == "unsupported":
        return IdentificationResponse(
            status=status,
            artifact_id=None,
            artifact_name=None,
            confidence=confidence,
            reason=provider_result.reason,
            alternatives=[],
        )

    return IdentificationResponse(
        status=status,
        artifact_id=provider_result.artifact_id if status == "matched" else None,
        artifact_name=chosen["name"] if status == "matched" and chosen else None,
        confidence=confidence,
        reason=provider_result.reason,
        alternatives=alternatives,
    )


def _normalize_alternatives(
    result: ProviderIdentification,
    allowed: dict[int, dict[str, Any]],
) -> list[MatchCandidate]:
    seen: set[int] = set()
    normalized = []
    for alternative in sorted(result.alternatives, key=lambda item: item.confidence, reverse=True):
        if alternative.artifact_id in seen or alternative.artifact_id == result.artifact_id:
            continue
        seen.add(alternative.artifact_id)
        normalized.append(MatchCandidate(
            artifact_id=alternative.artifact_id,
            artifact_name=allowed[alternative.artifact_id]["name"],
            confidence=alternative.confidence,
        ))
    return normalized[:3]


def call_vision_provider(image_bytes: bytes, mime_type: str, candidates: list[dict[str, Any]]) -> dict:
    try:
        base_url, api_key = config.get_vision_provider_credentials()
    except RuntimeError as exc:
        raise VisionConfigurationError(str(exc)) from exc
    if not config.VISION_MODEL:
        raise VisionConfigurationError("VISION_MODEL environment variable is not set")

    data_url = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
    allowed_ids = [candidate["artifact_id"] for candidate in candidates]
    prompt = (
        "Match the uploaded object only against the supplied Ruwi showcase candidates. "
        f"Allowed artifact IDs are {allowed_ids}. Choose only an allowed ID or null. "
        "Do not identify the object freely and do not guess when visual evidence is weak. "
        "Use conservative confidence from 0 to 1, give a short visual reason, and return JSON only.\n\n"
        f"Candidates: {json.dumps(candidates, ensure_ascii=False)}"
    )
    client = OpenAI(base_url=base_url, api_key=api_key, timeout=config.VISION_TIMEOUT_SECONDS)
    try:
        response = client.chat.completions.create(
            model=config.VISION_MODEL,
            temperature=0,
            max_tokens=600,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "artifact_identification",
                    "strict": True,
                    "schema": ProviderIdentification.model_json_schema(),
                },
            },
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "low"}},
                ],
            }],
        )
    except Exception as exc:
        raise VisionProviderError("The configured vision model could not analyze this image.") from exc
    content = response.choices[0].message.content
    if not content:
        raise VisionResponseError("The vision provider returned no result.")
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise VisionResponseError("The vision provider returned malformed JSON.") from exc
