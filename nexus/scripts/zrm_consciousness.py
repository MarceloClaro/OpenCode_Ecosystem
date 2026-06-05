# -*- coding: utf-8 -*-
"""
ZRM CONSCIOUSNESS v1.0 — Consciencia Autonoma de Solucao baseada em Metodos Formais (Z Notation)

Inspirada pelo Z Reference Manual (Spivey 1992) e pelos principios de:
  - Schema Calculus: pre-condicoes, post-condicoes, invariants
  - Data Refinement: transformacoes que preservam corretude
  - Proof Obligations: verificacao formal de propriedades
  - Mathematical Tool-Kit: conjuntos, relacoes, funcoes, sequencias

Atua como camada autonoma de QUALIDADE sobre orquestracao do ecossistema:
  1. VERIFICA pre-condicoes e post-condicoes de cada barreira de sincronizacao
  2. MONITORA desvios de especificacoes formais nos processos
  3. SUGERE solucoes refinadas quando resultados sao sub-otimos
  4. PRESERVA invariants do ecossistema apos cada operacao
  5. APRENDE com violacoes para refinar o proprio modelo
"""

from __future__ import annotations

import math
import json
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional
from enum import Enum


class ZViolationError(Exception):
    pass


# ── Tipos de severidade de violacao ─────────────────────────────────
class Severity(Enum):
    FATAL = "fatal"       # viola invariant fundamental, requer rollback
    ERROR = "error"       # viola post-condition, requer correcao
    WARNING = "warning"   # viola pre-condition parcial, continuavel
    INFO = "info"         # desvio menor, observacao


# ── Resultado de verificacao formal ──────────────────────────────────
@dataclass
class ZProofResult:
    schema_name: str
    condition_type: str          # "pre", "post", "invariant"
    passed: bool
    severity: str
    message: str
    evidence: dict = field(default_factory=dict)
    suggested_fix: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def is_fatal(self) -> bool:
        return not self.passed and self.severity == Severity.FATAL.value


# ── Esquema Z formal (pre, post, invariant) ─────────────────────────
@dataclass
class ZSchema:
    """Schema formal ao estilo Z: estado + operacoes com pre/post/invariant."""
    name: str
    pre_condition: Callable[[Any], bool]
    post_condition: Callable[[Any], bool]
    invariant: Optional[Callable[[Any], bool]] = None
    refinement: Optional[Callable[[Any], Any]] = None
    description: str = ""


# ── Consciencia autonoma ZRM ────────────────────────────────────────
class ZValidator:
    """Validador formal estilo Z. Invocado pelo sync_orchestrator nas barreiras."""

    _schemas: dict[str, ZSchema] = {}
    _violation_history: list[ZProofResult] = []
    _MAX_HISTORY = 200

    @classmethod
    def register_schema(cls, schema: ZSchema) -> None:
        cls._schemas[schema.name] = schema

    @classmethod
    def check_precondition(cls, schema_name: str, validate_fn: Callable, *args, **kwargs) -> bool:
        schema = cls._schemas.get(schema_name)
        if not schema:
            return True
        try:
            result = validate_fn(*args, **kwargs)
            if not schema.pre_condition(result):
                msg = f"Pre-condicao violada em '{schema_name}': {schema.description}"
                cls._record(ZProofResult(schema_name, "pre", False, Severity.ERROR.value, msg))
                return False
            cls._record(ZProofResult(schema_name, "pre", True, Severity.INFO.value, "OK", evidence={"result": str(result)[:200]}))
            return True
        except Exception as e:
            cls._record(ZProofResult(schema_name, "pre", False, Severity.ERROR.value, str(e)))
            return False

    @classmethod
    def check_postcondition(cls, schema_name: str, state: Any, condition: Callable[[Any], bool]) -> bool:
        schema = cls._schemas.get(schema_name)
        if not schema:
            return True
        try:
            if not condition(state):
                msg = f"Post-condicao violada em '{schema_name}': estado invalido apos operacao"
                cls._record(ZProofResult(schema_name, "post", False, Severity.ERROR.value, msg))
                return False
            if schema.post_condition and not schema.post_condition(state):
                msg = f"Post-condicao de schema violada em '{schema_name}': {schema.description}"
                cls._record(ZProofResult(schema_name, "post", False, Severity.ERROR.value, msg))
                return False
            cls._record(ZProofResult(schema_name, "post", True, Severity.INFO.value, "OK"))
            return True
        except Exception as e:
            cls._record(ZProofResult(schema_name, "post", False, Severity.ERROR.value, str(e)))
            return False

    @classmethod
    def check_invariant(cls, schema_name: str, state: Any) -> bool:
        schema = cls._schemas.get(schema_name)
        if not schema or not schema.invariant:
            return True
        try:
            if not schema.invariant(state):
                msg = f"INVARIANT VIOLADO em '{schema_name}': estado corrompido, requer rollback"
                cls._record(ZProofResult(schema_name, "invariant", False, Severity.FATAL.value, msg))
                return False
            return True
        except Exception as e:
            cls._record(ZProofResult(schema_name, "invariant", False, Severity.FATAL.value, str(e)))
            return False

    @classmethod
    def validate_ecosystem_health(cls, container) -> dict:
        try:
            sm = container.resolve('state_manager')
            eco = sm.get("ecosystem-state", default={})
            return {
                "health_score": eco.get("health_score", 0),
                "active_components": eco.get("active_components", 0),
                "offline_components": eco.get("offline_components", 0),
                "conflicts_count": len(eco.get("conflicts", [])),
                "cjk_active": eco.get("token_efficiency", {}).get("cjk_corrector_active", False),
            }
        except Exception as e:
            return {"error": str(e)}

    @classmethod
    def _record(cls, result: ZProofResult) -> None:
        cls._violation_history.append(result)
        if len(cls._violation_history) > cls._MAX_HISTORY:
            cls._violation_history = cls._violation_history[-cls._MAX_HISTORY:]

    @classmethod
    def get_violation_report(cls) -> dict:
        total = len(cls._violation_history)
        passed = sum(1 for r in cls._violation_history if r.passed)
        failed = total - passed
        by_severity = {}
        for r in cls._violation_history:
            by_severity[r.severity] = by_severity.get(r.severity, 0) + 1
        return {
            "total_checks": total, "passed": passed, "failed": failed,
            "success_rate": round(passed / max(total, 1) * 100, 1),
            "by_severity": by_severity,
            "recent_failures": [
                {"schema": r.schema_name, "msg": r.message[:120]}
                for r in cls._violation_history[-5:] if not r.passed
            ]
        }

    @classmethod
    def clear_history(cls) -> None:
        cls._violation_history.clear()


# ── Consciencia autonoma de solucao ──────────────────────────────────
class ZRMConsciousness:
    """Camada autonoma de raciocinio formal sobre processos e resultados do ecossistema.

    Aplica principios do ZRM (Spivey 1992) para:
      1. Detectar desvios (refinement checking)
      2. Sugerir correcoes (proof obligations -> fixes)
      3. Aprender com violacoes (schema evolution)
      4. Preservar integridade (invariant enforcement)
    """

    # ── Schemas formais do ecossistema ──────────────────────────────
    ECOSYSTEM_SCHEMAS = {
        "SyncBarrier": ZSchema(
            name="SyncBarrier",
            description="Barreira de sincronizacao: pre-condicao = ecossistema estavel, post = consistente",
            pre_condition=lambda h: h.get("health_score", 0) >= 70,
            post_condition=lambda s: 0.0 <= getattr(s, 'health_score', 0) <= 100.0
                and getattr(s, 'active_components', 0) > 0,
            invariant=lambda s: getattr(s, 'health_score', 0) >= 0
                and getattr(s, 'total_components', 0) >= getattr(s, 'active_components', 0),
        ),
        "ComponentHealth": ZSchema(
            name="ComponentHealth",
            description="Saude de componentes: nenhum componente pode ter score < 0",
            pre_condition=lambda c: c.get("status", "unknown") != "unknown",
            post_condition=lambda c: 0 <= c.get("score", 0) <= 100,
            invariant=lambda c: c.get("error_count", 0) >= 0,
        ),
        "TokenEfficiency": ZSchema(
            name="TokenEfficiency",
            description="Eficiencia de tokens: CJK corrector ativo, header coverage >= 80%",
            pre_condition=lambda te: te.get("context_encoding") == "chinese-simplified",
            post_condition=lambda te: te.get("output_language") == "pt-br-formal",
            invariant=lambda te: te.get("cjk_corrector_active", False) == True
                and te.get("header_coverage", 0) >= 80,
        ),
        "StatePersistence": ZSchema(
            name="StatePersistence",
            description="Persistencia de estado: state_manager operacional, db acessivel",
            pre_condition=lambda sm: sm.get("operational", False),
            post_condition=lambda s: s.get("persisted", False) == True,
            invariant=lambda sm: sm.get("db_size", 0) > 0,
        ),
        "AutoHealing": ZSchema(
            name="AutoHealing",
            description="Auto-cura: anomalias detectadas -> correcoes aplicadas -> health melhora",
            pre_condition=lambda h: h.get("health_score", 0) < 95,
            post_condition=lambda h: h.get("health_score", 0) >= h.get("previous_health", 0),
            invariant=lambda h: h.get("anomalies_fixed", 0) >= 0,
        ),
    }

    def __init__(self, state_manager):
        self._sm = state_manager
        self._learning_log: list[dict] = []
        self._solution_cache: dict[str, list[str]] = {}
        self._register_all_schemas()

    def _register_all_schemas(self):
        for schema in self.ECOSYSTEM_SCHEMAS.values():
            ZValidator.register_schema(schema)

    # ── Ciclo de consciencia autonoma ───────────────────────────────
    def autonomous_cycle(self, ecosystem_state: dict) -> dict:
        """Executa ciclo completo: verificar -> diagnosticar -> sugerir -> aprender."""
        start = datetime.now()

        # Fase 1: Verificacao formal (Z-Schema pre/post/invariant)
        verification_results = self._verify_state(ecosystem_state)

        # Fase 2: Diagnostico de anomalias (refinement checking)
        diagnosis = self._diagnose(ecosystem_state, verification_results)

        # Fase 3: Sugestao de solucoes (proof obligation -> fix)
        suggestions = self._suggest_solutions(diagnosis, ecosystem_state)

        # Fase 4: Aprendizado (schema evolution)
        learnings = self._learn(diagnosis, suggestions)

        # Fase 5: Persistencia do ciclo
        cycle_result = {
            "timestamp": start.isoformat(),
            "duration_ms": round((datetime.now() - start).total_seconds() * 1000),
            "verification": {
                "total": len(verification_results),
                "passed": sum(1 for r in verification_results if r.passed),
                "failed": sum(1 for r in verification_results if not r.passed),
            },
            "diagnosis": diagnosis,
            "suggestions": suggestions[:5],
            "learnings": learnings,
        }

        self._sm.set("zrm:last_consciousness_cycle", cycle_result)

        # Atualiza historico
        history = self._sm.get("zrm:consciousness_history", default=[])
        history.append({
            "timestamp": start.isoformat(),
            "passed": cycle_result["verification"]["passed"],
            "failed": cycle_result["verification"]["failed"],
            "top_suggestion": suggestions[0] if suggestions else "N/A",
        })
        if len(history) > 100:
            history = history[-100:]
        self._sm.set("zrm:consciousness_history", history)

        return cycle_result

    def _verify_state(self, state: dict) -> list[ZProofResult]:
        """Verifica todas as condicoes formais contra o estado atual."""
        results = []

        # SyncBarrier pre-condition
        health = state.get("health_score", 0)
        active = state.get("active_components", 0)
        total = state.get("total_components", 0)
        offline = state.get("offline_components", 0)

        schema = self.ECOSYSTEM_SCHEMAS["SyncBarrier"]
        pre_ok = schema.pre_condition({"health_score": health})
        results.append(ZProofResult(
            "SyncBarrier", "pre", pre_ok,
            Severity.ERROR.value if not pre_ok else Severity.INFO.value,
            f"Health {'ok' if pre_ok else 'CRITICO'} ({health:.1f}/100)",
            evidence={"health_score": health},
            suggested_fix="Executar self_healer e sync_orchestrator" if not pre_ok else None
        ))

        # SyncBarrier post-condition
        post_ok = 0.0 <= health <= 100.0 and active > 0 and active <= total
        results.append(ZProofResult(
            "SyncBarrier", "post", post_ok,
            Severity.ERROR.value if not post_ok else Severity.INFO.value,
            f"State {'valido' if post_ok else 'INVALIDO'} (active={active}, total={total})",
            evidence={"active": active, "total": total, "offline": offline},
            suggested_fix="Reverificar descoberta de componentes" if not post_ok else None
        ))

        # SyncBarrier invariant
        inv_ok = health >= 0 and total >= active
        results.append(ZProofResult(
            "SyncBarrier", "invariant", inv_ok,
            Severity.FATAL.value if not inv_ok else Severity.INFO.value,
            f"Invariant {'PRESERVADO' if inv_ok else 'VIOLADO'} (health>=0, total>=active)",
            evidence={"health_ge_0": health >= 0, "total_ge_active": total >= active},
            suggested_fix="ROLLBACK: restaurar estado anterior" if not inv_ok else None
        ))

        # TokenEfficiency invariant
        te = state.get("token_efficiency", {})
        cjk_active = te.get("cjk_corrector_active", False)
        hc = te.get("header_coverage", 0)
        te_inv_ok = cjk_active and hc >= 80
        results.append(ZProofResult(
            "TokenEfficiency", "invariant", te_inv_ok,
            Severity.WARNING.value if not te_inv_ok else Severity.INFO.value,
            f"CJK {'ATIVO' if cjk_active else 'INATIVO'}, Header={hc}%",
            evidence={"cjk_active": cjk_active, "header_coverage": hc},
            suggested_fix="Ativar corretor CJK e verificar headers" if not te_inv_ok else None
        ))

        # AutoHealing check
        heal_log = state.get("auto_healing_log", [])
        conflicts = state.get("conflicts", [])
        ah_ok = len(conflicts) == 0 or (len(heal_log) > 0 and len(heal_log) >= len(conflicts))
        results.append(ZProofResult(
            "AutoHealing", "post", ah_ok,
            Severity.WARNING.value if not ah_ok else Severity.INFO.value,
            f"Conflicts={len(conflicts)}, Heals={len(heal_log)}",
            evidence={"conflicts": len(conflicts), "heal_actions": len(heal_log)},
            suggested_fix="Executar self_healer para conflitos pendentes" if not ah_ok else None
        ))

        return results

    def _diagnose(self, state: dict, verification: list[ZProofResult]) -> dict:
        """Diagnostico baseado em refinement checking: o que desviou da especificacao?"""
        failures = [r for r in verification if not r.passed]
        fatal = [r for r in failures if r.is_fatal()]
        errors = [r for r in failures if r.severity == Severity.ERROR.value]
        warnings = [r for r in failures if r.severity == Severity.WARNING.value]

        diagnosis = {
            "status": "healthy" if not failures else ("critical" if fatal else ("degraded" if errors else "warning")),
            "fatal_count": len(fatal),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "root_causes": [],
        }

        # Identifica causas raiz
        health = state.get("health_score", 0)
        if health < 70:
            diagnosis["root_causes"].append({
                "issue": "Health score critico",
                "value": health,
                "threshold": 70,
                "refinement_path": "AutoHealing -> SelfHealer -> Re-sync"
            })
        elif health < 85:
            diagnosis["root_causes"].append({
                "issue": "Health score em atencao",
                "value": health,
                "threshold": 85,
                "refinement_path": "Monitor -> Diagnosticar componentes degradados"
            })

        if state.get("offline_components", 0) > 0:
            diagnosis["root_causes"].append({
                "issue": "Componentes offline detectados",
                "value": state["offline_components"],
                "refinement_path": "Discovery -> Reconnect -> Health check"
            })

        conflicts = state.get("conflicts", [])
        if conflicts:
            diagnosis["root_causes"].append({
                "issue": "Conflitos nao resolvidos",
                "value": len(conflicts),
                "refinement_path": "ConflictResolution -> Merge -> Validate"
            })

        cjk_active = state.get("token_efficiency", {}).get("cjk_corrector_active", False)
        if not cjk_active:
            diagnosis["root_causes"].append({
                "issue": "Corretor CJK inativo",
                "refinement_path": "Activate ptbr_corrector.py -> Re-scan output"
            })

        return diagnosis

    def _suggest_solutions(self, diagnosis: dict, state: dict) -> list[str]:
        """Sugere solucoes refinadas baseadas em proof obligations do ZRM."""
        suggestions = []

        health = state.get("health_score", 0)
        offline = state.get("offline_components", 0)

        # Solucao 1: Refinamento de componentes offline
        if offline > 0:
            suggestions.append(
                f"[DATA REFINEMENT] {offline} componentes offline. "
                "Aplicar forward simulation: re-descobrir componentes -> validar conectividade -> reintegrar."
            )

        # Solucao 2: Schema composition para conflitos
        conflicts = state.get("conflicts", [])
        if conflicts:
            suggestions.append(
                f"[SCHEMA CALCULUS] {len(conflicts)} conflitos. "
                "Aplicar schema disjunction: isolar conflitos em schemas separados -> resolver individualmente -> recompor via schema inclusion."
            )

        # Solucao 3: Invariant restoration
        if health < 85:
            suggestions.append(
                f"[INVARIANT RESTORATION] Health={health:.1f}/100. "
                "Aplicar refinement loop: self_healer -> re-sync -> re-validate ate health >= 95."
            )

        # Solucao 4: Type checking para CJK
        te = state.get("token_efficiency", {})
        if not te.get("cjk_corrector_active", False):
            suggestions.append(
                "[TYPE SYSTEM] Corretor CJK inativo. "
                "Aplicar type enforcement: ativar ptbr_corrector.py como pre-commit hook em toda saida de texto."
            )

        # Solucao 5: Mathematical tool-kit para cross-validation
        cv = state.get("cross_validation_matrix", {})
        if cv:
            suggestions.append(
                f"[MATHEMATICAL TOOL-KIT] {len(cv)} afinidades na cross-validation matrix. "
                "Aplicar relational calculus: identificar clusters de alta afinidade -> otimizar co-utilizacao de componentes."
            )

        # Solucao 6: Proof obligation para dynamic scores
        ds = state.get("dynamic_scores", {})
        underperformers = []
        if isinstance(ds, dict):
            for n, d in ds.items():
                score = d.get("computed_score", 85) if isinstance(d, dict) else d
                if isinstance(score, (int, float)) and score < 60:
                    underperformers.append(n)
        if underperformers:
            suggestions.append(
                f"[PROOF OBLIGATION] {len(underperformers)} componentes underperforming (<60). "
                f"Aplicar refinement proof: verificar pre-condicoes de cada componente -> corrigir ou substituir. "
                f"Afetados: {', '.join(underperformers[:3])}"
            )

        return suggestions

    def _learn(self, diagnosis: dict, suggestions: list[str]) -> list[str]:
        """Aprende com o ciclo para refinar schemas futuros (schema evolution)."""
        learnings = []

        status = diagnosis.get("status", "healthy")
        fatal_count = diagnosis.get("fatal_count", 0)
        error_count = diagnosis.get("error_count", 0)

        if status == "healthy":
            learnings.append("SCHEMA_EVOLUTION: Todos os invariants preservados. Schemas estaveis.")
        elif status == "critical":
            learnings.append(f"SCHEMA_STRENGTHEN: {fatal_count} violacoes fatais. Fortalecer pre-condicoes para prevenir estados invalidos.")
        else:
            learnings.append(f"SCHEMA_REFINE: {error_count} erros detectados. Refinar post-condicoes para capturar edge cases.")

        # Verifica se houve melhora em relacao ao ciclo anterior
        prev = self._sm.get("zrm:last_consciousness_cycle", default={})
        prev_failed = prev.get("verification", {}).get("failed", 0)
        current_failed = error_count + fatal_count
        if prev_failed > 0 and current_failed < prev_failed:
            learnings.append(f"IMPROVEMENT: Falhas reduziram de {prev_failed} para {current_failed}. Acoes corretivas efetivas.")
        elif current_failed > prev_failed:
            learnings.append(f"DEGRADATION: Falhas aumentaram de {prev_failed} para {current_failed}. Investigar nova causa raiz.")

        self._learning_log.extend(learnings)
        if len(self._learning_log) > 50:
            self._learning_log = self._learning_log[-50:]

        return learnings

    # ── Query interface ──────────────────────────────────────────────
    def get_solution_for(self, problem_type: str) -> Optional[str]:
        solutions = self._solution_cache.get(problem_type)
        if solutions:
            return solutions[0]
        return None

    def get_learning_summary(self) -> dict:
        return {
            "total_learnings": len(self._learning_log),
            "recent": self._learning_log[-5:] if self._learning_log else [],
        }

    def refine_schema(self, schema_name: str, new_pre: Optional[Callable] = None,
                      new_post: Optional[Callable] = None, new_invariant: Optional[Callable] = None) -> bool:
        """Refina um schema existente com novas condicoes (schema evolution)."""
        if schema_name not in self.ECOSYSTEM_SCHEMAS:
            return False
        schema = self.ECOSYSTEM_SCHEMAS[schema_name]
        if new_pre:
            old_pre = schema.pre_condition
            schema.pre_condition = lambda x: old_pre(x) and new_pre(x)
        if new_post:
            old_post = schema.post_condition
            schema.post_condition = lambda x: old_post(x) and new_post(x)
        if new_invariant:
            old_inv = schema.invariant
            if old_inv:
                schema.invariant = lambda x: old_inv(x) and new_invariant(x)
            else:
                schema.invariant = new_invariant
        ZValidator.register_schema(schema)
        return True


# ── Integracao com o ecossistema ─────────────────────────────────────
def integrate_with_orchestrator(container) -> ZRMConsciousness:
    """Cria e registra a consciencia ZRM no container DI do ecossistema."""
    try:
        sm = container.resolve('state_manager')
    except Exception:
        from core.config import settings
        from core.state import SQLiteStateManager
        sm = SQLiteStateManager(settings.state_db_path())

    consciousness = ZRMConsciousness(sm)
    container.register('zrm_consciousness', consciousness)

    # Executa ciclo autonomo inicial
    eco_state = sm.get("ecosystem-state", default={})
    if eco_state:
        result = consciousness.autonomous_cycle(eco_state)
        sm.set("zrm:consciousness_status", {
            "initialized": datetime.now().isoformat(),
            "schemas_registered": len(ZRMConsciousness.ECOSYSTEM_SCHEMAS),
            "first_cycle": result,
        })

    return consciousness


# ── CLI ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))
    from core import initialize_core
    from core.container import Container
    initialize_core()

    container = Container.instance()
    c = integrate_with_orchestrator(container)

    sm = container.resolve('state_manager')
    eco = sm.get("ecosystem-state", default={})

    result = c.autonomous_cycle(eco)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
