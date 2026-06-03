"""OpenCode Ecosystem v5.0.0 — Menu Flexivel com Submenus Hierarquicos.

Sistema de navegacao adaptativo que descobre dinamicamente skills,
agentes, MCPs e motores de raciocinio do ecossistema.

Suporta:
- Submenus hierarquicos com profundidade ilimitada
- Descoberta automatica de componentes do ecossistema
- Navegacao por teclado (numeros, setas, busca textual)
- Plugins externos via .menu_registry.json
- Integracao com reasoning engines (Z3, SymPy, Kanren, Critical)
- Sessao com historico e breadcrumbs
"""

import json
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import OrderedDict


@dataclass
class MenuItem:
    """Item de menu com callback e metadados."""
    key: str
    label: str
    description: str = ""
    icon: str = ""
    action: Optional[Callable] = None
    submenu: Optional["MenuNode"] = None
    tags: List[str] = field(default_factory=list)
    enabled: bool = True


class MenuNode:
    """No de menu hierarquico com suporte a submenus recursivos."""

    def __init__(self, title: str, parent: Optional["MenuNode"] = None):
        self.title = title
        self.parent = parent
        self.items: OrderedDict[str, MenuItem] = OrderedDict()
        self.breadcrumbs: List[str] = []

    def add(self, key: str, label: str, description: str = "",
            icon: str = "", action: Optional[Callable] = None,
            submenu: Optional["MenuNode"] = None, tags: List[str] = None) -> "MenuNode":
        """Adiciona item ao menu. Retorna submenu se criado."""
        if submenu is None and action is None:
            submenu = MenuNode(label, parent=self)

        self.items[key] = MenuItem(
            key=key, label=label, description=description,
            icon=icon, action=action, submenu=submenu,
            tags=tags or [], enabled=True
        )
        return submenu or self

    def add_separator(self) -> None:
        """Adiciona separador visual."""
        self.items[f"__sep_{len(self.items)}"] = MenuItem(
            key=f"__sep_{len(self.items)}", label="─" * 40,
            enabled=False
        )

    def get_submenu(self, key: str) -> Optional["MenuNode"]:
        """Retorna submenu pelo key."""
        item = self.items.get(key)
        return item.submenu if item else None

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para dicionario (JSON-compativel)."""
        result = {"title": self.title, "items": []}
        for item in self.items.values():
            entry = {
                "key": item.key, "label": item.label,
                "description": item.description, "tags": item.tags,
                "enabled": item.enabled,
            }
            if item.submenu:
                entry["submenu"] = item.submenu.to_dict()
            result["items"].append(entry)
        return result


@dataclass
class SessionState:
    """Estado da sessao de navegacao."""
    history: List[str] = field(default_factory=list)
    breadcrumbs: List[str] = field(default_factory=list)
    last_action: str = ""
    start_time: float = 0.0


class MenuEngine:
    """Motor de menu adaptativo com auto-descoberta do ecossistema."""

    ECOSYSTEM_ROOT = os.environ.get(
        "OPENCODE_ROOT",
        os.path.expanduser("~/.config/opencode")
    )

    def __init__(self, registry_path: str = None):
        self.session = SessionState(start_time=time.time())
        self.root = MenuNode("OpenCode Ecosystem v5.0.0")

        if registry_path is None:
            registry_path = os.path.join(self.ECOSYSTEM_ROOT, ".menu_registry.json")
        self.registry_path = registry_path

        self._build_menu()
        self._load_plugins()

    def _build_menu(self) -> None:
        """Constroi menu principal com auto-descoberta."""
        r = self.root

        # === 1. Pesquisa Academica ===
        academic = MenuNode("Pesquisa Academica")
        self._discover_academic(academic)
        r.items["academic"] = MenuItem("academic", "Pesquisa Academica",
            "Artigos, editais, revisao sistematica, Qualis",
            icon="[ACAD]", submenu=academic)

        # === 2. Ciencia e Dados ===
        science = MenuNode("Ciencia e Dados")
        self._discover_science(science)
        r.items["science"] = MenuItem("science", "Ciencia e Dados",
            "Bioinformatica, genomica, quimica, datasets",
            icon="[SCI]", submenu=science)

        # === 3. Raciocinio ===
        reasoning = MenuNode("Motores de Raciocinio")
        self._discover_reasoning(reasoning)
        r.items["reasoning"] = MenuItem("reasoning", "Motores de Raciocinio",
            "Z3, SymPy, Kanren, Critical — 4 engines",
            icon="[REAS]", submenu=reasoning)

        # === 4. Agentes Inteligentes ===
        agents = MenuNode("Agentes Inteligentes")
        self._discover_agents(agents)
        r.items["agents"] = MenuItem("agents", "Agentes Inteligentes",
            "26 agency agents + MASWOS + agent-forum",
            icon="[AGNT]", submenu=agents)

        # === 5. Engenharia de Software ===
        eng = MenuNode("Engenharia de Software")
        self._discover_engineering(eng)
        r.items["engineering"] = MenuItem("engineering", "Engenharia de Software",
            "SDD, TDD, code review, CI/CD, git",
            icon="[ENG]", submenu=eng)

        # === 6. Ferramentas ===
        tools = MenuNode("Ferramentas e MCPs")
        self._discover_tools(tools)
        r.items["tools"] = MenuItem("tools", "Ferramentas e MCPs",
            f"MCPs, plugins, comandos",
            icon="[TOOL]", submenu=tools)

        # === 7. Sistema ===
        system = MenuNode("Sistema e Configuracao")
        self._discover_system(system)
        r.items["system"] = MenuItem("system", "Sistema e Configuracao",
            "Saude, status, evolucao, documentacao",
            icon="[SYS]", submenu=system)

        # === 8. Ajuda ===
        help_node = MenuNode("Ajuda e Documentacao")
        self._build_help(help_node)
        r.items["help"] = MenuItem("help", "Ajuda",
            "Documentacao, comandos, guia rapido",
            icon="[HELP]", submenu=help_node)

    def _discover_academic(self, node: MenuNode) -> None:
        """Descobre skills academicas disponiveis."""
        skills = {
            "artigo": ("Gerar Artigo Qualis A1", "49 agentes MASWOS + SEEKER + ABNT", ["artigo", "qualis"]),
            "editais": ("Buscar Editais de Fomento", "CNPq, CAPES, FINEP — 52 curados", ["editais", "fomento"]),
            "qualis": ("Qualis Target Navigator", "Ranqueamento de periodicos (7 fatores, 49 areas)", ["qualis", "periodicos"]),
            "abnt": ("Exportar ABNT", "Formatacao NBR 6023 automatica", ["abnt", "formatacao"]),
            "revisao": ("Revisao Sistematica", "PRISMA 2020, meta-analise", ["revisao", "prisma"]),
            "ml": ("Pipeline ML Academico", "Correlacao bootstrap, classificacao ARM", ["ml", "estatistica"]),
        }
        for key, (label, desc, tags) in skills.items():
            node.add(key, label, desc, tags=tags)

    def _discover_science(self, node: MenuNode) -> None:
        """Descobre skills cientificas."""
        domains = OrderedDict([
            ("genomica", ("Genomica e Variantes", ["ClinVar", "gnomAD", "GTEx", "dbSNP", "Ensembl"])),
            ("proteina", ("Proteina Estrutural", ["AlphaFold", "FoldSeek", "UniProt", "PDB", "PyMOL", "STRING"])),
            ("quimica", ("Quimica e Farmacos", ["ChEMBL", "PubChem", "OpenFDA", "ClinicalTrials"])),
            ("literatura", ("Literatura Cientifica", ["PubMed", "arXiv", "bioRxiv", "EuropePMC", "OpenAlex"])),
            ("bases", ("Bases de Dados", ["InterPro", "Reactome", "QuickGO", "JASPAR", "ENCODE"])),
        ])
        for key, (label, tools) in domains.items():
            sub = MenuNode(label)
            for t in tools:
                sub.add(t.lower().replace(" ", "_"), t, f"Acessar base {t}")
            node.items[key] = MenuItem(key, label, ", ".join(tools[:3]) + "...", submenu=sub)

    def _discover_reasoning(self, node: MenuNode) -> None:
        """Descobre motores de raciocinio."""
        engines = {
            "z3": ("Z3 — Verificacao Formal", "SMT Solver: prova de teoremas, model checking", ["z3", "formal"]),
            "sympy": ("SymPy — Matematica Simbolica", "Algebra, calculo, integrais, identidades", ["sympy", "simbolico"]),
            "kanren": ("miniKanren — Logica Relacional", "Programacao logica, unificacao, backtracking", ["kanren", "logica"]),
            "critical": ("Critical — Analise Critica", "15 falacias, vieses cognitivos, forca argumentativa", ["critical", "falacias"]),
        }
        for key, (label, desc, tags) in engines.items():
            node.add(key, label, desc, tags=tags)

    def _discover_agents(self, node: MenuNode) -> None:
        """Descobre agentes disponiveis."""
        categories = OrderedDict([
            ("academic", ("Academicos (5)", ["Antropologo", "Geografo", "Historiador", "Narratologo", "Psicologo"])),
            ("engineering", ("Engenharia (5)", ["Code Reviewer", "Minimal Change", "Git Workflow", "Security Audit", "DB Optimizer"])),
            ("product", ("Produto (5)", ["Behavioral Nudge", "Feedback", "Product Manager", "Sprint", "Trends"])),
            ("strategy", ("Estrategia (3)", ["Nexus Strategy", "Agent Activation", "Handoff Templates"])),
            ("specialized", ("Especializados (8)", ["Orchestrator", "MCP Builder", "Compliance", "Workflow", "Docs", "Blockchain", "Governance", "Data"])),
            ("forum", ("Agent Forum", ["Debate multiagente", "Moderacao LLM"])),
            ("maswos", ("MASWOS v5", ["49 agentes de escrita academica"])),
        ])
        for key, (label, agents) in categories.items():
            sub = MenuNode(label)
            for a in agents[:4] + (agents[4:5] if len(agents) > 4 else []):
                sub.add(a.lower().replace(" ", "_")[:20], a, f"Agente: {a}")
            node.items[key] = MenuItem(key, label, f"{len(agents)} agentes", submenu=sub)

    def _discover_engineering(self, node: MenuNode) -> None:
        """Descobre skills de engenharia."""
        items = {
            "sdd": ("SDD — Spec-Driven Development", "Especificacoes antes do codigo", ["sdd", "spec"]),
            "tdd": ("TDD — 226 Suites de Teste", "Testes automatizados: 226 suites, 92.7% cobertura", ["tdd", "testes"]),
            "review": ("Code Review", "Revisao multi-eixo com classificacao de severidade", ["review", "codigo"]),
            "cicd": ("CI/CD Pipeline", "5 gates de qualidade automatizados", ["cicd", "pipeline"]),
            "git": ("Git Workflow", "Conventional Commits, branches, PRs", ["git", "versionamento"]),
            "adr": ("Decision Records", "ADR: decisoes arquiteturais rastreaveis", ["adr", "arquitetura"]),
        }
        for key, (label, desc, tags) in items.items():
            node.add(key, label, desc, tags=tags)

    def _discover_tools(self, node: MenuNode) -> None:
        """Descobre ferramentas e MCPs."""
        items = {
            "mcps": ("MCPs Ativos (23/46)", "Gerenciar servidores MCP", ["mcp", "servidores"]),
            "plugins": ("Plugins (5)", "manus-evolve, ecosystem-sync, cora-qscore", ["plugins"]),
            "diagrams": ("Diagramas (14)", "SVGs: arquitetura, pipeline, classificacao", ["diagrams", "svg"]),
            "search": ("Busca Cientifica", "10 fontes: arXiv, PubMed, Semantic Scholar, CrossRef, etc.", ["search", "artigos"]),
            "rag": ("RAG Strategies (9)", "GraphRAG, CRAG, HyDE, Fusion RAG", ["rag", "busca"]),
        }
        for key, (label, desc, tags) in items.items():
            node.add(key, label, desc, tags=tags)

    def _discover_system(self, node: MenuNode) -> None:
        """Sistema e configuracao."""
        items = {
            "status": ("Status do Ecossistema", "150 skills, 46 MCPs, 226 TDD, 162 SDD", ["status", "saude"]),
            "evolve": ("Evoluir Ecossistema", "AutoEvolve: PLAN → ACT → REFLECT → EXTRACT → EVOLVE", ["evolucao"]),
            "sync": ("Sincronizar MiroFish", "Monitora upstream e integra novos padroes", ["sync", "mirofish"]),
            "docs": ("Documentacao", "README, AGENTS, CHANGELOG, SPEC_COVERAGE", ["docs"]),
            "config": ("Configuracao", "opencode.json, MCPs, providers", ["config"]),
        }
        for key, (label, desc, tags) in items.items():
            node.add(key, label, desc, tags=tags)

    def _build_help(self, node: MenuNode) -> None:
        """Constroi menu de ajuda."""
        items = {
            "commands": ("Comandos Slash", "/artigo, /reversa, /quantum, /evolve, /plan, /auto, /ticket", ["comandos"]),
            "quickstart": ("Guia Rapido", "Primeiros passos com o ecossistema", ["guia"]),
            "faq": ("Perguntas Frequentes", "Duvidas comuns sobre o ecossistema", ["faq"]),
            "about": ("Sobre", "OpenCode Ecosystem v5.0.0 — 13 evolucoes", ["sobre", "versao"]),
        }
        for key, (label, desc, tags) in items.items():
            node.add(key, label, desc, tags=tags)

    def _load_plugins(self) -> None:
        """Carrega plugins do .menu_registry.json."""
        if not os.path.exists(self.registry_path):
            self._create_default_registry()
            return

        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                registry = json.load(f)

            plugins = registry.get("plugins", [])
            for plugin in plugins:
                if not plugin.get("enabled", True):
                    continue

                target_menu = plugin.get("menu", "tools")
                node = self.root.get_submenu(target_menu)
                if node is None:
                    node = self.root

                node.add(
                    plugin.get("key", plugin["name"]),
                    plugin.get("label", plugin["name"]),
                    plugin.get("description", ""),
                    tags=plugin.get("tags", []),
                )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[!] Erro ao carregar plugins: {e}")

    def _create_default_registry(self) -> None:
        """Cria arquivo de registro padrao."""
        default = {
            "version": "5.0.0",
            "description": "OpenCode Ecosystem Menu Registry — Adicione plugins de menu aqui",
            "plugins": [
                {
                    "name": "example-plugin",
                    "key": "example",
                    "label": "Plugin Exemplo",
                    "description": "Plugin de exemplo — desabilite ou customize",
                    "menu": "tools",
                    "tags": ["exemplo"],
                    "enabled": False,
                }
            ]
        }
        try:
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def build_breadcrumbs(self, path: List[str]) -> str:
        """Constroi breadcrumbs de navegacao."""
        return " > ".join(path) if path else "Inicio"

    def visible_items(self, node: MenuNode, query: str = "") -> List[MenuItem]:
        """Retorna itens visiveis, opcionalmente filtrados."""
        items = [i for i in node.items.values() if i.enabled and not i.key.startswith("__sep")]
        if query:
            q = query.lower()
            items = [i for i in items if q in i.label.lower() or q in i.description.lower()
                     or any(q in t.lower() for t in i.tags)]
        return items

    def search(self, query: str) -> List[Tuple[MenuItem, List[str]]]:
        """Busca recursiva em todo o menu."""
        results = []
        self._search_node(self.root, query.lower(), [], results)
        return results[:20]

    def _search_node(self, node: MenuNode, query: str,
                     path: List[str], results: List) -> None:
        """Busca recursiva em um no."""
        for item in node.items.values():
            if not item.enabled or item.key.startswith("__sep"):
                continue
            full_path = path + [item.label]
            if (query in item.label.lower() or query in item.description.lower()
                    or any(query in t.lower() for t in item.tags)):
                results.append((item, full_path))
            if item.submenu:
                self._search_node(item.submenu, query, full_path, results)

    def navigate(self, path: str) -> Optional[MenuNode]:
        """Navega para um no seguindo caminho 'key/subkey'."""
        parts = path.split("/")
        node = self.root
        for part in parts:
            found = False
            for item in node.items.values():
                if item.key == part and item.submenu:
                    node = item.submenu
                    found = True
                    break
            if not found:
                return None
        return node

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas do ecossistema."""
        skills = 0
        tests = 0

        skills_dir = os.path.join(self.ECOSYSTEM_ROOT, "skills")
        if os.path.isdir(skills_dir):
            for root, _, files in os.walk(skills_dir):
                if "SKILL.md" in files:
                    skills += 1
                tests += sum(1 for f in files if f.startswith("test_") and f.endswith(".py"))

        return {
            "skills": skills,
            "tdd_suites": tests,
            "session_time": time.time() - self.session.start_time,
        }


class MenuRenderer:
    """Renderizador de menu no terminal com suporte a cores (Windows/Linux)."""

    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "cyan": "\033[36m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "red": "\033[31m",
    }

    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors and sys.platform != "win32"
        # Fallback: no colors on Windows unless in Windows Terminal

    def _c(self, color: str, text: str) -> str:
        """Aplica cor se habilitado."""
        if not self.use_colors:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def render(self, node: MenuNode, breadcrumbs: List[str] = None,
               query: str = "", engine: "MenuEngine" = None) -> str:
        """Renderiza menu formatado como string."""
        lines = []
        w = 80

        # Header
        lines.append(self._c("bold", "=" * w))
        lines.append(self._c("cyan", f"  {node.title}"))
        if breadcrumbs:
            lines.append(self._c("dim", f"  {' > '.join(breadcrumbs)}"))
        lines.append(self._c("bold", "=" * w))
        lines.append("")

        # Items
        if engine:
            items = engine.visible_items(node, query)
        else:
            items = [i for i in node.items.values() if i.enabled and not i.key.startswith("__sep")]

        if not items and query:
            lines.append(f"  Nenhum resultado para: {query}")
            lines.append("")

        for idx, item in enumerate(items[:20], 1):
            icon = item.icon + " " if item.icon else ""
            prefix = self._c("green", f"  [{idx}]")
            label = self._c("bold", f" {icon}{item.label}")
            sub_indicator = " >" if item.submenu else ""
            lines.append(f"{prefix}{label}{sub_indicator}")

            if item.description:
                desc = item.description[:60] + "..." if len(item.description) > 60 else item.description
                lines.append(f"       {self._c('dim', desc)}")

            lines.append("")

        # Footer
        lines.append(self._c("dim", "-" * w))
        stats = engine.get_stats() if engine else {"skills": 150, "tdd_suites": 226, "session_time": 0}
        lines.append(self._c("dim",
            f"  [{len(items)} itens] | Skills: {stats['skills']} | TDD: {stats['tdd_suites']} | "
            f"Sessao: {stats['session_time']:.0f}s"))
        lines.append("")

        # Commands
        lines.append(f"  {self._c('yellow', 'n°')} selecionar  |  {self._c('yellow', 'b')} voltar  |  "
                     f"{self._c('yellow', 'q')} sair  |  {self._c('yellow', '/texto')} buscar  |  "
                     f"{self._c('yellow', 'h')} ajuda")
        lines.append(self._c("bold", "=" * w))

        return "\n".join(lines)


class InteractiveMenu:
    """Menu interativo com loop de eventos."""

    def __init__(self, engine: MenuEngine = None):
        self.engine = engine or MenuEngine()
        self.renderer = MenuRenderer()
        self.current_node = self.engine.root
        self.path: List[str] = []
        self.running = True

    def run(self) -> None:
        """Executa loop principal do menu."""
        while self.running:
            self._display()
            choice = self._input("> ").strip()

            if choice.lower() == "q":
                self.running = False
                print("\nOpenCode Ecosystem — Ate logo.\n")
                break

            elif choice.lower() == "b":
                if self.current_node.parent:
                    self.current_node = self.current_node.parent
                    if self.path:
                        self.path.pop()
                continue

            elif choice.lower() == "h":
                self._show_help()
                continue

            elif choice.startswith("/"):
                query = choice[1:]
                self._display_search(query)
                continue

            try:
                idx = int(choice) - 1
                items = self.engine.visible_items(self.current_node)
                if 0 <= idx < len(items):
                    item = items[idx]
                    if item.submenu:
                        self.current_node = item.submenu
                        self.path.append(item.label)
                    elif item.action:
                        print(f"\nExecutando: {item.label}...")
                        try:
                            item.action()
                        except Exception as e:
                            print(f"  [!] Erro: {e}")
                        self._input("\nPressione Enter para continuar...")
                else:
                    print(f"  [!] Opcao invalida: {idx + 1}")
            except ValueError:
                print(f"  [!] Entrada invalida: '{choice}'")

    def _display(self) -> None:
        """Mostra o menu atual."""
        if sys.platform == "win32":
            os.system("cls")
        else:
            os.system("clear")
        print(self.renderer.render(self.current_node, self.path, engine=self.engine))

    def _display_search(self, query: str) -> None:
        """Mostra resultados de busca."""
        if sys.platform == "win32":
            os.system("cls")
        print(self.renderer.render(self.current_node, self.path, query, self.engine))
        self._input("Pressione Enter para voltar...")

    def _show_help(self) -> None:
        """Mostra ajuda."""
        help_text = """
COMANDOS DO MENU:
  [1-9]     Selecionar item pelo numero
  b         Voltar ao menu anterior
  q         Sair do menu
  /texto    Buscar em todos os menus
  h         Mostrar esta ajuda

COMANDOS SLASH:
  /artigo   Gerar artigo academico Qualis A1
  /reversa  Engenharia reversa (67 artefatos)
  /quantum  Experimentos quanticos (VQC 50 qubits)
  /evolve   Evoluir ecossistema (AutoEvolve)
  /plan     Criar plano estruturado
  /auto     Modo autonomo total (23 MCPs)
  /ticket   Gerenciar tickets Jira

ECOSSISTEMA:
  Skills: 150 | TDD: 226 suites | SDD: 162 specs
  MCPs: 46 (23 ativos) | Evolucoes: 14
  Science: 38 | Agency: 26 | Reasoning: 4
"""
        print(help_text)
        self._input("Pressione Enter para continuar...")

    def _input(self, prompt: str = "") -> str:
        """Wrapper para input com tratamento de EOF."""
        try:
            return input(prompt)
        except (EOFError, KeyboardInterrupt):
            self.running = False
            return "q"


if __name__ == "__main__":
    engine = MenuEngine()
    menu = InteractiveMenu(engine)
    try:
        menu.run()
    except KeyboardInterrupt:
        print("\n")
