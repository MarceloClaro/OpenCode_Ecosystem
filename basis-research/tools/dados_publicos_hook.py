"""dados_publicos_hook.py — Ponte nativa entre SEEKER e extrator de dados públicos v2.0.

Importa diretamente as funcoes do extrator_dados_publicos.py (sem HTTP, sem subprocess).
Fornece API sincrona para os agentes SEEKER consultarem dados públicos
brasileiros e internacionais em 6 dominios.

Uso no pipeline SEEKER:
    from tools.dados_publicos_hook import (
        buscar_dados_publicos, listar_fontes, extrair_url,
        buscar_multidominio, formatar_resultados
    )
    resultados = buscar_dados_publicos("financeiro", "selic")
    fontes = listar_fontes("internacional")
"""

import json, sys
from pathlib import Path
from typing import Any, Dict, List, Optional

EXTRATOR_PATH = (
    Path(__file__).parent.parent.parent
    / "skills" / "research" / "editais-br" / "scripts"
)


def _import_extrator():
    """Importa extrator_dados_publicos.py como modulo."""
    path = str(EXTRATOR_PATH.resolve())
    if path not in sys.path:
        sys.path.insert(0, path)
    import extrator_dados_publicos
    import importlib
    importlib.reload(extrator_dados_publicos)
    return extrator_dados_publicos


# =============================================================================
# API PUBLICA — wrappers sincronos para agentes SEEKER
# =============================================================================

def buscar_dados_publicos(
    dominio: str,
    query: str = "",
    max_resultados: int = 10,
) -> List[Dict[str, Any]]:
    """Busca dados em todas as fontes de um dominio.

    Dominios disponiveis:
        financeiro  - BCB/SGS, Tesouro, CVM, BNDES, SICONFI
        ambiental   - INPE, ANA, MapBiomas, ICMBio, Clima
        geografico  - IBGE malhas/localidades, CPRM, INPE satelite
        economico   - IBGE/SIDRA, IPEADATA, dados.gov.br, Banco Mundial, RAIS
        institucional - Camara, Senado, TSE, DATASUS, ANS, ANATEL, ANEEL
        internacional - FMI, ONU, OCDE, OMS, BRICS, UNCTAD, FAO, OIT, UNESCO, ADB (v2.1)

    Args:
        dominio: Dominio tematico para busca
        query: Termo de busca (codigo, indicador, palavra-chave)
        max_resultados: Maximo de resultados por fonte

    Returns:
        Lista de dicts com fonte, dados, total por fonte
    """
    try:
        mod = _import_extrator()
        resultados = mod.buscar_por_dominio(dominio, query, max_resultados)
        return resultados
    except Exception as e:
        return [{"fonte": "extrator", "dominio": dominio, "erro": str(e)}]


def listar_fontes(dominio: str = "") -> List[Dict[str, Any]]:
    """Lista fontes disponiveis no extrator.

    Args:
        dominio: Opcional, filtra por dominio

    Returns:
        Lista de dicts com id, nome, dominio, tipo, descricao
    """
    try:
        mod = _import_extrator()
        return mod.listar_fontes(dominio)
    except Exception as e:
        return [{"erro": str(e)}]


def extrair_url(url: str) -> Optional[Dict[str, Any]]:
    """Tenta identificar e extrair dados de uma URL publica.

    Suporta URLs de: BCB/SGS, IBGE, BNDES, dados.gov.br,
    Banco Mundial, FMI.

    Args:
        url: URL completa do dataset

    Returns:
        Dict com fonte e dados extraidos
    """
    try:
        mod = _import_extrator()
        return mod.extrair_url_para_dataset(url)
    except Exception as e:
        return {"erro": str(e)}


def buscar_multidominio(query: str) -> Dict[str, list]:
    """Busca em todos os dominios simultaneamente.

    Args:
        query: Termo de busca

    Returns:
        Dict com resultados por dominio
    """
    try:
        mod = _import_extrator()
        return mod.buscar_multidominio(query)
    except Exception as e:
        return {"erro": [{"erro": str(e)}]}


def formatar_resultados(resultados: List[Dict], max_por_fonte: int = 3) -> str:
    """Formata resultados para exibicao textual (para agentes SEEKER).

    Args:
        resultados: Lista de dicts de buscar_dados_publicos()
        max_por_fonte: Maximo de itens a mostrar por fonte

    Returns:
        String formatada pronta para resposta textual
    """
    if not resultados:
        return "Nenhum resultado encontrado."

    linhas = []
    for i, r in enumerate(resultados, 1):
        fonte = r.get("fonte", "?")
        dados = r.get("dados", [])
        erro = r.get("erro")
        total = r.get("total", len(dados))

        if erro:
            linhas.append(f"{i}. [{fonte}] ERRO: {erro}")
            continue

        linhas.append(f"{i}. [{fonte}] {total} resultado(s)")
        for d in (dados or [])[:max_por_fonte]:
            nome = d.get("nome") or d.get("titulo") or d.get("ano", "") or d.get("indicador", "")
            url = d.get("url", "")
            desc = d.get("descricao", d.get("valor", ""))
            if nome:
                linhas.append(f"   {str(nome)[:80]}")
            if desc and desc != nome:
                linhas.append(f"   {str(desc)[:100]}")
            if url:
                linhas.append(f"   {str(url)[:90]}")
        if total > max_por_fonte:
            linhas.append(f"   ... mais {total - max_por_fonte} resultado(s)")

    return "\n".join(linhas)


def buscar_internacional(query: str = "NGDPD") -> List[Dict]:
    """Atalho para buscar especificamente em fontes internacionais.

    Args:
        query: Indicador (ex: NGDPD, GDP, POP, WHOSIS_000001)

    Returns:
        Resultados do dominio internacional
    """
    return buscar_dados_publicos("internacional", query)


def buscar_economico_br(query: str = "5938") -> List[Dict]:
    """Atalho para buscar dados economicos brasileiros.

    Args:
        query: Codigo SIDRA (ex: 5938=PIB, 4099=populacao)

    Returns:
        Resultados do dominio economico
    """
    return buscar_dados_publicos("economico", query)


# =============================================================================
# INTROSPECTION — para agentes descobrirem capacidades
# =============================================================================

CAPACIDADES = {
    "dominios": ["financeiro", "ambiental", "geografico", "economico",
                  "institucional", "internacional"],
    "total_fontes": 38,
    "tipo": "stdlib_only",
    "cache_ttl_segundos": 3600,
    "formatos_suportados": ["JSON", "CSV (via download)", "GeoJSON"],
    "requer_chaves_api": False,
    "exemplos_consulta": {
        "selic": "buscar_dados_publicos('financeiro', '432')",
        "pib_brasil": "buscar_dados_publicos('economico', '5938')",
        "fmi_pib": "buscar_internacional('NGDPD')",
        "onu_pop": "buscar_internacional('POP')",
        "ocde_gdp": "buscar_internacional('GDP')",
        "expectativa_vida": "buscar_internacional('WHOSIS_000001')",
        "fao_producao": "buscar_internacional('producao')",
        "oit_emprego": "buscar_internacional('EMP_TEMP')",
        "unesco_educacao": "buscar_internacional('EDUCATION')",
        "adb_crescimento": "buscar_internacional('GDP_GROWTH')",
        "proposicoes": "buscar_dados_publicos('institucional', 'PL')",
        "queimadas": "buscar_dados_publicos('ambiental', 'SP')",
    },
    "complementar_com": {
        "mcp_brasil": "MCP Server com 70 APIs brasileiras (economia, legislativo, transparencia, TCEs, TSE, INEP, saude, seguranca, compras)",
        "editais_br": "Busca de editais de fomento CNPq/CAPES/FINEP/FAPs com scoring 0-100",
    },
}


def obter_capacidades() -> Dict:
    """Retorna capacidades do extrator para agentes descobrirem."""
    return CAPACIDADES


# =============================================================================
# CLI de teste
# =============================================================================

if __name__ == "__main__":
    comando = sys.argv[1] if len(sys.argv) > 1 else "testar"

    if comando == "listar":
        dominio = sys.argv[2] if len(sys.argv) > 2 else ""
        fontes = listar_fontes(dominio)
        print(f"\n=== FONTES ({len(fontes)}) ===\n")
        for f in fontes[:10]:
            print(f"  [{f['id']}] {f['nome']} ({f['dominio']})")
        if len(fontes) > 10:
            print(f"  ... e mais {len(fontes)-10} fonte(s)")

    elif comando == "buscar":
        dominio = sys.argv[2] if len(sys.argv) > 2 else "internacional"
        query = sys.argv[3] if len(sys.argv) > 3 else "NGDPD"
        print(f"\n=== BUSCAR: {dominio} / {query} ===\n")
        resultados = buscar_dados_publicos(dominio, query)
        print(formatar_resultados(resultados))

    elif comando == "multidominio":
        query = sys.argv[2] if len(sys.argv) > 2 else "pib"
        print(f"\n=== MULTIDOMINIO: {query} ===\n")
        resultados = buscar_multidominio(query)
        for dom, res in resultados.items():
            print(f"\n--- {dom.upper()} ({len(res)} fontes) ---")
            print(formatar_resultados(res))

    elif comando == "testar":
        print("=== TESTE RAPIDO DO HOOK ===\n")

        print("1. Listar fontes internacionais:")
        intl = listar_fontes("internacional")
        for f in intl:
            print(f"   [{f['id']}] {f['nome']}")

        print("\n2. Buscar FMI:")
        fmi = buscar_dados_publicos("internacional", "NGDPD")
        print(formatar_resultados(fmi))

        print("\n3. Buscar ONU:")
        onu = buscar_dados_publicos("internacional", "POP")
        print(formatar_resultados(onu))

        print("\n4. Capacidades:")
        cap = obter_capacidades()
        print(f"   Dominios: {', '.join(cap['dominios'])}")
        print(f"   Total fontes: {cap['total_fontes']}")
        print(f"   Complementar com: {', '.join(cap['complementar_com'].keys())}")

    else:
        print(f"Comandos: listar, buscar, multidominio, testar")
        print(f"Ex: python tools/dados_publicos_hook.py buscar internacional NGDPD")
