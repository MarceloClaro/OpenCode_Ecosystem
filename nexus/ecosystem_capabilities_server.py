#!/usr/bin/env python3
"""
ECOSYSTEM CAPABILITIES MCP SERVER v1.0
======================================
Servidor MCP que expõe as capacidades do OpenCode Ecosystem para:
  - OpenCode CLI (via opencode.json mcp section)
  - Antigravity CLI (agy.exe via settings.json)
  - Qualquer cliente MCP compatível com stdio

Ferramentas expostas:
  - Scanner Noológico: análise de lacunas epistêmicas
  - Scanner Teleológico: alinhamento com objetivos
  - Scanner Evolutivo: maturidade evolutiva do ecossistema
  - Potentiality Estimator v2: estimativa de potencial epistêmico
  - Social Impact Scanner: impacto social e ESG
  - Reasoning Engines: Z3, SymPy, miniKanren, Critical
  - Metadados: skills, agentes, MCPs, status

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import json
import sys
import os
import asyncio
import logging
import time
import uuid
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [EcoCapabilities] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("ecosystem-capabilities")

# ============================================================
# Constantes
# ============================================================

MCP_SERVER_VERSION = "1.0.0"

# Auto-detect ecosystem root: environment variable > known paths > fallback
_eco_root_env = os.environ.get("ECOSYSTEM_ROOT")
if _eco_root_env and Path(_eco_root_env).exists():
    ECOSYSTEM_ROOT = Path(_eco_root_env)
elif Path(r"C:\Users\marce\Documents\OpenCode_Ecosystem").exists():
    ECOSYSTEM_ROOT = Path(r"C:\Users\marce\Documents\OpenCode_Ecosystem")
else:
    ECOSYSTEM_ROOT = Path(__file__).parent.parent

SKILLS_DIR = ECOSYSTEM_ROOT / "skills"
SPECS_DIR = ECOSYSTEM_ROOT / "specs"
MODULES_DIR = ECOSYSTEM_ROOT / "skills" / "system" / "academic-audit"
STATE_DIR = ECOSYSTEM_ROOT / ".evolve"
OBSERVABILITY_LOG = STATE_DIR / "ecosystem-capabilities-observability.jsonl"

# ============================================================
# Gerenciamento de Estado
# ============================================================

def ensure_state_dir() -> None:
    """Garante que o diretório de estado existe."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def log_tool_usage(tool_name: str, args: dict, result: dict, latency_ms: int) -> None:
    """Registra uso de ferramenta no log de observabilidade."""
    ensure_state_dir()
    entry = json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "server": "ecosystem-capabilities-mcp",
        "tool": tool_name,
        "args_summary": {k: str(v)[:100] for k, v in args.items()},
        "success": "erro" not in result,
        "latency_ms": latency_ms,
    }, ensure_ascii=False) + "\n"
    try:
        with open(OBSERVABILITY_LOG, "a", encoding="utf-8") as f:
            f.write(entry)
    except IOError:
        pass


# ============================================================
# Scanner Wrappers
# ============================================================

def run_noological_scanner(target: str = "ecossistema") -> dict:
    """Executa o Scanner Noológico e retorna resultados."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from scanner_integration import ScannerPipeline
        pipeline = ScannerPipeline()
        result = pipeline.run_noological(target=target)
        return {
            "scanner": "noologico",
            "status": "executado",
            "resultado": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "noologico",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_teleological_scanner(objective: str = "alinhamento global") -> dict:
    """Executa o Scanner Teleológico e retorna resultados."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from scanner_integration import ScannerPipeline
        pipeline = ScannerPipeline()
        result = pipeline.run_teleological(objective=objective)
        return {
            "scanner": "teleologico",
            "status": "executado",
            "resultado": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "teleologico",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_evolutionary_scanner() -> dict:
    """Executa o Scanner Evolutivo e retorna resultados."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from scanner_integration import ScannerPipeline
        pipeline = ScannerPipeline()
        result = pipeline.run_evolutionary()
        return {
            "scanner": "evolutivo",
            "status": "executado",
            "resultado": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "evolutivo",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_potentiality_estimator_v2() -> dict:
    """Executa o Potentiality Estimator v2 e retorna resultados."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        # Hot-reload: força recarga do módulo para refletir mudanças
        import importlib
        importlib.invalidate_caches()
        for mod_name in list(sys.modules.keys()):
            if 'potentiality_estimator_v2' in mod_name:
                del sys.modules[mod_name]
        from potentiality_estimator_v2 import PotentialityEstimatorV2
        estimator = PotentialityEstimatorV2()

        # Obter resultados reais dos outros scanners para popular a análise de potencialidade
        noo = run_noological_scanner("ecossistema")
        noological_res = noo.get("resultado", {}) if noo.get("status") == "executado" else {}

        tel = run_teleological_scanner("alinhamento global")
        teleological_res = tel.get("resultado", {}) if tel.get("status") == "executado" else {}

        evo = run_evolutionary_scanner()
        evolutionary_res = evo.get("resultado", {}) if evo.get("status") == "executado" else {}

        soc = run_social_impact_scanner("ecossistema")
        social_impact_res = soc.get("resultado", {}) if soc.get("status") == "executado" else {}

        div = run_cognitive_diversity_scanner("ecossistema")
        cds_res = div.get("resultado", {}) if div.get("status") == "executado" else div

        top = run_epistemic_topology_mapper("ecossistema")
        etm_res = top.get("resultado", {}) if top.get("status") == "executado" else top

        # Executar scanner de DNA para alimentar feasibility check
        try:
            sys.path.insert(0, str(MODULES_DIR))
            import importlib
            importlib.invalidate_caches()
            for mod_name in list(sys.modules.keys()):
                if 'potentiality_scanner' in mod_name:
                    del sys.modules[mod_name]
            from potentiality_scanner import PotentialityScanner
            dna_scanner = PotentialityScanner()
            dna_results = dna_scanner.extract_dna()
        except Exception:
            dna_results = {}

        result = estimator.scan(
            noological_results=noological_res,
            teleological_results=teleological_res,
            evolutionary_results=evolutionary_res,
            dna_results=dna_results,
            social_impact_results={"consolidated_score": social_impact_res.get("consolidated_score", 0.0) if isinstance(social_impact_res, dict) else 0.0},
            cds_results=cds_res,
            etm_results=etm_res
        )
        return {
            "scanner": "potentiality_v2",
            "status": "executado",
            "resultado": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "potentiality_v2",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_active_inference_step(observations: Optional[dict] = None) -> dict:
    """Executa um passo de inferência ativa e planejamento evolutivo (Fase A)."""
    try:
        sys.path.insert(0, str(ECOSYSTEM_ROOT / "nexus" / "scripts"))
        from active_inference_controller import ActiveInferenceController
        controller = ActiveInferenceController(state_dir=STATE_DIR)

        # Se observações não forem passadas, obtemos dados dinâmicos dos outros scanners
        if not observations:
            noo = run_noological_scanner("ecossistema")
            noo_val = noo.get("resultado", {}).get("coverage_pct", 85.0) / 100.0 if noo.get("status") == "executado" else 0.85

            tel = run_teleological_scanner("alinhamento global")
            tel_val = tel.get("resultado", {}).get("score", 80.0) / 100.0 if tel.get("status") == "executado" else 0.80

            # Para system_health, usamos a taxa de sucesso de testes ou um valor padrão estável
            health_val = 1.00

            # Para latência normalizada
            latency_val = 0.85

            # Para SROI
            soc = run_social_impact_scanner("ecossistema")
            sroi_val = soc.get("resultado", {}).get("sroi_ratio", 2.55) / 3.0 if soc.get("status") == "executado" else 0.75

            observations = {
                "noological_coverage": noo_val,
                "teleological_alignment": tel_val,
                "system_health": health_val,
                "normalized_latency": latency_val,
                "sroi_efficiency": sroi_val
            }

        result = controller.step(observations)
        return {
            "module": "active_inference",
            "status": "executado",
            "resultado": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "module": "active_inference",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_active_inference_status() -> dict:
    """Retorna o status atual dos priors e VFE da inferência ativa (Fase A)."""
    try:
        sys.path.insert(0, str(ECOSYSTEM_ROOT / "nexus" / "scripts"))
        from active_inference_controller import ActiveInferenceController
        controller = ActiveInferenceController(state_dir=STATE_DIR)
        return {
            "module": "active_inference",
            "status": "executado",
            "priors": {name: {"target": p.target_value, "tolerance": p.tolerance, "precision": p.precision} for name, p in controller.priors.items()},
            "history_length": len(controller.history),
            "last_step": controller.history[-1] if controller.history else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "module": "active_inference",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_self_evolution_cycle(target_component: str = "academic-audit") -> dict:
    """Inicia um ciclo completo de auto-evolução dinâmica Plan-Act-Reflect-Evolve."""
    try:
        sys.path.insert(0, str(ECOSYSTEM_ROOT / "nexus" / "scripts"))
        from active_inference_controller import ActiveInferenceController, PolicyProposal
        controller = ActiveInferenceController(state_dir=STATE_DIR)

        policy = PolicyProposal(
            policy_id=f"force_evolve_{target_component}",
            action_type="evolve_skill",
            target_component=target_component,
            expected_free_energy=0.1
        )

        obs = {
            "noological_coverage": 0.60,
            "teleological_alignment": 0.50,
            "system_health": 0.90,
            "normalized_latency": 0.70,
            "sroi_efficiency": 0.60
        }

        outcome = controller.execute_policy(policy, obs)
        return {
            "module": "self_evolution",
            "status": "executado",
            "outcome": outcome,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "module": "self_evolution",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_game_theory_solve(game_name: str, params: Optional[dict] = None) -> dict:
    """Resolve um dos 10 jogos clássicos da Teoria dos Jogos (Fase B)."""
    try:
        sys.path.insert(0, str(ECOSYSTEM_ROOT / "nexus" / "scripts"))
        from game_theory_models import GameTheorySolver
        result = GameTheorySolver.solve_game(game_name, params)
        return {
            "module": "game_theory",
            "status": "executado",
            "resultado": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "module": "game_theory",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_game_theory_to_rlt(game_name: str, params: Optional[dict] = None) -> dict:
    """Converte a resolução de um jogo em uma árvore lógica ARCHE RLT (Fase B)."""
    try:
        sys.path.insert(0, str(ECOSYSTEM_ROOT / "nexus" / "scripts"))
        from game_theory_models import convert_game_to_rlt
        result = convert_game_to_rlt(game_name, params)
        return {
            "module": "game_theory",
            "status": "executado",
            "rlt_node": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "module": "game_theory",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_game_theory_to_rumi(game_name: str, params: Optional[dict] = None) -> dict:
    """Mapeia dinâmicas de payoffs em hipóteses causais RUMI (Fase B)."""
    try:
        sys.path.insert(0, str(ECOSYSTEM_ROOT / "nexus" / "scripts"))
        from game_theory_models import convert_game_to_rumi_hypotheses
        result = convert_game_to_rumi_hypotheses(game_name, params)
        return {
            "module": "game_theory",
            "status": "executado",
            "hypotheses": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "module": "game_theory",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


dashboard_process = None

def run_dashboard_start(porta: int = 8081) -> dict:
    """Inicia o servidor HTTP do dashboard em background (Fase C)."""
    global dashboard_process
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            s.connect(("127.0.0.1", porta))
            s.close()
            return {
                "module": "dashboard",
                "status": "já ativo",
                "url": f"http://localhost:{porta}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except OSError:
            pass

        import subprocess
        cmd = [sys.executable, str(ECOSYSTEM_ROOT / "nexus" / "dashboard_server.py"), "--porta", str(porta)]
        dashboard_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(ECOSYSTEM_ROOT)
        )
        
        time.sleep(0.5)
        if dashboard_process.poll() is not None:
            stdout, stderr = dashboard_process.communicate()
            return {
                "module": "dashboard",
                "status": "erro",
                "erro": f"Processo terminou imediatamente com código {dashboard_process.returncode}",
                "stderr": stderr.decode("utf-8", errors="ignore")
            }

        return {
            "module": "dashboard",
            "status": "iniciado",
            "url": f"http://localhost:{porta}",
            "pid": dashboard_process.pid,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "module": "dashboard",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_dashboard_stop(porta: int = 8081) -> dict:
    """Para o servidor HTTP do dashboard ativo (Fase C)."""
    global dashboard_process
    try:
        stopped = False
        if dashboard_process is not None:
            dashboard_process.terminate()
            dashboard_process.wait(timeout=3)
            dashboard_process = None
            stopped = True

        import subprocess
        try:
            if sys.platform == "win32":
                out = subprocess.check_output(f"netstat -ano | findstr :{porta}", shell=True, text=True)
                for line in out.strip().splitlines():
                    parts = line.strip().split()
                    if len(parts) >= 5 and parts[1].endswith(f":{porta}"):
                        pid = parts[-1]
                        subprocess.run(f"taskkill /PID {pid} /F", shell=True)
                        stopped = True
            else:
                subprocess.run(f"fuser -k {porta}/tcp", shell=True)
                stopped = True
        except Exception:
            pass

        return {
            "module": "dashboard",
            "status": "parado" if stopped else "não estava rodando",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "module": "dashboard",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_dashboard_status(porta: int = 8081) -> dict:
    """Retorna se o servidor do dashboard está ativo (Fase C)."""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            s.connect(("127.0.0.1", porta))
            s.close()
            active = True
        except OSError:
            active = False

        return {
            "module": "dashboard",
            "ativo": active,
            "url": f"http://localhost:{porta}" if active else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "module": "dashboard",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_metacognitive_search(problem: str, difficulty: str = "medium") -> dict:
    """Executa busca metacognitiva com orçamento de profundidade adaptativo (SPEC-062)."""
    try:
        sys.path.insert(0, str(ECOSYSTEM_ROOT / "nexus" / "scripts"))
        from metacognitive_search import solve_with_metacognitive_search
        result = solve_with_metacognitive_search(problem, difficulty)
        return {
            "module": "metacognitive_search",
            "status": "executado",
            "resultado": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "module": "metacognitive_search",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_asde_experiment(scientific_problem: str, domain: str = "cognicao") -> dict:
    """Executa um experimento cognitivo completo integrado no ASDE (Fase E)."""
    try:
        sys.path.insert(0, str(ECOSYSTEM_ROOT / "nexus" / "scripts"))
        from asde_experiment_runner import ASDECognitiveExperimentRunner
        runner = ASDECognitiveExperimentRunner()
        result = runner.run_experiment(scientific_problem, domain)
        return {
            "module": "asde_experiment",
            "status": "executado",
            "resultado": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "module": "asde_experiment",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_asde_get_latest_experiment() -> dict:
    """Retorna os resultados do último experimento cognitivo integrado concluído no ASDE (Fase E)."""
    try:
        sys.path.insert(0, str(ECOSYSTEM_ROOT / "nexus" / "scripts"))
        from asde_experiment_runner import ASDECognitiveExperimentRunner
        runner = ASDECognitiveExperimentRunner()
        result = runner.get_latest_results()
        return {
            "module": "asde_experiment",
            "status": "executado" if result else "nenhum experimento encontrado",
            "resultado": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "module": "asde_experiment",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_social_impact_scanner(context: str = "ecossistema") -> dict:
    """Executa o Social Impact Scanner e retorna resultados."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from scanner_integration import ScannerPipeline
        pipeline = ScannerPipeline()
        result = pipeline.run_social_impact(context=context)
        return {
            "scanner": "social_impact",
            "status": "executado",
            "resultado": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "social_impact",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_full_pipeline() -> dict:
    """Executa o pipeline completo de scanners."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from scanner_integration import ScannerPipeline
        pipeline = ScannerPipeline()
        result = pipeline.run_full()
        return {
            "scanner": "full_pipeline",
            "status": "executado",
            "resultado": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "full_pipeline",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


# ============================================================
# Reasoning Engine Wrappers
# ============================================================

def run_z3_verification(formula: str) -> dict:
    """Executa verificação formal com Z3."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from reasoning_engines import Z3Engine
        engine = Z3Engine()
        result = engine.verify(formula)
        return {
            "engine": "z3",
            "status": "executado",
            "resultado": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "engine": "z3",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_sympy_analysis(expression: str) -> dict:
    """Executa análise simbólica com SymPy."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from reasoning_engines import SymPyEngine
        engine = SymPyEngine()
        result = engine.analyze(expression)
        return {
            "engine": "sympy",
            "status": "executado",
            "resultado": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "engine": "sympy",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_critical_analysis(argument: str) -> dict:
    """Executa análise de falácias e vieses cognitivos."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from reasoning_engines import CriticalEngine
        engine = CriticalEngine()
        result = engine.analyze(argument)
        return {
            "engine": "critical",
            "status": "executado",
            "resultado": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "engine": "critical",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_cross_paradigm_reasoning(problem: str, mode: str = "auto",
                                  context: Optional[dict] = None) -> dict:
    """Executa o Cross-Paradigm Reasoning Engine (SPEC-082, R38).

    Integra 4 motores (Z3, SymPy, Kanren, Critical) com 4 research
    skills (game_theory, temporal_population, theoretical_empirical,
    logical_multiscale) para resolver problemas multi-paradigma.

    Args:
        problem: O problema a ser resolvido
        mode: Modo de raciocínio (auto, formal, symbolic, logic,
              critical, research, all)
        context: Contexto adicional com facts, operation, params

    Returns:
        Dict com resultados sintetizados, confiança e reparos
    """
    try:
        cpr_path = str(Path(__file__).parent.parent /
                       "skills/research/cross-paradigm-reasoning")
        if cpr_path not in sys.path:
            sys.path.insert(0, cpr_path)
        import importlib
        importlib.invalidate_caches()
        from cross_paradigm_reasoning import (
            ReasoningOrchestrator, ReasoningMode, SystemSelfDiagnostic,
        )

        mode_map = {
            "auto": ReasoningMode.AUTO,
            "formal": ReasoningMode.FORMAL,
            "symbolic": ReasoningMode.SYMBOLIC,
            "logic": ReasoningMode.LOGIC,
            "critical": ReasoningMode.CRITICAL,
            "research": ReasoningMode.RESEARCH,
            "all": ReasoningMode.ALL,
        }

        orch = ReasoningOrchestrator()
        resolved_mode = mode_map.get(mode, ReasoningMode.AUTO)
        result = orch.solve(problem, resolved_mode, context or {})

        # Auto-diagnóstico
        diag = SystemSelfDiagnostic()

        return {
            "engine": "cross_paradigm",
            "status": "executado",
            "mode": mode,
            "synthesized_output": result.synthesized_output,
            "overall_confidence": result.overall_confidence,
            "engines_used": [r.engine for r in result.engine_results],
            "contradictions": [
                {"type": c["type"], "severity": c.get("severity", "low")}
                for c in result.contradictions
            ],
            "repairs_applied": len(result.repairs_applied),
            "engine_diagnostics": diag.diagnostic(),
            "time_ms": round(result.time_ms, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "engine": "cross_paradigm",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


# ============================================================
# Autonomous Self-Repair (SPEC-083 / R39)
# ============================================================

def run_self_repair(action: str = "heartbeat", engine: str = "",
                    ecosystem_state_path: str = "") -> dict:
    """Executa acoes do Autonomous Self-Repair System (SPEC-083).
    
    Args:
        action: heartbeat | pipeline | check_engine | reload | fallback | log | verify_chain
        engine: Nome do engine/skill (z3, sympy, kanren, critical, game_theory, etc.)
        ecosystem_state_path: Caminho opcional para ecosystem-state.json
    
    Returns:
        dict com resultado da acao
    """
    try:
        sys.path.insert(0, str(MODULES_DIR / "research" / "cross-paradigm-reasoning"))
        from autonomous_self_repair import (
            HealthMonitor, RepairEngine, RepairLogger,
            RepairNotifier, SelfRepairOrchestrator,
        )
    except Exception:
        # Fallback: tenta path relativo ao cenario
        try:
            from autonomous_self_repair import (
                HealthMonitor, RepairEngine, RepairLogger,
                RepairNotifier, SelfRepairOrchestrator,
            )
        except Exception as e:
            return {"engine": "self_repair", "status": "erro",
                    "erro": f"Import failed: {e}"}
        sys.path.pop(0)

    t0 = time.time()

    if action == "heartbeat":
        hm = HealthMonitor()
        hb = hm.heartbeat()
        return {
            "engine": "self_repair",
            "status": "executado",
            "action": "heartbeat",
            "resultado": hb,
            "time_ms": round((time.time() - t0) * 1000, 2),
        }

    elif action == "pipeline":
        orch = SelfRepairOrchestrator()
        result = orch.run_pipeline(
            ecosystem_state_path if ecosystem_state_path else None
        )
        return {
            "engine": "self_repair",
            "status": "executado",
            "action": "pipeline",
            "resultado": result,
            "time_ms": round((time.time() - t0) * 1000, 2),
        }

    elif action == "check_engine":
        if not engine:
            return {"engine": "self_repair", "status": "erro",
                    "action": "check_engine", "erro": "Parametro 'engine' obrigatorio"}
        hm = HealthMonitor()
        # Tenta como engine primeiro, depois como research skill
        from autonomous_self_repair import ENGINES, RESEARCH_SKILLS
        if engine in ENGINES:
            hc = hm.check_engine(engine)
        elif engine in RESEARCH_SKILLS:
            hc = hm.check_research_skill(engine)
        else:
            return {"engine": "self_repair", "status": "erro",
                    "action": "check_engine",
                    "erro": f"Engine/skill desconhecido: {engine}"}
        return {
            "engine": "self_repair",
            "status": "executado",
            "action": "check_engine",
            "check": {
                "engine": hc.engine,
                "available": hc.available,
                "response_time_ms": hc.response_time_ms,
                "version": hc.version,
                "last_error": hc.last_error,
            },
            "time_ms": round((time.time() - t0) * 1000, 2),
        }

    elif action == "reload":
        if not engine:
            return {"engine": "self_repair", "status": "erro",
                    "action": "reload", "erro": "Parametro 'engine' obrigatorio"}
        hm = HealthMonitor()
        re = RepairEngine(hm)
        record = re.reload_module(engine)
        return {
            "engine": "self_repair",
            "status": "executado",
            "action": "reload",
            "resultado": {
                "engine": record.engine,
                "diagnosis": record.diagnosis,
                "result": record.result,
                "detail": record.detail,
                "duration_ms": record.duration_ms,
            },
            "time_ms": round((time.time() - t0) * 1000, 2),
        }

    elif action == "fallback":
        if not engine:
            return {"engine": "self_repair", "status": "erro",
                    "action": "fallback", "erro": "Parametro 'engine' obrigatorio"}
        hm = HealthMonitor()
        re = RepairEngine(hm)
        record = re.fallback(engine)
        return {
            "engine": "self_repair",
            "status": "executado",
            "action": "fallback",
            "resultado": {
                "engine": record.engine,
                "diagnosis": record.diagnosis,
                "result": record.result,
                "detail": record.detail,
                "duration_ms": record.duration_ms,
            },
            "time_ms": round((time.time() - t0) * 1000, 2),
        }

    elif action == "log":
        logger = RepairLogger()
        return {
            "engine": "self_repair",
            "status": "executado",
            "action": "log",
            "entries": logger.get_log(),
            "chain_valid": logger.verify_chain(),
            "time_ms": round((time.time() - t0) * 1000, 2),
        }

    elif action == "verify_chain":
        logger = RepairLogger()
        return {
            "engine": "self_repair",
            "status": "executado",
            "action": "verify_chain",
            "chain_valid": logger.verify_chain(),
            "time_ms": round((time.time() - t0) * 1000, 2),
        }

    else:
        return {"engine": "self_repair", "status": "erro",
                "action": action, "erro": f"Action desconhecida: {action}"}


# ============================================================
# Scanners Cognitivos (SPEC-053, SPEC-054, SPEC-055)
# ============================================================

def run_oqs_uncertainty_scan(text: str) -> dict:
    """Executa o UncertaintyScanner (SPEC-056) e retorna incertezas."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from uncertainty_scanner import UncertaintyScanner
        scanner = UncertaintyScanner()
        result = scanner.scan(text)
        return {
            "scanner": "oqs_uncertainty",
            "status": "executado",
            "spec": "SPEC-056",
            "resultado": {
                "object_of_analysis": result.problem.object_of_analysis,
                "initial_scope": result.problem.initial_scope,
                "word_count": result.problem.word_count,
                "has_hypothesis": result.problem.has_hypothesis,
                "uncertainties": [
                    {
                        "category": u.category,
                        "description": u.description,
                        "severity": u.severity,
                    }
                    for u in result.uncertainties
                ],
                "noisy_elements": [
                    {
                        "type": n.type,
                        "rationale": n.removal_rationale,
                    }
                    for n in result.noisy_elements
                ],
                "critical_points": result.critical_points,
                "ambiguity_zones": result.ambiguity_zones,
            },
            "total_uncertainties": len(result.uncertainties),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "oqs_uncertainty",
            "status": "erro",
            "spec": "SPEC-056",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_oqs_question_analyze(problem: str, candidates: list[str]) -> dict:
    """Executa o QuestionVectorizer (SPEC-056) e retorna pergunta otima."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from question_vectorizer import QuestionVectorizer
        qv = QuestionVectorizer()
        result = qv.analyze(problem, candidates)
        return {
            "scanner": "oqs_question",
            "status": "executado",
            "spec": "SPEC-056",
            "resultado": {
                "problem": result.problem[:200] if result.problem else "",
                "total_candidates": len(result.candidate_questions),
                "optimal_question": {
                    "question": result.optimal_question.question if result.optimal_question else None,
                    "type": result.optimal_question.type.value if result.optimal_question else None,
                    "convergence_score": round(result.optimal_question.convergence_score, 2) if result.optimal_question else None,
                    "URS": round(result.optimal_question.uncertainty_reduction, 2) if result.optimal_question else None,
                    "SVS": round(result.optimal_question.structural_value, 2) if result.optimal_question else None,
                    "DRI": round(result.optimal_question.dispersion_risk_index, 2) if result.optimal_question else None,
                    "CCI": round(result.optimal_question.cognitive_cost_index, 2) if result.optimal_question else None,
                    "rationale": result.optimal_question.rationale if result.optimal_question else None,
                } if result.optimal_question else None,
                "discarded": result.discarded,
                "answer_direction_passed": result.answer_direction_test.get("passed", False),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "oqs_question",
            "status": "erro",
            "spec": "SPEC-056",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


# ============================================================
# R28 — ARCHE RLT, OPUS, Witness Pattern, RUMI
# ============================================================

def run_arche_rlt_analyze(steps: list) -> dict:
    """Analisa cadeia de raciocinio com ARCHE Reasoning Logic Tree."""
    try:
        rlt_dir = ECOSYSTEM_ROOT / "skills" / "system" / "reasoning-orchestrator"
        sys.path.insert(0, str(rlt_dir))
        from arche_rlt import ARCHEEngine
        engine = ARCHEEngine()
        result = engine.analyze_reasoning_chain(steps)
        return {
            "scanner": "arche_rlt",
            "status": "executado",
            "spec": "SPEC-057",
            "total_nodes": result["total_nodes"],
            "depth": result["depth"],
            "root_confidence": result["root_confidence"],
            "inference_types_used": result["validation"]["inference_types_used"],
            "is_valid": result["validation"]["is_valid"],
            "coherence_gaps": result["validation"]["coherence_gaps"],
            "rlt": result["rlt"],
            "mermaid": result["mermaid"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "arche_rlt",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_arche_rlt_map_types() -> dict:
    """Mapeia todos os tipos de raciocinio para os 6 tipos de Peirce."""
    try:
        rlt_dir = ECOSYSTEM_ROOT / "skills" / "system" / "reasoning-orchestrator"
        sys.path.insert(0, str(rlt_dir))
        from arche_rlt import ARCHEEngine
        engine = ARCHEEngine()
        result = engine.map_all_reasoning_types()
        return {
            "scanner": "arche_rlt_map",
            "status": "executado",
            "spec": "SPEC-057",
            "total_types_mapped": result["total_types_mapped"],
            "by_peirce_type": result["by_peirce_type"],
            "peirce_types": result["peirce_types"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "arche_rlt_map",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_opus_pipeline(mission: str) -> dict:
    """Executa pipeline OPUS 4-Phase."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from opus_orchestration import opus_execute_pipeline
        result = opus_execute_pipeline(mission)
        return {
            "scanner": "opus",
            "status": "executado",
            "mission": mission,
            "contract_id": result["report"]["contract_id"],
            "status_ciclo": result["report"]["status"],
            "phases_executed": result["report"]["phases_executed"],
            "total_decisions": result["report"]["total_decisions"],
            "total_steps": result["report"]["total_steps"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "opus",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_witness_observe(action: dict, context: dict = None) -> dict:
    """Observa uma acao com Witness Pattern."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from witness_pattern import WitnessObserver, TrustEngineBridge
        witness = WitnessObserver()
        bridge = TrustEngineBridge(witness)
        result = bridge.observe_and_decide(action, context or {})
        return {
            "scanner": "witness",
            "status": "executado",
            "risk": result["signal"]["risk"],
            "severity": result["signal"]["severity"],
            "decision": result["decision"]["decision"],
            "reason": result["decision"]["reason"],
            "signal_id": result["signal"]["id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "witness",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_rumi_discover(variables: list) -> dict:
    """Executa pipeline RUMI de descoberta causal."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from rumi_causal_discovery import RUMIEngine
        engine = RUMIEngine()
        result = engine.discover(variables, top_k=3)
        return {
            "scanner": "rumi_discovery",
            "status": "executado",
            "total_hypotheses": result["total_hypotheses_generated"],
            "confirmed": result["confirmed"],
            "refuted": result["refuted"],
            "adversarial_pass_rate": result["adversarial_pass_rate"],
            "top_hypotheses": result["top_hypotheses"],
            "causal_graph": result["causal_graph"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "rumi_discovery",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_rumi_analyze_claim(cause: str, effect: str, mechanism: str = "", confidence: float = 0.7) -> dict:
    """Analisa uma reivindicacao causal especifica."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from rumi_causal_discovery import RUMIEngine
        engine = RUMIEngine()
        result = engine.analyze_causal_claim(cause, effect, mechanism, confidence)
        return {
            "scanner": "rumi_claim",
            "status": "executado",
            "hypothesis": result["hypothesis"],
            "status_hipotese": result["status"],
            "passed_adversarial": result["passed_adversarial"],
            "recommendation": result["recommendation"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "rumi_claim",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


# ============================================================
# R29 — ASDE: Autonomous Scientific Discovery Engine
# ============================================================

def run_asde_pipeline(problem: str, domain: str = "general") -> dict:
    """Executa pipeline completo ASDE de descoberta científica."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from asde_engine import ASDEEngine
        engine = ASDEEngine()
        result = engine.run_pipeline(problem, domain)
        return {
            "scanner": "asde_pipeline",
            "status": "executado",
            "spec": "SPEC-058",
            "total_ideas": result["total_ideas"],
            "pipeline_steps": result["pipeline"],
            "best_idea": result["best_idea"],
            "ideas": result["ideas"],
            "ontology": result["ontology"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "asde_pipeline",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_asde_get_report(idea_index: int = 0) -> dict:
    """Retorna relatório IMRaD de uma ideia gerada pelo ASDE."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from asde_engine import ASDEEngine
        engine = ASDEEngine()
        # Executa pipeline com problema padrão se não houver sessão anterior
        engine.run_pipeline("Explorar a relacao entre polimatia e resiliencia cognitiva")
        report = engine.get_report(idea_index)
        return {
            "scanner": "asde_report",
            "status": "executado",
            "spec": "SPEC-058",
            "idea_index": idea_index,
            "report": report,
            "has_report": report is not None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "asde_report",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_asde_ontology_status() -> dict:
    """Retorna status do grafo ontológico do ASDE."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from asde_engine import ASDEEngine
        engine = ASDEEngine()
        status = engine.get_ontology_status()
        return {
            "scanner": "asde_ontology",
            "status": "executado",
            "spec": "SPEC-058",
            "ontology": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "asde_ontology",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_cognitive_diversity_scanner(target: str = "ecossistema") -> dict:
    """Executa o Cognitive Diversity Scanner (SPEC-053) para detectar câmaras de eco."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from cognitive_diversity_scanner import CognitiveDiversityScanner, ArtifactProfile

        cds = CognitiveDiversityScanner()

        # ── Registra artefatos do ecossistema (SPEC-056 R27) ──
        # 1. Artefato base do ecossistema
        cds.register_artifact(ArtifactProfile(
            artifact_id="ecossistema_global",
            text_preview=target,
            coverage_vector={"paradigmas": 0.7, "metodos": 0.6, "teorias": 0.5},
        ))

        # 2. Artefatos de diversidade cognitiva do injector (R27)
        n_injected = cds.register_from_injector()

        result = cds.compute_homogeneity_index()
        return {
            "scanner": "cognitive_diversity",
            "spec": "SPEC-053",
            "status": "executado",
            "homogeneity_index": result.get("global_hi"),
            "is_echo_chamber": result.get("is_echo_chamber"),
            "interpretation": result.get("interpretation"),
            "n_artifacts": result.get("n_artifacts"),
            "n_injected_artifacts": n_injected,
            "n_clusters": result.get("n_clusters"),
            "recommendations": result.get("recommendations", []),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "cognitive_diversity",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_epistemic_topology_mapper(target: str = "ecossistema") -> dict:
    """Executa o Epistemic Topology Mapper (SPEC-054) para projetar espaço de conhecimento."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from epistemic_topology_mapper import EpistemicTopologyMapper, TopologicalPoint

        etm = EpistemicTopologyMapper()
        # Pontos topológicos representando componentes do ecossistema
        etm.add_point(TopologicalPoint("skills", [0.8, 0.7, 0.6]))
        etm.add_point(TopologicalPoint("agentes", [0.7, 0.8, 0.5]))
        etm.add_point(TopologicalPoint("mcps", [0.6, 0.5, 0.9]))
        etm.add_point(TopologicalPoint("specs", [0.9, 0.6, 0.4]))
        etm.project(dimensions=2)

        return {
            "scanner": "epistemic_topology",
            "spec": "SPEC-054",
            "status": "executado",
            "islands": etm.detect_islands(),
            "holes": etm.detect_holes(),
            "bridge_potential": etm.compute_bridge_potential(),
            "num_points": 4,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "epistemic_topology",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


def run_rupture_potential_index(target: str = "ecossistema") -> dict:
    """Executa o Rupture Potential Index (SPEC-055) para análise de potencial de ruptura."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from rupture_potential_index import RupturePotentialIndex, ResearchOpportunity

        rpi = RupturePotentialIndex()
        rpi.register_opportunity(ResearchOpportunity(
            opportunity_id="ECO-01",
            label=f"Ruptura em {target}",
            epistemic_distance=0.7, fertility=0.6,
            risk_reward=0.5, cost_opportunity=0.4, eps_score=70.0,
        ))
        result = rpi.compute("ECO-01")
        return {
            "scanner": "rupture_potential",
            "spec": "SPEC-055",
            "status": "executado",
            "rpi_score": result.get("rpi_score"),
            "quadrant": result.get("quadrant"),
            "decision": result.get("decision"),
            "portfolio_position": result.get("portfolio_position"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "scanner": "rupture_potential",
            "status": "erro",
            "erro": str(e),
            "traceback": traceback.format_exc(),
        }


# ============================================================
# Skill/Agent Wrappers
# ============================================================

def list_ecosystem_skills() -> dict:
    """Lista todas as skills disponíveis no ecossistema."""
    skills = []
    if SKILLS_DIR.exists():
        for skill_md in SKILLS_DIR.rglob("SKILL.md"):
            rel_path = skill_md.relative_to(SKILLS_DIR)
            parts = rel_path.parts
            skill_name = parts[-2] if len(parts) > 1 else parts[0]
            skills.append({
                "name": skill_name,
                "path": str(rel_path),
                "category": parts[0] if len(parts) > 1 else "root",
            })
    return {
        "total_skills": len(skills),
        "skills": skills,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def list_ecosystem_agents() -> dict:
    """Lista todos os agentes disponíveis no ecossistema."""
    agents_dir = ECOSYSTEM_ROOT / "agents"
    agents = []
    if agents_dir.exists():
        for agent_md in agents_dir.glob("*.md"):
            agents.append({
                "name": agent_md.stem,
                "path": str(agent_md.relative_to(ECOSYSTEM_ROOT)),
            })
    return {
        "total_agents": len(agents),
        "agents": agents,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def list_ecosystem_mcps() -> dict:
    """Lista todos os MCPs disponíveis no ecossistema."""
    mcp_dir = ECOSYSTEM_ROOT / "nexus"
    mcps = []
    if mcp_dir.exists():
        for mcp_py in mcp_dir.glob("*mcp*.py"):
            mcps.append({
                "name": mcp_py.stem,
                "path": str(mcp_py.relative_to(ECOSYSTEM_ROOT)),
            })
    return {
        "total_mcps": len(mcps),
        "mcps": mcps,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def get_ecosystem_status() -> dict:
    """Retorna status geral do ecossistema."""
    eco_state_file = STATE_DIR / "ecosystem-state.json"
    eco_state = {}
    if eco_state_file.exists():
        try:
            eco_state = json.loads(eco_state_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    return {
        "versao": MCP_SERVER_VERSION,
        "ecosystem_root": str(ECOSYSTEM_ROOT),
        "saude": eco_state.get("overallHealth", "N/A"),
        "ultima_sync": eco_state.get("lastSync", "N/A"),
        "componentes": {
            "skills": len(list(SKILLS_DIR.rglob("SKILL.md"))) if SKILLS_DIR.exists() else 0,
            "agents": len(list((ECOSYSTEM_ROOT / "agents").glob("*.md"))) if (ECOSYSTEM_ROOT / "agents").exists() else 0,
            "mcps": len(list((ECOSYSTEM_ROOT / "nexus").glob("*mcp*.py"))) if (ECOSYSTEM_ROOT / "nexus").exists() else 0,
            "specs": len(list(SPECS_DIR.glob("SPEC-*.md"))) if SPECS_DIR.exists() else 0,
            "modules": len(list(MODULES_DIR.glob("*.py"))) if MODULES_DIR.exists() else 0,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================
# Protocolo MCP — Servidor
# ============================================================

class EcosystemCapabilitiesMCPServer:
    """Servidor MCP que expõe capacidades do OpenCode Ecosystem."""

    def __init__(self):
        ensure_state_dir()
        logger.info(f"EcosystemCapabilitiesMCPServer v{MCP_SERVER_VERSION} inicializado")
        logger.info(f"Ecosystem root: {ECOSYSTEM_ROOT}")

    def get_tools(self) -> list[dict]:
        """Retorna lista de ferramentas disponíveis no formato MCP."""
        return [
            # === SCANNERS ===
            {
                "name": "eco_run_noological_scanner",
                "description": "Executa o Scanner Noológico para análise de lacunas epistêmicas e estruturais do ecossistema.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "default": "ecossistema",
                            "description": "Alvo da análise (ex: 'ecossistema', 'modulo_especifico')",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "eco_run_teleological_scanner",
                "description": "Executa o Scanner Teleológico para verificar alinhamento com objetivos estratégicos.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "objective": {
                            "type": "string",
                            "default": "alinhamento global",
                            "description": "Objetivo a verificar alinhamento",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "eco_run_evolutionary_scanner",
                "description": "Executa o Scanner Evolutivo para avaliar maturidade evolutiva do ecossistema.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "eco_run_potentiality_v2",
                "description": "Executa o Potentiality Estimator v2 (SPEC-045) para estimar potencial epistêmico com 6 dimensões (CDI, TF, GTV, TA, CI, SI).",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "eco_active_inference_step",
                "description": "Executa um passo de inferência ativa (Fase A) calculando a energia livre e selecionando uma política corretiva.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "observations": {
                            "type": "object",
                            "description": "Dicionário de métricas reais (ex: system_health, noological_coverage, normalized_latency)"
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "eco_active_inference_status",
                "description": "Retorna o status atual do controlador de inferência ativa (priors cognitivos, histórico de VFE).",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "eco_run_self_evolution_cycle",
                "description": "Inicia um ciclo completo de auto-evolução dinâmica Plan-Act-Reflect-Evolve sobre um componente.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target_component": {
                            "type": "string",
                            "default": "academic-audit",
                            "description": "Componente alvo para o ciclo de auto-evolução"
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "eco_game_theory_solve",
                "description": "Resolve qualquer um dos 10 jogos clássicos da Teoria dos Jogos com parâmetros personalizados.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "game_name": {
                            "type": "string",
                            "description": "Nome do jogo (ex: 'prisoners_dilemma', 'battle_of_sexes', 'stag_hunt', 'chicken', 'matching_pennies', 'cournot', 'stackelberg', 'centipede', 'ultimatum', 'public_goods')"
                        },
                        "params": {
                            "type": "object",
                            "description": "Dicionário de parâmetros de payoffs ou de jogo"
                        }
                    },
                    "required": ["game_name"],
                },
            },
            {
                "name": "eco_game_theory_to_rlt",
                "description": "Converte a resolução de um jogo estratégico em uma árvore de inferência lógica ARCHE RLT.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "game_name": {
                            "type": "string",
                            "description": "Nome do jogo"
                        },
                        "params": {
                            "type": "object",
                            "description": "Dicionário de parâmetros de payoffs"
                        }
                    },
                    "required": ["game_name"],
                },
            },
            {
                "name": "eco_game_theory_to_rumi",
                "description": "Mapeia as dinâmicas de incentivos de um jogo em hipóteses causais RUMI.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "game_name": {
                            "type": "string",
                            "description": "Nome do jogo"
                        },
                        "params": {
                            "type": "object",
                            "description": "Dicionário de parâmetros"
                        }
                    },
                    "required": ["game_name"],
                },
            },
            {
                "name": "eco_dashboard_start",
                "description": "Inicializa o servidor HTTP do dashboard do ecossistema em segundo plano.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "porta": {
                            "type": "integer",
                            "default": 8081,
                            "description": "Porta TCP para o servidor HTTP"
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "eco_dashboard_stop",
                "description": "Para o servidor HTTP do dashboard ativo.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "porta": {
                            "type": "integer",
                            "default": 8081,
                            "description": "Porta do servidor HTTP a ser parado"
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "eco_dashboard_status",
                "description": "Retorna o status atual do servidor HTTP do dashboard do ecossistema.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "porta": {
                            "type": "integer",
                            "default": 8081,
                            "description": "Porta do servidor a ser verificado"
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "eco_metacognitive_search",
                "description": "Executa busca metacognitiva guiada por process verifier com orçamento de profundidade adaptativo.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "problem": {
                            "type": "string",
                            "description": "Problema científico ou matemático a ser raciocinado"
                        },
                        "difficulty": {
                            "type": "string",
                            "default": "medium",
                            "description": "Dificuldade do problema ('easy', 'medium')"
                        }
                    },
                    "required": ["problem"],
                },
            },
            {
                "name": "eco_run_asde_experiment",
                "description": "Executa um experimento cognitivo completo integrado no ASDE com Teoria dos Jogos e FEP.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "scientific_problem": {
                            "type": "string",
                            "description": "O problema científico a ser simulado e descoberto"
                        },
                        "domain": {
                            "type": "string",
                            "default": "cognicao",
                            "description": "Domínio da pesquisa científica ('cognicao', 'neurociencia', 'aprendizado', 'psicologia', 'educacao', 'computacao')"
                        }
                    },
                    "required": ["scientific_problem"],
                },
            },
            {
                "name": "eco_get_latest_experiment_results",
                "description": "Retorna os resultados detalhados do último experimento cognitivo concluído pelo ASDE.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "eco_run_social_impact",
                "description": "Executa o Social Impact Scanner (SPEC-044) para análise de impacto social e ESG.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "context": {
                            "type": "string",
                            "default": "ecossistema",
                            "description": "Contexto para análise de impacto social",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "eco_run_full_pipeline",
                "description": "Executa o pipeline completo de scanners (Noológico → Teleológico → Evolutivo → Potentiality → Social Impact).",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            # === OQS — OPTIMAL QUESTION SCANNER (SPEC-056) ===
            {
                "name": "eco_run_oqs_uncertainty_scan",
                "description": "(SPEC-056) Escaneia incertezas de um problema usando o UncertaintyScanner. Retorna categorias de incerteza, ruído estrutural e texto filtrado.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Texto do problema a ser analisado",
                        }
                    },
                    "required": ["text"],
                },
            },
            {
                "name": "eco_run_oqs_question_analyze",
                "description": "(SPEC-056) Analisa perguntas candidatas e seleciona a pergunta ótima usando QuestionVectorizer + Convergence Score (CS = URS + SVS - DRI - CCI).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "problem": {
                            "type": "string",
                            "description": "Descrição do problema ou contexto",
                        },
                        "candidates": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de perguntas candidatas",
                        },
                    },
                    "required": ["problem", "candidates"],
                },
            },
            # === R28 — ARCHE RLT (SPEC-057) ===
            {
                "name": "eco_run_arche_rlt_analyze",
                "description": "(SPEC-057 R28) Analisa cadeia de raciocinio com ARCHE Reasoning Logic Tree. Mapeia tipos para 6 inferencias de Peirce e constroi arvore logica.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "premise": {"type": "string", "description": "Premissa do passo"},
                                    "conclusion": {"type": "string", "description": "Conclusao do passo"},
                                    "inference_type": {"type": "string", "description": "Tipo de inferencia (opcional)"},
                                }
                            },
                            "description": "Lista de passos de raciocinio",
                        }
                    },
                    "required": ["steps"],
                },
            },
            {
                "name": "eco_run_arche_rlt_map_types",
                "description": "(SPEC-057 R28) Mapeia todos os tipos de raciocinio do ecossistema para os 6 tipos de inferencia de Peirce.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            # === R28 — OPUS 4-PHASE ORCHESTRATION ===
            {
                "name": "eco_run_opus_pipeline",
                "description": "(R28) Executa pipeline OPUS 4-Phase (Open->Plan->Unfold->Seal) com Action Authorization Boundary.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mission": {
                            "type": "string",
                            "description": "Descricao da missao a ser orquestrada",
                        }
                    },
                    "required": ["mission"],
                },
            },
            # === R28 — WITNESS PATTERN ===
            {
                "name": "eco_run_witness_observe",
                "description": "(R28) Observa uma acao com Witness Pattern e retorna classificacao de risco. Integra com TrustEngine para decisoes.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "object",
                            "description": "Acao a ser observada (name, type)",
                        },
                        "context": {
                            "type": "object",
                            "description": "Contexto adicional (goal_drift_score, phase, etc.)",
                        },
                    },
                    "required": ["action"],
                },
            },
            # === R28 — RUMI CAUSAL DISCOVERY ===
            {
                "name": "eco_run_rumi_discover",
                "description": "(R28) Executa pipeline RUMI de descoberta causal: gera hipoteses -> testa -> torneio -> revisao adversarial -> grafo causal.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "variables": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de variaveis observadas",
                        }
                    },
                    "required": ["variables"],
                },
            },
            {
                "name": "eco_run_rumi_analyze_claim",
                "description": "(R28) Analisa uma reivindicacao causal especifica com revisao adversarial.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cause": {"type": "string", "description": "Variavel causal"},
                        "effect": {"type": "string", "description": "Variavel efeito"},
                        "mechanism": {"type": "string", "description": "Mecanismo causal proposto"},
                        "confidence": {"type": "number", "description": "Confianca inicial (0-1)"},
                    },
                    "required": ["cause", "effect"],
                },
            },
            # === R29 — ASDE (SPEC-058) ===
            {
                "name": "eco_run_asde_pipeline",
                "description": "(SPEC-058 R29) Executa pipeline completo ASDE de descoberta cientifica: problema -> ideias -> critica -> plano -> relatorio IMRaD. Integra OQS+RUMI+ARCHE+OPUS.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "problem": {
                            "type": "string",
                            "description": "Problema de pesquisa em texto livre",
                        },
                        "domain": {
                            "type": "string",
                            "default": "general",
                            "description": "Dominio cientifico (educacao, cognicao, saude, etc.)",
                        },
                    },
                    "required": ["problem"],
                },
            },
            {
                "name": "eco_run_asde_get_report",
                "description": "(SPEC-058 R29) Retorna o relatorio IMRaD completo de uma ideia gerada pelo ASDE.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "idea_index": {
                            "type": "integer",
                            "default": 0,
                            "description": "Indice da ideia (0 = melhor)",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "eco_run_asde_ontology_status",
                "description": "(SPEC-058 R29) Retorna o status do grafo ontologico cientifico do ASDE.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            # === SCANNERS COGNITIVOS (SPEC-053/054/055) ===
            {
                "name": "eco_run_cognitive_diversity",
                "description": "Executa o Cognitive Diversity Scanner (SPEC-053) para detectar câmaras de eco e homogeneidade cognitiva no ecossistema.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "default": "ecossistema",
                            "description": "Alvo da análise de diversidade cognitiva",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "eco_run_epistemic_topology",
                "description": "Executa o Epistemic Topology Mapper (SPEC-054) para projetar espaço de conhecimento em 2D e detectar ilhas, buracos e pontes epistêmicas.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "default": "ecossistema",
                            "description": "Alvo da análise topológica epistêmica",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "eco_run_rupture_potential",
                "description": "Executa o Rupture Potential Index (SPEC-055) para calcular potencial de ruptura assimétrico e posicionamento em portfólio EPS×RPI.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "default": "ecossistema",
                            "description": "Alvo da análise de potencial de ruptura",
                        }
                    },
                    "required": [],
                },
            },
            # === REASONING ENGINES ===
            {
                "name": "eco_z3_verify",
                "description": "Executa verificação formal de fórmulas lógicas usando o motor Z3.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "formula": {
                            "type": "string",
                            "description": "Fórmula lógica a verificar (sintaxe Z3)",
                        }
                    },
                    "required": ["formula"],
                },
            },
            {
                "name": "eco_sympy_analyze",
                "description": "Executa análise simbólica de expressões matemáticas usando SymPy.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Expressão matemática a analisar",
                        }
                    },
                    "required": ["expression"],
                },
            },
            {
                "name": "eco_critical_analyze",
                "description": "Executa análise de falácias lógicas e vieses cognitivos em um argumento.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "argument": {
                            "type": "string",
                            "description": "Argumento a ser analisado criticamente",
                        }
                    },
                    "required": ["argument"],
                },
            },
            {
                "name": "eco_cross_paradigm",
                "description": "(SPEC-082) Cross-Paradigm Reasoning Engine — integra Z3, SymPy, Kanren, Critical + 4 research skills para resolver problemas multi-paradigma.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "problem": {
                            "type": "string",
                            "description": "Problema a ser resolvido com raciocínio multi-paradigma",
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["auto", "formal", "symbolic", "logic", "critical", "research", "all"],
                            "description": "Modo de raciocínio (default: auto)",
                            "default": "auto",
                        },
                        "context": {
                            "type": "object",
                            "description": "Contexto adicional (facts, operation, params para research skills)",
                        },
                    },
                    "required": ["problem"],
                },
            },
            {
                "name": "eco_self_repair",
                "description": "(SPEC-083) Autonomous Self-Repair System — monitora saude dos 4 motores (Z3, SymPy, Kanren, Critical) + 4 research skills, executa pipeline de reparo (reload/deps/fallback) e atualiza audit trail SHA-256.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["heartbeat", "pipeline", "check_engine", "reload", "fallback", "log", "verify_chain"],
                            "description": "Acao a executar no sistema de auto-reparo (default: heartbeat)",
                            "default": "heartbeat",
                        },
                        "engine": {
                            "type": "string",
                            "description": "Nome do engine/skill para checagem individual (z3, sympy, kanren, critical, game_theory, etc.)",
                        },
                        "ecosystem_state_path": {
                            "type": "string",
                            "description": "Caminho para ecosystem-state.json (usado em pipeline)",
                        },
                    },
                    "required": [],
                },
            },
            # === METADADOS DO ECOSSISTEMA ===
            {
                "name": "eco_list_skills",
                "description": "Lista todas as skills disponíveis no OpenCode Ecosystem (227+ skills em 13 categorias).",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "eco_list_agents",
                "description": "Lista todos os agentes disponíveis no OpenCode Ecosystem (128+ agentes).",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "eco_list_mcps",
                "description": "Lista todos os servidores MCP disponíveis no ecossistema (46 MCPs).",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "eco_status",
                "description": "Retorna o status geral do OpenCode Ecosystem: saúde, componentes, última sincronização.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        ]

    def handle_tool_call(self, tool_name: str, arguments: dict) -> Any:
        """Roteador central de chamadas de ferramenta."""
        handlers = {
            "eco_run_noological_scanner": lambda a: run_noological_scanner(a.get("target", "ecossistema")),
            "eco_run_teleological_scanner": lambda a: run_teleological_scanner(a.get("objective", "alinhamento global")),
            "eco_run_evolutionary_scanner": lambda a: run_evolutionary_scanner(),
            "eco_run_potentiality_v2": lambda a: run_potentiality_estimator_v2(),
            "eco_active_inference_step": lambda a: run_active_inference_step(a.get("observations")),
            "eco_active_inference_status": lambda a: run_active_inference_status(),
            "eco_run_self_evolution_cycle": lambda a: run_self_evolution_cycle(a.get("target_component", "academic-audit")),
            "eco_game_theory_solve": lambda a: run_game_theory_solve(a.get("game_name"), a.get("params")),
            "eco_game_theory_to_rlt": lambda a: run_game_theory_to_rlt(a.get("game_name"), a.get("params")),
            "eco_game_theory_to_rumi": lambda a: run_game_theory_to_rumi(a.get("game_name"), a.get("params")),
            "eco_dashboard_start": lambda a: run_dashboard_start(a.get("porta", 8081)),
            "eco_dashboard_stop": lambda a: run_dashboard_stop(a.get("porta", 8081)),
            "eco_dashboard_status": lambda a: run_dashboard_status(a.get("porta", 8081)),
            "eco_metacognitive_search": lambda a: run_metacognitive_search(a.get("problem"), a.get("difficulty", "medium")),
            "eco_run_social_impact": lambda a: run_social_impact_scanner(a.get("context", "ecossistema")),
            "eco_run_full_pipeline": lambda a: run_full_pipeline(),
            "eco_run_cognitive_diversity": lambda a: run_cognitive_diversity_scanner(a.get("target", "ecossistema")),
            "eco_run_epistemic_topology": lambda a: run_epistemic_topology_mapper(a.get("target", "ecossistema")),
            "eco_run_rupture_potential": lambda a: run_rupture_potential_index(a.get("target", "ecossistema")),
            "eco_z3_verify": lambda a: run_z3_verification(a.get("formula", "")),
            "eco_sympy_analyze": lambda a: run_sympy_analysis(a.get("expression", "")),
            "eco_critical_analyze": lambda a: run_critical_analysis(a.get("argument", "")),
            "eco_cross_paradigm": lambda a: run_cross_paradigm_reasoning(
                a.get("problem", ""), a.get("mode", "auto"), a.get("context")),
            # R39 — Autonomous Self-Repair
            "eco_self_repair": lambda a: run_self_repair(
                a.get("action", "heartbeat"),
                a.get("engine", ""),
                a.get("ecosystem_state_path", "")),
            "eco_run_oqs_uncertainty_scan": lambda a: run_oqs_uncertainty_scan(a.get("text", "")),
            "eco_run_oqs_question_analyze": lambda a: run_oqs_question_analyze(a.get("problem", ""), a.get("candidates", [])),
            # R28 — ARCHE RLT, OPUS, Witness, RUMI
            "eco_run_arche_rlt_analyze": lambda a: run_arche_rlt_analyze(a.get("steps", [])),
            "eco_run_arche_rlt_map_types": lambda a: run_arche_rlt_map_types(),
            "eco_run_opus_pipeline": lambda a: run_opus_pipeline(a.get("mission", "")),
            "eco_run_witness_observe": lambda a: run_witness_observe(a.get("action", {}), a.get("context")),
            "eco_run_rumi_discover": lambda a: run_rumi_discover(a.get("variables", [])),
            "eco_run_rumi_analyze_claim": lambda a: run_rumi_analyze_claim(
                a.get("cause", ""), a.get("effect", ""),
                a.get("mechanism", ""), a.get("confidence", 0.7)),
            # R29 — ASDE (SPEC-058)
            "eco_run_asde_pipeline": lambda a: run_asde_pipeline(
                a.get("problem", ""), a.get("domain", "general")),
            "eco_run_asde_get_report": lambda a: run_asde_get_report(a.get("idea_index", 0)),
            "eco_run_asde_ontology_status": lambda a: run_asde_ontology_status(),
            "eco_run_asde_experiment": lambda a: run_asde_experiment(
                a.get("scientific_problem"), a.get("domain", "cognicao")),
            "eco_get_latest_experiment_results": lambda a: run_asde_get_latest_experiment(),
            "eco_list_skills": lambda a: list_ecosystem_skills(),
            "eco_list_agents": lambda a: list_ecosystem_agents(),
            "eco_list_mcps": lambda a: list_ecosystem_mcps(),
            "eco_status": lambda a: get_ecosystem_status(),
        }

        handler = handlers.get(tool_name)
        if not handler:
            return {"erro": f"Ferramenta desconhecida: {tool_name}"}

        try:
            start = time.time()
            result = handler(arguments)
            latency_ms = int((time.time() - start) * 1000)
            log_tool_usage(tool_name, arguments, result, latency_ms)
            logger.info(f"Ferramenta {tool_name} executada em {latency_ms}ms")
            return result
        except Exception as e:
            logger.error(f"Erro em {tool_name}: {e}")
            return {"erro": f"Falha na execução de {tool_name}: {str(e)}"}

    def handle_request(self, request: dict) -> Optional[dict]:
        """Processa uma requisição MCP e retorna a resposta."""
        method = request.get("method", "")
        req_id = request.get("id")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "ecosystem-capabilities-server",
                        "version": MCP_SERVER_VERSION,
                    },
                },
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.get_tools()},
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            result = self.handle_tool_call(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False, default=str),
                        }
                    ]
                },
            }

        elif method == "notifications/initialized":
            return None

        else:
            logger.warning(f"Método desconhecido: {method}")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Método não encontrado: {method}",
                },
            }

    def send_response(self, response: dict) -> None:
        """Envia resposta via stdout no formato JSON-RPC."""
        import io
        line = json.dumps(response, ensure_ascii=False)
        # Use UTF-8 encoding for stdout to handle Unicode characters
        sys.stdout.buffer.write((line + "\n").encode("utf-8"))
        sys.stdout.buffer.flush()

    def run(self) -> None:
        """Loop principal do servidor MCP via stdio."""
        logger.info(f"EcosystemCapabilitiesMCPServer v{MCP_SERVER_VERSION} aguardando requisições via stdio...")

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
            except json.JSONDecodeError as e:
                logger.error(f"JSON inválido recebido: {e}")
                continue

            response = self.handle_request(request)
            if response is not None:
                self.send_response(response)


# ============================================================
# Entrypoint
# ============================================================

if __name__ == "__main__":
    ensure_state_dir()
    server = EcosystemCapabilitiesMCPServer()
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Servidor encerrado pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal no servidor: {e}")
        sys.exit(1)
