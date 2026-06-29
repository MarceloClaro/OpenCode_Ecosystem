# -*- coding: utf-8 -*-
"""
OPUS 4-Phase Orchestration Contract — R28
Inspirado em OPUS (Rynaro/OPUS): Open -> Plan -> Unfold -> Seal

Substitui orquestracao fixa por contrato governado com 4 fases,
Action Authorization Boundary (AAB) e auditoria integrada.
"""

import uuid
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime


class Phase(Enum):
    """As 4 fases do ciclo OPUS"""
    OPEN = "open"        # Abrir problema, explorar escopo
    PLAN = "plan"        # Planejar abordagem, mapear dependencias
    UNFOLD = "unfold"    # Executar plano, delegar acoes
    SEAL = "seal"        # Validar, consolidar, selar resultado


class ActionCategory(Enum):
    """Categorias de acao para o AAB"""
    READ = "read"              # Leitura de dados (seguro)
    COMPUTE = "compute"        # Computacao local (seguro)
    WRITE = "write"            # Escrita em disco (requer autorizacao)
    NETWORK = "network"        # Acesso a rede (requer autorizacao)
    EXECUTE = "execute"        # Execucao de comandos (requer autorizacao)
    DELEGATE = "delegate"      # Delegacao para subagentes (requer autorizacao)
    MUTATE_STATE = "mutate"    # Mutacao de estado global (requer autorizacao)


class AuthorizationLevel(Enum):
    """Niveis de autorizacao AAB"""
    AUTO = "auto"              # Autorizado automaticamente
    REVIEW = "review"          # Requer revisao
    BLOCKED = "blocked"        # Bloqueado


@dataclass
class ActionAuthorizationBoundary:
    """
    Action Authorization Boundary (AAB) — Controle de permissoes.

    Define o que cada acao pode fazer baseado na fase atual e
    no nivel de autorizacao configurado.
    """
    allowed_actions: Dict[Phase, List[ActionCategory]] = field(default_factory=lambda: {
        Phase.OPEN: [ActionCategory.READ, ActionCategory.COMPUTE],
        Phase.PLAN: [ActionCategory.READ, ActionCategory.COMPUTE, ActionCategory.WRITE],
        Phase.UNFOLD: [ActionCategory.READ, ActionCategory.COMPUTE, ActionCategory.WRITE,
                       ActionCategory.NETWORK, ActionCategory.EXECUTE, ActionCategory.DELEGATE],
        Phase.SEAL: [ActionCategory.READ, ActionCategory.COMPUTE, ActionCategory.WRITE,
                     ActionCategory.MUTATE_STATE],
    })

    def is_authorized(self, phase: Phase, action: ActionCategory) -> bool:
        """Verifica se uma acao e autorizada na fase atual"""
        return action in self.allowed_actions.get(phase, [])

    def authorize(self, phase: Phase, action: ActionCategory) -> AuthorizationLevel:
        """Retorna nivel de autorizacao para uma acao na fase"""
        if self.is_authorized(phase, action):
            return AuthorizationLevel.AUTO
        return AuthorizationLevel.BLOCKED


@dataclass
class OPUSState:
    """Estado rastreavel de uma execucao OPUS"""
    phase: Phase = Phase.OPEN
    artifacts: Dict[str, Any] = field(default_factory=dict)
    decisions: List[Dict] = field(default_factory=list)
    history: List[Dict] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def record_decision(self, action: str, reason: str, phase: Phase) -> None:
        """Registra uma decisao tomada durante a execucao"""
        self.decisions.append({
            "action": action,
            "reason": reason,
            "phase": phase.value,
            "timestamp": datetime.now().isoformat(),
        })

    def record_step(self, phase: Phase, step_name: str, result: Any) -> None:
        """Registra um passo executado"""
        self.history.append({
            "phase": phase.value,
            "step": step_name,
            "result": str(result)[:200] if result else "None",
            "timestamp": datetime.now().isoformat(),
        })

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "phase": self.phase.value,
            "artifacts": {k: str(v)[:100] for k, v in self.artifacts.items()},
            "decisions": self.decisions[-10:],  # ultimas 10
            "history": self.history[-20:],       # ultimos 20
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


class OPUSContract:
    """
    Contrato de orquestracao OPUS 4-Phase.

    Uso:
        contract = OPUSContract("Analisar impacto da polimatia")
        contract.open()      # Fase 1: Explorar
        contract.plan()      # Fase 2: Planejar
        contract.unfold()    # Fase 3: Executar
        contract.seal()      # Fase 4: Validar e selar
    """

    def __init__(self, mission: str, aab: Optional[ActionAuthorizationBoundary] = None):
        self.mission = mission
        self.state = OPUSState()
        self.aab = aab or ActionAuthorizationBoundary()
        self._phase_handlers: Dict[Phase, List[Callable]] = {
            Phase.OPEN: [],
            Phase.PLAN: [],
            Phase.UNFOLD: [],
            Phase.SEAL: [],
        }

    def register_handler(self, phase: Phase, handler: Callable) -> None:
        """Registra um handler para uma fase especifica"""
        if phase in self._phase_handlers:
            self._phase_handlers[phase].append(handler)

    def _check_authorization(self, action: ActionCategory) -> None:
        """Verifica se a acao e autorizada na fase atual"""
        level = self.aab.authorize(self.state.phase, action)
        if level == AuthorizationLevel.BLOCKED:
            raise PermissionError(
                f"ACAO BLOQUEADA: {action.value} nao permitida na fase {self.state.phase.value}. "
                f"Acao: {action.value}, Fase: {self.state.phase.value}"
            )

    def _transition_to(self, new_phase: Phase) -> None:
        """Transiciona para uma nova fase"""
        self.state.record_decision(
            action=f"transition:{self.state.phase.value}->{new_phase.value}",
            reason=f"Avancando da fase {self.state.phase.value} para {new_phase.value}",
            phase=self.state.phase,
        )
        self.state.phase = new_phase

    def open(self, context: Optional[Dict] = None) -> Dict:
        """
        Fase 1: OPEN — Abrir problema, explorar escopo.

        Acoes permitidas: READ, COMPUTE
        """
        if self.state.phase != Phase.OPEN:
            raise RuntimeError(f"Fase atual e {self.state.phase.value}, esperada OPEN")

        self.state.record_step(Phase.OPEN, "init", f"Abrindo missao: {self.mission}")

        # Executar handlers registrados
        results = []
        for handler in self._phase_handlers[Phase.OPEN]:
            result = handler(self.state, context or {})
            results.append(result)
            self.state.record_step(Phase.OPEN, handler.__name__, result)

        # Artefato padrao: escopo definido
        self.state.artifacts["scope"] = {
            "mission": self.mission,
            "context": context or {},
            "handlers_executed": len(results),
        }

        return {
            "phase": "open",
            "mission": self.mission,
            "artifacts": self.state.artifacts,
            "next": "plan",
            "aab_authorized_actions": [
                a.value for a in self.aab.allowed_actions[Phase.OPEN]
            ],
        }

    def plan(self, plan: Optional[Dict] = None) -> Dict:
        """
        Fase 2: PLAN — Planejar abordagem, mapear dependencias.

        Acoes permitidas: READ, COMPUTE, WRITE
        """
        self._transition_to(Phase.PLAN)
        self.state.record_step(Phase.PLAN, "init", f"Planejando: {self.mission}")

        # Executar handlers registrados
        results = []
        for handler in self._phase_handlers[Phase.PLAN]:
            result = handler(self.state, plan or {})
            results.append(result)
            self.state.record_step(Phase.PLAN, handler.__name__, result)

        # Artefato padrao: plano
        self.state.artifacts["plan"] = plan or {
            "steps": [],
            "dependencies": [],
            "estimated_phases": 4,
        }
        self.state.artifacts["plan"]["handlers_executed"] = len(results)

        return {
            "phase": "plan",
            "plan": self.state.artifacts["plan"],
            "next": "unfold",
        }

    def unfold(self, actions: Optional[List[Dict]] = None) -> Dict:
        """
        Fase 3: UNFOLD — Executar plano, delegar acoes.

        Acoes permitidas: READ, COMPUTE, WRITE, NETWORK, EXECUTE, DELEGATE
        """
        self._transition_to(Phase.UNFOLD)
        self.state.record_step(Phase.UNFOLD, "init", f"Executando: {self.mission}")

        # Verificar se ha um plano
        if "plan" not in self.state.artifacts:
            raise RuntimeError("Nao e possivel executar UNFOLD sem PLAN. Execute plan() primeiro.")

        # Executar handlers registrados
        results = []
        for handler in self._phase_handlers[Phase.UNFOLD]:
            self._check_authorization(ActionCategory.DELEGATE)
            result = handler(self.state, actions or [])
            results.append(result)
            self.state.record_step(Phase.UNFOLD, handler.__name__, result)

        self.state.artifacts["execution_results"] = {
            "actions_executed": len(actions or []),
            "handlers_executed": len(results),
            "results": [str(r)[:100] for r in results],
        }

        return {
            "phase": "unfold",
            "execution": self.state.artifacts["execution_results"],
            "next": "seal",
        }

    def seal(self, validation: Optional[Dict] = None) -> Dict:
        """
        Fase 4: SEAL — Validar, consolidar, selar resultado.

        Acoes permitidas: READ, COMPUTE, WRITE, MUTATE_STATE
        """
        self._transition_to(Phase.SEAL)
        self.state.record_step(Phase.SEAL, "init", f"Selando: {self.mission}")

        # Executar handlers registrados
        results = []
        for handler in self._phase_handlers[Phase.SEAL]:
            self._check_authorization(ActionCategory.MUTATE_STATE)
            result = handler(self.state, validation or {})
            results.append(result)
            self.state.record_step(Phase.SEAL, handler.__name__, result)

        # Finalizar
        self.state.completed_at = datetime.now().isoformat()
        self.state.artifacts["validation"] = validation or {
            "status": "completed",
            "checks": [],
        }
        self.state.artifacts["validation"]["handlers_executed"] = len(results)

        return {
            "phase": "seal",
            "mission": self.mission,
            "validation": self.state.artifacts["validation"],
            "completed_at": self.state.completed_at,
            "total_decisions": len(self.state.decisions),
            "total_steps": len(self.state.history),
            "status": "COMPLETED",
        }

    def get_report(self) -> Dict:
        """Retorna relatorio completo da execucao OPUS"""
        return {
            "contract_id": self.state.id,
            "mission": self.mission,
            "current_phase": self.state.phase.value,
            "created_at": self.state.created_at,
            "completed_at": self.state.completed_at,
            "status": "COMPLETED" if self.state.completed_at else "IN_PROGRESS",
            "phases_executed": list(dict.fromkeys(
                [h["phase"] for h in self.state.history]
            )),
            "total_decisions": len(self.state.decisions),
            "total_steps": len(self.state.history),
            "artifacts_summary": list(self.state.artifacts.keys()),
        }


def opus_execute_pipeline(
    mission: str,
    open_fn: Optional[Callable] = None,
    plan_fn: Optional[Callable] = None,
    unfold_fn: Optional[Callable] = None,
    seal_fn: Optional[Callable] = None,
) -> Dict:
    """
    Funcao de conveniencia para executar pipeline OPUS completo.

    Args:
        mission: Descricao da missao
        open_fn: Handler para fase OPEN (recebe state, context)
        plan_fn: Handler para fase PLAN (recebe state, plan)
        unfold_fn: Handler para fase UNFOLD (recebe state, actions)
        seal_fn: Handler para fase SEAL (recebe state, validation)

    Returns:
        Relatorio completo da execucao
    """
    contract = OPUSContract(mission)

    if open_fn:
        contract.register_handler(Phase.OPEN, open_fn)
    if plan_fn:
        contract.register_handler(Phase.PLAN, plan_fn)
    if unfold_fn:
        contract.register_handler(Phase.UNFOLD, unfold_fn)
    if seal_fn:
        contract.register_handler(Phase.SEAL, seal_fn)

    # Executar ciclo completo
    contract.open()
    contract.plan()
    contract.unfold()
    result = contract.seal()

    return {
        "report": contract.get_report(),
        "result": result,
        "state": contract.state.to_dict(),
    }
