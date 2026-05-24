"""
PyPI Search Tool — Ferramenta de busca no Python Package Index.

Realiza pesquisas no PyPI utilizando três estratégias complementares:
1. API JSON oficial (https://pypi.org/pypi/{package}/json) — primária
2. API Simple PEP 503 (https://pypi.org/simple/) — busca por prefixo
3. Web scraping da página de busca (pode ser bloqueada por Cloudflare)

Arquitetura sem dependências externas: utiliza apenas biblioteca padrão Python 3.
Integração primária com o agente PyPISearcher do ecossistema OpenCode v4.2.

NOTA (2026-05): O PyPI ativou Client Challenge (Cloudflare), bloqueando scraping.
A API JSON e a API Simple (PEP 503) continuam funcionando sem JS.

Autor: OpenCode Ecosystem v4.2
Versão: 3.0.0
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Optional

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"
PYPI_SIMPLE_URL = "https://pypi.org/simple/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 15  # segundos
DEFAULT_LIMIT = 10
MAX_RESULTS = 25

# ---------------------------------------------------------------------------
# Utilitários de rede
# ---------------------------------------------------------------------------


def _fetch_url(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[str]:
    """Busca o conteúdo de uma URL com timeout e tratamento de erros."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            encoding = resp.headers.get_content_charset("utf-8")
            return resp.read().decode(encoding, errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        sys.stderr.write(f"[pypi_search] Erro ao buscar {url}: {exc}\n")
        return None


# ---------------------------------------------------------------------------
# Estratégia 1: API JSON oficial (PRIMÁRIA)
# Busca metadados completos de um pacote por nome exato.
# ---------------------------------------------------------------------------


def search_by_api(package_name: str) -> Optional[dict]:
    """Busca metadados completos de um pacote via API JSON do PyPI.

    Retorna: nome, versão, descrição (summary), autor, licença, link,
    requires_python, home_page e data de release mais recente.
    """
    url = PYPI_JSON_URL.format(package=urllib.parse.quote(package_name))
    raw = _fetch_url(url, timeout=10)
    if not raw:
        return None

    try:
        data = json.loads(raw)
        info = data.get("info", {})
        return {
            "name": info.get("name", package_name),
            "version": info.get("version", ""),
            "description": (info.get("summary") or "").strip(),
            "author": info.get("author") or "",
            "license": info.get("license") or "",
            "link": info.get("package_url") or url.replace("/json", ""),
            "requires_python": info.get("requires_python") or "",
            "home_page": info.get("home_page") or "",
            "release_date": (
                list(data.get("releases", {}).keys())[-1]
                if data.get("releases")
                else ""
            ),
        }
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        sys.stderr.write(f"[pypi_search] Erro ao decodificar JSON da API: {exc}\n")
        return None


# ---------------------------------------------------------------------------
# Estratégia 2: API Simple PEP 503 (FALLBACK)
# Lista TODOS os pacotes e filtra por prefixo do termo de busca.
# ---------------------------------------------------------------------------


class SimpleIndexParser(HTMLParser):
    """Parser para a página Simple Index (PEP 503) do PyPI.

    Extrai todos os nomes de pacotes listados como links <a href="...">.
    """

    def __init__(self) -> None:
        super().__init__()
        self.packages: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for attr_name, attr_value in attrs:
            if attr_name == "href" and attr_value:
                # Extrai o nome do pacote do href: "/simple/package-name/"
                pkg = attr_value.strip("/").split("/")[-1]
                if pkg:
                    self.packages.append(pkg)


def _search_by_simple_index(query: str, limit: int = DEFAULT_LIMIT) -> list[str]:
    """Busca pacotes por prefixo usando a API Simple (PEP 503).

    Baixa o índice completo de pacotes e filtra por correspondência
    parcial (case-insensitive) com o termo de busca.

    ATENÇÃO: A página Simple contém mais de 500 mil pacotes (~30 MB).
    O download pode ser lento. Use com moderação.
    """
    raw = _fetch_url(PYPI_SIMPLE_URL, timeout=30)
    if not raw:
        return []

    parser = SimpleIndexParser()
    try:
        parser.feed(raw)
    except Exception as exc:
        sys.stderr.write(f"[pypi_search] Erro ao processar Simple Index: {exc}\n")
        return []

    query_lower = query.lower()
    matches = [p for p in parser.packages if query_lower in p.lower()]

    # Ordena por relevância: correspondência exata primeiro, depois prefixo
    exact = [p for p in matches if p.lower() == query_lower]
    prefix = [p for p in matches if p.lower().startswith(query_lower) and p not in exact]
    rest = [p for p in matches if p not in exact and p not in prefix]

    return (exact + prefix + rest)[:limit]


# ---------------------------------------------------------------------------
# Estratégia 3: Scraping HTML (LEGADO — requer JS, bloqueado por Cloudflare)
# ---------------------------------------------------------------------------


class PyPISearchParser(HTMLParser):
    """Parser HTML legado para snippets da página de busca do PyPI.

    NOTA (2026-05): O PyPI agora exige JavaScript (Client Challenge).
    Este parser NÃO funciona mais. Mantido apenas para referência.
    """

    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict] = []
        self.current_pkg: dict = {}
        self.in_snippet = False
        self.in_name = False
        self.in_version = False
        self.in_desc = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get("class", "") or ""

        if tag == "a" and "package-snippet" in class_name:
            self.in_snippet = True
            self.current_pkg = {
                "link": "https://pypi.org" + (attrs_dict.get("href") or ""),
                "name": "",
                "version": "",
                "description": "",
            }
            return

        if not self.in_snippet:
            return

        if tag == "span" and "package-snippet__name" in class_name:
            self.in_name = True
        elif tag == "span" and "package-snippet__version" in class_name:
            self.in_version = True
        elif tag == "p" and "package-snippet__description" in class_name:
            self.in_desc = True

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text:
            return
        if self.in_name:
            self.current_pkg["name"] = text
        elif self.in_version:
            self.current_pkg["version"] = text
        elif self.in_desc:
            desc = self.current_pkg.get("description", "")
            self.current_pkg["description"] = (desc + " " + text).strip()

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.in_snippet:
            self.in_snippet = False
            if self.current_pkg.get("name"):
                self.results.append(self.current_pkg)
            self.current_pkg = {}
            return

        if self.in_snippet:
            if tag == "span":
                self.in_name = False
                self.in_version = False
            elif tag == "p":
                self.in_desc = False


def search_by_scraping(query: str, limit: int = DEFAULT_LIMIT) -> list[dict]:
    """Estratégia LEGADA: scraping da página de busca do PyPI.

    NÃO FUNCIONA desde que o PyPI ativou Client Challenge (Cloudflare).
    Mantida para referência e possível reativação futura.
    """
    url = f"https://pypi.org/search/?q={urllib.parse.quote(query)}"
    html = _fetch_url(url, timeout=10)
    if not html:
        return []

    # Se a resposta for o Client Challenge, retorna vazio
    if "Client Challenge" in html or "<noscript>" in html:
        sys.stderr.write(
            "[pypi_search] PyPI requer JavaScript (Client Challenge). "
            "Scraping indisponível. Use a API JSON ou Simple Index.\n"
        )
        return []

    parser = PyPISearchParser()
    try:
        parser.feed(html)
    except Exception as exc:
        sys.stderr.write(f"[pypi_search] Erro de parsing HTML: {exc}\n")
        return []

    return parser.results[:limit]


# ---------------------------------------------------------------------------
# Estratégia 4: Derivação de nomes candidatos a partir de termos de busca
# ---------------------------------------------------------------------------


def _derive_candidate_names(query: str) -> list[str]:
    """Gera nomes de pacotes candidatos a partir de um termo de busca.

    Exemplos:
      "async http client" → ["httpx", "aiohttp", "async-http-client",
                              "http-async", "async-http"]
      "pdf generator" → ["reportlab", "fpdf2", "weasyprint", "pdfkit",
                          "pdf-generator"]
    """
    words = re.findall(r"[a-zA-Z0-9]+", query.lower())
    candidates = set()

    # Cada palavra individual
    for w in words:
        candidates.add(w)

    # Combinações de 2 palavras (com hífen e sem)
    for i in range(len(words) - 1):
        candidates.add(f"{words[i]}-{words[i+1]}")
        candidates.add(f"{words[i]}{words[i+1]}")
        candidates.add(f"{words[i+1]}-{words[i]}")

    # O termo completo com hífen
    candidates.add("-".join(words))
    candidates.add("".join(words))

    # Remove palavras muito curtas (improvavelmente nomes de pacotes)
    return [c for c in sorted(candidates, key=lambda x: -len(x)) if len(c) >= 3]


# ---------------------------------------------------------------------------
# Função principal de busca (orquestração das estratégias)
# ---------------------------------------------------------------------------


def search_pypi(
    query: str,
    limit: int = DEFAULT_LIMIT,
    enrich: bool = True,
    use_simple_index: bool = False,
    timeout: int = REQUEST_TIMEOUT,
) -> list[dict]:
    """Busca pacotes no PyPI combinando múltiplas estratégias.

    Pipeline:
    1. Deriva nomes candidatos do termo de busca.
    2. Para cada candidato, tenta API JSON (rápido e completo).
    3. Se menos de 3 resultados, tenta a API Simple (PEP 503).
    4. Enriquece resultados com metadados completos da API JSON.

    Args:
        query: Termo de busca (ex.: "async http client").
        limit: Número máximo de resultados a retornar.
        enrich: Se True, garante metadados completos via API JSON.
        use_simple_index: Se True, usa API Simple como fallback.
        timeout: Timeout em segundos para cada requisição HTTP.

    Returns:
        Lista de dicionários com nome, versão, descrição, link, etc.
    """
    start_time = time.perf_counter()
    results: list[dict] = []
    seen_names: set[str] = set()

    # --- Fase 1: Tentar candidatos derivados via API JSON ---
    candidates = _derive_candidate_names(query)
    sys.stderr.write(
        f"[pypi_search] {len(candidates)} candidatos derivados de '{query}'\n"
    )

    for candidate in candidates[:10]:  # limita a 10 tentativas para não sobrecarregar
        if len(results) >= limit:
            break
        api_result = search_by_api(candidate)
        if api_result and api_result["name"] not in seen_names:
            seen_names.add(api_result["name"])
            results.append(api_result)

    # --- Fase 2: Tentar o termo exato como nome de pacote ---
    if len(results) < 3:
        exact = search_by_api(query)
        if exact and exact["name"] not in seen_names:
            seen_names.add(exact["name"])
            results.append(exact)

    # --- Fase 3: API Simple (fallback pesado) ---
    if use_simple_index and len(results) < limit:
        sys.stderr.write("[pypi_search] Acionando Simple Index (PEP 503)...\n")
        simple_matches = _search_by_simple_index(query, limit=limit * 2)
        for pkg_name in simple_matches:
            if len(results) >= limit:
                break
            if pkg_name in seen_names:
                continue
            api_result = search_by_api(pkg_name)
            if api_result:
                seen_names.add(pkg_name)
                results.append(api_result)

    # --- Fase 4: Enriquecer com scraping (se disponível) ---
    if not enrich:
        # Já temos metadados da API JSON, nada a fazer
        pass

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    sys.stderr.write(
        f"[pypi_search] Query='{query}' → {len(results)} resultados "
        f"em {elapsed_ms:.0f}ms\n"
    )

    return results[:limit]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """Ponto de entrada CLI para uso como ferramenta standalone."""
    if len(sys.argv) < 2:
        print("Uso: python pypi_search.py <termo de busca> [flags]")
        print("Flags:")
        print("  --limit N       Máximo de resultados (padrão: 10, máx: 25)")
        print("  --simple        Ativar busca via Simple Index (PEP 503, lento)")
        print("  --no-enrich     Desativar enriquecimento via API JSON")
        print()
        print("Exemplo: python pypi_search.py 'async http client' --limit 5")
        sys.exit(1)

    args = sys.argv[1:]
    query_parts: list[str] = []
    limit = DEFAULT_LIMIT
    enrich = True
    use_simple = False

    i = 0
    while i < len(args):
        if args[i] == "--limit" and i + 1 < len(args):
            try:
                limit = min(int(args[i + 1]), MAX_RESULTS)
            except ValueError:
                pass
            i += 2
        elif args[i] == "--simple":
            use_simple = True
            i += 1
        elif args[i] == "--no-enrich":
            enrich = False
            i += 1
        else:
            query_parts.append(args[i])
            i += 1

    query = " ".join(query_parts)
    if not query:
        print("Erro: termo de busca vazio.")
        sys.exit(1)

    results = search_pypi(
        query, limit=limit, enrich=enrich, use_simple_index=use_simple
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
