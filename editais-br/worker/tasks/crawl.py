"""Task: crawl_portal — busca editais de um portal e salva no banco."""

import logging

from api.database import SessionLocal
from api.models.edital import Edital
from api.models.portal import Portal
from pipeline.deduplicator import deduplicate
from worker.celery_app import app
from worker.tasks.extract import extract_edital  # noqa: E402
from worker.connectors.cnpq import CnpqConnector
from worker.connectors.fapeg import FapegConnector
from worker.connectors.finep import FinepConnector
from worker.connectors.prosas import ProsasConnector
from worker.connectors.sebrae import SebraeConnector
from worker.connectors.sigepe import SigepeConnector

logger = logging.getLogger(__name__)

CONNECTORS = {
    "prosas": ProsasConnector,
    "finep": FinepConnector,
    "sebrae": SebraeConnector,
    "cnpq": CnpqConnector,
    "fapeg": FapegConnector,
    "sigepe": SigepeConnector,
}


@app.task(bind=True, name="crawl_portal")
def crawl_portal(self, portal_id: str):
    """Busca editais de um portal e salva no banco.

    Args:
        portal_id: UUID do portal no banco de dados.
    """
    db = SessionLocal()
    try:
        portal = db.query(Portal).filter(Portal.id == portal_id).first()
        if not portal:
            logger.error(f"Portal {portal_id} não encontrado")
            return {"error": "Portal não encontrado"}

        connector_class = CONNECTORS.get(portal.nome.lower())
        if not connector_class:
            logger.error(f"Nenhum conector para portal '{portal.nome}'")
            return {"error": f"Conector não encontrado para {portal.nome}"}

        connector = connector_class()
        raw_editais = connector.fetch_editais()

        # Converte para dicionários e deduplica
        raw_dicts = [
            {
                "titulo": e.titulo,
                "url_original": e.url,
                "pdf_url": e.pdf_url,
                "data_publicacao": e.data_publicacao,
                "portal_id": str(portal.id),
            }
            for e in raw_editais
        ]
        unique = deduplicate(raw_dicts)

        novos = 0
        novos_ids = []
        for data in unique:
            existente = db.query(Edital).filter(
                Edital.url_original == data["url_original"]
            ).first()
            if not existente:
                edital = Edital(
                    portal_id=portal.id,
                    titulo=data["titulo"],
                    url_original=data["url_original"],
                    pdf_url=data.get("pdf_url"),
                    status="pendente",
                )
                db.add(edital)
                db.flush()
                novos_ids.append(str(edital.id))
                novos += 1

        db.commit()
        logger.info(f"Portal '{portal.nome}': {len(raw_editais)} raw, {novos} novos")

        # ⛓️ Pipeline: extrai texto de cada novo edital
        for eid in novos_ids:
            extract_edital.delay(eid)
            logger.info(f"  ⛓️ Extração enfileirada: {eid[:8]}...")
        return {"total_raw": len(raw_editais), "novos": novos}

    except Exception as e:
        logger.exception(f"Erro no crawl do portal {portal_id}: {e}")
        db.rollback()
        raise
    finally:
        db.close()
