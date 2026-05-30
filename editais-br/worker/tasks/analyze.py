"""Task: analyze_edital — analisa texto de edital com IA (Agente 1)."""

import logging
import os

from agents.extractor import ExtractorAgent
from api.database import SessionLocal
from api.models.edital import Edital
from worker.celery_app import app

logger = logging.getLogger(__name__)


@app.task(bind=True, name="analyze_edital")
def analyze_edital(self, edital_id: str):
    """Analisa o texto de um edital e extrai requisitos estruturados.

    Args:
        edital_id: UUID do edital no banco de dados.
    """
    db = SessionLocal()
    try:
        edital = db.query(Edital).filter(Edital.id == edital_id).first()
        if not edital:
            logger.error(f"Edital {edital_id} não encontrado")
            return {"error": "Edital não encontrado"}

        if not edital.raw_text:
            logger.error(f"Edital {edital_id}: sem texto para analisar")
            return {"error": "Edital sem texto extraído — execute extract_edital primeiro"}

        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        if not api_key:
            logger.error("DEEPSEEK_API_KEY não configurada")
            return {"error": "API key não configurada"}

        agent = ExtractorAgent(api_key=api_key)
        result = agent.execute(edital.raw_text)

        # Salva resultado
        edital.requisitos_json = result
        edital.titulo = result.get("titulo", edital.titulo)
        edital.financiador = result.get("financiador")
        edital.valor_min = result.get("valor_min")
        edital.valor_max = result.get("valor_max")
        edital.eixos_tematicos = result.get("eixos_tematicos")
        edital.perfil_elegivel = result.get("perfil_elegivel")
        edital.mecanismo_financiamento = result.get("mecanismo_financiamento")
        edital.status_inscricao = result.get("status")
        edital.nivel_trl_min = result.get("nivel_trl_min")
        edital.nivel_trl_max = result.get("nivel_trl_max")
        edital.score_complexidade = result.get("score_complexidade")
        edital.resumo = result.get("resumo")
        edital.status = "analisado"

        db.commit()
        logger.info(f"Edital {edital_id}: análise concluída")
        return {"status": "analisado", "titulo": edital.titulo}

    except Exception as e:
        logger.exception(f"Erro na análise do edital {edital_id}: {e}")
        db.rollback()
        raise
    finally:
        db.close()
