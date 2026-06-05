"""EditalService refatorado com DI.

Implementa IEditalService com injecao de dependencia para:
- Sessao de banco (ISessionManager)
- Extratores (IExtractor para HTML e PDF)
- Motor de busca (ISearchEngine)
- Classificador (IEditalClassifier)
- Agente de extracao (IAgent)
"""

from __future__ import annotations
import logging
import os
import time
import uuid as uuid_lib
from typing import Any

try:
    from interfaces import (
        IEditalService,
        ISessionManager,
        IExtractor,
        ISearchEngine,
        IEditalClassifier,
        IAgent,
        EditalResult,
        JobInfo,
        EditalRaw,
    )
except ImportError:
    from editais_br_interfaces import (
        IEditalService,
        ISessionManager,
        IExtractor,
        ISearchEngine,
        IEditalClassifier,
        IAgent,
        EditalResult,
        JobInfo,
        EditalRaw,
    )

try:
    from extractors.html import HTMLExtractor
    from extractors.pdf import PDFExtractor
except ImportError:
    from editais_br_html_extractor import HTMLExtractor
    from editais_br_pdf_extractor import PDFExtractor

logger = logging.getLogger(__name__)


class SQLAlchemySessionManager(ISessionManager):
    """Gerenciador de sessao SQLAlchemy com DI."""

    def __init__(self, session_factory):
        self._factory = session_factory

    def get_session(self):
        db = self._factory()
        try:
            yield db
        finally:
            db.close()


class EditalService(IEditalService):
    """Implementacao concreta do servico de editais com DI.

    Args:
        session_mgr: Gerenciador de sessao do banco.
        html_extractor: Extrator de HTML.
        pdf_extractor: Extrator de PDF.
        search_engine: Motor de busca web.
        classifier: Classificador de paginas.
        extractor_agent: Agente de extracao com IA.
    """

    def __init__(
        self,
        session_mgr: ISessionManager,
        html_extractor: IExtractor | None = None,
        pdf_extractor: IExtractor | None = None,
        search_engine: ISearchEngine | None = None,
        classifier: IEditalClassifier | None = None,
        extractor_agent: IAgent | None = None,
    ):
        self._session = session_mgr
        self._html_extractor = html_extractor or HTMLExtractor.create_default()
        self._pdf_extractor = pdf_extractor or PDFExtractor.create_default()
        self._search_engine = search_engine
        self._classifier = classifier
        self._extractor_agent = extractor_agent

    # -- IEditalService ------------------------------------------------------

    def listar_editais(
        self,
        skip: int = 0,
        limit: int = 20,
        eixo_tematico: str | None = None,
        perfil_elegivel: str | None = None,
        mecanismo: str | None = None,
        abrangencia_tipo: str | None = None,
        estado: str | None = None,
        status: str | None = None,
        valor_min: float | None = None,
        valor_max: float | None = None,
        trl_min: int | None = None,
        trl_max: int | None = None,
        ordem: str = "data_publicacao",
    ) -> list[EditalResult]:
        """Lista editais com filtros e paginacao."""
        db = next(self._session.get_session())
        try:
            from api.models.edital import Edital

            query = db.query(Edital)

            if eixo_tematico:
                query = query.filter(Edital.eixos_tematicos.contains([eixo_tematico]))
            if perfil_elegivel:
                query = query.filter(Edital.perfil_elegivel.contains([perfil_elegivel]))
            if mecanismo:
                query = query.filter(Edital.mecanismo_financiamento == mecanismo)
            if abrangencia_tipo:
                query = query.filter(
                    Edital.abrangencia_geografica["tipo"].astext == abrangencia_tipo
                )
            if estado:
                query = query.filter(
                    Edital.abrangencia_geografica["estados"].contains([estado])
                )
            if status:
                query = query.filter(Edital.status_inscricao == status)
            if valor_min is not None:
                query = query.filter(Edital.valor_max >= valor_min)
            if valor_max is not None:
                query = query.filter(Edital.valor_min <= valor_max)
            if trl_min is not None:
                query = query.filter(Edital.nivel_trl_min >= trl_min)
            if trl_max is not None:
                query = query.filter(Edital.nivel_trl_max <= trl_max)

            ordem_coluna = getattr(Edital, ordem, Edital.criado_em)
            query = query.order_by(ordem_coluna.desc())

            editais = query.offset(skip).limit(limit).all()
            return [_edital_to_result(e) for e in editais]
        finally:
            db.close()

    def obter_edital(self, edital_id: str) -> EditalResult:
        """Obtem edital por ID."""
        try:
            uid = uuid_lib.UUID(edital_id)
        except ValueError:
            return EditalResult(error="UUID invalido")

        db = next(self._session.get_session())
        try:
            from api.models.edital import Edital

            edital = db.query(Edital).filter(Edital.id == uid).first()
            if not edital:
                return EditalResult(error="Edital nao encontrado")
            return _edital_to_result(edital)
        finally:
            db.close()

    def buscar_editais(self, query: str, max_results: int = 8) -> list[EditalResult]:
        """Busca editais sob demanda na web.

        Usa search_engine + classifier injetados para pipeline completo.
        """
        if not self._search_engine or not self._classifier:
            logger.error("SearchEngine e Classifier necessarios para busca")
            return []

        start = time.time()
        search_query = f'"{query}" edital fomento 2026'
        results = self._search_engine.search(search_query, max_results=max_results)

        resultados: list[EditalResult] = []
        for item in results:
            try:
                import httpx

                with httpx.Client(timeout=15, headers={"User-Agent": "Mozilla/5.0"}) as client:
                    resp = client.get(item["url"])
                    html = resp.text

                classification = self._classifier.classify(html)
                if classification.get("tipo") == "outro":
                    continue

                raw_text = self._extrair_conteudo(item["url"], html)

                resultados.append(
                    EditalResult(
                        titulo=item.get("title", ""),
                        url_original=item["url"],
                        raw_text=raw_text,
                        resumo=raw_text[:400] if raw_text else "",
                    )
                )

                if len(resultados) >= 5:
                    break

            except Exception as e:
                logger.warning(f"Erro ao processar {item.get('url', '')[:60]}: {e}")
                continue

        logger.info(f"Busca concluida: {len(resultados)} editais em {round(time.time() - start, 1)}s")
        return resultados

    def iniciar_crawl(self, portal_id: str) -> JobInfo:
        """Dispara job de crawl para portal."""
        try:
            uid = uuid_lib.UUID(portal_id)
        except ValueError:
            return JobInfo(id="", portal_id=portal_id, tipo="crawl", status="falhou",
                           mensagem="UUID invalido")

        db = next(self._session.get_session())
        try:
            from api.models.portal import Portal
            from api.models.job import Job

            portal = db.query(Portal).filter(Portal.id == uid).first()
            if not portal:
                return JobInfo(id="", portal_id=portal_id, tipo="crawl", status="falhou",
                               mensagem="Portal nao encontrado")

            job = Job(portal_id=uid, tipo="crawl", status="pendente")
            db.add(job)
            db.commit()
            db.refresh(job)

            return JobInfo(
                id=str(job.id),
                portal_id=str(job.portal_id),
                tipo=job.tipo,
                status=job.status,
            )
        finally:
            db.close()

    def obter_job(self, job_id: str) -> JobInfo:
        """Obtem status de um job."""
        try:
            uid = uuid_lib.UUID(job_id)
        except ValueError:
            return JobInfo(id="", portal_id="", tipo="crawl", status="falhou",
                           mensagem="UUID invalido")

        db = next(self._session.get_session())
        try:
            from api.models.job import Job

            job = db.query(Job).filter(Job.id == uid).first()
            if not job:
                return JobInfo(id="", portal_id="", tipo="crawl", status="falhou",
                               mensagem="Job nao encontrado")

            return JobInfo(
                id=str(job.id),
                portal_id=str(job.portal_id),
                tipo=job.tipo,
                status=job.status,
                progresso=job.progresso,
                mensagem=job.mensagem,
                resultado=job.resultado,
                created_at=str(job.created_at) if job.created_at else None,
                updated_at=str(job.updated_at) if job.updated_at else None,
            )
        finally:
            db.close()

    # -- Metodos internos ----------------------------------------------------

    def _extrair_conteudo(self, url: str, html: str) -> str:
        """Tenta extrair conteudo: PDF > HTML."""
        pdf_text = self._pdf_extractor.extract(url)
        if pdf_text:
            return pdf_text
        return self._html_extractor.extract(html)


# -- Funcoes auxiliares ------------------------------------------------------


def _edital_to_result(e: Any) -> EditalResult:
    """Converte modelo ORM Edital para EditalResult."""
    return EditalResult(
        id=str(e.id),
        titulo=e.titulo,
        financiador=e.financiador or "",
        url_original=e.url_original,
        pdf_url=e.pdf_url,
        valor_min=e.valor_min,
        valor_max=e.valor_max,
        moeda=e.moeda,
        data_abertura=str(e.data_abertura) if e.data_abertura else None,
        data_encerramento=str(e.data_encerramento) if e.data_encerramento else None,
        eixos_tematicos=e.eixos_tematicos or [],
        perfil_elegivel=e.perfil_elegivel or [],
        mecanismo_financiamento=e.mecanismo_financiamento,
        abrangencia_geografica=e.abrangencia_geografica,
        status=e.status_inscricao or e.status,
        nivel_trl_min=e.nivel_trl_min,
        nivel_trl_max=e.nivel_trl_max,
        score_complexidade=e.score_complexidade,
        resumo=e.resumo or "",
        raw_text=e.raw_text or "",
        requisitos_json=e.requisitos_json,
    )
