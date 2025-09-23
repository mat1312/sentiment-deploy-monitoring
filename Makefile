.PHONY: dev test fmt lint

dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest -q

docker-build:
	docker build -t sentiment-api:local .

compose-up:
	docker compose up -d

compose-down:
	docker compose down
