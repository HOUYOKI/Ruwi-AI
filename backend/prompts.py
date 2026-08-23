"""System prompt for Ruwi, the archaeological interpreter."""

# Descriptive fields a handful of source records are missing (curatorial
# data-entry gaps, not file corruption). Defaulted rather than refusing to
# load the whole artifact catalog over a few incomplete entries. Single
# source of truth: main.py's load_artifacts() uses this for defaulting,
# build_artifact_context_block() below uses it to detect a placeholder and
# decide whether to fall back to the raw Arabic label.
OPTIONAL_TEXT_FIELDS = {
    "age": "Not available",
    "location": "Not available",
    "material": "Not available",
    "description": "No description is available for this artifact yet.",
}


def build_artifact_context_block(artifact: dict) -> str:
    """Turns a grounded artifact record into the <artifact_context> block
    the model sees. Single source of truth for this — both the Narrator
    loop (agents/narrator/narrator.py) and (formerly) main.py's inline
    single-shot call render context through this exact function. ocr_arabic
    is included whenever present, not just to backfill placeholder fields."""
    ocr_arabic = artifact.get("ocr_arabic")

    context_lines = [
        "<artifact_context>",
        f"Name: {artifact['name']}",
        f"Age: {artifact['age']}",
        f"Location: {artifact['location']}",
        f"Material: {artifact['material']}",
        f"Description: {artifact['description']}",
    ]
    # ocr_arabic is the raw museum panel text — closer to the original
    # source than `description` (a curated English summary, not a literal
    # translation). Always include it when present: it fills gaps in the
    # placeholder fields above, and should be treated as the more
    # authoritative field if it and the English description conflict.
    if ocr_arabic:
        context_lines.append(
            f"Original museum panel text (Arabic, primary source): {ocr_arabic}"
        )
    context_lines.append("</artifact_context>")
    return "\n".join(context_lines)
