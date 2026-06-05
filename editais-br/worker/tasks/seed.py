"""Task: seed_automatico — garante dados iniciais no banco."""

import logging

from worker.celery_app import app
from api.database import SessionLocal
from api.models.portal import Portal

logger = logging.getLogger(__name__)

PORTAIS_PADRAO = [
    {"nome": "prosas", "base_url": "https://prosas.com.br/editais", "mode": "http"},
    {"nome": "finep", "base_url": "https://www.finep.gov.br/chamadas-publicas", "mode": "http"},
    {"nome": "fapeg", "base_url": "https://fapeg.go.gov.br/editais", "mode": "http"},
    {"nome": "sebrae", "base_url": "https://www.sebrae.com.br/editais", "mode": "http"},
    {"nome": "cnpq", "base_url": "https://www.gov.br/cnpq", "mode": "http"},
]


@app.task(bind=True, name="seed_automatico")
def seed_automatico(self) -> dict:
    """Garante que os portais padrão estejam cadastrados no banco.

    Executado automaticamente pelo Celery Beat na inicialização.
    Idempotente: só insere portais que ainda não existem.
    """
    db = SessionLocal()
    criados = 0

    try:
        for portal_data in PORTAIS_PADRAO:
            exists = db.query(Portal).filter(Portal.nome == portal_data["nome"]).first()
            if not exists:
                db.add(Portal(**portal_data))
                criados += 1
                logger.info(f"📡 Portal cadastrado: {portal_data['nome']}")

        db.commit()

        if criados:
            logger.info(f"✅ {criados} novos portais cadastrados")
        else:
            logger.info("✅ Todos os portais já estavam cadastrados")

        return {"portais_criados": criados, "total": len(PORTAIS_PADRAO)}

    except Exception as e:
        logger.exception(f"Erro no seed automático: {e}")
        db.rollback()
        raise
    finally:
        db.close()
