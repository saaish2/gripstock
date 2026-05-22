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