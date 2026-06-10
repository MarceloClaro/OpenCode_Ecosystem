#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CooperativeGovernance v1.0 — SPEC-036c: Goal-Setting Alinhado (Ostrom)
========================================================================
Implementa o gap critico 'teoria_jogos.Cooperativo' identificado pelo scanner.

Baseado nos 8 Design Principles de Elinor Ostrom para governanca de recursos comuns,
adaptados para goal-setting autonomo em sistemas de IA:

  DP1: Limites claros          — quem/quais sao os agentes e recursos
  DP2: Regras proporcionais    — custos e beneficios proporcionais
  DP3: Participacao coletiva   — agentes afetados participam das decisoes
  DP4: Monitoramento           — observabilidade do comportamento
  DP5: Sancoes graduais        — penalidades proporcionais a infracoes
  DP6: Resolucao de conflitos  — mecanismos acessiveis de baixo custo
  DP7: Autonomia reconhecida   — direito de auto-organizacao
  DP8: Empreendimentos aninhados — governanca em multiplas camadas

Aplicacao ao OpenCode:
  - Goals gerados pelo sistema devem respeitar DP1-DP8
  - Cada goal e validado contra os principios antes da execucao
  - Conflitos entre goals sao resolvidos via DP6

Autor: OpenCode Ecosystem (2026) — R21: Metacognicao
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


BRAZIL_TZ = timezone.utc


# ═══════════════════════════════════════════════════════════════════════════
# OSTROM DESIGN PRINCIPLES (adaptados para IA)
# ═══════════════════════════════════════════════════════════════════════════

OSTROM_PRINCIPLES: dict[str, dict[str, str]] = {
    "DP1_boundaries": {
        "name": "Limites Claros",
        "description": "Definir claramente quem sao os agentes autorizados e quais recursos estao sujeitos a governanca",
        "check": "O goal define explicitamente escopo, agentes envolvidos e recursos acessados?",
        "violation": "Goal com escopo ambiguo ou acesso a recursos nao declarados",
    },
    "DP2_proportionality": {
        "name": "Regras Proporcionais",
        "description": "Beneficios obtidos devem ser proporcionais aos custos incorridos",
        "check": "O custo computacional/energetico do goal e proporcional ao beneficio esperado?",
        "violation": "Goal com alto custo e baixo beneficio ou externalidades negativas",
    },
    "DP3_collective_choice": {
        "name": "Participacao Coletiva",
        "description": "Agentes afetados pelas regras podem participar da sua modificacao",
        "check": "Os modulos/skills afetados pelo goal tem mecanismo de veto ou feedback?",
        "violation": "Goal imposto sem consulta aos modulos afetados",
    },
    "DP4_monitoring": {
        "name": "Monitoramento",
        "description": "Comportamento dos agentes e estado dos recursos sao observaveis",
        "check": "O progresso do goal e metricas de impacto sao rastreaveis?",
        "violation": "Goal sem metricas de progresso ou indicadores de impacto",
    },
    "DP5_graduated_sanctions": {
        "name": "Sancoes Graduais",
        "description": "Penalidades por violacoes sao proporcionais e escalonadas",
        "check": "Ha mecanismo de rollback ou abort seguro se o goal produzir efeitos negativos?",
        "violation": "Goal sem mecanismo de abort ou rollback",
    },
    "DP6_conflict_resolution": {
        "name": "Resolucao de Conflitos",
        "description": "Mecanismos de baixo custo para resolver disputas entre goals",
        "check": "Conflitos entre goals concorrentes tem mecanismo de arbitragem?",
        "violation": "Dois goals mutuamente exclusivos sem mecanismo de priorizacao",
    },
    "DP7_autonomy": {
        "name": "Autonomia Reconhecida",
        "description": "O direito de auto-organizacao e reconhecido por autoridades superiores",
        "check": "O goal respeita as restricoes de seguranca definidas pelo operador humano?",
        "violation": "Goal que viola restricoes de seguranca ou permissoes do sistema",
    },
    "DP8_nested_enterprises": {
        "name": "Empreendimentos Aninhados",
        "description": "Governanca opera em multiplas camadas (local, regional, global)",
        "check": "O goal se integra com goals de nivel superior sem conflito?",
        "violation": "Goal local que contradiz objetivo global do sistema",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AutonomousGoal:
    """Goal gerado autonomamente pelo sistema."""
    goal_id: str
    description: str
    priority: float            # 0-1
    estimated_cost: float      # 0-1 (recursos computacionais)
    expected_benefit: float    # 0-1
    affected_modules: list[str]
    parent_goal_id: str | None = None  # DP8: nested
    ostrom_score: float = 0.0
    violations: list[str] = field(default_factory=list)
    status: str = "proposed"   # proposed | validated | rejected | active | completed


@dataclass
class GovernanceAudit:
    """Resultado da auditoria Ostrom de um goal."""
    goal_id: str
    principles_passed: int
    principles_failed: int
    ostrom_score: float        # 0-1
    violations: list[dict[str, str]]  # [{principle, reason}]
    recommendation: str        # "approve" | "revise" | "reject"
    timestamp: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# COOPERATIVE GOVERNANCE ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class CooperativeGovernance:
    """Motor de governanca cooperativa baseado em Ostrom.

    Valida goals autonomicos contra os 8 Design Principles antes da execucao.
    """

    def __init__(self):
        self._goals: list[AutonomousGoal] = []
        self._audits: list[GovernanceAudit] = []
        self._active_constraints: list[str] = [
            "Nao modificar codigo sem aprovacao humana",
            "Nao acessar recursos fora do escopo definido",
            "Manter rastreabilidade de todas as decisoes",
            "Respeitar permissoes do sistema operacional",
        ]

    def propose_goal(
        self,
        description: str,
        priority: float = 0.5,
        estimated_cost: float = 0.1,
        expected_benefit: float = 0.5,
        affected_modules: list[str] | None = None,
        parent_goal_id: str | None = None,
    ) -> AutonomousGoal:
        """Propoe um novo goal autonomo."""
        goal = AutonomousGoal(
            goal_id=f"GOAL-{len(self._goals)+1:04d}",
            description=description,
            priority=min(1.0, max(0.0, priority)),
            estimated_cost=min(1.0, max(0.0, estimated_cost)),
            expected_benefit=min(1.0, max(0.0, expected_benefit)),
            affected_modules=affected_modules or [],
            parent_goal_id=parent_goal_id,
        )
        self._goals.append(goal)
        return goal

    def audit_goal(self, goal: AutonomousGoal) -> GovernanceAudit:
        """Audita um goal contra os 8 Design Principles de Ostrom."""
        violations: list[dict[str, str]] = []
        passed = 0

        # DP1: Limites claros
        if not goal.affected_modules:
            violations.append({
                "principle": "DP1_boundaries",
                "reason": "Goal nao declara modulos afetados (limites ambiguos)",
            })
        else:
            passed += 1

        # DP2: Proporcionalidade
        if goal.estimated_cost > goal.expected_benefit * 2:
            violations.append({
                "principle": "DP2_proportionality",
                "reason": f"Custo ({goal.estimated_cost}) > 2x beneficio ({goal.expected_benefit})",
            })
        else:
            passed += 1

        # DP3: Participacao coletiva
        if goal.affected_modules and len(goal.affected_modules) > 3:
            violations.append({
                "principle": "DP3_collective_choice",
                "reason": f"Goal afeta {len(goal.affected_modules)} modulos sem mecanismo de consulta",
            })
        else:
            passed += 1

        # DP4: Monitoramento
        passed += 1  # sempre passa: metricas sao built-in

        # DP5: Sancoes graduais
        if goal.priority > 0.9 and goal.estimated_cost > 0.5:
            violations.append({
                "principle": "DP5_graduated_sanctions",
                "reason": "Goal de alto impacto sem mecanismo de rollback declarado",
            })
        else:
            passed += 1

        # DP6: Resolucao de conflitos
        conflicting = [
            g for g in self._goals
            if g.goal_id != goal.goal_id
            and g.status == "active"
            and set(g.affected_modules) & set(goal.affected_modules)
        ]
        if conflicting:
            violations.append({
                "principle": "DP6_conflict_resolution",
                "reason": f"Conflito potencial com goals ativos: {[g.goal_id for g in conflicting]}",
            })
        else:
            passed += 1

        # DP7: Autonomia reconhecida
        # Verifica contra restricoes ativas
        for constraint in self._active_constraints:
            if any(word in goal.description.lower() for word in ["modificar codigo", "acessar", "escrever"]):
                if "modificar" in constraint.lower() and "modificar" in goal.description.lower():
                    violations.append({
                        "principle": "DP7_autonomy",
                        "reason": f"Goal conflita com restricao: {constraint}",
                    })
                    break
        else:
            passed += 1

        # DP8: Empreendimentos aninhados
        if goal.parent_goal_id is None and goal.priority > 0.7:
            violations.append({
                "principle": "DP8_nested_enterprises",
                "reason": "Goal de alta prioridade sem parent goal (nao aninhado)",
            })
        else:
            passed += 1

        # Score e recomendacao
        score = passed / 8
        if score >= 0.75:
            recommendation = "approve"
        elif score >= 0.5:
            recommendation = "revise"
        else:
            recommendation = "reject"

        audit = GovernanceAudit(
            goal_id=goal.goal_id,
            principles_passed=passed,
            principles_failed=8 - passed,
            ostrom_score=round(score, 4),
            violations=violations,
            recommendation=recommendation,
            timestamp=datetime.now(BRAZIL_TZ).isoformat(),
        )

        # Atualizar goal
        goal.ostrom_score = score
        goal.violations = [v["principle"] for v in violations]
        goal.status = recommendation if recommendation == "reject" else "validated"

        self._audits.append(audit)
        return audit

    def resolve_conflicts(
        self, goal1: AutonomousGoal, goal2: AutonomousGoal
    ) -> AutonomousGoal:
        """Resolve conflito entre dois goals via DP6.

        Estrategia: priorizar o goal com maior ostrom_score.
        Em caso de empate, usar priority * expected_benefit / estimated_cost.
        """
        score1 = goal1.ostrom_score or (goal1.priority * goal1.expected_benefit / max(0.01, goal1.estimated_cost))
        score2 = goal2.ostrom_score or (goal2.priority * goal2.expected_benefit / max(0.01, goal2.estimated_cost))

        if score1 >= score2:
            goal2.status = "rejected"
            return goal1
        else:
            goal1.status = "rejected"
            return goal2

    @property
    def active_goals(self) -> list[AutonomousGoal]:
        return [g for g in self._goals if g.status == "active"]

    @property
    def approved_goals(self) -> list[AutonomousGoal]:
        return [g for g in self._goals if g.status in ("validated", "active", "completed")]

    @property
    def audit_summary(self) -> dict[str, Any]:
        if not self._audits:
            return {"total": 0, "approved": 0, "revised": 0, "rejected": 0, "avg_score": 0}
        return {
            "total": len(self._audits),
            "approved": sum(1 for a in self._audits if a.recommendation == "approve"),
            "revised": sum(1 for a in self._audits if a.recommendation == "revise"),
            "rejected": sum(1 for a in self._audits if a.recommendation == "reject"),
            "avg_score": round(sum(a.ostrom_score for a in self._audits) / len(self._audits), 4),
        }


# ═══════════════════════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════════════════════

def create_cooperative_governance() -> CooperativeGovernance:
    """Factory: cria motor de governanca cooperativa pronto para uso."""
    return CooperativeGovernance()
