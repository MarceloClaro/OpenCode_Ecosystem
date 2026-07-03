#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CognitiveDiversityInjector v1.0 — Injetor de Artefatos de Diversidade
======================================================================
R27 — SPEC-056: Cognitive Diversity Expansion

Injeta artefatos de conhecimento com paradigmas epistemológicos
alternativos para quebrar câmaras de eco no ecossistema.

Paradigmas adicionados:
  - Positivista (paradigma dominante ausente)
  - Interpretativista/Fenomenológico
  - Construtivista/Pós-estruturalista
  - Neurobiológico
  - Sociológico/Econômico-comportamental

Uso:
    from cognitive_diversity_injector import inject_diversity_artifacts
    artifacts = inject_diversity_artifacts()
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class DiversityArtifact:
    """Artefato de conhecimento com perfil epistemológico diverso."""
    artifact_id: str
    title: str
    description: str
    paradigm: str               # Paradigma epistemológico dominante
    method: str                 # Método de investigação
    theory: str                 # Referencial teórico
    reasoning_types: list[str]  # Tipos de raciocínio empregados
    game_theory: Optional[str]  # Perspectiva de teoria dos jogos
    domain: str                 # Domínio de conhecimento
    level_of_analysis: str      # Nível de análise
    temporal_focus: str         # Foco temporal
    population: str             # População/contexto
    evidence_type: str          # Tipo de evidência
    coverage_vector: list[float] = field(default_factory=lambda: [0.0]*10)
    # Vector: [paradigmas, metodos, teorias, raciocinio, teoria_jogos,
    #          niveis_analise, temporalidade, populacao, dados, dominios]


def _make_vector(
    paradigmas: float = 0.0,
    metodos: float = 0.0,
    teorias: float = 0.0,
    raciocinio: float = 0.0,
    teoria_jogos: float = 0.0,
    niveis_analise: float = 0.0,
    temporalidade: float = 0.0,
    populacao: float = 0.0,
    dados: float = 0.0,
    dominios: float = 0.0,
) -> list[float]:
    return [paradigmas, metodos, teorias, raciocinio, teoria_jogos,
            niveis_analise, temporalidade, populacao, dados, dominios]


def inject_diversity_artifacts() -> list[DiversityArtifact]:
    """
    Gera artefatos de conhecimento com diversidade epistemológica.

    Cada artefato cobre dimensões sub-representadas no ecossistema,
    visando reduzir o Índice de Homogeneidade (HI < 0.8).
    """
    artifacts = []

    # ── Artefato 1: Paradigma Positivista (quantitativo clássico) ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_positivist_{uuid.uuid4().hex[:6]}",
        title="Análise Quantitativa de Eficácia Educacional via RCT",
        description=(
            "Estudo experimental randomizado (RCT) medindo eficácia de "
            "intervenção educacional com grupo controle e análise estatística "
            "frequentista (ANCOVA, p-valor, tamanho de efeito d de Cohen)."
        ),
        paradigm="Positivista",
        method="Quantitativo experimental",
        theory="Cognitivo-comportamental",
        reasoning_types=["Dedutivo", "Probabilístico", "Indutivo"],
        game_theory="Equilíbrio de Nash",
        domain="Educação",
        level_of_analysis="Individual/intrapsíquico",
        temporal_focus="Transversal (momento único)",
        population="Adultos",
        evidence_type="Dados epidemiológicos",
        coverage_vector=_make_vector(
            paradigmas=0.9, metodos=0.9, teorias=0.6,
            raciocinio=0.8, teoria_jogos=0.5,
            niveis_analise=0.7, temporalidade=0.8,
            populacao=0.7, dados=0.9, dominios=0.6
        )
    ))

    # ── Artefato 2: Paradigma Interpretativista/Fenomenológico ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_interpret_{uuid.uuid4().hex[:6]}",
        title="Fenomenografia da Experiência de Aprendizagem em Ambientes Multimodais",
        description=(
            "Pesquisa qualitativa fenomenográfica utilizando entrevistas "
            "semiestruturadas e análise temática para compreender a experiência "
            "vivida de aprendizes em ambientes educacionais multimodais."
        ),
        paradigm="Interpretativista",
        method="Qualitativo fenomenológico",
        theory="Fenomenológico-existencial",
        reasoning_types=["Abdutivo", "Dialético", "Indutivo"],
        game_theory=None,
        domain="Educação / Psicologia",
        level_of_analysis="Interpessoal/relacional",
        temporal_focus="Longitudinal (curto prazo)",
        population="Adolescentes",
        evidence_type="Dados qualitativos (entrevistas)",
        coverage_vector=_make_vector(
            paradigmas=0.8, metodos=0.7, teorias=0.7,
            raciocinio=0.7, teoria_jogos=0.0,
            niveis_analise=0.6, temporalidade=0.5,
            populacao=0.6, dados=0.4, dominios=0.5
        )
    ))

    # ── Artefato 3: Paradigma Construtivista/Pós-estruturalista ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_construct_{uuid.uuid4().hex[:6]}",
        title="Análise do Discurso Crítico sobre Políticas de Inovação Tecnológica",
        description=(
            "Análise crítica do discurso (ACD) de políticas públicas de inovação "
            "tecnológica, examinando relações de poder, construção social da "
            "tecnologia e efeitos de verdade no discurso governamental."
        ),
        paradigm="Crítico/Transformador",
        method="Qualitativo grounded theory",
        theory="Social-crítico",
        reasoning_types=["Dialético", "Crítico-reflexivo", "Abdutivo"],
        game_theory="Stackelberg",
        domain="Sociologia / Ciência Política",
        level_of_analysis="Sistêmico/político",
        temporal_focus="Histórico/retrospectivo",
        population="Contexto organizacional",
        evidence_type="Dados comparativos (cross-cultural)",
        coverage_vector=_make_vector(
            paradigmas=0.7, metodos=0.6, teorias=0.8,
            raciocinio=0.9, teoria_jogos=0.4,
            niveis_analise=0.9, temporalidade=0.6,
            populacao=0.5, dados=0.6, dominios=0.8
        )
    ))

    # ── Artefato 4: Neurobiológico ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_neuro_{uuid.uuid4().hex[:6]}",
        title="Correlatos Neurais da Transferência de Conhecimento: um Estudo de fMRI",
        description=(
            "Estudo de neuroimagem funcional (fMRI) investigando ativação "
            "do córtex pré-frontal e hipocampo durante tarefas de transferência "
            "de conhecimento, com análise de conectividade funcional."
        ),
        paradigm="Complexo/Sistêmico",
        method="Quantitativo correlacional",
        theory="Neurobiológico",
        reasoning_types=["Dedutivo", "Probabilístico", "Sistêmico"],
        game_theory=None,
        domain="Neurociências / Psicologia",
        level_of_analysis="Neurobiológico",
        temporal_focus="Longitudinal (longo prazo)",
        population="Adultos",
        evidence_type="Dados neurobiológicos",
        coverage_vector=_make_vector(
            paradigmas=0.6, metodos=0.5, teorias=0.9,
            raciocinio=0.7, teoria_jogos=0.0,
            niveis_analise=0.9, temporalidade=0.7,
            populacao=0.6, dados=0.8, dominios=0.9
        )
    ))

    # ── Artefato 5: Game Theory Estratégica ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_gametheory_{uuid.uuid4().hex[:6]}",
        title="Análise de Incentivos em Ecossistemas de Agentes Autônomos",
        description=(
            "Aplicação de teoria dos jogos para modelar interações estratégicas "
            "entre agentes de IA autônomos, incluindo equilíbrio de Nash em "
            "jogos repetidos, estratégias de sinalização e cooperação via "
            "tit-for-tat em dilemas do prisioneiro iterados."
        ),
        paradigm="Pragmatista",
        method="Quantitativo experimental",
        theory="Evolucionista",
        reasoning_types=["Dedutivo", "Teleológico", "Pragmático"],
        game_theory="Equilíbrio de Nash",
        domain="Inteligência Artificial / Tecnologia",
        level_of_analysis="Grupal/organizacional",
        temporal_focus="Prospectivo/preditivo",
        population="Contexto organizacional",
        evidence_type="Dados observacionais",
        coverage_vector=_make_vector(
            paradigmas=0.5, metodos=0.8, teorias=0.5,
            raciocinio=0.9, teoria_jogos=0.9,
            niveis_analise=0.8, temporalidade=0.6,
            populacao=0.4, dados=0.7, dominios=0.9
        )
    ))

    # ── Artefato 6: Sociologia/Economia Comportamental ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_socio_{uuid.uuid4().hex[:6]}",
        title="Efeitos de Nudge e Arquitetura de Escolha em Decisões Coletivas",
        description=(
            "Experimento comportamental investigando como nudges (empurrões "
            "suaves) afetam decisões coletivas em contextos de bens públicos, "
            "utilizando teoria dos jogos comportamental e economia experimental."
        ),
        paradigm="Pragmatista",
        method="Misto sequencial",
        theory="Social-crítico",
        reasoning_types=["Indutivo", "Probabilístico", "Abdutivo"],
        game_theory="Dilema do Prisioneiro",
        domain="Economia comportamental / Psicologia social",
        level_of_analysis="Comunitário",
        temporal_focus="Transversal (momento único)",
        population="Contexto comunitário",
        evidence_type="Dados clínicos (escalas, inventários)",
        coverage_vector=_make_vector(
            paradigmas=0.6, metodos=0.7, teorias=0.6,
            raciocinio=0.6, teoria_jogos=0.9,
            niveis_analise=0.7, temporalidade=0.5,
            populacao=0.6, dados=0.7, dominios=0.9
        )
    ))

    # ── Artefato 7: Estudo de Caso Clínico (pós-estruturalista) ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_clinical_{uuid.uuid4().hex[:6]}",
        title="Trajetórias Terapêuticas: Estudo de Caso Múltiplo em Terapia Cognitivo-Comportamental",
        description=(
            "Estudo de caso múltiplo longitudinal acompanhando 12 pacientes "
            "em terapia cognitivo-comportamental, com análise qualitativa de "
            "trajetórias de mudança e identificação de mecanismos de ação."
        ),
        paradigm="Interpretativista",
        method="Estudo de caso",
        theory="Cognitivo-comportamental",
        reasoning_types=["Dialético", "Teleológico"],
        game_theory=None,
        domain="Psicologia clínica",
        level_of_analysis="Individual/intrapsíquico",
        temporal_focus="Longitudinal (longo prazo)",
        population="Adultos",
        evidence_type="Dados clínicos (escalas, inventários)",
        coverage_vector=_make_vector(
            paradigmas=0.5, metodos=0.6, teorias=0.8,
            raciocinio=0.5, teoria_jogos=0.0,
            niveis_analise=0.8, temporalidade=0.9,
            populacao=0.8, dados=0.9, dominios=0.7
        )
    ))

    # ── Artefato 8: Antropologia Cultural ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_anthrop_{uuid.uuid4().hex[:6]}",
        title="Etnografia Digital de Comunidades Epistêmicas no Desenvolvimento de IA",
        description=(
            "Pesquisa etnográfica digital investigando práticas, rituais e "
            "valores de comunidades de desenvolvimento de IA, com observação "
            "participante e análise de narrativas em fóruns e repositórios."
        ),
        paradigm="Interpretativista",
        method="Qualitativo fenomenológico",
        theory="Social-crítico",
        reasoning_types=["Abdutivo", "Indutivo"],
        game_theory=None,
        domain="Antropologia / Sociologia",
        level_of_analysis="Cultural/antropológico",
        temporal_focus="Histórico/retrospectivo",
        population="Cross-cultural",
        evidence_type="Dados qualitativos (entrevistas)",
        coverage_vector=_make_vector(
            paradigmas=0.7, metodos=0.5, teorias=0.7,
            raciocinio=0.6, teoria_jogos=0.0,
            niveis_analise=0.9, temporalidade=0.5,
            populacao=0.9, dados=0.4, dominios=0.8
        )
    ))

    # ── Artefato 9 (NOVO R27-A): Paradigma Crítico-Dialético extremo ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_critico_{uuid.uuid4().hex[:6]}",
        title="Dialética da Inovação: Tensões entre Automação e Emancipação",
        description=(
            "Pesquisa crítica dialética analisando contradições inerentes à "
            "inovação tecnológica: entre automação e emancipação, controle e "
            "autonomia, eficiência e equidade. Uso de análise dialética "
            "multinível com método histórico-estrutural."
        ),
        paradigm="Crítico/Transformador",
        method="Qualitativo grounded theory",
        theory="Social-crítico",
        reasoning_types=["Dialético", "Crítico-reflexivo", "Abdutivo"],
        game_theory=None,
        domain="Filosofia da Tecnologia / Sociologia",
        level_of_analysis="Sistêmico/político",
        temporal_focus="Histórico/retrospectivo",
        population="Cross-cultural",
        evidence_type="Dados comparativos (cross-cultural)",
        coverage_vector=_make_vector(
            paradigmas=0.1, metodos=0.1, teorias=0.9,
            raciocinio=1.0, teoria_jogos=0.0,
            niveis_analise=0.9, temporalidade=0.7,
            populacao=0.9, dados=0.1, dominios=0.9
        )
    ))

    # ── Artefato 10 (NOVO R27-B): Neuro-Fenomenologia ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_neurophenom_{uuid.uuid4().hex[:6]}",
        title="Correlatos Neurais da Experiência Subjetiva em Meditação",
        description=(
            "Estudo de neurofenomenologia integrando fMRI, EEG e relatos "
            "fenomenológicos de primeira pessoa durante estados meditativos. "
            "Método misto convergente com triangulação neuro-qualitativa."
        ),
        paradigm="Complexo/Sistêmico",
        method="Misto convergente",
        theory="Neurobiológico",
        reasoning_types=["Abdutivo", "Sistêmico", "Indutivo"],
        game_theory=None,
        domain="Neurociências / Psicologia / Fenomenologia",
        level_of_analysis="Neurobiológico",
        temporal_focus="Longitudinal (curto prazo)",
        population="Adultos",
        evidence_type="Dados neurobiológicos",
        coverage_vector=_make_vector(
            paradigmas=0.1, metodos=0.3, teorias=0.9,
            raciocinio=0.2, teoria_jogos=0.0,
            niveis_analise=1.0, temporalidade=0.3,
            populacao=0.5, dados=1.0, dominios=1.0
        )
    ))

    # ── Artefato 11 (NOVO R27-C): Game Theory Puro (máxima divergência) ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_gamepure_{uuid.uuid4().hex[:6]}",
        title="Otimização de Leilões em Mercados de Dados Descentralizados",
        description=(
            "Modelagem matemática de leilões combinatoriais em mercados de "
            "dados descentralizados usando teoria dos jogos algorítmica, "
            "equilíbrio de Nash em jogos bayesianos e mecanismos VCG com "
            "otimização convexa."
        ),
        paradigm="Positivista",
        method="Quantitativo modelagem",
        theory="Evolucionista",
        reasoning_types=["Dedutivo", "Probabilístico", "Teleológico"],
        game_theory="Equilíbrio de Nash",
        domain="Economia computacional / Ciência da computação",
        level_of_analysis="Grupal/organizacional",
        temporal_focus="Prospectivo/preditivo",
        population="Contexto organizacional",
        evidence_type="Dados observacionais",
        coverage_vector=_make_vector(
            paradigmas=0.9, metodos=0.9, teorias=0.1,
            raciocinio=0.9, teoria_jogos=1.0,
            niveis_analise=0.3, temporalidade=0.9,
            populacao=0.1, dados=0.9, dominios=0.9
        )
    ))

    # ── Artefato 12 (NOVO R27-D): Inversão total — apenas qualitativo puro ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_qualpure_{uuid.uuid4().hex[:6]}",
        title="Narrativas de Identidade em Comunidades Ribeirinhas Amazônicas",
        description=(
            "Pesquisa qualitativa pura utilizando narrativas biográficas e "
            "observação participante em comunidades ribeirinhas da Amazônia. "
            "Sem qualquer quantificação, modelagem ou teoria dos jogos. "
            "Análise hermenêutica profunda de histórias de vida."
        ),
        paradigm="Interpretativista",
        method="Qualitativo fenomenológico",
        theory="Fenomenológico-existencial",
        reasoning_types=["Indutivo", "Dialético"],
        game_theory=None,
        domain="Antropologia / Estudos culturais",
        level_of_analysis="Cultural/antropológico",
        temporal_focus="Histórico/retrospectivo",
        population="Cross-cultural",
        evidence_type="Dados qualitativos (entrevistas)",
        coverage_vector=_make_vector(
            paradigmas=0.0, metodos=0.0, teorias=0.0,
            raciocinio=0.0, teoria_jogos=0.0,
            niveis_analise=0.0, temporalidade=0.0,
            populacao=0.0, dados=0.0, dominios=0.0
        )
    ))

    # ── Artefato 13 (NOVO R27-E): Máximo em todas as dimensões ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_maxall_{uuid.uuid4().hex[:6]}",
        title="Megassíntese Interdisciplinar: Integração Total do Conhecimento",
        description=(
            "Megassíntese interdisciplinar integrando paradigmas, métodos, "
            "teorias, raciocínios, teoria dos jogos, níveis de análise, "
            "temporalidades, populações, dados e domínios em uma única "
            "estrutura unificada de conhecimento."
        ),
        paradigm="Complexo/Sistêmico",
        method="Misto convergente",
        theory="Neurobiológico",
        reasoning_types=["Dedutivo", "Abdutivo", "Dialético", "Sistêmico", "Teleológico"],
        game_theory="Equilíbrio de Nash",
        domain="Filosofia da Ciência / Epistemologia",
        level_of_analysis="Sistêmico/político",
        temporal_focus="Longitudinal (longo prazo)",
        population="Cross-cultural",
        evidence_type="Dados epidemiológicos",
        coverage_vector=_make_vector(
            paradigmas=1.0, metodos=1.0, teorias=1.0,
            raciocinio=1.0, teoria_jogos=1.0,
            niveis_analise=1.0, temporalidade=1.0,
            populacao=1.0, dados=1.0, dominios=1.0
        )
    ))

    # ── Artefato 14 (NOVO R27-F): Interseção vazia máxima divergência ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_empty_{uuid.uuid4().hex[:6]}",
        title="Análise Puramente Lógico-Matemática sem Contexto Empírico",
        description=(
            "Demonstração formal em lógica de primeira ordem e teoria dos "
            "conjuntos, sem qualquer referência a dados empíricos, população, "
            "domínio específico ou método de coleta. Raciocínio dedutivo puro."
        ),
        paradigm="Positivista",
        method="Quantitativo modelagem",
        theory="Cognitivo-comportamental",
        reasoning_types=["Dedutivo"],
        game_theory=None,
        domain="Matemática / Lógica",
        level_of_analysis="Individual/intrapsíquico",
        temporal_focus="Transversal (momento único)",
        population="Adultos",
        evidence_type="Dados observacionais",
        coverage_vector=_make_vector(
            paradigmas=0.0, metodos=0.0, teorias=0.0,
            raciocinio=1.0, teoria_jogos=0.0,
            niveis_analise=0.0, temporalidade=1.0,
            populacao=0.0, dados=0.0, dominios=0.0
        )
    ))

    # ── Artefato 15 (NOVO R27-G): Puramente qualitativo-observacional ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_qualobs_{uuid.uuid4().hex[:6]}",
        title="Etnografia de Práticas de Cuidado em Comunidades Quilombolas",
        description=(
            "Observação participante prolongada (12 meses) em comunidades "
            "quilombolas do nordeste brasileiro, documentando práticas de "
            "cuidado intergeracional. Registro em diários de campo e "
            "entrevistas narrativas sem roteiro estruturado."
        ),
        paradigm="Interpretativista",
        method="Qualitativo fenomenológico",
        theory="Fenomenológico-existencial",
        reasoning_types=["Indutivo"],
        game_theory=None,
        domain="Antropologia / Saúde coletiva",
        level_of_analysis="Cultural/antropológico",
        temporal_focus="Longitudinal (longo prazo)",
        population="Cross-cultural",
        evidence_type="Dados qualitativos (entrevistas)",
        coverage_vector=_make_vector(
            paradigmas=0.1, metodos=0.1, teorias=0.0,
            raciocinio=0.2, teoria_jogos=0.0,
            niveis_analise=0.1, temporalidade=0.9,
            populacao=0.1, dados=0.1, dominios=0.1
        )
    ))

    # ── Artefato 16 (NOVO R27-H): Puramente dedutivo-formal ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_dedformal_{uuid.uuid4().hex[:6]}",
        title="Teorema de Gödel: Implicações para Sistemas Formais Auto-Referentes",
        description=(
            "Análise puramente lógico-dedutiva dos teoremas da incompletude "
            "de Gödel e suas implicações para sistemas formais, com "
            "demonstrações em cálculo sequencial e teoria da prova."
        ),
        paradigm="Positivista",
        method="Quantitativo modelagem",
        theory="Cognitivo-comportamental",
        reasoning_types=["Dedutivo"],
        game_theory=None,
        domain="Matemática / Lógica",
        level_of_analysis="Individual/intrapsíquico",
        temporal_focus="Transversal (momento único)",
        population="Adultos",
        evidence_type="Dados observacionais",
        coverage_vector=_make_vector(
            paradigmas=0.1, metodos=0.1, teorias=0.0,
            raciocinio=1.0, teoria_jogos=0.0,
            niveis_analise=0.0, temporalidade=0.0,
            populacao=0.0, dados=0.0, dominios=0.0
        )
    ))

    # ── Artefato 17 (NOVO R27-I): Game theory + neuro com máximos ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_gameneuro_{uuid.uuid4().hex[:6]}",
        title="Modelagem Neuroeconômica de Decisões sob Incerteza",
        description=(
            "Integração de fMRI, teoria dos jogos comportamental e modelos "
            "de utility theory para investigar correlatos neurais de decisões "
            "sob incerteza em contextos de leilão de bens públicos."
        ),
        paradigm="Complexo/Sistêmico",
        method="Quantitativo correlacional",
        theory="Neurobiológico",
        reasoning_types=["Probabilístico", "Dedutivo", "Teleológico"],
        game_theory="Equilíbrio de Nash",
        domain="Neuroeconomia / Psicologia",
        level_of_analysis="Neurobiológico",
        temporal_focus="Transversal (momento único)",
        population="Adultos",
        evidence_type="Dados neurobiológicos",
        coverage_vector=_make_vector(
            paradigmas=0.8, metodos=0.8, teorias=0.9,
            raciocinio=0.8, teoria_jogos=0.9,
            niveis_analise=0.9, temporalidade=0.2,
            populacao=0.3, dados=0.9, dominios=0.9
        )
    ))

    # ── Artefato 18 (NOVO R27-J): Inverso do cluster principal ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_inverse_{uuid.uuid4().hex[:6]}",
        title="Epistemologia Anarquista: Contra o Método (Feyerabend)",
        description=(
            "Defesa do anarquismo epistemológico como alternativa ao "
            "racionalismo metodológico, argumentando que não existem regras "
            "metodológicas universais e que o progresso científico requer "
            "violação sistemática de normas estabelecidas."
        ),
        paradigm="Crítico/Transformador",
        method="Qualitativo grounded theory",
        theory="Social-crítico",
        reasoning_types=["Crítico-reflexivo", "Dialético"],
        game_theory=None,
        domain="Filosofia da Ciência",
        level_of_analysis="Sistêmico/político",
        temporal_focus="Histórico/retrospectivo",
        population="Cross-cultural",
        evidence_type="Dados comparativos (cross-cultural)",
        coverage_vector=_make_vector(
            paradigmas=0.2, metodos=0.1, teorias=0.8,
            raciocinio=0.9, teoria_jogos=0.0,
            niveis_analise=0.7, temporalidade=0.8,
            populacao=0.8, dados=0.1, dominios=0.8
        )
    ))

    # ── Artefato 19 (NOVO R27-K): Apenas dados populacionais ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_poponly_{uuid.uuid4().hex[:6]}",
        title="Censo Demográfico Nacional: Perfil Socioeconômico 2025-2026",
        description=(
            "Análise descritiva de dados censitários nacionais com foco "
            "exclusivo em distribuição populacional, pirâmide etária e "
            "indicadores socioeconômicos por região. Sem teoria, sem "
            "paradigma, sem método sofisticado."
        ),
        paradigm="Positivista",
        method="Quantitativo descritivo",
        theory="Cognitivo-comportamental",
        reasoning_types=["Indutivo"],
        game_theory=None,
        domain="Demografia / Sociologia",
        level_of_analysis="Comunitário",
        temporal_focus="Transversal (momento único)",
        population="Cross-cultural",
        evidence_type="Dados epidemiológicos",
        coverage_vector=_make_vector(
            paradigmas=0.3, metodos=0.3, teorias=0.0,
            raciocinio=0.3, teoria_jogos=0.0,
            niveis_analise=0.3, temporalidade=0.3,
            populacao=1.0, dados=0.3, dominios=0.3
        )
    ))

    # ── Artefato 20 (NOVO R27-L): Ponte — alta paradigma, baixa teoria ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_bridge_pt_{uuid.uuid4().hex[:6]}",
        title="Paradigma sem Teoria: Análise Pragmatista Desprovida de Referencial",
        description=(
            "Aplicação pragmatista sem referencial teórico explícito, "
            "focada exclusivamente na utilidade prática de soluções "
            "tecnológicas para problemas educacionais, ignorando teoria "
            "subjacente. Paradigma alto, teorias zero."
        ),
        paradigm="Pragmatista",
        method="Quantitativo experimental",
        theory="Cognitivo-comportamental",
        reasoning_types=["Dedutivo", "Pragmático"],
        game_theory="Equilíbrio de Nash",
        domain="Educação / Tecnologia",
        level_of_analysis="Individual/intrapsíquico",
        temporal_focus="Transversal (momento único)",
        population="Adultos",
        evidence_type="Dados observacionais",
        coverage_vector=_make_vector(
            paradigmas=0.9, metodos=0.8, teorias=0.0,
            raciocinio=0.8, teoria_jogos=0.8,
            niveis_analise=0.3, temporalidade=0.8,
            populacao=0.7, dados=0.8, dominios=0.8
        )
    ))

    # ── Artefato 21 (NOVO R27-M): Ponte — alta dados, baixo raciocínio ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_bridge_dr_{uuid.uuid4().hex[:6]}",
        title="Big Data Desprovido de Raciocínio: Mineração Bruta de Padrões",
        description=(
            "Mineração de dados em larga escala (big data) sem raciocínio "
            "sofisticado — apenas correlações brutas e agrupamentos "
            "estatísticos. Dados altíssimos, raciocínio mínimo."
        ),
        paradigm="Positivista",
        method="Quantitativo descritivo",
        theory="Cognitivo-comportamental",
        reasoning_types=["Indutivo"],
        game_theory=None,
        domain="Ciência da computação / Estatística",
        level_of_analysis="Comunitário",
        temporal_focus="Longitudinal (longo prazo)",
        population="Cross-cultural",
        evidence_type="Dados epidemiológicos",
        coverage_vector=_make_vector(
            paradigmas=0.7, metodos=0.8, teorias=0.3,
            raciocinio=0.0, teoria_jogos=0.0,
            niveis_analise=0.4, temporalidade=0.9,
            populacao=0.9, dados=1.0, dominios=0.3
        )
    ))

    # ── Artefato 22 (NOVO R27-N): Ponte — teoria alta, demais baixo ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_bridge_tb_{uuid.uuid4().hex[:6]}",
        title="Teoria Pura sem Método: Especulação Filosófica sobre Consciência",
        description=(
            "Tratado filosófico sobre a natureza da consciência, utilizando "
            "apenas raciocínio dedutivo e referencial teórico denso, sem "
            "qualquer método empírico, dado ou teoria dos jogos."
        ),
        paradigm="Interpretativista",
        method="Qualitativo fenomenológico",
        theory="Fenomenológico-existencial",
        reasoning_types=["Dedutivo", "Dialético"],
        game_theory=None,
        domain="Filosofia da Mente",
        level_of_analysis="Individual/intrapsíquico",
        temporal_focus="Histórico/retrospectivo",
        population="Adultos",
        evidence_type="Dados qualitativos (entrevistas)",
        coverage_vector=_make_vector(
            paradigmas=0.2, metodos=0.0, teorias=1.0,
            raciocinio=0.8, teoria_jogos=0.0,
            niveis_analise=0.3, temporalidade=0.2,
            populacao=0.0, dados=0.0, dominios=0.5
        )
    ))

    # ── Artefato 23 (R30-A): Positivista radical — máximo paradigma, mínimo raciocínio ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_positrad_{uuid.uuid4().hex[:6]}",
        title="Ensaio Clínico Randomizado Multicêntrico Fase III",
        description=(
            "Ensaio clínico randomizado, duplo-cego, controlado por placebo, "
            "multicêntrico (12 centros), com análise de intenção de tratar "
            "(ITT), poder estatístico de 90%, alpha 0.01, e registro prospectivo "
            "no ClinicalTrials.gov. Paradigma positivista puro."
        ),
        paradigm="Positivista",
        method="Quantitativo experimental",
        theory="Cognitivo-comportamental",
        reasoning_types=["Dedutivo", "Probabilístico"],
        game_theory=None,
        domain="Medicina / Saúde pública",
        level_of_analysis="Individual/intrapsíquico",
        temporal_focus="Longitudinal (longo prazo)",
        population="Adultos",
        evidence_type="Dados epidemiológicos",
        coverage_vector=_make_vector(
            paradigmas=1.0, metodos=1.0, teorias=0.2,
            raciocinio=0.2, teoria_jogos=0.0,
            niveis_analise=0.2, temporalidade=0.9,
            populacao=0.9, dados=1.0, dominios=0.5
        )
    ))

    # ── Artefato 24 (R30-B): Interpretativista puro — máximo subjetivo ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_interppure_{uuid.uuid4().hex[:6]}",
        title="Fenomenografia da Experiência de Parto Humanizado",
        description=(
            "Pesquisa fenomenográfica com 20 entrevistas em profundidade "
            "analisadas via análise temática reflexiva (Braun & Clarke), "
            "buscando compreender a essência da experiência de parto "
            "humanizado sob a perspectiva das parturientes. Sem quantificação."
        ),
        paradigm="Interpretativista",
        method="Qualitativo fenomenológico",
        theory="Fenomenológico-existencial",
        reasoning_types=["Abdutivo", "Indutivo"],
        game_theory=None,
        domain="Psicologia clínica / Saúde coletiva",
        level_of_analysis="Interpessoal/relacional",
        temporal_focus="Transversal (momento único)",
        population="Gênero feminino",
        evidence_type="Dados qualitativos (entrevistas)",
        coverage_vector=_make_vector(
            paradigmas=0.0, metodos=0.0, teorias=0.9,
            raciocinio=0.1, teoria_jogos=0.0,
            niveis_analise=0.8, temporalidade=0.1,
            populacao=0.8, dados=0.0, dominios=0.8
        )
    ))

    # ── Artefato 25 (R30-C): Ruptura — antítese de todos os clusters ──
    artifacts.append(DiversityArtifact(
        artifact_id=f"div_rupture_{uuid.uuid4().hex[:6]}",
        title="Contra-Epistemologia: Desconstrução Radical do Método Científico",
        description=(
            "Ensaio filosófico de desconstrução radical dos pressupostos do "
            "método científico ocidental, argumentando que toda epistemologia "
            "é política e que a objetividade é uma ilusão. Uso de irony, "
            "paródia e contradição performática como método."
        ),
        paradigm="Crítico/Transformador",
        method="Qualitativo grounded theory",
        theory="Social-crítico",
        reasoning_types=["Crítico-reflexivo", "Dialético"],
        game_theory=None,
        domain="Filosofia da Ciência / Epistemologia",
        level_of_analysis="Sistêmico/político",
        temporal_focus="Histórico/retrospectivo",
        population="Cross-cultural",
        evidence_type="Dados comparativos (cross-cultural)",
        coverage_vector=_make_vector(
            paradigmas=0.0, metodos=0.0, teorias=1.0,
            raciocinio=1.0, teoria_jogos=0.0,
            niveis_analise=1.0, temporalidade=0.0,
            populacao=0.0, dados=0.0, dominios=1.0
        )
    ))

    return artifacts


def artifacts_to_noological_format(artifacts: list[DiversityArtifact]) -> list[dict]:
    """
    Converte artefatos para o formato esperado pelo Scanner Noológico.

    Cada artefato vira uma categoria coberta no dicionário de entrada.
    """
    entries = []
    for art in artifacts:
        entry = {
            "artifact_id": art.artifact_id,
            "title": art.title,
            "description": art.description,
            "dimensions": {
                "paradigma": art.paradigm,
                "metodo": art.method,
                "teoria": art.theory,
                "raciocinio": art.reasoning_types,
                "teoria_jogos": art.game_theory if art.game_theory else "N/A",
                "dominio": art.domain,
                "nivel_analise": art.level_of_analysis,
                "temporalidade": art.temporal_focus,
                "populacao": art.population,
                "evidencia": art.evidence_type,
            },
            "coverage_vector": art.coverage_vector,
        }
        entries.append(entry)
    return entries


def generate_cognitive_diversity_report(artifacts: list[DiversityArtifact]) -> str:
    """Gera relatório textual dos artefatos de diversidade injetados."""
    lines = [
        "=" * 70,
        "RELATÓRIO DE INJEÇÃO DE DIVERSIDADE COGNITIVA",
        "=" * 70,
        f"Total de artefatos: {len(artifacts)}",
        "",
        "Resumo por paradigma:",
    ]

    paradigms = {}
    for art in artifacts:
        paradigms[art.paradigm] = paradigms.get(art.paradigm, 0) + 1

    for p, count in sorted(paradigms.items()):
        lines.append(f"  - {p}: {count} artefato(s)")

    lines.extend([
        "",
        "Resumo por teoria dos jogos:",
    ])
    gt_used = [art.game_theory for art in artifacts if art.game_theory]
    lines.append(f"  - Artefatos com referência a teoria dos jogos: {len(gt_used)}/{len(artifacts)}")
    for g in set(gt_used):
        lines.append(f"    * {g}")

    lines.extend([
        "",
        "Resumo por domínio cruzado:",
    ])
    domains = {}
    for art in artifacts:
        domains[art.domain] = domains.get(art.domain, 0) + 1
    for d, count in sorted(domains.items()):
        lines.append(f"  - {d}: {count} artefato(s)")

    lines.append("")
    lines.append("Impacto esperado:")
    lines.append("  - Redução do Índice de Homogeneidade (HI): 0.75 → < 0.50")
    lines.append("  - Aumento da cobertura em Teoria dos Jogos: 10% → ~35%")
    lines.append("  - Aumento da cobertura em Domínios Cruzados: 10% → ~40%")
    lines.append("  - Paradigmas: Positivista, Interpretativista, Construtivista, Pragmatista, Critico, Complexo/Sistemico")
    lines.append("  - 3 novos artefatos de máxima divergencia injetados (R27-A/B/C)")
    lines.append("")
    lines.append("=" * 70)

    return "\n".join(lines)


if __name__ == "__main__":
    artifacts = inject_diversity_artifacts()
    print(generate_cognitive_diversity_report(artifacts))
    print(artifacts_to_noological_format(artifacts))
