"""FastAPI routes for interactive experiences."""

from fastapi import APIRouter, HTTPException

from .graph import build_experience_graph
from .schemas import ExperienceResponse


def create_experience_router(artifacts_by_id: dict[int, dict]) -> APIRouter:
    router = APIRouter(tags=["experiences"])
    graph = build_experience_graph(artifacts_by_id)

    @router.get("/artifacts/{artifact_id}/experience", response_model=ExperienceResponse)
    def get_artifact_experience(artifact_id: int):
        if artifact_id not in artifacts_by_id:
            raise HTTPException(status_code=404, detail="Artifact not found")
        state = graph.invoke({"requested_artifact_id": artifact_id, "warnings": []})
        experience = state.get("experience")
        if experience is None:
            raise HTTPException(status_code=404, detail="No interactive experience is available for this artifact")
        return experience

    return router
