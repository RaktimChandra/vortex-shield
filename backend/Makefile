.PHONY: help install test lint format run dev migrate train clean docker-up docker-down

help:
	@echo "VORTEX Shield 2.0 - Development Commands"
	@echo ""
	@echo "install     - Install all dependencies"
	@echo "test        - Run all tests"
	@echo "test-cov    - Run tests with coverage"
	@echo "lint        - Run linters"
	@echo "format      - Format code"
	@echo "run         - Run backend server"
	@echo "dev         - Run in development mode"
	@echo "migrate     - Run database migrations"
	@echo "train       - Train AI models"
	@echo "clean       - Clean temporary files"
	@echo "docker-up   - Start Docker services"
	@echo "docker-down - Stop Docker services"

install:
	pip install -r requirements.txt
	pip install -r requirements.prod.txt

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-integration:
	pytest tests/test_integration.py -v

test-performance:
	pytest tests/test_performance.py -v --benchmark-only

lint:
	flake8 app/ tests/
	pylint app/
	mypy app/

format:
	black app/ tests/
	isort app/ tests/

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(message)"

train:
	python -m app.ai.model_trainer

init-db:
	python app/scripts/init_database.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .mypy_cache

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
