# Ruwi | رُوي

Ruwi is an interactive museum-experience MVP for the Saudi National Museum. Visitors can browse 102 artifacts or upload a photo, open one of six curated showcase experiences, interact with structured story templates, and ask a grounded AI narrator questions with optional ElevenLabs audio.

## Current product

- React, Vite, and TypeScript frontend
- FastAPI backend
- Arabic/English UI with RTL/LTR and light/dark themes
- Touch-friendly carousel gallery with all 102 artifacts
- Six Featured Experiences: `6, 14, 18, 43, 46, 79`
- Structured Experience JSON rendered as hotspot stories, object anatomy, timelines, quizzes, and trusted sources
- Small LangGraph experience workflow with validated curated offline fallback
- Upload/mobile camera flow and constrained vision identification
- Ask Ruwi narrator using a configurable OpenAI-compatible provider
- Local-first Connector extension with trusted-domain filtering and an injectable retrieval provider
- Lightweight deterministic Reflection metadata for narrator answers
- ElevenLabs English/Arabic TTS with text fallback
- Non-secret provider readiness at `GET /health/config`

The Connector is wired into `/chat`, but its default external retrieval provider is intentionally unconfigured; it falls back to local museum context without failing the request. Reflection performs lightweight deterministic checks rather than a second LLM pass. True vector RAG, embeddings, and a vector database are not implemented. Vision supports only the six showcase candidates and requires a configured multimodal provider.

The conversational path is: local-first Connector decision → optional trusted evidence → Narrator → Reflection metadata → existing TTS. Connector evidence is accepted only from the trusted-domain policy in `backend/agents/connector/tools.py`; a future provider can implement the `RetrievalProvider` interface without changing Narrator.

## Repository layout

```text
backend/                 FastAPI, Narrator, Connector, Reflection, TTS, Experience, and Vision
frontend/                React/Vite visitor interface
data/artifacts.json      Grounded catalog data
data/showcase_*.json     English and Arabic showcase experiences
assets/clean_artifacts/  Artifact PNG images
docs/BOOTH_CHECKLIST.md  Final manual booth QA
```

## Backend startup

From the repository root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item ..\.env.example ..\.env
uvicorn main:app --host 0.0.0.0 --port 8000
```

Use another port by changing `--port`. If the browser origin differs from `http://localhost:5173`, update `FRONTEND_ORIGIN` in the root `.env`.

External credentials are optional at startup. Without them, the collection and six curated experiences still work; `/chat` and `/identify` return controlled unavailable responses.

## Frontend startup

```powershell
cd frontend
npm install
Set-Content .env 'VITE_API_BASE_URL=http://localhost:8000'
npm run dev -- --host 0.0.0.0 --port 5173
```

`VITE_API_BASE_URL` must be reachable by the booth browser. Never place backend secrets in a `VITE_` variable because Vite exposes those values to browser code.

Open `http://localhost:5173`.

## Provider configuration

Copy `.env.example` to `.env` and replace placeholders only on the booth machine.

- Narrator: `NARRATOR_PROVIDER`, `NARRATOR_MODEL`, and the named provider's `{PROVIDER}_BASE_URL` / `{PROVIDER}_API_KEY`.
- Vision: `VISION_MODEL` plus either `VISION_PROVIDER` reusing a named provider pair or dedicated `VISION_BASE_URL` / `VISION_API_KEY`.
- TTS: `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID_EN`, and `ELEVENLABS_VOICE_ID_AR`.

Connector currently has no live provider adapter or credential variables. Tests use its static provider, and production defaults to a controlled local-only fallback. Reflection is deterministic and requires no credentials.

Do not commit `.env` or real keys.

## Readiness check

Open `http://localhost:8000/health/config`. It reports booleans only for:

- core collection
- curated experiences
- narrator
- vision
- TTS and English/Arabic voices

It never returns keys or provider URLs.

## Main API routes

- `GET /artifacts?lang=en|ar`
- `GET /artifacts/{id}?lang=en|ar`
- `GET /artifacts/{id}/experience?lang=en|ar`
- `GET /images/{id}.png`
- `POST /identify`
- `POST /chat` (text/audio plus optional trusted `sources` and structured `reflection` metadata)
- `GET /health/config`
- `GET /static/audio/{filename}.mp3`

## Validation

```powershell
cd backend
.\venv\Scripts\python.exe -m unittest discover -s tests -v
.\venv\Scripts\python.exe -m compileall -q -x "venv" .

cd ..\frontend
npm test -- --run
npm run build
npm run lint
```

Live provider calls and physical camera/audio behavior are covered by the booth checklist rather than automated tests.
