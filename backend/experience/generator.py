"""Optional structured-LLM enhancement with a curated offline baseline."""

import json
import logging

from openai import OpenAI

import config
from .schemas import ExperienceResponse

logger = logging.getLogger("ruwi.experience")


def generate_experience(
    artifact: dict,
    curated: dict,
    template: str,
) -> dict:
    """Return curated content by default; optionally request schema-bound copy.

    The checked-in content is the booth-safe source of truth. Live generation is
    opt-in and may only reshape content already present in the supplied context.
    """
    baseline = build_curated_response(artifact, curated, template)
    if not config.EXPERIENCE_LLM_ENABLED:
        return baseline

    base_url, api_key = config.get_narrator_provider_credentials()
    client = OpenAI(base_url=base_url, api_key=api_key)
    response = client.chat.completions.create(
        model=config.NARRATOR_MODEL,
        temperature=0.2,
        max_tokens=config.NARRATOR_MAX_TOKENS,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "ruwi_experience",
                "strict": True,
                "schema": ExperienceResponse.model_json_schema(),
            },
        },
        messages=[
            {
                "role": "system",
                "content": (
                    "Create a museum experience using only the supplied trusted JSON. "
                    "Do not add claims or sources. Preserve artifact IDs and source URLs."
                ),
            },
            {"role": "user", "content": json.dumps(baseline, ensure_ascii=False)},
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("experience model returned no content")
    generated = json.loads(content)
    generated.setdefault("metadata", {})["generated"] = True
    return generated


def build_curated_response(artifact: dict, curated: dict, template: str) -> dict:
    language = curated.get("language", "en")

    def localized(field: str) -> str:
        return artifact.get(f"{field}_ar") or artifact[field] if language == "ar" else artifact[field]

    return {
        "artifact": {
            "id": artifact["id"],
            "name": localized("name"),
            "age": localized("age"),
            "location": localized("location"),
            "material": localized("material"),
            "image_url": f"/images/{artifact['id']}.png",
        },
        "template": template,
        "title": curated["title"],
        "summary": curated["summary"],
        "narration": curated["narration"],
        "story_sections": curated.get("story_sections", []),
        "timeline": curated.get("timeline", []),
        "facts": curated.get("facts", []),
        "hotspots": curated.get("hotspots", []),
        "quiz": curated.get("quiz", []),
        "sources": curated["sources"],
        "metadata": {
            "language": language,
            "confidence": curated.get("confidence", 1.0),
            "generated": False,
            "warnings": [],
            "schema_version": "1.0",
        },
    }
