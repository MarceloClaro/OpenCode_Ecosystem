.PHONY: up down logs test test-integration shell deploy migrate

# --- Desenvolvimento ---
up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

build:
	docker compose build --no-cache

# --- Testes ---
test:
	docker compose exec api pytest tests/unit/ -v

test-integration:
	docker compose exec api pytest tests/integration/ -v -m integration

test-all:
	docker compose exec api pytest -v

# --- Banco ---
migrate:
	docker compose exec api alembic upgrade head

migration:
	docker compose exec api alembic revision --autogenerate -m "$(msg)"

# --- Utilitários ---
shell:
	docker compose exec api bash

psql:
	docker compose exec postgres psql -U editais -d editais

# --- Deploy (VPS) ---
deploy:
	git push origin main
	ssh $(VPS_USER)@$(VPS_HOST) "cd /opt/editais-br && git pull && docker compose up -d --build"
