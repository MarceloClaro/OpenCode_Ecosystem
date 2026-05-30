#!/usr/bin/env python3
"""
OpenCode PyPI Scout — Buscador inteligente de bibliotecas Python para o ecossistema OpenCode.

Busca bibliotecas no PyPI, compara com o catálogo curado do ecossistema,
sugere instalação com pip e exibe afinidade com componentes do OpenCode.

Usage:
    python pypi_scout.py search <termo>       # Busca no PyPI
    python pypi_scout.py catalog              # Lista catálogo curado
    python pypi_scout.py category <nome>      # Filtra por categoria
    python pypi_scout.py install <pacote>     # Instala via pip
    python pypi_scout.py recommend <pipeline> # Recomenda pacotes para um pipeline
    python pypi_scout.py diff <pacote>        # Mostra diferenças entre versões do catálogo e PyPI
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# ── Constantes ──────────────────────────────────────────────────────────

CATALOG_PATH = Path(__file__).parent / "opencode_catalog.json"
PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"
REQUEST_TIMEOUT = 15  # segundos

# ── Dataclasses ─────────────────────────────────────────────────────────


@dataclass
class PyPIPackage:
    """Representa um pacote do PyPI com metadados essenciais."""

    name: str
    version: str
    summary: str
    description: str = ""
    author: str = ""
    license_info: str = ""
    requires_python: str = ""
    home_page: str = ""
    project_url: str = ""
    keywords: str = ""
    classifiers: list[str] = field(default_factory=list)
    install_command: str = ""

    def __post_init__(self) -> None:
        if not self.install_command:
            self.install_command = f"pip install {self.name}"


@dataclass
class CatalogPackage:
    """Representa um pacote do catálogo curado OpenCode."""

    name: str
    version: str
    description: str
    install: str
    docs_url: str
    affinity: dict[str, float]
    requires_python: str
    license_info: str
    ecosystem_integration: str = ""
    note: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CatalogPackage:
        return cls(
            name=data.get("name", ""),
            version=data.get("version", "unknown"),
            description=data.get("description", ""),
            install=data.get("install", ""),
            docs_url=data.get("docs_url", ""),
            affinity=data.get("affinity", {}),
            requires_python=data.get("requires_python", ""),
            license_info=data.get("license", ""),
            ecosystem_integration=data.get("ecosystem_integration", ""),
            note=data.get("note", ""),
        )


@dataclass
class ScoutResult:
    """Resultado combinado: dados PyPI + catálogo + recomendação."""

    pypi: PyPIPackage | None = None
    catalog: CatalogPackage | None = None
    in_catalog: bool = False
    recommendation: str = ""


# ── Catálogo Loader ─────────────────────────────────────────────────────


def load_catalog() -> dict[str, Any]:
    """Carrega o catálogo curado do disco."""
    if not CATALOG_PATH.exists():
        return {"categories": {}, "affinity_matrix": {}}
    with CATALOG_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def get_all_catalog_packages(catalog: dict[str, Any]) -> list[CatalogPackage]:
    """Extrai todos os pacotes do catálogo em uma lista plana."""
    packages: list[CatalogPackage] = []
    for category_data in catalog.get("categories", {}).values():
        for pkg_data in category_data.get("packages", []):
            packages.append(CatalogPackage.from_dict(pkg_data))
    return packages


def find_in_catalog(
    name: str, catalog: dict[str, Any]
) -> CatalogPackage | None:
    """Busca um pacote no catálogo curado por nome (case-insensitive)."""
    name_lower = name.lower()
    for pkg in get_all_catalog_packages(catalog):
        if pkg.name.lower() == name_lower:
            return pkg
    return None


# ── PyPI API ─────────────────────────────────────────────────────────────


def fetch_pypi_package(name: str) -> PyPIPackage | None:
    """Busca metadados de um pacote na API JSON do PyPI."""
    url = PYPI_JSON_URL.format(package=name)
    req = Request(url, headers={"User-Agent": "opencode-pypi-scout/1.0"})
    try:
        with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            data: dict[str, Any] = json.loads(resp.read().decode())
    except (URLError, HTTPError, json.JSONDecodeError) as exc:
        print(f"  ⚠️  Erro ao buscar '{name}' no PyPI: {exc}")
        return None

    info = data.get("info", {})
    return PyPIPackage(
        name=info.get("name", name),
        version=info.get("version", "unknown"),
        summary=info.get("summary", ""),
        description=(info.get("description", "") or "")[:200],
        author=info.get("author", ""),
        license_info=info.get("license", ""),
        requires_python=info.get("requires_python", ""),
        home_page=info.get("home_page", ""),
        project_url=info.get("project_url", ""),
        keywords=info.get("keywords", ""),
        classifiers=info.get("classifiers", []),
    )


def search_pypi(query: str, max_results: int = 10) -> list[PyPIPackage]:
    """Busca pacotes no PyPI por termo usando a API de busca."""
    search_url = (
        f"https://pypi.org/search/?q={query}"
    )
    # PyPI search via simple JSON endpoint
    json_url = f"https://pypi.org/pypi?%3Aaction=search&term={query}&submit="
    req = Request(json_url, headers={
        "User-Agent": "opencode-pypi-scout/1.0",
        "Accept": "application/json",
    })
    try:
        with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            # Tenta parse como JSON
            raw = resp.read().decode()
            # PyPI search não retorna JSON diretamente; usamos a API simples
            # Tenta a API de busca alternativa
            pass
    except (URLError, HTTPError):
        pass

    # Fallback: busca por nome exato + sugestões via XMLRPC (deprecated)
    # Usamos múltiplas queries individuais como fallback
    results: list[PyPIPackage] = []

    # Estratégia: buscar por nomes comuns relacionados ao termo
    candidates = [
        query,
        f"{query}-py",
        f"py{query}",
        f"{query}-api",
        f"{query}-cli",
        f"{query}-sdk",
    ]
    seen: set[str] = set()
    for candidate in candidates:
        if len(seen) >= max_results:
            break
        if candidate in seen:
            continue
        seen.add(candidate)
        pkg = fetch_pypi_package(candidate)
        if pkg is not None:
            results.append(pkg)

    return results[:max_results]


# ── Display Formatting ───────────────────────────────────────────────────


def print_header(text: str) -> None:
    """Imprime cabeçalho formatado."""
    print(f"\n{'═' * 70}")
    print(f"  {text}")
    print(f"{'═' * 70}")


def print_package_card(pypi: PyPIPackage | None, catalog: CatalogPackage | None) -> None:
    """Imprime um card de pacote com informações do PyPI e catálogo."""
    name = pypi.name if pypi else (catalog.name if catalog else "desconhecido")
    print(f"\n  📦 {name}")

    if pypi:
        print(f"     Versão PyPI : {pypi.version}")
        if pypi.summary:
            print(f"     Resumo       : {pypi.summary[:120]}")
        if pypi.requires_python:
            print(f"     Python       : {pypi.requires_python}")
        if pypi.license_info:
            print(f"     Licença      : {pypi.license_info}")
        print(f"     Instalar     : {pypi.install_command}")

    if catalog:
        print(f"     🌟 Catálogo OpenCode : SIM")
        print(f"     Versão Catálogo     : {catalog.version}")
        print(f"     Descrição           : {catalog.description[:120]}")
        if catalog.ecosystem_integration:
            print(f"     Pipeline            : {catalog.ecosystem_integration}")
        if catalog.affinity:
            affinities = sorted(
                catalog.affinity.items(), key=lambda x: x[1], reverse=True
            )[:5]
            aff_str = ", ".join(
                f"{comp}({score:.0%})" for comp, score in affinities
            )
            print(f"     Afinidade           : {aff_str}")
        if catalog.note:
            print(f"     Nota                : {catalog.note}")
    else:
        print(f"     🌟 Catálogo OpenCode : NÃO (não curado)")


def print_affinity_matrix(matrix: dict[str, Any]) -> None:
    """Exibe a matriz de afinidade do catálogo."""
    print_header("Matriz de Afinidade — Top Pacotes por Componente")
    for component, data in matrix.items():
        if isinstance(data, dict):
            packages = data.get("top_packages", [])
            desc = data.get("description", "")
            print(f"\n  🔗 {component}: {desc}")
            print(f"     → {' | '.join(packages)}")


# ── Commands ─────────────────────────────────────────────────────────────


def cmd_search(query: str) -> None:
    """Busca pacotes no PyPI e compara com catálogo."""
    print_header(f"Busca PyPI: '{query}'")
    catalog = load_catalog()
    results = search_pypi(query, max_results=8)

    if not results:
        print("  Nenhum resultado encontrado no PyPI.")
        print(f"  Tente buscar no catálogo local: pypi_scout.py catalog")
        return

    print(f"  Encontrados: {len(results)} pacotes\n")
    for pkg in results:
        cat_pkg = find_in_catalog(pkg.name, catalog)
        print_package_card(pypi=pkg, catalog=cat_pkg)

    # Sugere também do catálogo
    catalog_pkgs = get_all_catalog_packages(catalog)
    related = [
        cp for cp in catalog_pkgs
        if query.lower() in cp.name.lower() or query.lower() in cp.description.lower()
    ]
    if related:
        print(f"\n  📚 Pacotes relacionados no catálogo ({len(related)}):")
        for cp in related[:5]:
            if not any(r.name.lower() == cp.name.lower() for r in results):
                print(f"     → {cp.name}: {cp.description[:100]}")


def cmd_catalog() -> None:
    """Lista o catálogo curado completo."""
    catalog = load_catalog()
    categories = catalog.get("categories", {})

    print_header("Catálogo Curado OpenCode")
    print(f"  Total de pacotes: {sum(len(c.get('packages', [])) for c in categories.values())}")
    print(f"  Categorias: {len(categories)}\n")

    for cat_key, cat_data in categories.items():
        label = cat_data.get("label", cat_key)
        desc = cat_data.get("description", "")
        packages = cat_data.get("packages", [])
        print(f"\n  📂 [{cat_key}] {label}")
        print(f"     {desc}")
        print(f"     Pacotes ({len(packages)}):")
        for pkg in packages:
            name = pkg.get("name", "?")
            install = pkg.get("install", "")
            print(f"       • {name:30s} → {install}")


def cmd_category(category_name: str) -> None:
    """Filtra o catálogo por categoria."""
    catalog = load_catalog()
    categories = catalog.get("categories", {})

    # Busca fuzzy por categoria
    matched = None
    for cat_key, cat_data in categories.items():
        if category_name.lower() in cat_key.lower():
            matched = (cat_key, cat_data)
            break
        if category_name.lower() in cat_data.get("label", "").lower():
            matched = (cat_key, cat_data)
            break

    if matched is None:
        print(f"  ❌ Categoria '{category_name}' não encontrada.")
        print(f"  Categorias disponíveis: {', '.join(categories.keys())}")
        return

    cat_key, cat_data = matched
    print_header(f"Categoria: {cat_data.get('label', cat_key)}")
    print(f"  {cat_data.get('description', '')}\n")

    for pkg_data in cat_data.get("packages", []):
        pkg = CatalogPackage.from_dict(pkg_data)
        print_package_card(pypi=None, catalog=pkg)


def cmd_install(package_name: str) -> None:
    """Instala um pacote via pip."""
    catalog = load_catalog()
    cat_pkg = find_in_catalog(package_name, catalog)

    install_cmd = f"pip install {package_name}"
    if cat_pkg and cat_pkg.install:
        install_cmd = cat_pkg.install

    print(f"\n  📥 Instalando: {install_cmd}")
    print(f"  {'─' * 50}")

    try:
        result = subprocess.run(
            install_cmd.split(),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print(f"  ✅ Instalação concluída com sucesso!")
            if result.stdout:
                for line in result.stdout.splitlines()[-5:]:
                    print(f"     {line}")
        else:
            print(f"  ❌ Erro na instalação (código {result.returncode}):")
            for line in (result.stderr or result.stdout).splitlines()[-10:]:
                print(f"     {line}")
    except subprocess.TimeoutExpired:
        print(f"  ⏰ Timeout: a instalação excedeu 120 segundos.")
    except FileNotFoundError:
        print(f"  ❌ pip não encontrado. Verifique sua instalação Python.")


def cmd_recommend(pipeline: str) -> None:
    """Recomenda pacotes para um componente/pipeline do ecossistema."""
    catalog = load_catalog()
    matrix = catalog.get("affinity_matrix", {})
    all_pkgs = get_all_catalog_packages(catalog)

    # Busca fuzzy no pipeline name
    matched_component = None
    for comp_key, comp_data in matrix.items():
        if pipeline.lower() in comp_key.lower():
            matched_component = comp_key
            break
        if pipeline.lower() in comp_data.get("description", "").lower():
            matched_component = comp_key
            break

    if matched_component is None:
        # Busca por afinidade em todos os pacotes
        print(f"\n  🔍 Pipeline '{pipeline}' não encontrado na matriz.")
        print(f"  Pipelines conhecidos: {', '.join(matrix.keys())}")
        return

    comp_data = matrix[matched_component]
    print_header(f"Recomendações para: {matched_component}")
    print(f"  {comp_data.get('description', '')}\n")

    top_names = comp_data.get("top_packages", [])
    for name in top_names:
        cat_pkg = find_in_catalog(name, catalog)
        if cat_pkg:
            print(f"  ⭐ {cat_pkg.name}")
            print(f"     {cat_pkg.description[:120]}")
            print(f"     Instalar: {cat_pkg.install}")


def cmd_diff(package_name: str) -> None:
    """Compara versão do catálogo com a versão atual no PyPI."""
    catalog = load_catalog()
    cat_pkg = find_in_catalog(package_name, catalog)

    print_header(f"Diff: {package_name}")

    if cat_pkg:
        print(f"  📋 Catálogo OpenCode:")
        print(f"     Versão registrada: {cat_pkg.version}")
        print(f"     Instalar: {cat_pkg.install}")

    print(f"\n  🌐 PyPI (ao vivo):")
    pypi_pkg = fetch_pypi_package(package_name)
    if pypi_pkg:
        print(f"     Versão atual: {pypi_pkg.version}")
        print(f"     Python requerido: {pypi_pkg.requires_python}")
        print(f"     Licença: {pypi_pkg.license_info}")
        if cat_pkg and pypi_pkg.version != cat_pkg.version:
            print(f"\n  ⚠️  Divergência de versão! Catálogo: {cat_pkg.version} | PyPI: {pypi_pkg.version}")
    else:
        print(f"     ❌ Não encontrado no PyPI.")


# ── Main ─────────────────────────────────────────────────────────────────


def print_usage() -> None:
    """Exibe ajuda de uso."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║        OpenCode PyPI Scout v1.0                                 ║
║        Buscador inteligente de bibliotecas Python               ║
╚══════════════════════════════════════════════════════════════════╝

Uso:
  python pypi_scout.py <comando> [argumentos]

Comandos:
  search <termo>       Busca pacotes no PyPI e compara com catálogo
  catalog               Lista todo o catálogo curado
  category <nome>       Filtra pacotes por categoria
  install <pacote>      Instala um pacote via pip
  recommend <pipeline>  Recomenda pacotes para um pipeline OpenCode
  diff <pacote>         Compara versão do catálogo com PyPI

Categorias:
  artigos_academicos    Sci-Hub, arXiv, Semantic Scholar, Google Scholar
  dados_mundiais        Banco Mundial (WDI), ONU (SDG), OCDE (FRED)
  mcp_ecosystem         MCP SDK, adaptadores OpenAI/LangChain
  dados_cientificos     BioPython, NCBI, PubMed
  infra_ferramentas     Click, Rich, HTTPX

Pipelines (para recommend):
  SEEKER                Pesquisa bibliográfica
  MASWOS                Criação de artigos científicos
  PhD_Auditor           Auditoria estatística Qualis
  data_analysis         Análise de dados socioeconômicos
  MCP_server            Servidores e clientes MCP

Exemplos:
  python pypi_scout.py search scihub
  python pypi_scout.py category dados_mundiais
  python pypi_scout.py recommend SEEKER
  python pypi_scout.py install wbgapi
  python pypi_scout.py diff scholarly
""")


def main() -> None:
    """Ponto de entrada principal."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    commands: dict[str, Any] = {
        "search": lambda: cmd_search(" ".join(args)) if args else print("Uso: search <termo>"),
        "catalog": cmd_catalog,
        "category": lambda: cmd_category(args[0]) if args else print("Uso: category <nome>"),
        "install": lambda: cmd_install(args[0]) if args else print("Uso: install <pacote>"),
        "recommend": lambda: cmd_recommend(args[0]) if args else print("Uso: recommend <pipeline>"),
        "diff": lambda: cmd_diff(args[0]) if args else print("Uso: diff <pacote>"),
        "help": print_usage,
        "--help": print_usage,
        "-h": print_usage,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"  ❌ Comando desconhecido: '{command}'")
        print_usage()


if __name__ == "__main__":
    main()
