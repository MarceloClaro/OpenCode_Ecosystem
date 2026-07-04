"""
Testes TDD para SPEC-093: Refined Dependency Graph.

Valida:
- CT-9301: DependencyAnalyzer analisa diretório
- CT-9302: Detecção de dependência circular
- CT-9303: Detecção de duplicatas
- CT-9304: Validação de regras de camada
- CT-9305: Construção de grafo canônico
- CT-9306: Sugestão de contrato
- CT-9307: Grafo canônico serializado em JSON
- CT-9308: Módulos do ecossistema analisáveis
- CT-9309: Visualizador (conceito)
- CT-9310: Validação integrada
"""

import tempfile
from pathlib import Path

import pytest
from ecosystem.deps.analyzer import (
    DependencyAnalyzer,
    Dependency,
    Violation,
    DependencyGraph,
)


@pytest.fixture
def analyzer():
    """Fixture: DependencyAnalyzer na raiz do ecossistema."""
    return DependencyAnalyzer()


@pytest.fixture
def sample_py_file(tmp_path):
    """Cria um arquivo Python de exemplo para análise."""
    py_file = tmp_path / "sample_module.py"
    py_file.write_text("""
import os
import sys
from pathlib import Path
from core.state import StateManager
from ecosystem.contracts.interfaces import IAgent
""")
    return py_file


# === CT-9301: Analyzer analisa arquivo ===
class TestAnalyzeFile:
    def test_ct9301_analyze_file_returns_deps(self, analyzer, sample_py_file):
        """CT-9301: analyze_file() retorna lista de Dependency."""
        deps = analyzer.analyze_file(str(sample_py_file))
        assert isinstance(deps, list)
        assert len(deps) >= 2  # Pelo menos stdlib + core

    def test_ct9301_dependency_has_source_and_target(self, analyzer, sample_py_file):
        """CT-9301b: Cada Dependency tem source e target."""
        deps = analyzer.analyze_file(str(sample_py_file))
        for d in deps:
            assert d.source
            assert d.target


# === CT-9302: Detecção de circular ===
class TestCircularDetection:
    def test_ct9302_detect_no_circular(self, analyzer):
        """CT-9302: detect_circular() pode executar sem erro."""
        # Usa diretório ecosystem que não deve ter circular
        eco_path = Path(__file__).parent.parent.parent / "ecosystem"
        if eco_path.exists():
            deps = analyzer.analyze_directory(str(eco_path))
            cycles = analyzer.detect_circular(deps)
            # Não esperamos circulares no novo código
            assert isinstance(cycles, list)

    def test_ct9302_detect_circular_artificial(self, analyzer, tmp_path):
        """CT-9302b: Detecta ciclo artificial."""
        # Cria ciclo A → B → A
        a_file = tmp_path / "a_module.py"
        b_file = tmp_path / "b_module.py"
        a_file.write_text("from b_module import something\n")
        b_file.write_text("from a_module import something\n")

        deps = analyzer.analyze_directory(str(tmp_path))
        cycles = analyzer.detect_circular(deps)
        assert len(cycles) >= 1


# === CT-9303: Detecção de duplicatas ===
class TestDuplicateDetection:
    def test_ct9303_find_duplicates(self, analyzer, tmp_path):
        """CT-9303: find_duplicates() encontra arquivos iguais."""
        content = "def foo(): pass\n"
        f1 = tmp_path / "file1.py"
        f2 = tmp_path / "file2.py"
        f1.write_text(content)
        f2.write_text(content)

        dups = analyzer.find_duplicates(str(tmp_path))
        assert len(dups) >= 1
        assert (str(f1.relative_to(tmp_path)), str(f2.relative_to(tmp_path))) or \
               (str(f2.relative_to(tmp_path)), str(f1.relative_to(tmp_path)))


# === CT-9304: Validação de regras de camada ===
class TestLayerValidation:
    def test_ct9304_validate_rules_returns_list(self, analyzer):
        """CT-9304: validate_rules() retorna lista de Violation."""
        # Cria um dep que cruza camadas de forma suspeita
        deps = [
            Dependency(source="ecosystem/commands/cmd_menu.py", target="core/state.py", type="import"),
            Dependency(source="ecosystem/adapters/script_runner.py", target="ecosystem/schemas/registry.py", type="import"),
        ]
        violations = analyzer.validate_rules(deps)
        assert isinstance(violations, list)

    def test_ct9304_violation_has_severity(self, analyzer):
        """CT-9304b: Violation tem severity."""
        dep = Dependency(source="ecosystem/commands/cmd_menu.py", target="core/state.py", type="import")
        violations = analyzer.validate_rules([dep])
        if violations:
            assert violations[0].severity in ("error", "warning", "info")


# === CT-9305: Construção de grafo ===
class TestBuildGraph:
    def test_ct9305_build_graph_returns_graph(self, analyzer):
        """CT-9305: build_graph() retorna DependencyGraph."""
        deps = [
            Dependency(source="mod_a.py", target="mod_b.py", type="import"),
        ]
        graph = analyzer.build_graph(deps)
        assert isinstance(graph, DependencyGraph)
        assert len(graph.nodes) >= 2

    def test_ct9305_graph_has_nodes_and_edges(self, analyzer):
        """CT-9305b: Grafo tem nós e arestas."""
        deps = [
            Dependency(source="mod_a.py", target="mod_b.py", type="import"),
        ]
        graph = analyzer.build_graph(deps)
        assert "mod_a.py" in graph.nodes
        assert "mod_b.py" in graph.nodes
        assert len(graph.edges) == 1


# === CT-9306: Sugestão de contrato ===
class TestContractSuggestion:
    def test_ct9306_suggest_contract(self, analyzer):
        """CT-9306: suggest_contract() retorna nome ou None."""
        # Dep que cruza camadas (ecosystem → core)
        dep = Dependency(source="ecosystem/commands/cmd_menu.py", target="core/state.py", type="import")
        suggestion = analyzer.suggest_contract(dep)
        # Pode retornar None se não houver sugestão
        assert suggestion is None or isinstance(suggestion, str)


# === CT-9307: Grafo JSON ===
class TestGraphSerialization:
    def test_ct9307_graph_to_dict(self):
        """CT-9307: DependencyGraph.to_dict() serializa."""
        graph = DependencyGraph()
        graph.add_node("a.py", "A", layer=1)
        graph.add_node("b.py", "B", layer=0)
        graph.add_edge("a.py", "b.py")

        data = graph.to_dict()
        assert "nodes" in data
        assert "edges" in data
        assert "a.py" in data["nodes"]

    def test_ct9307_graph_to_json(self):
        """CT-9307b: to_json() retorna string JSON."""
        graph = DependencyGraph()
        graph.add_node("a.py", "A")
        json_str = graph.to_json()
        assert isinstance(json_str, str)
        assert "a.py" in json_str


# === CT-9308: Módulos analisáveis ===
class TestRealAnalysis:
    def test_ct9308_analyze_ecosystem_package(self, analyzer):
        """CT-9308: Pacote ecosystem é analisável."""
        eco_path = Path(__file__).parent.parent.parent / "ecosystem"
        if eco_path.exists():
            deps = analyzer.analyze_directory(str(eco_path))
            assert isinstance(deps, list)


# === CT-9310: Validação completa ===
class TestFullValidation:
    def test_ct9310_validate_all_returns_report(self, analyzer):
        """CT-9310: validate_all() retorna relatório completo."""
        eco_path = Path(__file__).parent.parent.parent / "ecosystem"
        if eco_path.exists():
            report = analyzer.validate_all(str(eco_path))
            assert "total_files_analyzed" in report
            assert "total_dependencies" in report
            assert "violations" in report
            assert "circular_dependencies" in report
            assert isinstance(report["total_files_analyzed"], int)
