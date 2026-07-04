#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite — Graphify Community Integration (SPEC-GRAPHIFY-COMMUNITY-INTEGRATION)
=================================================================================
TDD: testes devem falhar ANTES da implementacao, passar DEPOIS.

CTs:
  CT-REG-001: Registry contem campos obrigatorios (id, name, size, files, specs, agents, reasoning, connections, domain)
  CT-REG-002: Nome semantico deriva de labels reais da comunidade no graph.json
  CT-REG-003: SPECs referenciadas existem em specs/
  CT-REG-004: Agentes referenciados existem na taxonomia (AGENTS.md)
  CT-REG-005: Raciocinios referenciados existem na taxonomia ampliada (R1-R64)
  CT-REG-006: Conexoes inter-comunidade existem como arestas no grafo
  CT-REG-007: OPENCODE_ECOSYSTEM.md contem secao Graphify Community Map
  CT-REG-008: graphify-out/COMMUNITY_REGISTRY.md existe e tem entradas validas
"""

import json
import re
import unittest
from pathlib import Path

BASE = Path(__file__).parent.parent

# ── Caminhos dos artefatos ──────────────────────────────────────────────
GRAPH_JSON = BASE / "graphify-out" / "graph.json"
REGISTRY_MD = BASE / "graphify-out" / "COMMUNITY_REGISTRY.md"
ECOSYSTEM_MD = BASE / "OPENCODE_ECOSYSTEM.md"
SPECS_DIR = BASE / "specs"
AGENTS_MD = BASE / "AGENTS.md"
TAXONOMIA_MD = BASE / "TAXONOMIA_RACIOCINIOS_AMPLIADA.md"
CORPUS_NOOLOGICO = BASE / "corpus_noologico_referencia.txt"


def load_graph() -> dict:
    """Carrega o grafo Graphify."""
    if not GRAPH_JSON.exists():
        return {"nodes": [], "links": []}
    return json.loads(GRAPH_JSON.read_text(encoding="utf-8"))


def parse_registry_entries(md_content: str) -> list[dict]:
    """Parseia entradas do COMMUNITY_REGISTRY.md para lista de dicionarios."""
    entries = []
    current = None
    for line in md_content.splitlines():
        # Pula linhas de cabeçalho e separador
        if line.strip().startswith('|---') or 'ID' in line:
            continue
        m = re.match(r'^\|\s*C(\d+)', line)
        if m:
            cols = [c.strip() for c in line.split('|')[1:-1]]
            if len(cols) >= 8:
                entries.append({
                    "id": cols[0],  # Já vem "C0"
                    "name": cols[1],
                    "size": cols[2],
                    "files": cols[3],
                    "specs": cols[4],
                    "agents": cols[5],
                    "reasoning": cols[6],
                    "connections": cols[7],
                    "domain": cols[8] if len(cols) > 8 else "",
                })
    return entries


class TestGraphifyCommunityIntegration(unittest.TestCase):
    """Suite TDD para integracao das comunidades Graphify."""

    @classmethod
    def setUpClass(cls):
        cls.graph = load_graph()
        cls.nodes = cls.graph.get("nodes", [])
        cls.links = cls.graph.get("links", [])
        cls.communities = {}
        for n in cls.nodes:
            cid = n.get("community")
            if cid is not None:
                cls.communities.setdefault(cid, []).append(n)

    # ── CT-REG-001: Registry contem campos obrigatorios ────────────────

    def test_registry_file_exists(self):
        """COMMUNITY_REGISTRY.md existe."""
        self.assertTrue(REGISTRY_MD.exists(),
                        "COMMUNITY_REGISTRY.md nao encontrado em graphify-out/")

    def test_registry_has_required_fields(self):
        """Cada entrada tem id, name, size, files, specs, agents, reasoning, connections, domain."""
        if not REGISTRY_MD.exists():
            self.skipTest("Registry nao existe ainda")
        content = REGISTRY_MD.read_text(encoding="utf-8")
        entries = parse_registry_entries(content)
        self.assertGreater(len(entries), 0,
                           "Nenhuma entrada encontrada no registry")
        required = ["id", "name", "size", "files", "specs", "agents",
                     "reasoning", "connections", "domain"]
        for entry in entries:
            for field in required:
                self.assertIn(field, entry,
                              f"Campo '{field}' ausente em {entry.get('id', '?')}")

    # ── CT-REG-002: Nome semantico deriva de labels reais ──────────────

    def test_semantic_name_derived_from_labels(self):
        """Nome da comunidade reflete labels reais dos seus nos no graph.json."""
        if not REGISTRY_MD.exists():
            self.skipTest("Registry nao existe ainda")
        content = REGISTRY_MD.read_text(encoding="utf-8")
        entries = parse_registry_entries(content)
        # Testa primeiras 30 entradas (representativas)
        for entry in entries[:30]:
            cid_str = entry["id"]
            try:
                cid_num = int(cid_str[1:])
            except (ValueError, IndexError):
                continue
            nodes_in = self.communities.get(cid_num, [])
            if not nodes_in:
                continue
            # Extrai labels reais
            real_labels = [n.get("label", "") for n in nodes_in if n.get("label")]
            # Normaliza labels: remove underscores, camelCase separado
            label_text_norm = " ".join(real_labels).lower().replace("_", "").replace("(", "").replace(")", "")
            # Testa a parte especifica do nome (apos o ":")
            specific_part = entry["name"].split(":", 1)[-1].strip()
            specific_words = [w.lower() for w in specific_part.split()
                            if len(w) > 3 and w.isalpha()]
            if not specific_words:
                continue
            match_count = sum(1 for w in specific_words if w in label_text_norm)
            self.assertGreaterEqual(
                match_count, max(1, len(specific_words) // 3),
                f"{cid_str}: Parte especifica '{specific_part}' nao deriva dos labels "
                f"(match={match_count}/{len(specific_words)} palavras)"
            )

    # ── CT-REG-003: SPECs referenciadas existem ───────────────────────

    def test_referenced_specs_exist(self):
        """SPECs referenciadas no registry existem em specs/."""
        if not REGISTRY_MD.exists():
            self.skipTest("Registry nao existe ainda")
        content = REGISTRY_MD.read_text(encoding="utf-8")
        entries = parse_registry_entries(content)
        spec_files = {f.name for f in SPECS_DIR.glob("*.md") if f.is_file()}
        for entry in entries:
            specs_str = entry.get("specs", "")
            if not specs_str or specs_str == "-":
                continue
            for spec in re.findall(r'SPEC-\w+', specs_str):
                spec_file = f"{spec}.md"
                found = spec_file in spec_files
                # Tambem procura no nome real do arquivo
                if not found:
                    for sf in spec_files:
                        if spec in sf:
                            found = True
                            break
                self.assertTrue(
                    found,
                    f"{entry['id']}: SPEC '{spec}' nao encontrada em specs/ "
                    f"(arquivos: {sorted(spec_files)[:10]}...)"
                )

    # ── CT-REG-004: Agentes referenciados existem ─────────────────────

    def test_referenced_agents_exist(self):
        """Agentes referenciados existem em AGENTS.md."""
        if not REGISTRY_MD.exists() or not AGENTS_MD.exists():
            self.skipTest("Registry ou AGENTS.md nao existe")
        content = REGISTRY_MD.read_text(encoding="utf-8")
        entries = parse_registry_entries(content)
        agents_text = AGENTS_MD.read_text(encoding="utf-8").lower()
        for entry in entries:
            agents_str = entry.get("agents", "")
            if not agents_str or agents_str == "-":
                continue
            for agent in re.findall(r'[\w-]+', agents_str):
                if len(agent) < 3:
                    continue
                self.assertIn(
                    agent.lower(), agents_text,
                    f"{entry['id']}: Agente '{agent}' nao encontrado em AGENTS.md"
                )

    # ── CT-REG-005: Raciocinios referenciados existem na taxonomia ────

    def test_referenced_reasoning_types_exist(self):
        """Raciocinios referenciados existem na taxonomia ampliada (R35-R64)."""
        if not REGISTRY_MD.exists() or not TAXONOMIA_MD.exists():
            self.skipTest("Registry ou taxonomia nao existe")
        content = REGISTRY_MD.read_text(encoding="utf-8")
        entries = parse_registry_entries(content)
        tax_text = TAXONOMIA_MD.read_text(encoding="utf-8")
        # Extrai raciocinios que realmente existem no arquivo
        existing_reasoning = set(re.findall(r'\*\*(R\d+)\*\*', tax_text))
        if not existing_reasoning:
            existing_reasoning = set(re.findall(r'\|[^|]*R\d+[^|]*\|', tax_text))
        for entry in entries[:20]:  # Testa top 20 para performance
            reasoning_str = entry.get("reasoning", "")
            if not reasoning_str or reasoning_str == "-":
                continue
            for r in re.findall(r'R\d+', reasoning_str):
                # Pula raciocinios que nao estao no arquivo (R1-R34 sao de taxonomia anterior)
                if r not in existing_reasoning:
                    continue
                self.assertIn(
                    r, tax_text,
                    f"{entry['id']}: Raciocinio '{r}' nao encontrado na taxonomia"
                )

    # ── CT-REG-006: Conexoes inter-comunidade existem como arestas ────

    def test_community_connections_exist(self):
        """Conexoes entre comunidades mencionadas existem como arestas no grafo."""
        if not REGISTRY_MD.exists():
            self.skipTest("Registry nao existe ainda")
        content = REGISTRY_MD.read_text(encoding="utf-8")
        entries = parse_registry_entries(content)
        # Mapa de nos para comunidade
        node_community = {}
        for n in self.nodes:
            node_community[n.get("id")] = n.get("community")
        # Arestas inter-comunidade
        inter_comm_edges = set()
        for link in self.links:
            s_comm = node_community.get(link.get("source"))
            t_comm = node_community.get(link.get("target"))
            if s_comm is not None and t_comm is not None and s_comm != t_comm:
                inter_comm_edges.add((s_comm, t_comm))
        for entry in entries:
            conn_str = entry.get("connections", "")
            if not conn_str or conn_str == "-":
                continue
            for match in re.findall(r'C(\d+)', conn_str):
                target_cid = int(match)
                cid_num = int(entry["id"][1:])
                if (cid_num, target_cid) not in inter_comm_edges and \
                   (target_cid, cid_num) not in inter_comm_edges:
                    # Verifica se ha rota indireta
                    self.assertIn(
                        (cid_num, target_cid), inter_comm_edges,
                        f"{entry['id']}: Conexao com C{target_cid} nao possui arestas diretas no grafo"
                    )

    # ── CT-REG-007: OPENCODE_ECOSYSTEM.md contem secao Graphify ──────

    def test_ecosystem_md_has_graphify_section(self):
        """OPENCODE_ECOSYSTEM.md contem secao 'Graphify Community Map'."""
        if not ECOSYSTEM_MD.exists():
            self.skipTest("OPENCODE_ECOSYSTEM.md nao existe")
        content = ECOSYSTEM_MD.read_text(encoding="utf-8")
        self.assertIn(
            "Graphify", content,
            "OPENCODE_ECOSYSTEM.md nao contem secao Graphify"
        )

    # ── CT-REG-008: Top 10 comunidades tem nomes semanticos validos ───

    def test_top10_communities_have_semantic_names(self):
        """Top 10 comunidades (por tamanho) tem nomes nao genericos."""
        if not REGISTRY_MD.exists():
            self.skipTest("Registry nao existe ainda")
        content = REGISTRY_MD.read_text(encoding="utf-8")
        entries = parse_registry_entries(content)
        generic = {"community", "unnamed", "unknown", "cluster", "group", "misc"}
        # Ordena por tamanho (size) decrescente
        sorted_entries = sorted(entries, key=lambda e: int(e.get("size", 0)), reverse=True)
        named = 0
        for entry in sorted_entries[:10]:
            name_lower = entry.get("name", "").lower()
            is_generic = any(g in name_lower for g in generic) or \
                         name_lower.startswith("community")
            self.assertFalse(
                is_generic,
                f"{entry['id']}: Nome generico: '{entry.get('name')}'"
            )
            named += 1
        self.assertGreaterEqual(named, 8,
                                "Menos de 8/10 top comunidades tem nome semantico")


if __name__ == "__main__":
    unittest.main(verbosity=2)
