.PHONY: install lint test test-integration migrate migrate-down up down

install:
	uv sync --all-extras

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src

test:
	uv run pytest -q

test-integration:
	uv run pytest tests/integration/db -v

migrate:
	uv run alembic upgrade head

migrate-down:
	uv run alembic downgrade base

up:
	docker compose up -d postgres minio temporal temporal-ui

down:
	docker compose down -v
