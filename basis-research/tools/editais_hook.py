"""editais_hook.py - Ponte nativa entre SEEKER e editais-br.

Importa diretamente as funcoes do edital_search.py (sem HTTP, sem subprocess).
Fornece API sincrona para os agentes SEEKER consultarem editais de fomento.

Uso no pipeline SEEKER:
    from tools.editais_hook import buscar_editais, extrair_edital
    resultados = buscar_editais("inteligencia artificial saude")
"""

import json
import sys
from pathlib import Path
from typing import Any, Optional

EDITAIS_PATH = Path(__file__).parent.parent.parent / "skills" / "research" / "editais-br" / "scripts"


def _import_edital_search():
    """Importa edital_search.py como modulo."""
    edital_path = str(EDITAIS_PATH.resolve())
    if edital_path not in sys.path:
        sys.path.insert(0, edital_path)
    import edital_search
    import importlib
    importlib.reload(edital_search)
    return edital_search


def buscar_editais(
    query: str,
    tipo: str = "",
    perfil: str = "pesquisador",
    max_resultados: int = 5,
) -> list[dict[str, Any]]:
    """Busca editais via importacao direta do edital_search.py.

    Args:
        query: Termo de busca (ex: "ia saude", "inovacao")
        tipo: Tipo de edital (pesquisa, mestrado, doutorado, startup)
        perfil: Perfil do usuario (pesquisador, mestrando, doutorando, empreendedor)
        max_resultados: Maximo de resultados

    Returns:
        Lista de dicts com titulo, url, score, dimensoes, portal, fonte
    """
    try:
        mod = _import_edital_search()
        resultados = mod.buscar_sync(
            query=query,
            tipo=tipo,
            perfil=perfil,
            max_results=max_resultados,
        )
        return resultados[:max_resultados]
    except Exception as e:
        return [{"titulo": f"Erro ao buscar editais: {e}", "url": "", "score": 0}]


def extrair_edital(caminho_pdf: str) -> Optional[dict[str, Any]]:
    """Extrai requisitos de um PDF de edital usando extracao_profunda.py.

    Args:
        caminho_pdf: Caminho local do PDF

    Returns:
        Dict com categorias, documentos, datas, valores, restricoes ou None
    """
    try:
        sys.path.insert(0, str(EDITAIS_PATH.resolve()))
        import extracao_profunda
        return extracao_profunda.extrair_de_pdf(caminho_pdf)
    except Exception:
        return None


def classificar_edital(titulo: str, url: str = "") -> dict[str, list[str]]:
    """Classifica um edital em dimensoes (area, perfil, mecanismo).

    Args:
        titulo: Titulo do edital
        url: URL opcional para contexto

    Returns:
        Dict com keys: area, perfil, mecanismo, cada uma com lista de tags
    """
    try:
        mod = _import_edital_search()
        return mod.classificar(titulo, url)
    except Exception:
        return {"area": ["nao_classificado"], "perfil": [], "mecanismo": []}


def formatar_resultados(resultados: list[dict]) -> str:
    """Formata resultados para exibicao textual (para agentes SEEKER).

    Args:
        resultados: Lista de dicts de buscar_editais()

    Returns:
        String formatada pronta para exibicao
    """
    if not resultados:
        return "Nenhum edital encontrado."

    linhas = []
    for i, r in enumerate(resultados, 1):
        areas = ", ".join(r.get("dimensoes", {}).get("area", []))
        linhas.append(
            f"{i}. {r.get('titulo', '?')[:80]}\n"
            f"   Score: {r.get('score', 0):.0f}/100 | {r.get('fonte', '?')} | {areas}\n"
            f"   {r.get('url', '')[:90]}"
        )
    return "\n\n".join(linhas)


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "inovacao"
    print(f"=== Teste editais_hook nativo: '{query}' ===")
    res = buscar_editais(query, max_resultados=5)
    print(f"Resultados: {len(res)}")
    for r in res[:3]:
        score = r.get("score", "?")
        titulo = r.get("titulo", "")[:60]
        orgao = r.get("portal", "")
        print(f"  {score:.0f} - {titulo} ({orgao})")
