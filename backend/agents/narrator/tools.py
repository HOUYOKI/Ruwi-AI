"""
Ruwi Agent Core — Tool Definitions
Layer 1 of the Agentic AI Workflow.

Provider-agnostic by design: uses the OpenAI-compatible function-calling
schema, which OpenRouter, DeepSeek, GLM (Z.ai), Kimi (Moonshot), and most
other providers all speak natively. No vendor is hardcoded here — the
provider is a config value in narrator.py, not a code choice.

Only ONE decision-tool exists at this layer: get_artifact.
consult_connector, speak_text, and log_visit_turn are intentionally NOT
implemented — they belong to later build layers (Connector Agent, Visit
Record, TTS) per the Stage 3 spec.
"""

from typing import Any


# --- Tool schema, OpenAI-compatible function-calling format ---
GET_ARTIFACT_TOOL = {
    "type": "function",
    "function": {
        "name": "get_artifact",
        "description": (
            "Look up grounded facts for a DIFFERENT artifact than the one "
            "currently being discussed. Use this only when the visitor "
            "references or asks about another piece, e.g. 'is this related "
            "to the one I saw earlier?'. Do not use this for the artifact "
            "already in context — you already have those facts."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "artifact_id": {
                    "type": "string",
                    "description": "The id of the artifact to look up.",
                }
            },
            "required": ["artifact_id"],
        },
    },
}

# Only tools in this list count against the reasoning iteration cap.
# (log_visit_turn / speak_text, once they exist, are AUTOMATIC pipeline
# steps, not model decisions — they should never count against
# MAX_DECISION_ITERATIONS. See Stage 3 spec, Narrator §3.)
DECISION_TOOLS = [GET_ARTIFACT_TOOL]


def execute_tool(
    name: str,
    tool_input: dict[str, Any],
    artifacts_by_id: dict[str, dict],
) -> dict[str, Any]:
    """
    Dispatches a tool call to its implementation.

    Layer 1 only implements get_artifact. Any other tool name reaching
    here means either a wiring bug (a tool was offered without an
    implementation) or a future layer's tool arriving early — fail
    loudly here, in testing, rather than surfacing silently to a visitor.
    """
    if name == "get_artifact":
        raw_artifact_id = tool_input["artifact_id"]
        # The tool schema declares artifact_id as a string (models send
        # string args), but the real ARTIFACTS_BY_ID store (main.py's
        # load_artifacts) is keyed by int. Coerce before lookup rather
        # than silently missing every real cross-reference.
        try:
            artifact_id = int(raw_artifact_id)
        except (TypeError, ValueError):
            return {"found": False, "artifact_id": raw_artifact_id}
        artifact = artifacts_by_id.get(artifact_id)
        if artifact is None:
            # Fail closed: tell the MODEL plainly the lookup was empty,
            # and let the Narrator's own prompt rules decide how to
            # phrase that to the visitor. Never invent a fact here.
            return {"found": False, "artifact_id": artifact_id}
        return {"found": True, "artifact": artifact}

    raise NotImplementedError(
        f"Tool '{name}' is not implemented at this layer. "
        f"consult_connector, speak_text, and log_visit_turn are "
        f"future-layer tools — see Stage 3 spec, section 7 (tool inventory)."
    )