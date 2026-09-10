install:
	pip install -e ".[dev]"

dev-qdrant:
	docker compose up -d qdrant

ingest:
	python -m backend.ingestion.ingest --pdf data/docker_kubernetes_dataset.pdf

backend:
	uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	python frontend/app.py

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

compose:
	docker compose --profile app up --build

down:
	docker compose down

clean:
	docker compose down -v
