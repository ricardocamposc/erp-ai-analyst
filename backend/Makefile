SHELL := /bin/sh

COMPOSE := docker compose --project-name $${COMPOSE_PROJECT_NAME:-erp-ai-analyst}

.PHONY: run run_docker migrate refresh_db confirmed_refresh_db seed_db seed_db_local validate_data evaluate test lint format typecheck check

run:
	$(COMPOSE) up -d db
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run_docker:
	$(COMPOSE) up --build api db

migrate:
	$(COMPOSE) up -d db
	alembic upgrade head

refresh_db:
	@printf 'This removes the local database volume. Type RESET to continue: '; read answer; [ "$$answer" = "RESET" ] || { echo 'Cancelled.'; exit 1; }; $(MAKE) confirmed_refresh_db

confirmed_refresh_db:
	$(COMPOSE) down -v
	$(COMPOSE) up -d db
	alembic upgrade head

seed_db: migrate
	python scripts/seed_database.py

seed_db_local: seed_db

validate_data:
	python scripts/validate_data.py

evaluate:
	python scripts/run_evaluation.py

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy app tests

check: lint typecheck test
