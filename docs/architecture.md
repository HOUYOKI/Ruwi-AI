# Architecture

Next.js communicates with a versioned FastAPI API. The backend separates API, schemas, repositories, services, AI providers, RAG, planning, storage, and persistence. PostgreSQL/pgvector is the production database; SQLite is used only for lightweight automated tests.
