"""Typed shared state for the small experience workflow."""

from typing import Any, Literal, TypedDict


class ExperienceState(TypedDict, total=False):
    requested_artifact_id: int
    language: Literal["en", "ar"]
    artifact_id: int
    artifact: dict[str, Any]
    curated_context: dict[str, Any]
    local_context: str
    match_status: Literal["matched", "unsupported"]
    needs_external_context: bool
    external_context: list[dict[str, Any]]
    template: str
    draft: dict[str, Any]
    experience: dict[str, Any]
    warnings: list[str]
    error: str
