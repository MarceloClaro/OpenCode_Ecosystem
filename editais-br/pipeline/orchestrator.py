"""OrchestratorAgent — supervisor do pipeline de processamento de editais.

Coordena o fluxo: crawl → dedup → extract → analyze.
"""

import logging

from agents.base import BaseAgent
from pipeline.deduplicator import deduplicate
from worker.connectors.base import BaseConnector

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Orquestrador do pipeline de processamento de editais.

    Responsável por coordenar o fluxo completo:
    1. Crawl do portal (via connector)
    2. Deduplicação dos editais brutos
    3. Extração de texto (PDF ou HTML)
    4. Análise com IA (via agent)
    """

    def __init__(
        self,
        connector: BaseConnector,
        extractor,  # BaseExtractor (sem dependência circular)
        agent: BaseAgent,
    ):
        self.connector = connector
        self.extractor = extractor
        self.agent = agent

    def run(self) -> list[dict]:
        """Executa o pipeline completo para o portal configurado.

        Returns:
            Lista de dicionários com os resultados da análise de cada edital.
        """
        # 1. Crawl
        logger.info(f"Iniciando crawl: {self.connector.base_url}")
        raw_editais = self.connector.fetch_editais()
        logger.info(f"Encontrados {len(raw_editais)} editais brutos")

        # 2. Deduplicação
        raw_dicts = [
            {
                "titulo": e.titulo,
                "url_original": e.url,
                "pdf_url": e.pdf_url,
                "data_publicacao": e.data_publicacao,
                "portal_id": None,  # será preenchido pelo caller com DB
            }
            for e in raw_editais
        ]
        unique = deduplicate(raw_dicts)
        logger.info(f"Após deduplicação: {len(unique)} editais únicos")

        resultados = []

        for edital_data in unique:
            try:
                # 3. Extração de texto (se tiver PDF URL)
                raw_text = None
                if edital_data.get("pdf_url"):
                    raw_text = self.extractor.extract(edital_data["pdf_url"])
                    logger.debug(f"Texto extraído: {len(raw_text or '')} caracteres")

                # 4. Análise com IA
                input_text = raw_text or edital_data.get("titulo", "")
                analysis = self.agent.execute(input_text)
                analysis["url_original"] = edital_data["url_original"]
                analysis["titulo"] = edital_data.get("titulo", "")

                resultados.append(analysis)
                logger.info(f"Analisado: {edital_data.get('titulo', 'sem título')}")

            except Exception as e:
                logger.error(f"Erro ao processar {edital_data.get('url_original')}: {e}")
                continue

        logger.info(f"Pipeline concluído. {len(resultados)} editais analisados.")
        return resultados
