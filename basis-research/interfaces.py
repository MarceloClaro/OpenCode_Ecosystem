"""
seeker/interfaces.py (proposto) - Contratos Abstratos para Agentes SEEKER.
Define as interfaces que todos os agentes SEEKER devem implementar,
permitindo injeção de dependência do Container (IStateManager, IEventBus).
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol


# ─── Tipos Compartilhados ─────────────────────────────────────────────────────

class ResearchContext(Protocol):
    """Contexto de execução passado entre agentes na pipeline."""
    run_id: str
    problem: str
    config: dict


# ─── Interfaces Base ──────────────────────────────────────────────────────────

class ISeekerAgent(ABC):
    """Contrato base que todo agente SEEKER deve implementar."""

    @property
    @abstractmethod
    def agent_name(self) -> str: ...

    @abstractmethod
    def run(self, context: str, run_id: str, **kwargs) -> dict:
        """
        Executa o agente.
        Retorna dict com resultados (estrutura varia por agente).
        """
        ...


class ILLMRouter(ABC):
    """Router de LLM com fallback Claude → Ollama."""

    @abstractmethod
    def call(
        self,
        prompt: str,
        system: str = "You are a helpful research assistant.",
        agent_name: str = "unknown",
        force_local: bool = False,
    ) -> str: ...

    @abstractmethod
    def health_check(self) -> dict:
        """Retorna status dos modelos disponíveis."""
        ...


class IArgumentTree(ABC):
    """Árvore de argumentos persistente."""

    @abstractmethod
    def create_root(self, problem: str) -> str: ...

    @abstractmethod
    def add_question(
        self, parent_id: str, question_text: str,
        question_level: str = "foundational", agent: str = "grounder",
    ) -> str: ...

    @abstractmethod
    def add_claim(
        self, parent_question_id: str, claim_text: str,
        confidence: float = 0.5, agent: str = "grounder",
        source_ids: list = None,
    ) -> str: ...

    @abstractmethod
    def add_evidence(
        self, parent_claim_id: str, source_id: str,
        evidence_type: str = "paper", relationship: str = "supports",
        snippet: str = "", agent: str = "grounder",
        metadata: dict = None,
    ) -> str: ...

    @abstractmethod
    def add_bridge(
        self, from_node_id: str, to_node_id: str,
        source_id: str, bridge_type: str = "temporal",
        description: str = "", agent: str = "social",
    ) -> str: ...

    @abstractmethod
    def add_counter(
        self, parent_claim_id: str, counter_text: str,
        source_id: str, agent: str = "grounder",
    ) -> str: ...

    @abstractmethod
    def get_tree(self) -> dict: ...

    @abstractmethod
    def get_branch(self, node_id: str) -> dict: ...

    @abstractmethod
    def find_gaps(self) -> list[dict]: ...

    @abstractmethod
    def find_bridge_needs(self, min_gap_years: int = 15) -> list[dict]: ...

    @abstractmethod
    def to_context(self, max_depth: int = 4, include_evidence: bool = True) -> str: ...

    @abstractmethod
    def get_stats(self) -> dict: ...

    @abstractmethod
    def close(self) -> None: ...


class IDatabase(ABC):
    """Interface de persistência do pipeline."""

    @abstractmethod
    def get_sources_by_type(self, source_type: str, run_id: str) -> list[dict]: ...

    @abstractmethod
    def get_gaps(self, run_id: str, significance: str = None) -> list[dict]: ...

    @abstractmethod
    def get_implications(self, run_id: str) -> list[dict]: ...

    @abstractmethod
    def get_proposals(self, run_id: str, status: str = None) -> list[dict]: ...

    @abstractmethod
    def get_evaluations(self, run_id: str) -> list[dict]: ...

    @abstractmethod
    def get_synthesis(self, run_id: str) -> Optional[dict]: ...

    @abstractmethod
    def get_directions(self, run_id: str) -> list[dict]: ...

    @abstractmethod
    def get_artifacts(self, run_id: str) -> list[dict]: ...

    @abstractmethod
    def get_run(self, run_id: str) -> Optional[dict]: ...

    @abstractmethod
    def create_run(self, run_id: str, problem: str) -> None: ...

    @abstractmethod
    def update_run_status(self, run_id: str, status: str) -> None: ...

    @abstractmethod
    def close(self) -> None: ...


class IContextBuilder(ABC):
    """Constrói contexto específico para cada agente."""

    @abstractmethod
    def for_grounder(self, run_id: str, problem: str, social_sources: list) -> str: ...

    @abstractmethod
    def for_historian(self, run_id: str, problem: str) -> str: ...

    @abstractmethod
    def for_gaper(self, run_id: str, problem: str, break1: str = None) -> str: ...

    @abstractmethod
    def for_vision(self, run_id: str, problem: str, break1: str = None) -> str: ...

    @abstractmethod
    def for_theorist(self, run_id: str, problem: str, break1: str = None) -> str: ...

    @abstractmethod
    def for_rude(self, run_id: str, problem: str, break1: str = None) -> str: ...

    @abstractmethod
    def for_synthesizer(self, run_id: str, problem: str, break1: str = None) -> str: ...

    @abstractmethod
    def for_thinker(self, run_id: str, problem: str, break2: str = None) -> str: ...

    @abstractmethod
    def for_scribe(self, run_id: str, problem: str, output_type: str,
                   audience: str, break2: str = None) -> str: ...

    @abstractmethod
    def for_understanding_map(self, run_id: str, problem: str) -> str: ...


# ─── Interfaces de Pipeline ───────────────────────────────────────────────────

class IPipelineOrchestrator(ABC):
    """Orquestrador da pipeline SEEKER."""

    @abstractmethod
    def run_pipeline(
        self, problem: str, run_id: str = None, resume: bool = False,
    ) -> dict: ...

    @abstractmethod
    def run_step(
        self, step_name: str, agent_fn, context: str, run_id: str,
        extra: dict = None,
    ) -> bool: ...

    @abstractmethod
    def agent_done(self, run_id: str, agent: str) -> bool: ...


class ISourceHandler(ABC):
    """Handler de fonte acadêmica (OpenAlex, arXiv, etc.)."""

    SOURCE_ID: str = "unknown"
    BASE_URL: str = ""

    @abstractmethod
    def search(self, query: str, keywords: list[str],
               limit: int = 10, run_id: str = "") -> list[dict]: ...

    @abstractmethod
    def check_link(self, url: str) -> str: ...


# ─── Agentes Específicos ──────────────────────────────────────────────────────

class IGrounderAgent(ISeekerAgent):
    """Decompõe problema em sub-questões e busca obras seminais."""


class ISocialAgent(ISeekerAgent):
    """Busca fontes contemporâneas e conecta pontes temporais."""


class IHistorianAgent(ISeekerAgent):
    """Audita árvore, busca contexto histórico e fatores externos."""


class IGaperAgent(ISeekerAgent):
    """Mapeia lacunas na árvore de argumentos."""


class IVisionAgent(ISeekerAgent):
    """Implicações e direções futuras da pesquisa."""


class ITheoristAgent(ISeekerAgent):
    """Propõe enquadramentos teóricos e hipóteses."""


class IRudeAgent(ISeekerAgent):
    """Revisão adversarial crítica de propostas."""


class ISynthesizerAgent(ISeekerAgent):
    """Sintetiza descobertas em narrativa coesa."""


class IThinkerAgent(ISeekerAgent):
    """Raciocínio aprofundado e novas direções."""


class IScribeAgent(ISeekerAgent):
    """Produz artefatos finais (understanding_map, research_brief, etc.)."""
