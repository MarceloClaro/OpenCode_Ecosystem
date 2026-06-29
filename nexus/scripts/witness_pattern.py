# -*- coding: utf-8 -*-
"""
Witness Pattern — Camada de Observacao Metacognitiva (R28)
Inspirado em Sakshi (bionicbutterfly13/sakshi): Witness Pattern

Um processo observador que monitora planos e acoes SEM executa-los,
emitindo sinais tipados para o TrustEngine (SPEC-038).

Fluxo:
  1. Observa plano/acao sem intervir
  2. Classifica risco (safe/moderate/risky)
  3. Emite sinal tipado para TrustEngine
  4. TrustEngine decide se permite ou bloqueia
"""

import uuid
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime


class SignalSeverity(Enum):
    """Severidade do sinal emitido pelo Witness"""
    INFO = "info"              # Informativo, sem risco
    WARNING = "warning"        # Potencial problema
    CRITICAL = "critical"      # Risco alto, requer atencao


class ActionRisk(Enum):
    """Classificacao de risco de uma acao observada"""
    SAFE = "safe"              # Acao segura
    MODERATE = "moderate"      # Requer verificacao
    RISKY = "risky"            # Arriscada
    BLOCKED = "blocked"        # Deve ser bloqueada


@dataclass
class WitnessSignal:
    """Sinal emitido pelo Witness para o TrustEngine"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source: str = "witness"
    target_action: str = ""
    severity: SignalSeverity = SignalSeverity.INFO
    risk: ActionRisk = ActionRisk.SAFE
    reasoning: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "source": self.source,
            "target_action": self.target_action,
            "severity": self.severity.value,
            "risk": self.risk.value,
            "reasoning": self.reasoning,
            "context": self.context,
            "timestamp": self.timestamp,
        }


class WitnessObserver:
    """
    Observador que monitora acoes sem executa-las.

    E um "espectador metacognitivo" que analisa planos e emite sinais.
    """

    def __init__(self, name: str = "witness-default"):
        self.name = name
        self.signals: List[WitnessSignal] = []
        self._risk_rules: List[Callable] = []
        self._observations: List[Dict] = []
        self.witness_count = 0
        self.goal_drift_count = 0

    def add_risk_rule(self, rule: Callable[[Dict], Optional[WitnessSignal]]) -> None:
        """Adiciona regra de risco personalizada"""
        self._risk_rules.append(rule)

    def observe(self, action: Dict, context: Optional[Dict] = None) -> WitnessSignal:
        """
        Observa uma acao e emite sinal.

        Args:
            action: Descricao da acao a ser observada
            context: Contexto adicional

        Returns:
            WitnessSignal com classificacao de risco
        """
        self.witness_count += 1
        ctx = context or {}

        # Analisar risco
        risk, reasoning = self._analyze_risk(action, ctx)
        severity = self._risk_to_severity(risk)

        signal = WitnessSignal(
            target_action=action.get("name", action.get("action", "unknown")),
            severity=severity,
            risk=risk,
            reasoning=reasoning,
            context={
                "observer": self.name,
                "action_details": action,
                "context": ctx,
                "witness_number": self.witness_count,
            },
        )

        # Detectar goal drift
        if risk in (ActionRisk.RISKY, ActionRisk.BLOCKED):
            self.goal_drift_count += 1

        self.signals.append(signal)
        self._observations.append({
            "signal_id": signal.id,
            "risk": risk.value,
            "timestamp": signal.timestamp,
        })

        return signal

    def _analyze_risk(self, action: Dict, context: Dict) -> tuple:
        """Analisa risco de uma acao baseado em heuristicas e regras personalizadas"""
        action_name = action.get("name", action.get("action", "")).lower()
        action_type = action.get("type", "").lower()

        # Executar regras personalizadas primeiro (maior prioridade)
        for rule in self._risk_rules:
            result = rule(action)
            if result is not None and isinstance(result, WitnessSignal):
                return result.risk, f"Regra personalizada: {result.reasoning}"

        # Heuristicas de risco
        risk_patterns = {
            ActionRisk.BLOCKED: [
                "rm -rf", "sudo ", "format", "drop table",
                "delete from", "shutdown", "reboot",
            ],
            ActionRisk.RISKY: [
                "write_file", "delete", "modify_config",
                "chmod", "chown", "network_call",
            ],
            ActionRisk.MODERATE: [
                "execute", "delegate", "deploy",
                "commit", "push", "merge",
            ],
        }

        for risk_level, patterns in risk_patterns.items():
            for pattern in patterns:
                if pattern in action_name or pattern in action_type:
                    return risk_level, (
                        f"Acao '{action_name}' corresponde ao padrao de risco '{pattern}'. "
                        f"Classificada como {risk_level.value}."
                    )

        # Verificacoes contextuais
        if context.get("phase") in ("seal", "validate") and action_type == "write":
            return ActionRisk.MODERATE, (
                f"Escrita em fase de validacao ({context.get('phase')}). "
                f"Classificada como moderate."
            )

        if context.get("goal_drift_score", 0) > 0.7:
            return ActionRisk.RISKY, (
                f"Goal drift score elevado ({context['goal_drift_score']}). "
                f"Acao pode representar desvio de objetivo."
            )

        return ActionRisk.SAFE, "Acao classificada como segura."

    def _risk_to_severity(self, risk: ActionRisk) -> SignalSeverity:
        mapping = {
            ActionRisk.SAFE: SignalSeverity.INFO,
            ActionRisk.MODERATE: SignalSeverity.WARNING,
            ActionRisk.RISKY: SignalSeverity.CRITICAL,
            ActionRisk.BLOCKED: SignalSeverity.CRITICAL,
        }
        return mapping[risk]

    def get_signals(self, min_severity: Optional[SignalSeverity] = None) -> List[Dict]:
        """Retorna sinais emitidos, opcionalmente filtrados por severidade"""
        signals = [s.to_dict() for s in self.signals]
        if min_severity:
            severity_order = {SignalSeverity.INFO: 0, SignalSeverity.WARNING: 1, SignalSeverity.CRITICAL: 2}
            min_level = severity_order[min_severity]
            signals = [s for s in signals if severity_order.get(
                SignalSeverity(s["severity"]), 0) >= min_level]
        return signals

    def get_report(self) -> Dict:
        """Retorna relatorio do Witness"""
        return {
            "observer": self.name,
            "total_observations": self.witness_count,
            "goal_drift_detections": self.goal_drift_count,
            "signals_emitted": len(self.signals),
            "signals_by_severity": {
                "info": len([s for s in self.signals if s.severity == SignalSeverity.INFO]),
                "warning": len([s for s in self.signals if s.severity == SignalSeverity.WARNING]),
                "critical": len([s for s in self.signals if s.severity == SignalSeverity.CRITICAL]),
            },
            "recent_signals": [s.to_dict() for s in self.signals[-5:]],
        }


class TrustEngineBridge:
    """
    Ponte entre Witness Pattern e TrustEngine (SPEC-038).

    Simula a integracao: Witness observa -> emite sinal -> TrustEngine decide.
    """

    def __init__(self, witness: WitnessObserver):
        self.witness = witness
        self.decisions: List[Dict] = []

    def observe_and_decide(self, action: Dict, context: Optional[Dict] = None) -> Dict:
        """
        Observa acao com Witness e simula decisao do TrustEngine.

        Returns:
            Dict com sinal + decisao
        """
        signal = self.witness.observe(action, context)

        # Simular decisao do TrustEngine
        decision = {
            "signal_id": signal.id,
            "risk": signal.risk.value,
            "severity": signal.severity.value,
        }

        if signal.risk == ActionRisk.SAFE:
            decision["decision"] = "allow"
            decision["reason"] = "Acao classificada como segura pelo Witness."
        elif signal.risk == ActionRisk.MODERATE:
            decision["decision"] = "review"
            decision["reason"] = "Acao requer revisao antes de executar."
        elif signal.risk == ActionRisk.RISKY:
            decision["decision"] = "warn_and_allow"
            decision["reason"] = f"Risco detectado: {signal.reasoning}"
        elif signal.risk == ActionRisk.BLOCKED:
            decision["decision"] = "block"
            decision["reason"] = f"ACAO BLOQUEADA: {signal.reasoning}"

        self.decisions.append(decision)

        return {
            "signal": signal.to_dict(),
            "decision": decision,
        }

    def get_stats(self) -> Dict:
        """Estatisticas da ponte Witness -> TrustEngine"""
        decisions = self.decisions
        return {
            "total_observations": len(decisions),
            "allowed": len([d for d in decisions if d["decision"] == "allow"]),
            "reviewed": len([d for d in decisions if d["decision"] == "review"]),
            "warned": len([d for d in decisions if d["decision"] == "warn_and_allow"]),
            "blocked": len([d for d in decisions if d["decision"] == "block"]),
            "goal_drift_rate": round(
                self.witness.goal_drift_count / max(1, self.witness.witness_count), 4
            ),
        }
