"""Deterministic validation for generated and curated experiences."""

from .schemas import ExperienceResponse


def validate_experience(draft: dict, artifact_id: int, allowed_source_urls: set[str]) -> ExperienceResponse:
    experience = ExperienceResponse.model_validate(draft)
    if experience.artifact.id != artifact_id:
        raise ValueError("experience artifact ID does not match the request")
    for source in experience.sources:
        if source.url not in allowed_source_urls:
            raise ValueError(f"experience included an unapproved source: {source.url}")
    return experience
