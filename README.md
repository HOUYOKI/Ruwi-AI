# Ruwi (رُوي) — MVP

Dark-themed, minimalist interactive artifact explorer for the Saudi National Museum. Pick an artifact, view it in 3D, and ask Ruwi — an AI "Archaeological Interpreter" — how it connects across cultures and civilizations.

## Structure

```
backend/    FastAPI app (artifacts API, /chat via Claude)
frontend/   React + Vite + Three.js UI
data/       artifacts.json (grounded artifact data)
assets/     clean_artifacts/ (isolated PNG artifact images)
```

## Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
copy .env.example .env       # Windows; `cp` on macOS/Linux
```

Edit `backend/.env` and set `ANTHROPIC_API_KEY` to a valid Anthropic API key. Leave `CLAUDE_MODEL` and the path overrides at their defaults unless you've moved `data/artifacts.json` or `assets/clean_artifacts/`.

Run the server:

```bash
uvicorn main:app --reload
```

Backend serves on `http://localhost:8000`. It loads `data/artifacts.json` at startup and fails immediately (non-zero exit, clear error) if the file is missing or malformed — check the terminal output if it won't start.

## Frontend setup

```bash
cd frontend
npm install
copy .env.example .env       # Windows; `cp` on macOS/Linux
npm run dev
```

`frontend/.env` only needs `VITE_API_BASE_URL` (defaults to `http://localhost:8000`). Never put `ANTHROPIC_API_KEY` or any backend secret in a `VITE_`-prefixed variable — anything with that prefix is bundled into the browser-visible JS.

Frontend serves on `http://localhost:5173`. Run the backend first — the gallery shows a real error state (not a blank page) if it can't be reached.

## Environment variables

| File | Variable | Required | Notes |
|---|---|---|---|
| `backend/.env` | `ANTHROPIC_API_KEY` | Yes | Never commit; `.env` is gitignored |
| `backend/.env` | `CLAUDE_MODEL` | No | Defaults to `claude-sonnet-5` |
| `backend/.env` | `ARTIFACTS_JSON_PATH`, `ASSETS_DIR`, `FRONTEND_ORIGIN` | No | Only needed if paths/origin differ from defaults |
| `frontend/.env` | `VITE_API_BASE_URL` | Yes | Backend origin, e.g. `http://localhost:8000` |

## API

- `GET /artifacts` — list all artifacts (summary fields)
- `GET /artifacts/{id}` — full detail for one artifact, 404 if unknown
- `GET /images/{id}.png` — the artifact's isolated PNG
- `POST /chat` — `{ artifact_id, question }` → `{ answer }`; 502 (no stack trace) if the Claude call fails
