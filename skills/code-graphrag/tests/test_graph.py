"""
TDD tests for Code GraphRAG — Builder do Grafo de Conhecimento.
CT-1: test_init — inicializacao do banco SQLite e schema
CT-2: test_insert_nodes — insercao e consulta de nos
CT-3: test_check_integrity — verificacao de integridade do grafo
CT-4: test_available — scan de agents/skills/MCPs retorna dados
"""

import os
import sys
import json
import tempfile
import pytest

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, SCRIPT_DIR)

import build_graph as bg


class TestCodeGraphRAG:

    def test_init(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            conn = bg.init_db(db_path)
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
            table_names = [t[0] for t in tables]
            assert "graph_nodes" in table_names
            assert "graph_edges" in table_names
            assert "graph_tags" in table_names
            conn.close()
        finally:
            os.unlink(db_path)

    def test_insert_nodes(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            conn = bg.init_db(db_path)
            bg.clear_db(conn)
            nodes = [
                {"id": "agent:test", "type": "agent", "name": "TestAgent",
                 "description": "Agent de teste", "path": "agents/test.md",
                 "metadata": "{}", "checksum": "abc123"},
            ]
            bg.insert_nodes(conn, nodes)
            row = conn.execute(
                "SELECT id, name FROM graph_nodes WHERE id = 'agent:test'"
            ).fetchone()
            assert row is not None
            assert row[1] == "TestAgent"
            conn.close()
        finally:
            os.unlink(db_path)

    def test_check_integrity(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            conn = bg.init_db(db_path)
            bg.clear_db(conn)
            bg.insert_nodes(conn, [
                {"id": "agent:a", "type": "agent", "name": "A",
                 "description": "Agent A", "path": "", "metadata": "{}", "checksum": ""},
                {"id": "skill:s", "type": "skill", "name": "S",
                 "description": "Skill S", "path": "", "metadata": "{}", "checksum": ""},
            ])
            bg.insert_edges(conn, [
                ("agent:a", "skill:s", "depends_on", 0.8, "{}"),
            ])
            issues, stats, by_type = bg.verify_integrity(conn)
            assert stats["total_nodes"] == 2
            assert stats["total_edges"] == 1
            conn.close()
        finally:
            os.unlink(db_path)

    def test_available(self):
        assert len(bg.REASONING_TYPES) > 0
        assert len(bg.REASONING_KEYWORDS) > 0
        assert len(bg.TOOL_MCP_MAP) > 0
        reasoning_nodes, reasoning_tags = bg.generate_reasoning_nodes()
        assert len(reasoning_nodes) > 10
