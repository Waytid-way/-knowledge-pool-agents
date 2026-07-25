.PHONY: install lint test up down

install:
	uv sync --all-extras

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src

test:
	uv run pytest -q

up:
	docker compose up -d postgres minio temporal temporal-ui

down:
	docker compose down -v
