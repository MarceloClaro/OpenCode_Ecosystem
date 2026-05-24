#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reasoning Audit Bridge v1.0 — Reasoning Orchestrator ↔ AuditSystem
====================================================================
Conecta o reasoning-orchestrator v9.0 (68 tipos de raciocínio,
incluindo 10 de Teoria dos Jogos) ao sistema de auditoria caixa branca.

Integrações:
  1. GameTheoryValidator — avalia diversidade de raciocínio na sessão
  2. ReasoningDiversityScore — componente do ResearcherScore (novo critério)
  3. PublicationLevelMapper — mapeia níveis N1/N2/N3 para TokenEconomy
  4. ReasoningLogger — registra escolha de raciocínio no InteractionLogger

Uso:
  from reasoning_audit_bridge import GameTheoryValidator, ReasoningDiversityScore
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ═══════════════════════════════════════════════════════════════════════
# Constantes — 68 Tipos de Raciocínio (58 base + 10 Teoria dos Jogos)
# ═══════════════════════════════════════════════════════════════════════

REASONING_CATEGORIES: dict[str, list[str]] = {
    "logica_formal": ["Dedutivo", "Indutivo", "Abdutivo", "Silogístico", "Analógico"],
    "sistemas": ["Sistêmico", "Modular", "Recursivo", "Reducionista", "Holístico", "de Fluxo"],
    "rigor_cientifico": ["Hipotético-Dedutivo", "Falsificacionista", "Cético", "Dialético", "Probabilístico", "Contrafactual"],
    "estrategia": ["Primeiros Princípios", "Custo de Oportunidade", "Segunda Ordem", "Inversão", "Algorítmico", "Heurístico"],
    "computacional": ["Vetorial/Latente", "Semântico", "Bayesiano", "de Grafo", "Baseado em Casos"],
    "cognicao": ["Metacognitivo", "Divergente", "Convergente", "Lateral", "Temporal", "Espacial", "Abstrato", "Pragmático", "Teleológico", "Axiomático"],
    "economia": ["Equilíbrio de Nash", "Soma Zero", "Sinalização", "Incentivos Distorcidos", "Tragédia dos Comuns"],
    "psicologia": ["Ancoragem", "Viés de Confirmação", "Dissonância Cognitiva", "Efeito Dunning-Kruger", "Heurística de Disponibilidade"],
    "etica": ["Utilitarista", "Deontológico", "Ética da Virtude", "Equidade", "Princípio da Precaução"],
    "caos": ["Efeito Borboleta", "Dependência de Trajetória", "Antifragilidade", "Escalabilidade", "Emergência"],
    # ── NOVA CATEGORIA v9.0 ──
    "teoria_dos_jogos": [
        "Equilíbrio de Nash", "Dilema do Prisioneiro", "Soma Zero (Jogos)",
        "Tit-for-Tat", "Stackelberg (Líder-Seguidor)", "Barganha de Nash",
        "Sinalização (Jogos)", "Evolutivo (Jogos)", "Bayesiano (Harsanyi)",
        "Cooperativo (Shapley)",
    ],
}

# ═══════════════════════════════════════════════════════════════════════
# 1. GameTheoryValidator
# ═══════════════════════════════════════════════════════════════════════

class GameTheoryValidator:
    """Valida uso de Teoria dos Jogos em sessões de pesquisa.

    Integra-se ao ResearcherScore como critério adicional de qualidade.
    """

    GAME_THEORY_STRATEGIES = REASONING_CATEGORIES["teoria_dos_jogos"]

    @classmethod
    def evaluate_session(
        cls,
        audit_trail: Any,
        required_strategies: int = 2,
    ) -> dict[str, Any]:
        """Avalia diversidade de raciocínio (incluindo Teoria dos Jogos).

        Args:
            audit_trail: Instância de AcademicAuditTrail
            required_strategies: Mínimo de estratégias exigidas (N1=3, N2=2, N3=1)

        Returns:
            Dict com score de diversidade e estratégias detectadas
        """
        # Extrair decisões do log
        decisions = []
        if hasattr(audit_trail, "decision_log"):
            decisions = audit_trail.decision_log
        elif hasattr(audit_trail, "logger"):
            # Buscar nos registros do logger
            pass

        # Detectar estratégias usadas
        used_strategies: list[str] = []
        for d in decisions:
            text = str(d).lower()
            for strategy in cls.GAME_THEORY_STRATEGIES:
                if strategy.lower() in text:
                    if strategy not in used_strategies:
                        used_strategies.append(strategy)

        # Calcular score de diversidade
        categories_used = 0
        for cat, strategies in REASONING_CATEGORIES.items():
            if any(s.lower() in str(decisions).lower() for s in strategies):
                categories_used += 1

        diversity_score = min(categories_used / max(1, len(REASONING_CATEGORIES)), 1.0)

        # Score de Teoria dos Jogos
        gt_count = len(used_strategies)
        gt_score = min(gt_count / max(1, required_strategies), 1.0)

        passed = gt_count >= required_strategies

        return {
            "passed": passed,
            "game_theory_strategies_found": gt_count,
            "game_theory_strategies_required": required_strategies,
            "game_theory_score": round(gt_score * 100),
            "strategies_detected": used_strategies,
            "diversity_categories": categories_used,
            "diversity_score": round(diversity_score * 100),
            "recommendation": cls._get_recommendation(gt_count, required_strategies),
        }

    @staticmethod
    def _get_recommendation(found: int, required: int) -> str:
        if found >= required:
            return f"Diversidade adequada ({found}/{required} estratégias de Teoria dos Jogos)"
        elif found > 0:
            missing = required - found
            return f"Considere adicionar {missing} estratégia(s) de Teoria dos Jogos para rigor máximo"
        else:
            return "Nenhuma estratégia de Teoria dos Jogos detectada. Recomendado para N1 (Qualis A1)"


# ═══════════════════════════════════════════════════════════════════════
# 2. ReasoningDiversityScore
# ═══════════════════════════════════════════════════════════════════════

class ReasoningDiversityScore:
    """Calcula diversidade de raciocínio como componente do ResearcherScore.

    Peso sugerido: 5% do ResearcherScore total (adicional aos 6 critérios existentes).
    """

    @classmethod
    def calculate(cls, audit_trail: Any, publication_level: int = 2) -> dict[str, Any]:
        """Calcula score de diversidade de raciocínio.

        Args:
            audit_trail: AcademicAuditTrail
            publication_level: N1(3 estratégias min), N2(2), N3(1)

        Returns:
            Dict com score 0-100
        """
        required = {1: 3, 2: 2, 3: 1}.get(publication_level, 2)
        validator = GameTheoryValidator()
        result = validator.evaluate_session(audit_trail, required_strategies=required)

        # Score combinado: 50% diversidade geral + 50% Teoria dos Jogos
        combined = round((result["diversity_score"] * 0.5 + result["game_theory_score"] * 0.5))

        return {
            "reasoning_diversity_score": combined,
            "categories_used": result["diversity_categories"],
            "game_theory_strategies": result["game_theory_strategies_found"],
            "passed": result["passed"],
        }


# ═══════════════════════════════════════════════════════════════════════
# 3. PublicationLevelMapper
# ═══════════════════════════════════════════════════════════════════════

class PublicationLevelMapper:
    """Mapeia níveis de publicação N1/N2/N3 para configurações do ecossistema."""

    LEVELS = {
        1: {
            "name": "Magnum/Tese/Qualis A1",
            "agents": 43,
            "token_budget": 500_000,
            "reasoning_min": 5,
            "game_theory_min": 3,
            "depth": "L3-L4",
        },
        2: {
            "name": "Standard Paper/Q1-Q2",
            "agents": 20,
            "token_budget": 200_000,
            "reasoning_min": 3,
            "game_theory_min": 2,
            "depth": "L2-L3",
        },
        3: {
            "name": "Short Communication/Congresso",
            "agents": 10,
            "token_budget": 50_000,
            "reasoning_min": 1,
            "game_theory_min": 1,
            "depth": "L1-L2",
        },
    }

    @classmethod
    def get_config(cls, level: int) -> dict[str, Any]:
        """Retorna configuração completa para um nível de publicação."""
        return cls.LEVELS.get(level, cls.LEVELS[2])

    @classmethod
    def recommend_level(cls, token_budget: int, rigor_required: bool = True) -> int:
        """Recomenda nível baseado no orçamento de tokens e rigor exigido."""
        if rigor_required and token_budget >= 400_000:
            return 1
        elif token_budget >= 150_000:
            return 2
        else:
            return 3


# ═══════════════════════════════════════════════════════════════════════
# 4. ReasoningLogger
# ═══════════════════════════════════════════════════════════════════════

class ReasoningLogger:
    """Registra escolha de raciocínio no InteractionLogger."""

    @staticmethod
    def log_reasoning_choice(
        logger: Any,
        category: str,
        strategy: str,
        depth: str = "L2",
        context: str = "",
    ) -> None:
        """Registra escolha de tipo de raciocínio no log de auditoria.

        Args:
            logger: InteractionLogger instance
            category: Categoria (ex: "teoria_dos_jogos", "logica_formal")
            strategy: Estratégia específica (ex: "Equilíbrio de Nash")
            depth: Nível de profundidade (L1-L4)
            context: Contexto da decisão
        """
        if hasattr(logger, "log_decision"):
            logger.log_decision(
                decision=f"Raciocínio: {strategy} [{category}]",
                rationale=f"Profundidade: {depth} | Contexto: {context}",
                context="ReasoningOrchestrator",
            )

    @staticmethod
    def validate_diversity(
        audit_trail: Any,
        level: int = 2,
    ) -> dict[str, Any]:
        """Valida diversidade de raciocínio e retorna relatório."""
        diversity = ReasoningDiversityScore.calculate(audit_trail, level)
        gt_validator = GameTheoryValidator()
        gt_result = gt_validator.evaluate_session(
            audit_trail,
            required_strategies=PublicationLevelMapper.get_config(level)["game_theory_min"],
        )

        return {
            "level": level,
            "level_name": PublicationLevelMapper.get_config(level)["name"],
            "diversity": diversity,
            "game_theory": gt_result,
            "recommendation": gt_result["recommendation"],
        }
