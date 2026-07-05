"""
Dependency Analyzer — Análise estática de dependências Python via AST.

Detecta:
- Importações entre módulos
- Dependências circulares
- Duplicatas funcionais
- Violações de regras de camada
- Acoplamentos que deveriam ser contratos
"""

from __future__ import annotations

import ast
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal


@dataclass
class Dependency:
    """Uma dependência entre dois módulos.

    Attributes:
        source: Módulo origem (caminho relativo)
        target: Módulo destino (caminho relativo)
        type: Tipo de dependência
        line: Linha onde ocorre
        symbol: Símbolo importado (opcional)
    """
    source: str
    target: str
    type: Literal["import", "adapter", "contract", "data"]
    line: int = 0
    symbol: str = ""


@dataclass
class Violation:
    """Violação de regra de dependência.

    Attributes:
        source: Módulo origem
        target: Módulo destino
        rule: Regra violada
        severity: gravidade
        message: Descrição
        fix: Sugestão de correção (opcional)
    """
    source: str
    target: str
    rule: str
    severity: Literal["error", "warning", "info"]
    message: str
    fix: str | None = None


class DependencyGraph:
    """Grafo canônico de dependências do ecossistema."""

    def __init__(self):
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []

    def add_node(self, node_id: str, label: str, layer: int = 0, **kwargs: Any) -> None:
        """Adiciona um nó ao grafo."""
        self.nodes[node_id] = {
            "id": node_id,
            "label": label,
            "layer": layer,
            **kwargs,
        }

    def add_edge(
        self,
        source: str,
        target: str,
        dep_type: str = "import",
        line: int = 0,
    ) -> None:
        """Adiciona uma aresta ao grafo."""
        self.edges.append({
            "source": source,
            "target": target,
            "type": dep_type,
            "line": line,
        })

    def to_dict(self) -> dict[str, Any]:
        """Serializa grafo para dict."""
        return {
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nodes": self.nodes,
            "edges": self.edges,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serializa grafo para JSON."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DependencyGraph:
        """Carrega grafo de dict."""
        g = cls()
        g.nodes = data.get("nodes", {})
        g.edges = data.get("edges", [])
        return g


class DependencyAnalyzer:
    """Analisador estático de dependências Python.

    Usa AST para detectar imports sem executar o código.
    """

    # Mapeamento de diretório para camada
    LAYER_MAP: dict[str, int] = {
        "ecosystem/commands": 6,
        "ecosystem/adapters": 5,
        "ecosystem/schemas": 4,
        "ecosystem/contracts": 3,
        "ecosystem/deps": 2,
        "ecosystem": 4,
        "menu.py": 6,
        "core": 1,
        "nexus": 0,
        "skills": 0,
        "basis-research": 0,
        "criador-artigo": 0,
        "editais-br": 0,
        "plugins": 0,
        "tests": 0,
        "quantum": 0,
    }

    # Regras: camada origem pode importar de camadas >= limite inferior
    # O limite é a própria camada (permite imports intra-pacote).
    # A restrição real: camada N não pode importar de camada < N.
    LAYER_RULES: dict[int, int] = {
        6: 6,   # commands pode importar de layer 6+
        5: 5,   # adapters pode importar de layer 5+
        4: 4,   # schemas pode importar de layer 4+
        3: 3,   # contracts pode importar de layer 3+ (stdlib + contracts)
        2: 2,   # deps pode importar de layer 2+
        1: 1,   # core pode importar de layer 1+ (stdlib)
        0: 0,   # skills/nexus pode importar de layer 0+
    }

    def __init__(self, root_path: str | None = None):
        self.root_path = Path(root_path) if root_path else Path.cwd()

    def _get_layer(self, module_path: str) -> int:
        """Determina a camada de um módulo baseado no caminho."""
        path = module_path.replace("\\", "/")
        for prefix, layer in sorted(self.LAYER_MAP.items(), key=lambda x: -len(x[0])):
            if path.startswith(prefix):
                return layer
        return 0

    def _resolve_import(
        self, module: str, current_file: str
    ) -> str | None:
        """Resolve um nome de módulo para caminho relativo."""
        # Converte notação de pacote para caminho
        module_path = module.replace(".", "/")

        # Tenta resolução direta
        candidates = [
            Path(module_path + ".py"),
            Path(module_path) / "__init__.py",
        ]

        # Verifica relativo ao arquivo atual
        current_dir = Path(current_file).parent
        for candidate in candidates:
            full = (current_dir / candidate).resolve()
            if full.exists():
                try:
                    return str(full.relative_to(self.root_path))
                except ValueError:
                    return str(full)

        # Verifica na raiz
        for candidate in candidates:
            full = self.root_path / candidate
            if full.exists():
                try:
                    return str(full.relative_to(self.root_path))
                except ValueError:
                    return str(full)

        # Tenta com diretórios conhecidos
        for base in ["core", "nexus", "ecosystem", "plugins"]:
            for candidate in candidates:
                full = self.root_path / base / candidate
                if full.exists():
                    try:
                        return str(full.relative_to(self.root_path))
                    except ValueError:
                        return str(full)

        return None

    def analyze_file(self, file_path: str) -> list[Dependency]:
        """Analisa dependências de um arquivo Python via AST.

        Args:
            file_path: Caminho do arquivo a analisar

        Returns:
            Lista de dependências encontradas
        """
        deps: list[Dependency] = []
        path = Path(file_path)

        if not path.exists():
            return deps

        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            return deps

        # Converte path para relativo
        try:
            rel_path = str(path.relative_to(self.root_path))
        except ValueError:
            rel_path = str(path)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    resolved = self._resolve_import(alias.name, file_path)
                    if resolved:
                        deps.append(Dependency(
                            source=rel_path,
                            target=resolved,
                            type="import",
                            line=node.lineno,
                            symbol=alias.name,
                        ))

            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("."):
                    # Import relativo — resolve baseado no módulo atual
                    continue

                if node.module:
                    resolved = self._resolve_import(node.module, file_path)
                    if resolved:
                        names = [n.name for n in node.names if n.name]
                        deps.append(Dependency(
                            source=rel_path,
                            target=resolved,
                            type="import",
                            line=node.lineno,
                            symbol=", ".join(names),
                        ))

        return deps

    def analyze_directory(self, path: str | None = None) -> list[Dependency]:
        """Analisa todas as dependências de um diretório.

        Args:
            path: Caminho do diretório (padrão: raiz do ecossistema)

        Returns:
            Lista completa de dependências
        """
        search_path = Path(path) if path else self.root_path
        all_deps: list[Dependency] = []

        for py_file in search_path.rglob("*.py"):
            # Tenta resolver caminho relativo; se falhar (ex: tmp_path), usa absoluto
            try:
                rel = py_file.relative_to(self.root_path)
                parts = rel.parts
            except ValueError:
                parts = py_file.parts

            if any(
                part.startswith(".") or part in ("venv", "node_modules", "__pycache__")
                for part in parts
            ):
                continue
            all_deps.extend(self.analyze_file(str(py_file)))

        return all_deps

    def detect_circular(self, deps: list[Dependency] | None = None) -> list[list[str]]:
        """Detecta dependências circulares no grafo.

        Usa DFS para encontrar ciclos.

        Args:
            deps: Lista de dependências (analisa diretório se None)

        Returns:
            Lista de ciclos encontrados (cada ciclo é uma lista de módulos)
        """
        if deps is None:
            deps = self.analyze_directory()

        # Constrói grafo de adjacência
        graph: dict[str, list[str]] = defaultdict(list)
        for d in deps:
            graph[d.source].append(d.target)

        cycles: list[list[str]] = []
        visited: set[str] = set()
        recursion_stack: set[str] = set()
        path: list[str] = []

        def dfs(node: str) -> None:
            visited.add(node)
            recursion_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in recursion_stack:
                    # Encontrou ciclo
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            path.pop()
            recursion_stack.discard(node)

        for node in list(graph.keys()):
            if node not in visited:
                dfs(node)

        return cycles

    def find_duplicates(self, directory: str | None = None) -> list[tuple[str, str, float]]:
        """Encontra arquivos duplicados por similaridade de conteúdo.

        Args:
            directory: Diretório a analisar (padrão: root)

        Returns:
            Lista de (arquivo1, arquivo2, similaridade)
        """
        search_dir = Path(directory) if directory else self.root_path
        files: list[tuple[str, str]] = []

        for py_file in search_dir.rglob("*.py"):
            try:
                rel = str(py_file.relative_to(self.root_path))
            except ValueError:
                rel = str(py_file)
            parts = Path(rel).parts
            if any(
                part.startswith(".") or part in ("venv", "node_modules", "__pycache__")
                for part in parts
            ):
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                # Usa hash das primeiras 100 linhas (ignora docstrings)
                lines = content.split("\n")
                code_lines = [l for l in lines if not l.strip().startswith(('"""', "'''", "#"))]
                sample = "\n".join(code_lines[:100])
                hash_val = hashlib.md5(sample.encode()).hexdigest()
                files.append((rel, hash_val))
            except (UnicodeDecodeError, IOError):
                continue

        # Agrupa por hash
        hash_groups: dict[str, list[str]] = defaultdict(list)
        for path_str, hash_val in files:
            hash_groups[hash_val].append(path_str)

        # Retorna grupos com mais de 1 arquivo
        duplicates: list[tuple[str, str, float]] = []
        for hash_val, paths in hash_groups.items():
            if len(paths) > 1:
                for i in range(len(paths)):
                    for j in range(i + 1, len(paths)):
                        duplicates.append((paths[i], paths[j], 1.0))

        return duplicates

    def find_dead_code(self, directory: str | None = None) -> list[dict[str, str | int]]:
        """Encontra código morto: definições não referenciadas fora do módulo.

        Varre todos os arquivos Python do diretório, coleta símbolos definidos
        em cada módulo e verifica se são importados ou referenciados por outros
        módulos.

        Args:
            directory: Diretório a analisar (padrão: root_path)

        Returns:
            Lista de dicts com 'file', 'name', 'type' (função/classe/var) e 'line'
        """
        search_dir = Path(directory) if directory else self.root_path
        # Usa o search_dir como base para caminhos relativos;
        # se directory foi fornecido explicitamente, base = search_dir,
        # senão usa self.root_path.
        base_path = search_dir if directory else self.root_path
        all_defs: dict[str, list[dict[str, str | int]]] = {}
        all_refs: set[str] = set()

        # 1ª passada: coleta definições e referências
        for py_file in search_dir.rglob("*.py"):
            try:
                rel = str(py_file.relative_to(base_path))
            except ValueError:
                continue
            parts = Path(rel).parts
            if any(
                part.startswith(".") or part in ("venv", "node_modules", "__pycache__")
                for part in parts
            ):
                continue

            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source)
            except (SyntaxError, UnicodeDecodeError, IOError):
                continue

            # Coleta definições deste módulo
            defs_here: list[dict[str, str | int]] = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    defs_here.append({
                        "file": rel,
                        "name": node.name,
                        "type": "function",
                        "line": node.lineno,
                    })
                elif isinstance(node, ast.ClassDef):
                    defs_here.append({
                        "file": rel,
                        "name": node.name,
                        "type": "class",
                        "line": node.lineno,
                    })
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            name = target.id
                            if not name.startswith("_"):
                                defs_here.append({
                                    "file": rel,
                                    "name": name,
                                    "type": "variable",
                                    "line": node.lineno,
                                })
            if defs_here:
                all_defs[rel] = defs_here

            # Coleta referências a outros módulos
            module_base = rel.replace(".py", "").replace("/", ".")
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        all_refs.add(alias.name.split(".")[0])
                        all_refs.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        parts = node.module.split(".")
                        all_refs.add(parts[0])
                        all_refs.add(node.module)
                        for alias in node.names:
                            if alias.name != "*":
                                all_refs.add(f"{node.module}.{alias.name}")
                                # Tenta com from X import Y: o símbolo Y pode ser
                                # o nome sem o prefixo do módulo
                                all_refs.add(alias.name)

        # 2ª passada: verifica quais definições são referenciadas por outros módulos
        dead: list[dict[str, str | int]] = []
        for mod_path, defs in all_defs.items():
            module_name = mod_path.replace(".py", "").replace("/", ".")
            for d in defs:
                full_name = f"{module_name}.{d['name']}"
                short_name = str(d["name"])

                # Pula dunder methods e atributos privados
                if short_name.startswith("__") or short_name.startswith("_"):
                    continue

                # Verifica se o símbolo é referenciado fora do próprio módulo
                referenced_externally = False
                for ref in all_refs:
                    # Procura: nome completo, nome curto, ou módulo.nome
                    if ref == full_name or ref == short_name:
                        referenced_externally = True
                        break
                    if ref.endswith(f".{short_name}"):
                        referenced_externally = True
                        break

                if not referenced_externally:
                    dead.append(d)

        return dead

    def _same_package(self, source: str, target: str) -> bool:
        """Verifica se source e target estão no mesmo pacote Python.

        Um __init__.py sempre pode importar de submodulos do seu pacote.
        """
        source = source.replace("\\", "/")
        target = target.replace("\\", "/")

        # Se o source é um __init__.py, extrai o diretório do pacote
        if source.endswith("__init__.py"):
            pkg_dir = source.rsplit("/", 1)[0] if "/" in source else ""
            # O target deve estar dentro do mesmo diretório do pacote
            return target.startswith(pkg_dir + "/") if pkg_dir else False

        return False

    def validate_rules(self, deps: list[Dependency] | None = None) -> list[Violation]:
        """Valida dependências contra regras de camada.

        Args:
            deps: Lista de dependências (analisa diretório se None)

        Returns:
            Lista de violações
        """
        if deps is None:
            deps = self.analyze_directory()

        violations: list[Violation] = []

        for d in deps:
            source_layer = self._get_layer(d.source)
            target_layer = self._get_layer(d.target)

            # Ignora módulos fora das camadas conhecidas
            if source_layer not in self.LAYER_RULES:
                continue
            if target_layer not in self.LAYER_RULES:
                continue

            # Exceção: __init__.py pode importar de submodulos do seu pacote
            if self._same_package(d.source, d.target):
                continue

            min_allowed = self.LAYER_RULES[source_layer]
            if target_layer < min_allowed:
                violations.append(Violation(
                    source=d.source,
                    target=d.target,
                    rule=f"layer_violation",
                    severity="error",
                    message=(
                        f"Módulo '{d.source}' (layer {source_layer}) "
                        f"importa de '{d.target}' (layer {target_layer}), "
                        f"mas layer {source_layer} só pode importar de layer ≥{min_allowed}"
                    ),
                    fix=f"Mover '{d.target}' para layer ≥{min_allowed} ou usar adapter",
                ))

        return violations

    def suggest_contract(self, dep: Dependency) -> str | None:
        """Sugere um contrato para substituir acoplamento direto.

        Args:
            dep: Dependência a analisar

        Returns:
            Nome do contrato sugerido ou None
        """
        # Se a dependência cruza camadas, sugere contrato
        source_layer = self._get_layer(dep.source)
        target_layer = self._get_layer(dep.target)

        if abs(source_layer - target_layer) >= 2:
            target_name = Path(dep.target).stem.replace("_", " ").title().replace(" ", "")
            return f"I{target_name}"

        return None

    def visualize(self, graph: DependencyGraph) -> str:
        """Gera saída Mermaid Flowchart a partir de um grafo de dependências.

        Args:
            graph: DependencyGraph a visualizar

        Returns:
            String no formato Mermaid flowchart
        """
        lines = ["flowchart LR"]
        for node_name, node_data in graph.nodes.items():
            label = node_data.get("label", node_name)
            layer = node_data.get("layer", "?")
            lines.append(f"    {node_name}[\"{label} (L{layer})\"]")
        for edge in graph.edges:
            source = edge["source"]
            target = edge["target"]
            lines.append(f"    {source} --> {target}")
        return "\n".join(lines)

    def build_graph(self, deps: list[Dependency] | None = None) -> DependencyGraph:
        """Constrói o grafo canônico de dependências.

        Args:
            deps: Lista de dependências (analisa diretório se None)

        Returns:
            DependencyGraph
        """
        if deps is None:
            deps = self.analyze_directory()

        graph = DependencyGraph()

        for d in deps:
            source_layer = self._get_layer(d.source)
            target_layer = self._get_layer(d.target)

            # Adiciona nós
            if d.source not in graph.nodes:
                label = Path(d.source).stem
                graph.add_node(d.source, label, layer=source_layer)

            if d.target not in graph.nodes:
                label = Path(d.target).stem
                graph.add_node(d.target, label, layer=target_layer)

            # Adiciona aresta
            graph.add_edge(d.source, d.target, dep_type=d.type, line=d.line)

        return graph

    def validate_all(self, directory: str | None = None) -> dict[str, Any]:
        """Validação completa: análise + regras + circulares + duplicatas.

        Returns:
            Dict com resultados consolidados
        """
        deps = self.analyze_directory(directory)
        violations = self.validate_rules(deps)
        cycles = self.detect_circular(deps)
        duplicates = self.find_duplicates(directory)

        return {
            "total_files_analyzed": len(set(d.source for d in deps)),
            "total_dependencies": len(deps),
            "violations": [
                {"source": v.source, "target": v.target, "rule": v.rule, "severity": v.severity}
                for v in violations
            ],
            "critical_violations": sum(1 for v in violations if v.severity == "error"),
            "circular_dependencies": [
                " → ".join(cycle) for cycle in cycles
            ],
            "duplicates": [
                {"file1": d[0], "file2": d[1], "similarity": d[2]}
                for d in duplicates
            ],
            "contract_suggestions": [
                {"source": d.source, "target": d.target, "suggested_contract": self.suggest_contract(d)}
                for d in deps[:20] if self.suggest_contract(d)
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
