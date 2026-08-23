"""Deterministic template selection for reliable booth behavior."""

from .schemas import ExperienceTemplate


SUPPORTED_TEMPLATES = {
    "visual_story",
    "story_timeline",
    "hotspot_story",
    "object_anatomy",
}


def select_template(curated: dict) -> ExperienceTemplate:
    preferred = curated.get("preferred_template")
    if preferred in SUPPORTED_TEMPLATES:
        return preferred
    if curated.get("hotspots"):
        return "hotspot_story"
    if curated.get("timeline"):
        return "story_timeline"
    return "visual_story"
