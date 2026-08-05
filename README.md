# Ruwi | رُوي

> Every Artifact Has a Story. Ruwi Brings It to Life.

Ruwi is a bilingual AI-powered interactive museum platform for Saudi and regional cultural heritage. It combines image analysis, grounded knowledge retrieval, interactive stories, timelines, hotspots, quizzes, narration, follow-up chat, curator review, and administration.

## Features

- Arabic/English interface with complete RTL/LTR switching
- Public artifact exploration and three complete bilingual demo experiences
- Registration, JWT login, refresh tokens, profile and saved experiences
- Secure artifact-image upload with validation and processing status
- Provider-based Vision, Text, Embedding, and TTS architecture
- Grounded RAG services with source metadata and pgvector-ready schema
- Curator review, editing, approval, rejection, and publication workflows
- Admin users, museums, collections, categories, settings, analytics, and audit logs
- Responsive premium museum design, dark mode, accessible controls, empty/loading/error states
- FastAPI OpenAPI documentation, migrations, seed data, Docker Compose, and tests

## Quick start with Docker

```bash
cp .env.example .env
docker compose up --build
```

URLs:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

The backend container runs migrations and seeds demo content before starting.

## Demo accounts

| Role | Email | Password |
|---|---|---|
| Administrator | admin@example.com | Admin123! |
| Curator | curator@example.com | Curator123! |
| Visitor | visitor@example.com | Visitor123! |

Change all demo credentials outside local development.

## AI configuration

The app starts safely with `AI_PROVIDER=none`. Seeded demo experiences remain usable, while real analysis endpoints return a clear `AI_PROVIDER_NOT_CONFIGURED` error. Configure one provider:

```env
AI_PROVIDER=gemini
AI_API_KEY=replace-me
VISION_MODEL=gemini-2.5-flash
TEXT_MODEL=gemini-2.5-flash
```

The provider interfaces are under `backend/app/ai/providers`. Prompts are versioned under `backend/app/ai/prompts`.

## Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp ../.env.example ../.env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Validation commands

```bash
make lint
make typecheck
make test
make build
```

See `docs/verification-report.md` for commands actually executed in the delivered archive.

## Project structure

```text
ruwi/
├── frontend/       Next.js App Router application
├── backend/        FastAPI layered application
├── database/       schema and seed documentation
├── docs/           architecture, security, deployment, and workflows
├── assets/         branding and demo assets
├── scripts/        developer utilities
├── .github/        CI workflow
├── docker-compose.yml
├── Makefile
└── .env.example
```

## Documentation

- `docs/architecture.md`
- `docs/installation.md`
- `docs/local-development.md`
- `docs/docker.md`
- `docs/api.md`
- `docs/database.md`
- `docs/ai-workflow.md`
- `docs/rag-ingestion.md`
- `docs/curator-workflow.md`
- `docs/deployment.md`
- `docs/testing.md`
- `docs/security.md`
- `docs/troubleshooting.md`

## License

MIT. Demo heritage text is original content written for this repository and is not copied from external copyrighted sources.
