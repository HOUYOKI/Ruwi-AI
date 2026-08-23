"""Public API contract for structured Ruwi experiences."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


ExperienceTemplate = Literal[
    "visual_story",
    "story_timeline",
    "hotspot_story",
    "object_anatomy",
]


class ArtifactRef(BaseModel):
    id: int
    name: str
    age: str
    location: str
    material: str
    image_url: str


class StorySection(BaseModel):
    id: str
    title: str
    body: str


class TimelineEvent(BaseModel):
    id: str
    label: str
    title: str
    body: str


class Fact(BaseModel):
    label: str
    value: str


class Hotspot(BaseModel):
    id: str
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    title: str
    body: str


class QuizQuestion(BaseModel):
    id: str
    prompt: str
    choices: list[str] = Field(min_length=2)
    correct_index: int = Field(ge=0)
    explanation: str

    @model_validator(mode="after")
    def correct_answer_must_exist(self):
        if self.correct_index >= len(self.choices):
            raise ValueError("correct_index must point to an available choice")
        return self


class Source(BaseModel):
    id: str
    title: str
    publisher: str
    url: str
    source_type: Literal["museum_panel", "museum", "government", "academic"]


class ExperienceMetadata(BaseModel):
    language: Literal["en", "ar"] = "en"
    confidence: float = Field(ge=0, le=1)
    generated: bool
    warnings: list[str] = Field(default_factory=list)
    schema_version: Literal["1.0"] = "1.0"


class ExperienceResponse(BaseModel):
    artifact: ArtifactRef
    template: ExperienceTemplate
    title: str
    summary: str
    narration: str
    sources: list[Source] = Field(min_length=1)
    metadata: ExperienceMetadata
    story_sections: list[StorySection] = Field(default_factory=list)
    timeline: list[TimelineEvent] = Field(default_factory=list)
    facts: list[Fact] = Field(default_factory=list)
    hotspots: list[Hotspot] = Field(default_factory=list)
    quiz: list[QuizQuestion] = Field(default_factory=list)

    @model_validator(mode="after")
    def template_has_required_content(self):
        if self.template == "hotspot_story" and not self.hotspots:
            raise ValueError("hotspot_story requires at least one hotspot")
        if self.template == "story_timeline" and not self.timeline:
            raise ValueError("story_timeline requires at least one timeline event")
        if self.template == "object_anatomy" and not (self.hotspots or self.facts):
            raise ValueError("object_anatomy requires hotspots or facts")
        return self
