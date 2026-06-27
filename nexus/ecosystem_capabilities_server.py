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
        from potentiality_estimator_v2 import PotentialityEstimatorV2
        estimator = PotentialityEstimatorV2()
        result = estimator.estimate()
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


# ============================================================
# Scanners Cognitivos (SPEC-053, SPEC-054, SPEC-055)
# ============================================================

def run_cognitive_diversity_scanner(target: str = "ecossistema") -> dict:
    """Executa o Cognitive Diversity Scanner (SPEC-053) para detectar câmaras de eco."""
    try:
        sys.path.insert(0, str(MODULES_DIR))
        from cognitive_diversity_scanner import CognitiveDiversityScanner, ArtifactProfile

        cds = CognitiveDiversityScanner()
        # Registra artefatos de exemplo do ecossistema
        cds.register_artifact(ArtifactProfile(
            artifact_id="ecossistema_global",
            text_preview=target,
            coverage_vector={"paradigmas": 0.7, "metodos": 0.6, "teorias": 0.5},
        ))
        result = cds.compute_homogeneity_index()
        return {
            "scanner": "cognitive_diversity",
            "spec": "SPEC-053",
            "status": "executado",
            "homogeneity_index": result.get("global_hi"),
            "is_echo_chamber": result.get("is_echo_chamber"),
            "interpretation": result.get("interpretation"),
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
            "eco_run_social_impact": lambda a: run_social_impact_scanner(a.get("context", "ecossistema")),
            "eco_run_full_pipeline": lambda a: run_full_pipeline(),
            "eco_run_cognitive_diversity": lambda a: run_cognitive_diversity_scanner(a.get("target", "ecossistema")),
            "eco_run_epistemic_topology": lambda a: run_epistemic_topology_mapper(a.get("target", "ecossistema")),
            "eco_run_rupture_potential": lambda a: run_rupture_potential_index(a.get("target", "ecossistema")),
            "eco_z3_verify": lambda a: run_z3_verification(a.get("formula", "")),
            "eco_sympy_analyze": lambda a: run_sympy_analysis(a.get("expression", "")),
            "eco_critical_analyze": lambda a: run_critical_analysis(a.get("argument", "")),
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
