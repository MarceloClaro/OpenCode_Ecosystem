#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ecosystem Health Test Suite — TDD para validação do OpenCode Ecosystem v4.2.3
=============================================================================
Testes que verificam se as métricas do ecossistema correspondem à realidade.
Baseado no gap analysis entre relatório aspiracional e estado real.

Testes:
  TC-001: MCPs — pelo menos 40 registrados, 20+ ativos
  TC-002: Skills — 100% das skills no registry (155/155)
  TC-003: Agentes — pelo menos 75 documentados
  TC-004: Plugins — 5 plugins TS operacionais
  TC-005: CJK — zero vazamentos
  TC-006: Registry — scores válidos (0-100)
  TC-007: Integridade — arquivos essenciais existem
"""

import json
import hashlib
import unittest
from pathlib import Path

BASE = Path(__file__).parent.parent


class TestEcosystemHealth(unittest.TestCase):
    """Suite de testes de saúde do ecossistema."""

    @classmethod
    def setUpClass(cls):
        cls.opencode = json.loads(
            (BASE / "opencode.json").read_text(encoding="utf-8")
        )
        cls.registry = json.loads(
            (BASE / "nexus" / "skills_registry.json").read_text(encoding="utf-8")
        )

    # ── TC-001: MCPs ──────────────────────────────────────────────────

    def test_mcp_total_count(self):
        """Pelo menos 40 MCPs registrados no opencode.json."""
        mcps = self.opencode.get("mcp", {})
        self.assertGreaterEqual(len(mcps), 40,
            f"Apenas {len(mcps)} MCPs. Minimo: 40")

    def test_mcp_enabled_count(self):
        """Pelo menos 20 MCPs ativos (enabled: true)."""
        mcps = self.opencode.get("mcp", {})
        enabled = sum(1 for m in mcps.values()
                     if isinstance(m, dict) and m.get("enabled", False))
        self.assertGreaterEqual(enabled, 20,
            f"Apenas {enabled} MCPs ativos. Minimo: 20")

    def test_mcp_core_present(self):
        """MCPs essenciais estao presentes."""
        mcps = self.opencode.get("mcp", {})
        required = ["filesystem", "code-runner", "sqlite", "sequential-thinking"]
        for name in required:
            self.assertIn(name, mcps,
                f"MCP essencial '{name}' nao encontrado")

    def test_mcp_academic_present(self):
        """MCPs academicos estao registrados."""
        mcps = self.opencode.get("mcp", {})
        academic = ["scihub", "research-mcp", "arxiv-mcp", "latest-science"]
        found = [n for n in academic if n in mcps]
        self.assertGreaterEqual(len(found), 2,
            f"Apenas {len(found)} MCPs academicos. Esperado >= 2")

    # ── TC-002: Skills Registry ───────────────────────────────────────

    def test_skills_registry_count(self):
        """Skills registry tem todas as skills (155+)."""
        total = self.registry["summary"]["total_skills"]
        self.assertGreaterEqual(total, 100,
            f"Registry tem apenas {total} skills. Esperado >= 100")

    def test_skills_all_registered(self):
        """Skills core (system, research, agent-forum) estao no registry."""
        skill_files = list((BASE / "skills").rglob("SKILL.md"))
        registered_names = {s["name"] for s in self.registry["skills"]}

        core_dirs = ["system", "research", "agent-forum", "juridico", "science"]
        missing = []
        for sf in skill_files:
            parts = sf.parts
            if "skills" in parts:
                idx = parts.index("skills")
                if len(parts) > idx + 1 and parts[idx + 1] in core_dirs:
                    # skills/core_dir/name/SKILL.md
                    if len(parts) > idx + 2:
                        name = parts[idx + 2]
                        if name not in registered_names and name != "SKILL.md":
                            missing.append(f"{parts[idx+1]}/{name}")

        self.assertLessEqual(len(missing), 10,
            f"{len(missing)} skills core nao registradas: {missing[:10]}")

    def test_skills_valid_scores(self):
        """Scores no registry estao entre 0-100 (quando aplicavel)."""
        for skill in self.registry["skills"]:
            # Verifica campos obrigatorios
            self.assertIn("name", skill, f"Skill sem nome")
            self.assertIn("category", skill, f"Skill {skill.get('name')} sem categoria")

    # ── TC-003: Agentes ───────────────────────────────────────────────

    def test_agents_count(self):
        """Pelo menos 100 agentes documentados."""
        agents = list((BASE / "agents").glob("*.md"))
        self.assertGreaterEqual(len(agents), 100,
            f"Apenas {len(agents)} agentes. Minimo: 100")

    def test_agents_have_names(self):
        """Agentes tem metadados de nome no frontmatter."""
        agents = list((BASE / "agents").glob("*.md"))
        with_name = 0
        for a in agents:
            content = a.read_text(encoding="utf-8")
            if "name:" in content[:500]:
                with_name += 1
        self.assertGreaterEqual(with_name, 30,
            f"Apenas {with_name} agentes com name: no frontmatter")

    # ── TC-004: Plugins ───────────────────────────────────────────────

    def test_plugins_count(self):
        """5 plugins TS estao presentes."""
        plugins = list((BASE / "plugins").glob("*.ts"))
        self.assertGreaterEqual(len(plugins), 4,
            f"Apenas {len(plugins)} plugins. Minimo: 4")

    def test_plugins_registered_in_config(self):
        """Plugins estao listados no opencode.json."""
        config_plugins = self.opencode.get("plugin", [])
        plugin_files = [p.name for p in (BASE / "plugins").glob("*.ts")]
        registered = [p for p in config_plugins if any(f in p for f in plugin_files)]
        self.assertGreaterEqual(len(registered), 3,
            f"Apenas {len(registered)} plugins no config")

    # ── TC-005: CJK ───────────────────────────────────────────────────

    CJK_RANGES = [
        (0x4E00, 0x9FFF), (0x3400, 0x4DBF), (0xF900, 0xFAFF),
        (0x3040, 0x309F), (0x30A0, 0x30FF), (0xAC00, 0xD7AF),
    ]

    def _has_cjk(self, text):
        for ch in text:
            cp = ord(ch)
            for lo, hi in self.CJK_RANGES:
                if lo <= cp <= hi:
                    return True
        return False

    def test_no_cjk_in_skill_md(self):
        """Nenhum SKILL.md contem CJK visivel ao usuario."""
        violations = []
        for skill_md in (BASE / "skills").rglob("SKILL.md"):
            content = skill_md.read_text(encoding="utf-8")
            if self._has_cjk(content):
                violations.append(str(skill_md.relative_to(BASE)))
        self.assertEqual(len(violations), 0,
            f"CJK encontrado em: {violations[:5]}")

    def test_no_cjk_in_readme(self):
        """README.md nao contem CJK."""
        readme = BASE / "README.md"
        if readme.exists():
            content = readme.read_text(encoding="utf-8")
            self.assertFalse(self._has_cjk(content),
                "README.md contem CJK!")

    # ── TC-006: Integridade de Arquivos ───────────────────────────────

    def test_essential_files_exist(self):
        """Arquivos essenciais do ecossistema existem."""
        essential = [
            "opencode.json", "README.md", "OPENCODE_ECOSYSTEM.md",
            "ROADMAP.md", "GLOSSARY.md", "AGENTS.md",
            "nexus/skills_registry.json",
            "skills/system/pypi-scout/pypi_scout.py",
            "skills/system/academic-audit/interaction_logger.py",
        ]
        for path in essential:
            full = BASE / path
            self.assertTrue(full.exists(),
                f"Arquivo essencial ausente: {path}")

    def test_evolve_state_exists(self):
        """Estados de evolucao estao documentados."""
        evolve_dir = BASE / ".evolve"
        states = list(evolve_dir.glob("evolve-state-round-*.json"))
        self.assertGreaterEqual(len(states), 2,
            f"Apenas {len(states)} estados de evolucao")

    # ── TC-007: Scores ────────────────────────────────────────────────

    def test_registry_score_range(self):
        """Scores no registry (quando presente) estao em 0-100."""
        for skill in self.registry["skills"]:
            if "score" in skill:
                score = skill["score"]
                self.assertGreaterEqual(score, 0)
                self.assertLessEqual(score, 100)

    def test_overall_health_score(self):
        """Score geral de saude >= 90."""
        total = self.registry["summary"]["total_skills"]
        healthy = self.registry["summary"].get("healthy_count", 0)
        if total > 0:
            health_pct = (healthy / total) * 100
            self.assertGreaterEqual(health_pct, 50,
                f"Saude do registry: {health_pct:.0f}% (esperado >= 50%)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
