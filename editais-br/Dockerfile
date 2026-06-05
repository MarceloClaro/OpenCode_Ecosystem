# =============================================================================
# editais-br — Dockerfile multi-stage (Python 3.12)
# Targets: api (FastAPI), worker (Celery)
# =============================================================================

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Dependências de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

# --- Target: API ---
FROM base AS api
COPY alembic.ini .
COPY api/ /app/api/
COPY agents/ /app/agents/
COPY extractors/ /app/extractors/
COPY worker/ /app/worker/
COPY pipeline/ /app/pipeline/
COPY templates/ /app/templates/
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# --- Target: Worker ---
FROM base AS worker
COPY alembic.ini .
COPY api/ /app/api/
COPY agents/ /app/agents/
COPY extractors/ /app/extractors/
COPY worker/ /app/worker/
COPY pipeline/ /app/pipeline/
CMD ["celery", "-A", "worker.celery_app", "worker", "--loglevel=info"]
