"""Contracts for artifact identification."""

from typing import Literal

from pydantic import BaseModel, Field


class MatchCandidate(BaseModel):
    artifact_id: int
    artifact_name: str
    confidence: float = Field(ge=0, le=1)


class IdentificationResponse(BaseModel):
    status: Literal["matched", "partial", "unsupported"]
    artifact_id: int | None
    artifact_name: str | None
    confidence: float = Field(ge=0, le=1)
    reason: str
    alternatives: list[MatchCandidate] = Field(default_factory=list, max_length=3)


class ProviderAlternative(BaseModel):
    artifact_id: int
    confidence: float = Field(ge=0, le=1)


class ProviderIdentification(BaseModel):
    artifact_id: int | None
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(min_length=1, max_length=500)
    alternatives: list[ProviderAlternative] = Field(default_factory=list, max_length=5)
