"""Interfaces abstratas para o modulo editais-br.

Define contratos para extratores (HTML/PDF) e servico principal,
permitindo injecao de dependencia e testabilidade isolada.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal


# -- DTOs --------------------------------------------------------------------


@dataclass
class EditalRaw:
    """Dados brutos de um edital extraido de portal, antes do processamento."""

    titulo: str
    url: str
    pdf_url: str | None = None
    data_publicacao: str | None = None


@dataclass
class EditalResult:
    """Resultado final apos pipeline completo (crawl -> extract -> analyze)."""

    id: str = ""
    titulo: str = ""
    financiador: str = ""
    url_original: str = ""
    pdf_url: str | None = None
    valor_min: float | None = None
    valor_max: float | None = None
    moeda: str = "BRL"
    data_abertura: str | None = None
    data_encerramento: str | None = None
    eixos_tematicos: list[str] = field(default_factory=list)
    perfil_elegivel: list[str] = field(default_factory=list)
    mecanismo_financiamento: str | None = None
    abrangencia_geografica: dict | None = None
    status: str | None = None
    nivel_trl_min: int | None = None
    nivel_trl_max: int | None = None
    score_complexidade: int | None = None
    resumo: str = ""
    raw_text: str = ""
    requisitos_json: dict | None = None
    error: str | None = None


@dataclass
class JobInfo:
    """Informacoes de um job de processamento."""

    id: str
    portal_id: str
    tipo: Literal["crawl", "extract", "analyze"]
    status: Literal["pendente", "executando", "concluido", "falhou"]
    progresso: int = 0
    mensagem: str | None = None
    resultado: dict | None = None
    created_at: str | None = None
    updated_at: str | None = None


# -- Interfaces --------------------------------------------------------------


class IExtractor(ABC):
    """Contrato para extratores de texto (HTML, PDF)."""

    @abstractmethod
    def extract(self, raw: bytes | str) -> str:
        """Extrai texto do conteudo bruto."""
        ...


class IHTMLParser(ABC):
    """Contrato para parsing de conteudo HTML."""

    @abstractmethod
    def clean_html(self, html: str) -> str:
        """Remove scripts, estilos e tags, retornando texto limpo."""
        ...

    @abstractmethod
    def find_pdf_links(self, html: str, base_url: str) -> list[str]:
        """Encontra links de PDF em uma pagina HTML."""
        ...


class IPDFParser(ABC):
    """Contrato para parsing de conteudo PDF."""

    @abstractmethod
    def pdf_to_text(self, pdf_bytes: bytes) -> str:
        """Converte bytes PDF para texto."""
        ...

    @abstractmethod
    def pdf_to_markdown(self, pdf_bytes: bytes) -> str:
        """Converte bytes PDF para Markdown."""
        ...


class IConnector(ABC):
    """Contrato para conectores de portais de editais."""

    mode: Literal["http", "browser"] = "http"
    base_url: str = ""
    crawl_interval_hours: int = 24

    @abstractmethod
    def fetch_editais(self) -> list[EditalRaw]:
        """Busca lista de editais do portal."""
        ...

    @abstractmethod
    def parse(self, content: str) -> list[EditalRaw]:
        """Converte HTML/JSON do portal em objetos EditalRaw."""
        ...


class ISearchEngine(ABC):
    """Contrato para motores de busca web."""

    @abstractmethod
    def search(self, query: str, max_results: int = 20) -> list[dict]:
        """Busca na web e retorna resultados."""
        ...


class IEditalClassifier(ABC):
    """Contrato para classificadores de paginas web."""

    @abstractmethod
    def classify(self, html: str) -> dict:
        """Classifica pagina como edital, portal_list ou outro."""
        ...


class IAgent(ABC):
    """Contrato para agentes de IA no pipeline."""

    model: str = ""
    api_key: str = ""

    @abstractmethod
    def execute(self, input_data: str) -> dict:
        """Executa o agente com dados de entrada."""
        ...


class IOrchestrator(ABC):
    """Contrato para o orquestrador do pipeline."""

    @abstractmethod
    def run(self) -> list[dict]:
        """Executa pipeline completo (crawl -> dedup -> extract -> analyze)."""
        ...


class IDeduplicator(ABC):
    """Contrato para deduplicacao de editais."""

    @abstractmethod
    def is_duplicate(self, a: dict, b: dict, threshold: float = 0.85) -> bool:
        """Verifica se dois editais sao duplicatas."""
        ...

    @abstractmethod
    def deduplicate(self, editais: list[dict]) -> list[dict]:
        """Remove duplicatas de uma lista."""
        ...


class IEditalService(ABC):
    """Contrato para o servico central de editais.

    Agrupa as operacoes de dominio expostas pela API FastAPI.
    """

    @abstractmethod
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
        """Lista editais com filtros opcionais e paginacao."""
        ...

    @abstractmethod
    def obter_edital(self, edital_id: str) -> EditalResult:
        """Obtem edital especifico por ID."""
        ...

    @abstractmethod
    def buscar_editais(self, query: str, max_results: int = 8) -> list[EditalResult]:
        """Busca editais sob demanda na web."""
        ...

    @abstractmethod
    def iniciar_crawl(self, portal_id: str) -> JobInfo:
        """Dispara job de crawl para um portal."""
        ...

    @abstractmethod
    def obter_job(self, job_id: str) -> JobInfo:
        """Obtem status de um job."""
        ...


class ISessionManager(ABC):
    """Contrato para gerenciamento de sessao de banco de dados."""

    @abstractmethod
    def get_session(self):
        """Retorna uma sessao do banco."""
        ...
