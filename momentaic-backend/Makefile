# MomentAIc Backend Makefile
# Convenience commands for development and deployment

.PHONY: help install dev test lint format migrate run docker-up docker-down clean

# Default target
help:
	@echo "MomentAIc Backend Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Run development server"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linter"
	@echo "  make format     - Format code"
	@echo ""
	@echo "Database:"
	@echo "  make migrate    - Run database migrations"
	@echo "  make migration  - Create new migration (MSG=description)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up   - Start all services"
	@echo "  make docker-down - Stop all services"
	@echo "  make docker-logs - View logs"
	@echo ""
	@echo "Celery:"
	@echo "  make worker     - Start Celery worker"
	@echo "  make beat       - Start Celery beat"
	@echo "  make flower     - Start Flower monitoring"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean      - Remove generated files"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install ruff mypy pytest pytest-asyncio pytest-cov aiosqlite

# Development
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-unit:
	pytest tests/ -v -m unit

test-integration:
	pytest tests/ -v -m integration

# Linting & Formatting
lint:
	ruff check app/ tests/

lint-fix:
	ruff check app/ tests/ --fix

format:
	ruff format app/ tests/

format-check:
	ruff format app/ tests/ --check

typecheck:
	mypy app/ --ignore-missing-imports

# Database
migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(MSG)"

migrate-down:
	alembic downgrade -1

migrate-history:
	alembic history

# Docker
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	docker-compose build

docker-rebuild:
	docker-compose build --no-cache

docker-shell:
	docker-compose exec api /bin/bash

# Celery
worker:
	celery -A app.tasks.celery_app worker --loglevel=info -Q default,workflows,signals,content,email

beat:
	celery -A app.tasks.celery_app beat --loglevel=info

flower:
	celery -A app.tasks.celery_app flower --port=5555

# Production
prod-build:
	docker build -t momentaic:latest .

prod-push:
	docker push your-registry/momentaic:latest

# Security
security-scan:
	bandit -r app/ -ll -ii

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	find . -type d -name ".ruff_cache" -delete
	find . -type d -name "htmlcov" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete

# Quick development setup
setup: install-dev migrate
	@echo "Setup complete! Run 'make dev' to start the server."

# All checks before commit
check: lint-fix format typecheck test
	@echo "All checks passed!"
