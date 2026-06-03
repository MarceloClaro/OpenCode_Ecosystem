"""TDD Tests for OpenCode Menu System v5.0.0."""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from menu import MenuEngine, MenuNode, MenuItem, MenuRenderer, InteractiveMenu, SessionState


class TestMenuNode:
    """Testes para MenuNode — estrutura hierarquica."""

    def setup_method(self):
        self.root = MenuNode("Root")

    def test_create_node(self):
        assert self.root.title == "Root"
        assert self.root.parent is None
        assert len(self.root.items) == 0

    def test_add_item(self):
        self.root.add("test", "Test Item", "A test item")
        assert "test" in self.root.items
        assert self.root.items["test"].label == "Test Item"
        assert self.root.items["test"].description == "A test item"

    def test_add_creates_submenu(self):
        submenu = self.root.add("sub", "Sub Menu")
        assert submenu is not None
        assert isinstance(submenu, MenuNode)
        assert self.root.items["sub"].submenu is submenu

    def test_add_with_action(self):
        called = []
        def action():
            called.append(True)
        self.root.add("act", "Action Item", action=action)
        self.root.items["act"].action()
        assert len(called) == 1

    def test_get_submenu(self):
        sub = self.root.add("s", "Sub")
        found = self.root.get_submenu("s")
        assert found is sub

    def test_get_submenu_nonexistent(self):
        assert self.root.get_submenu("nope") is None

    def test_to_dict(self):
        self.root.add("a", "Alpha", "First")
        self.root.add("b", "Beta", "Second")
        d = self.root.to_dict()
        assert d["title"] == "Root"
        assert len(d["items"]) == 2
        assert d["items"][0]["key"] == "a"

    def test_visible_items_excludes_separators(self):
        self.root.add("a", "A")
        self.root.add_separator()
        self.root.add("b", "B")
        engine = MenuEngine.__new__(MenuEngine)
        visible = engine.visible_items(self.root)
        assert len(visible) == 2


class TestMenuEngine:
    """Testes para MenuEngine — descoberta e navegacao."""

    def setup_method(self):
        self.engine = MenuEngine()

    def test_engine_initializes(self):
        assert self.engine.root is not None
        assert len(self.engine.root.items) > 0
        assert isinstance(self.engine.session, SessionState)

    def test_root_has_all_categories(self):
        expected = ["academic", "science", "reasoning", "agents",
                     "engineering", "tools", "system", "help"]
        for key in expected:
            assert key in self.engine.root.items, f"Missing category: {key}"

    def test_academic_submenu(self):
        academic = self.engine.root.get_submenu("academic")
        assert academic is not None
        items = self.engine.visible_items(academic)
        assert len(items) >= 4

    def test_science_submenu(self):
        science = self.engine.root.get_submenu("science")
        assert science is not None
        items = self.engine.visible_items(science)
        assert len(items) >= 4

    def test_reasoning_has_4_engines(self):
        reasoning = self.engine.root.get_submenu("reasoning")
        items = self.engine.visible_items(reasoning)
        engine_keys = [i.key for i in items]
        for e in ["z3", "sympy", "kanren", "critical"]:
            assert e in engine_keys, f"Missing engine: {e}"

    def test_navigate_valid_path(self):
        node = self.engine.navigate("reasoning")
        assert node is not None
        assert "Motores" in node.title or "Raciocinio" in node.title

    def test_navigate_invalid_path(self):
        node = self.engine.navigate("nonexistent/deep/path")
        assert node is None

    def test_search_finds_results(self):
        results = self.engine.search("z3")
        assert len(results) > 0

    def test_search_no_results(self):
        results = self.engine.search("xyznonexistent123")
        assert len(results) == 0

    def test_stats(self):
        stats = self.engine.get_stats()
        assert "skills" in stats
        assert "tdd_suites" in stats
        assert stats["skills"] >= 0

    def test_build_breadcrumbs(self):
        crumbs = self.engine.build_breadcrumbs(["Home", "Science", "Genomica"])
        assert "Home" in crumbs
        assert "Genomica" in crumbs

    def test_visible_items_with_query(self):
        node = self.engine.root.get_submenu("reasoning")
        items = self.engine.visible_items(node, "z3")
        assert len(items) == 1
        assert items[0].key == "z3"

    def test_menu_registry_created(self):
        registry = os.path.join(tempfile.gettempdir(), "test_menu_registry.json")
        engine = MenuEngine(registry_path=registry)
        assert os.path.exists(registry)
        with open(registry) as f:
            data = json.load(f)
        assert "plugins" in data
        os.remove(registry)

    def test_invalid_registry_handled(self):
        registry = os.path.join(tempfile.gettempdir(), "bad_registry.json")
        with open(registry, "w") as f:
            f.write("not json")
        engine = MenuEngine(registry_path=registry)
        assert engine.root is not None
        os.remove(registry)


class TestMenuRenderer:
    """Testes para renderizacao."""

    def setup_method(self):
        self.engine = MenuEngine()
        self.renderer = MenuRenderer(use_colors=False)

    def test_render_root(self):
        output = self.renderer.render(self.engine.root, engine=self.engine)
        assert "OpenCode" in output
        assert "Pesquisa Academica" in output
        assert "sair" in output.lower() or "q" in output

    def test_render_submenu(self):
        node = self.engine.root.get_submenu("reasoning")
        output = self.renderer.render(node, ["Raciocinio"], engine=self.engine)
        assert "Z3" in output
        assert "SymPy" in output

    def test_render_with_query(self):
        node = self.engine.root.get_submenu("science")
        output = self.renderer.render(node, ["Ciencia"], "alphafold", self.engine)
        assert "AlphaFold" in output.upper() or "alphafold" in output.lower()


class TestInteractiveMenu:
    """Testes para o menu interativo (sem I/O real)."""

    def setup_method(self):
        self.engine = MenuEngine()
        self.menu = InteractiveMenu(self.engine)

    def test_init(self):
        assert self.menu.engine is self.engine
        assert self.menu.current_node is self.engine.root
        assert self.menu.running is True

    def test_show_help(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "")
        self.menu._show_help()
        assert True


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
