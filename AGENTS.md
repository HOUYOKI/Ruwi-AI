# Ruwi Development Instructions

## Goal

Ruwi is an AI-powered interactive museum experience platform.

Core flow:
Browse/Upload Artifact → Identify → Retrieve Trusted Knowledge →
Experience Planner → Structured Experience → Interactive Frontend.

## Current Priorities

- Preserve existing working functionality.
- Add LangGraph orchestration incrementally.
- Add vision/upload artifact identification.
- Add structured Experience JSON.
- Build reusable interactive experience components.
- Keep Ask Ruwi and narrator functionality.
- Prioritize booth reliability and UX.

## Constraints

- Deadline is only a few days.
- Do not rewrite working systems unnecessarily.
- Do not train custom models.
- Do not add AR, photogrammetry, authentication, analytics, or unnecessary infrastructure.
- LLMs generate structured content, NOT arbitrary frontend code.
- Historical/cultural claims must remain grounded in trusted data/sources.
- Prefer small, testable changes.
