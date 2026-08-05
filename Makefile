.PHONY: dev test lint typecheck build migrate seed reset

dev:
	docker compose up --build

test:
	cd backend && pytest -q
	cd frontend && npm test -- --run

lint:
	cd backend && ruff check app tests
	cd frontend && npm run lint

typecheck:
	cd backend && mypy app
	cd frontend && npm run typecheck

build:
	cd frontend && npm run build

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -m app.seed

reset:
	docker compose down -v
