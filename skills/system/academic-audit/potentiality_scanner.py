#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PotentialityScanner v1.0 — Scanner de Potenciais Latentes (Módulo 1)
======================================================================
Extrai o DNA estrutural do ecossistema mapeando os componentes e
skills ativos para suas capacidades fundamentais. Identifica o núcleo central,
redundâncias críticas e lacunas epistemológicas emergentes.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Set

class PotentialityScanner:
    """Scanner de Potenciais Latentes do OpenCode Ecosystem."""

    # Mapeamento estático das capacidades dos componentes core do ecossistema
    CORE_COMPONENT_MAP = {
        "noological_scanner": ["gap_detection", "epistemological_analysis", "vocabulary_boundary"],
        "teleological_scanner": ["prescriptive_inference", "normative_analysis", "teleological_mapping"],
        "cross_validation_engine": ["cross_validation", "consistency_checking", "validation_matrix"],
        "polymathic_convergence": ["polymathic_reasoning", "interdisciplinary_synthesis"],
        "trajectory_mapper": ["trajectory_mapping", "evolutionary_path_planning"],
        "autoevolve": ["self_evolution", "pipeline_optimization", "metacognitive_feedback"],
        "mcp_ecosystem": ["dependency_mapping", "context_offloading", "mcp_connection"],
        "antigravity_bridge": ["parallel_orchestration", "external_agent_delegation", "image_generation", "browser_automation"],
        "master_orchestrator": ["central_coordination", "task_delegation", "session_management"],
        "stage_orchestrator": ["pipeline_execution", "stage_sequencing"],
        "trust_engine": ["cognitive_guardrails", "goal_drift_prevention", "realtime_interception"],
        "cooperative_governance": ["governance_enforcement", "conflict_resolution"],
        "dialectical_engine": ["thesis_antithesis_synthesis", "contradiction_analysis"],
        "epistemological_potential": ["potential_estimation", "opportunity_ranking"],
        "structural_compression_engine": ["structural_compression", "token_optimization"],
        "structural_noise_scanner": ["noise_filtering", "information_density"],
    }

    # Heurísticas de mapeamento de palavras-chave para skills dinâmicas
    KEYWORD_TO_CAPABILITY = {
        "test": "tdd_validation",
        "tdd": "tdd_validation",
        "mock": "tdd_validation",
        "git": "version_control",
        "worktree": "version_control",
        "branch": "version_control",
        "agent": "agent_orchestration",
        "subagent": "agent_orchestration",
        "swarm": "agent_orchestration",
        "paper": "academic_synthesis",
        "article": "academic_synthesis",
        "qualis": "academic_synthesis",
        "academic": "academic_synthesis",
        "quantum": "quantum_computing",
        "qubit": "quantum_computing",
        "contract": "legal_processing",
        "law": "legal_processing",
        "juridico": "legal_processing",
        "data": "data_management",
        "db": "data_management",
        "sqlite": "data_management",
        "mcp": "mcp_connection",
        "server": "mcp_connection",
        "token": "token_optimization",
        "cost": "token_optimization",
    }

    # Lista de capacidades latentes que representam o roadmap futuro do ecossistema
    TARGET_EVOLVING_CAPABILITIES = [
        "autonomous_self_repair",
        "distributed_consensus",
        "proactive_alignment",
        "cross_paradigm_reasoning",
        "dynamic_dependency_injection",
        "predictive_teleology",
    ]

    def __init__(self, workspace_path: str | Path = None):
        if workspace_path is None:
            self.workspace = Path(__file__).parent.parent.parent.parent.resolve()
        else:
            self.workspace = Path(workspace_path)
            
        self.registry_path = self.workspace / "nexus" / "skills_registry.json"
        self.capability_map: Dict[str, List[str]] = {}

    def extract_dna(self) -> Dict[str, Any]:
        """Extrai o DNA de capacidades estruturais do ecossistema."""
        # 1. Carregar mapeamento do núcleo (core)
        self.capability_map = {k: list(v) for k, v in self.CORE_COMPONENT_MAP.items()}

        # 2. Carregar skills dinâmicas do skills_registry.json
        skills = []
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    skills = data.get("skills", [])
            except Exception as e:
                print(f"[PotentialityScanner] Erro ao ler registro de skills: {e}")

        # 3. Mapear skills dinâmicas via heurística
        for skill in skills:
            skill_name = skill.get("name", "")
            skill_path = skill.get("path", "")
            
            # Combinar texto de busca
            search_text = (skill_name + " " + skill_path).lower()
            
            # Encontrar capacidades correspondentes
            caps = []
            for kw, cap in self.KEYWORD_TO_CAPABILITY.items():
                if kw in search_text:
                    caps.append(cap)
            
            if caps:
                # Se a skill já existir no mapa, apenas estende as capacidades
                if skill_name in self.capability_map:
                    self.capability_map[skill_name] = list(set(self.capability_map[skill_name] + caps))
                else:
                    self.capability_map[skill_name] = list(set(caps))

        # 4. Calcular frequência das capacidades
        cap_frequency: Dict[str, int] = {}
        for caps in self.capability_map.values():
            for cap in caps:
                cap_frequency[cap] = cap_frequency.get(cap, 0) + 1

        # 5. Identificar Capacidades Centrais (Core)
        # Qualquer capacidade que apareça em 2 ou mais componentes é considerada central
        core_capabilities = {cap for cap, freq in cap_frequency.items() if freq >= 2}

        # 6. Identificar Capacidades Redundantes
        # Qualquer capacidade com 3 ou mais componentes implementando
        redundant_capabilities = {cap for cap, freq in cap_frequency.items() if freq >= 3}

        # 7. Identificar Capacidades Ausentes
        # Qualquer capacidade do roadmap alvo que não esteja presente em nenhuma skill ativa
        all_extracted_caps = set(cap_frequency.keys())
        missing_capabilities = {
            cap for cap in self.TARGET_EVOLVING_CAPABILITIES
            if cap not in all_extracted_caps
        }

        return {
            "capability_map": self.capability_map,
            "core_capabilities": sorted(list(core_capabilities)),
            "redundant_capabilities": sorted(list(redundant_capabilities)),
            "missing_capabilities": sorted(list(missing_capabilities)),
            "frequencies": cap_frequency
        }

    def scan(self) -> Dict[str, Any]:
        """Executa a varredura completa de potenciais latentes (DNA Extractor)."""
        return self.extract_dna()

    def save_report(self, report_data: Dict[str, Any], output_path: str | Path) -> None:
        """Gera e salva um relatório formatado em markdown."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "# Relatório de DNA Estrutural (Potentiality Scanner)",
            "",
            "## 🧬 1. Resumo do DNA de Capacidades",
            f"- **Componentes/Skills mapeados:** {len(report_data['capability_map'])}",
            f"- **Capacidades distintas identificadas:** {len(report_data['frequencies'])}",
            f"- **Capacidades centrais (Core):** {len(report_data['core_capabilities'])}",
            f"- **Capacidades redundantes (Sobreposição):** {len(report_data['redundant_capabilities'])}",
            f"- **Capacidades ausentes (Lacunas evolutivas):** {len(report_data['missing_capabilities'])}",
            "",
            "## 🔑 2. Capacidades Centrais (Core)",
            "Estas capacidades formam o núcleo de inteligência do ecossistema e são amplamente utilizadas:",
        ]

        for cap in report_data["core_capabilities"]:
            freq = report_data["frequencies"].get(cap, 0)
            lines.append(f"- `{cap}` (Presente em {freq} componentes)")

        lines.extend([
            "",
            "## ⚠️ 3. Capacidades Redundantes (Potencial de Convergência)",
            "Múltiplos componentes implementam estas capacidades. Há oportunidade de refatorar ou convergência de código:",
        ])

        for cap in report_data["redundant_capabilities"]:
            components = [k for k, v in report_data["capability_map"].items() if cap in v]
            lines.append(f"- `{cap}` (Implementado por: {', '.join(components)})")

        lines.extend([
            "",
            "## 🔍 4. Capacidades Ausentes (Lacunas do Roadmap Evolutivo)",
            "Estas capacidades pertencem ao roadmap planejado para o ecossistema mas não foram detectadas em nenhum componente:",
        ])

        for cap in report_data["missing_capabilities"]:
            lines.append(f"- `{cap}` 🔴 (Sem implementação ativa)")

        lines.extend([
            "",
            "## 🗺️ 5. Mapa Detalhado de Capacidades",
            "| ID do Componente | Capacidades Mapeadas |",
            "|------------------|----------------------|",
        ])

        for comp, caps in sorted(report_data["capability_map"].items()):
            lines.append(f"| `{comp}` | {', '.join(f'`{c}`' for c in caps)} |")

        out.write_text("\n".join(lines), encoding="utf-8")
        print(f"[PotentialityScanner] Relatório salvo em: {out}")
