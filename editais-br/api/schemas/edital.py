"""Schemas Pydantic para o sistema editais-br.

Define os modelos de dados validados usados na API e nos agentes.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class AbrangenciaGeografica(BaseModel):
    """Abrangência geográfica de um edital (Filtro 4)."""

    tipo: Literal["nacional", "regional", "estadual", "municipal"]
    regioes: list[str] = Field(default_factory=list)  # ex: ['sudeste', 'nordeste']
    estados: list[str] = Field(default_factory=list)  # ex: ['SP', 'RJ']
    municipios: list[str] = Field(default_factory=list)  # ex: ['São Paulo']


class EditalRequisitos(BaseModel):
    """Output estruturado do Agente 1 — requisitos de um edital (7 filtros)."""

    titulo: str
    financiador: str
    url_original: str
    valor_min: float | None = None
    valor_max: float | None = None
    moeda: str = "BRL"
    data_abertura: date | None = None
    data_encerramento: date | None = None

    # --- Filtro 1: Área / Eixo Temático ---
    eixos_tematicos: list[str] = Field(default_factory=list)
    # taxonomia: saude, educacao, meio_ambiente, tecnologia,
    # agricultura, cultura, esporte, direitos_humanos, desenvolvimento_social,
    # infraestrutura, energia, defesa, turismo, comercio_exterior, inovacao,
    # ciencias_exatas, ciencias_humanas, ciencias_biologicas, engenharia, outro

    # --- Filtro 2: Perfil do Proponente ---
    perfil_elegivel: list[str] = Field(default_factory=list)
    # osc, startup_early_stage, startup_growth, mpe, me, empresa_medio_porte,
    # empresa_grande, ict, pesquisador_individual, pessoa_fisica,
    # cooperativa, governo_estadual, governo_municipal, outro

    # --- Filtro 3: Mecanismo de Financiamento ---
    mecanismo_financiamento: str | None = None
    # bolsa, auxilio_pesquisa, subvencao_economica, emprestimo,
    # equity, premio, incentivo_fiscal, outro

    # --- Filtro 4: Abrangência Geográfica ---
    abrangencia_geografica: AbrangenciaGeografica | None = None

    # --- Filtro 5: Status ---
    status: Literal[
        "inscricoes_abertas",
        "em_breve",
        "encerrado",
        "fluxo_continuo",
        "suspenso",
        "cancelado",
    ] | None = None

    # --- Filtro 6: Faixa de Valor → coberto por valor_min/valor_max ---

    # --- Filtro 7: TRL (Technology Readiness Level) ---
    nivel_trl_min: int | None = Field(None, ge=1, le=9)
    nivel_trl_max: int | None = Field(None, ge=1, le=9)

    # --- Campos complementares ---
    temas: list[str] = Field(default_factory=list)  # tags livres
    requisitos_obrigatorios: list[str] = Field(default_factory=list)
    documentos_necessarios: list[str] = Field(default_factory=list)
    contrapartida_exigida: bool = False
    resumo: str = ""
    score_complexidade: int = Field(1, ge=1, le=5)
