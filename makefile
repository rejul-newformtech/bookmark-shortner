.DEFAULT_GOAL := help

APP := app.main:app

.PHONY: help install dev run-prod run test test-unit test-integration lint format typecheck check migrate revision seed seed-reset docker-up docker-down docker-logs

help: ## Show available commands
	@echo "Available commands:"
	@findstr /R /C:"^[a-zA-Z_-][a-zA-Z0-9_-]*:.*##" makefile

install: ## Install project and development dependencies
	uv sync --dev

dev: ## Start the development server with auto-reload
	uv run uvicorn $(APP) --reload

run-prod: ## Start the production server
	uv run uvicorn $(APP) --host 0.0.0.0 --port 8000 --workers 1

run: ## Start the application and database containers
	docker compose up

test: ## Run the full test suite
	uv run pytest

test-unit: ## Run only unit tests
	uv run pytest tests/unit

test-integration: ## Run only integration and route tests
	uv run pytest tests/integration

lint: ## Check the code with Ruff
	uv run ruff check .

format: ## Format the code with Ruff
	uv run ruff format .

typecheck: ## Run MyPy
	uv run mypy app

check: ## Run all pre-commit checks against the repository
	pre-commit run --all-files

migrate: ## Apply all pending database migrations
	uv run alembic upgrade head

revision: ## Create a migration; use msg="describe the change"
	uv run alembic revision --autogenerate -m "$(msg)"

seed: ## Seed the database using Alembic [seeders] configuration
	uv run alembic --name seeders upgrade head

seed-reset: ## Reset and reseed the database using Alembic seeders
	uv run alembic --name seeders downgrade base
	uv run alembic --name seeders upgrade head

docker-up: ## Start the application and database containers
	docker compose up -d

docker-down: ## Stop the application and database containers
	docker compose down

docker-logs: ## Follow application and database logs
	docker compose logs -f
