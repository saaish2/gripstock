.PHONY: install dev initdb seed run test cov lint fmt migrate sweep clean

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

initdb:
	gripstock initdb

seed:
	gripstock seed

run:
	uvicorn app.main:app --reload

test:
	pytest

cov:
	pytest --cov=app --cov-report=term-missing

lint:
	ruff check app tests
	mypy app

fmt:
	ruff check --fix app tests
	ruff format app tests

migrate:
	alembic upgrade head

sweep:
	gripstock sweep

clean:
	rm -f gripstock.db
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache .mypy_cache
