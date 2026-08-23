"""Minimal LangGraph orchestration for browsed-artifact experiences."""

import logging

from langgraph.graph import END, START, StateGraph

from prompts import build_artifact_context_block
from .generator import build_curated_response, generate_experience
from .planner import select_template
from .repository import load_showcase_experiences
from .state import ExperienceState
from .validation import validate_experience

logger = logging.getLogger("ruwi.experience")


def build_experience_graph(artifacts_by_id: dict[int, dict]):
    def resolve_artifact(state: ExperienceState):
        artifact_id = state["requested_artifact_id"]
        artifact = artifacts_by_id.get(artifact_id)
        if artifact is None:
            return {"match_status": "unsupported", "error": "Artifact not found"}
        return {"artifact_id": artifact_id, "artifact": artifact, "match_status": "matched"}

    def retrieve_local_context(state: ExperienceState):
        curated = load_showcase_experiences(state.get("language", "en")).get(state["artifact_id"], {})
        return {
            "curated_context": curated,
            "local_context": build_artifact_context_block(state["artifact"]),
        }

    def select_experience_template(state: ExperienceState):
        return {"template": select_template(state["curated_context"])}

    def generate(state: ExperienceState):
        curated = state["curated_context"]
        if not curated:
            return {"error": "No curated experience is available for this artifact"}
        try:
            draft = generate_experience(state["artifact"], curated, state["template"])
            return {"draft": draft}
        except Exception as exc:  # live generation must never break curated content
            logger.exception("Live experience generation failed; using curated fallback")
            return {
                "draft": build_curated_response(state["artifact"], curated, state["template"]),
                "warnings": [f"Live generation unavailable: {type(exc).__name__}"],
            }

    def validate(state: ExperienceState):
        if "draft" not in state:
            return {}
        curated = state["curated_context"]
        allowed_urls = {source["url"] for source in curated["sources"]}
        try:
            experience = validate_experience(state["draft"], state["artifact_id"], allowed_urls)
        except Exception as exc:
            logger.exception("Generated experience failed validation; using curated fallback")
            fallback = build_curated_response(state["artifact"], curated, state["template"])
            experience = validate_experience(fallback, state["artifact_id"], allowed_urls)
            warnings = [*state.get("warnings", []), f"Validation fallback: {type(exc).__name__}"]
            experience.metadata.warnings = warnings
        else:
            experience.metadata.warnings = state.get("warnings", [])
        return {"experience": experience.model_dump(mode="json")}

    graph = StateGraph(ExperienceState)
    graph.add_node("resolve_artifact", resolve_artifact)
    graph.add_node("retrieve_local_context", retrieve_local_context)
    graph.add_node("select_template", select_experience_template)
    graph.add_node("generate_experience", generate)
    graph.add_node("validate_experience", validate)
    graph.add_edge(START, "resolve_artifact")
    graph.add_edge("resolve_artifact", "retrieve_local_context")
    graph.add_edge("retrieve_local_context", "select_template")
    graph.add_edge("select_template", "generate_experience")
    graph.add_edge("generate_experience", "validate_experience")
    graph.add_edge("validate_experience", END)
    return graph.compile()
