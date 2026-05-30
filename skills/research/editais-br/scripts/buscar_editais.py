#!/usr/bin/env python3
"""
Busca automatizada de editais de fomento.

Uso:
    python buscar_editais.py "inteligencia artificial saude"
    python buscar_editais.py --portal finep "industria 4.0"
    python buscar_editais.py --tipo mestrado "ciencia dados"
"""

import argparse
import json
import sys
from datetime import datetime

try:
    import httpx
except ImportError:
    httpx = None


PORTAIS = {
    "finep": "http://finep.gov.br/chamadas-publicas",
    "prosas": "https://prosas.com.br/editais",
    "cnpq": "http://cnpq.br/editais",
    "sebrae": "https://sebrae.com.br/editais",
    "fapeg": "https://fapeg.go.gov.br/editais",
}


def buscar_editais(query: str, portal: str | None = None, max_results: int = 10) -> list[dict]:
    """Busca editais via DuckDuckGo com termos direcionados."""
    if httpx is None:
        print("Erro: httpx nao instalado. Instale com: pip install httpx beautifulsoup4")
        return []

    termos = f"edital fomento {query} 2026"
    if portal:
        url_base = PORTAIS.get(portal, "")
        termos = f"site:{url_base} {termos}"

    url = "https://html.duckduckgo.com/html/"
    try:
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            resp = client.post(url, data={"q": termos}, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            # Parse basico — retorna URLs encontradas
            from html.parser import HTMLParser

            class LinkParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.results = []
                    self._capture = False
                def handle_starttag(self, tag, attrs):
                    attrs_dict = dict(attrs)
                    if tag == "a" and "result__a" in attrs_dict.get("class", ""):
                        self._capture = True
                        self._url = attrs_dict.get("href", "")
                def handle_data(self, data):
                    if self._capture and hasattr(self, "_url"):
                        self.results.append({"title": data.strip(), "url": self._url})
                        self._capture = False

            parser = LinkParser()
            parser.feed(resp.text)
            return parser.results[:max_results]
    except Exception as e:
        print(f"Erro na busca: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Busca editais de fomento")
    parser.add_argument("query", help="Termo de busca")
    parser.add_argument("--portal", choices=list(PORTAIS.keys()), help="Filtrar por portal")
    parser.add_argument("--tipo", choices=["mestrado", "doutorado", "inovacao", "cultura", "social"],
                        help="Tipo de edital")
    parser.add_argument("--max", type=int, default=10, help="Maximo resultados")
    args = parser.parse_args()

    tipo_map = {
        "mestrado": "bolsa mestrado CAPES CNPq",
        "doutorado": "bolsa doutorado CAPES CNPq",
        "inovacao": "subvencao inovacao FINEP SEBRAE",
        "cultura": "edital cultura Lei Rouanet",
        "social": "edital impacto social OSC",
    }

    query = f"{tipo_map.get(args.tipo, '')} {args.query}"
    resultados = buscar_editais(query, args.portal, args.max)

    print(json.dumps({
        "consulta": query,
        "data": datetime.now().isoformat(),
        "resultados": resultados,
        "total": len(resultados),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
