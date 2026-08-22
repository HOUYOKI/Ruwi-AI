# Ruwi (رُوي) — MVP

Dark-themed, minimalist interactive artifact explorer for the Saudi National Museum. Pick an artifact, view it in 3D, and ask Ruwi — an AI narrator — how it connects across cultures and civilizations.

Ruwi's target design is three agents (Narrator, Connector, Reflection). Right now, only the Narrator is wired into the running app.

## Structure

```
backend/    FastAPI app (artifacts API, /chat via Narrator agent + TTS)
frontend/   React + Vite + Three.js UI
data/       artifacts.json (grounded artifact data)
assets/     clean_artifacts/ (isolated PNG artifact images)
```

## Current scope

**Works, wired into the running app:**
- Narrator agent, Interpreter posture — ReAct loop (`backend/agents/narrator/`), answers directly, calls `get_artifact` to cross-reference another artifact, or declines in-character. Model is provider-agnostic (OpenAI-compatible chat-completions format), currently configured for GLM (Z.ai).
- Text-to-speech (ElevenLabs) — fires once, automatically, after the Narrator's turn ends. Never model-invoked, never part of the reasoning loop. If TTS fails or isn't configured, the text answer is still returned (`audio_url: null`) — a voice outage never blocks the response.

**Designed, not yet built:**
- Connector agent (cross-cultural connections — the project's stated "moat")
- Reflection agent (end-of-visit synthesis)
- Visit Record (shared state across a visit)
- Storyteller posture (one-time opening narration gate)

> Two `requirements.txt` files currently exist: `backend/requirements.txt` (real, used below) and a root-level `requirements.txt` that appears corrupted/stray (wrong encoding, mismatched pin). Unresolved — flagging rather than silently picking one.

## Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

Copy the example env file **at the repo root** (there is no `backend/.env.example` — `python-dotenv`'s `load_dotenv()` walks up from the working directory and finds the root `.env`):

```bash
copy ..\.env.example ..\.env       # Windows, run from backend/
# cp ../.env.example ../.env       # macOS/Linux
```

Edit `.env` and set the variables below. Then run the server from `backend/`:

```bash
uvicorn main:app --reload
```

Backend serves on `http://localhost:8000`. It loads `data/artifacts.json` at startup and fails immediately (non-zero exit, clear error) if the file is missing, malformed, or if `NARRATOR_MODEL` / the Narrator provider credentials aren't set — check the terminal output if it won't start.

## Environment variables

All read by `backend/config.py`. Placeholders below, not real values.

| Variable | Required | Notes |
|---|---|---|
| `NARRATOR_PROVIDER` | Yes | Names which `{PROVIDER}_BASE_URL`/`{PROVIDER}_API_KEY` pair to use, e.g. `glm` → `GLM_BASE_URL`/`GLM_API_KEY` |
| `NARRATOR_MODEL` | Yes | Checked at boot — app won't start without it |
| `GLM_BASE_URL` / `GLM_API_KEY` (or whichever provider you named above) | Yes | e.g. `GLM_BASE_URL=https://api.z.ai/api/paas/v4`, `GLM_API_KEY=your_glm_api_key_here` |
| `NARRATOR_TEMPERATURE` | No | Default `0.5` |
| `NARRATOR_MAX_TOKENS` | No | Default `2048` |
| `ELEVENLABS_API_KEY` | No | TTS is skipped (text-only response) if unset |
| `ELEVENLABS_VOICE_ID_EN` / `ELEVENLABS_VOICE_ID_AR` | No | Voice ID per detected language; TTS is skipped for a language with no ID set |
| `TTS_STABILITY` | No | Default `0.21` |
| `TTS_STYLE` | No | Default `0.3` |
| `TTS_SIMILARITY_BOOST` | No | Default `0.75` |
| `ARTIFACTS_JSON_PATH` | No | Default `../data/artifacts.json` |
| `ASSETS_DIR` | No | Default `../assets/clean_artifacts` |
| `FRONTEND_ORIGIN` | No | Default `http://localhost:5173` |

`ANTHROPIC_API_KEY` and `CLAUDE_MODEL` are also read by `config.py` but are orphaned — leftover from an earlier stage, not required, nothing in the current `/chat` flow uses them. The Anthropic API is explicitly excluded from this project's agents (see `CLAUDE.md`).

## Frontend setup

```bash
cd frontend
npm install
copy .env.example .env       # Windows; `cp` on macOS/Linux
npm run dev
```

`frontend/.env` only needs `VITE_API_BASE_URL` (defaults to `http://localhost:8000`). Never put a backend secret in a `VITE_`-prefixed variable — anything with that prefix is bundled into browser-visible JS.

Frontend serves on `http://localhost:5173`. Run the backend first — the gallery shows a real error state (not a blank page) if it can't be reached.

## API

- `GET /artifacts` — list all artifacts (summary fields)
- `GET /artifacts/{id}` — full detail for one artifact, 404 if unknown
- `GET /images/{id}.png` — the artifact's isolated PNG
- `GET /static/audio/{filename}.mp3` — generated TTS audio, directly playable
- `POST /chat` — `{ artifact_id, question }` → `{ answer, hit_iteration_cap, audio_url }`; `audio_url` is `null` if TTS wasn't configured or failed; 502 (no stack trace) if the Narrator call itself fails
