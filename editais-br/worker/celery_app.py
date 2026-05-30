"""Celery app configuration — com agendamento automático (Beat)."""

import os

from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

app = Celery(
    "editais-br",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "worker.tasks.crawl",
        "worker.tasks.extract",
        "worker.tasks.analyze",
        "worker.tasks.discover",
        "worker.tasks.seed",
    ],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        # Seed automático: roda 30s após startup
        "seed_automatico_startup": {
            "task": "seed_automatico",
            "schedule": 30.0,
            "options": {"expires": 60},
        },
        # Descoberta a cada 2 horas (durante o dia)
        "discover_editais_frequente": {
            "task": "discover_editais",
            "schedule": crontab(hour="6-22/2", minute=30),
            "kwargs": {"max_results": 15},
        },
    },
)
