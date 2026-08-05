# Verification report

Verification was performed on August 6, 2026 in the available build environment.

## Executed successfully

```text
python -m compileall -q app tests alembic
Result: passed; all backend Python files compiled.

pytest -q
Result: 10 passed in 1.20s.

FastAPI app.openapi()
Result: passed; OpenAPI schema generated with 30 paths.

YAML/JSON parsing
Result: passed for docker-compose.yml, frontend/package.json, and frontend/tsconfig.json.
```

The backend tests covered health, authentication/current user, registration, role permissions, public demo artifacts and complete experience data, image validation, safe AI configuration failure, experience planning, quiz submission, and curator editing.

## Environment limitations, reported without claiming success

- Docker was not installed in the archive-generation environment, so `docker compose config` and full container startup could not be executed here. The Compose YAML was parsed successfully and includes database, backend, and frontend health/dependency configuration.
- The environment's package mirrors did not provide the pinned Python and npm packages, so a fresh dependency installation, frontend typecheck, frontend test suite, lint, and production Next.js build could not be executed here. Dockerfiles and CI run those commands in a normal network-enabled development or CI environment.
- `ruff` was not installed in the build environment and therefore was not claimed as executed.

## Archive hygiene

- `.env.example` is included; no `.env` file or real secret is included.
- Python caches, pytest caches, SQLite test databases, virtual environments, `node_modules`, `.next`, and package-install remnants were removed.
- The archive extracts into one `ruwi` root directory.
