#!/usr/bin/env python3
"""
extrator_dados_publicos.py — Extrator de Dados Publicos v2.1
============================================================

Extrai datasets de fontes abertas brasileiras e internacionais.
6 dominios, 38 fontes: financeiro, ambiental, geografico, economico, institucional, internacional

Uso:
    python extrator_dados_publicos.py listar-fontes
    python extrator_dados_publicos.py buscar --dominio internacional --q "pib"
    python extrator_dados_publicos.py extrair --url "https://..."
    python extrator_dados_publicos.py servidor --porta 8082

v2.0: dominio INTERNACIONAL (FMI, ONU, OCDE, OMS, BRICS, UNCTAD)
      + novas brasileiras (BCB Estatisticas, RAIS, ANS, ANATEL, ANEEL, Clima)

Requisitos: Python 3.8+ (stdlib, sem dependencias externas)
"""

import json, re, sys, time, hashlib, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

CACHE_DIR = Path.home() / '.config/opencode/cache/dados_publicos'
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_TTL = 3600
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'


# =============================================================================
# CATALOGO DE FONTES (38 fontes, 6 dominios)
# =============================================================================

FONTES = {
    # --- FINANCEIRO ---
    "bcb_sgs": {
        "nome": "Banco Central - SGS (Series Temporais)",
        "dominio": "financeiro", "tipo": "api_rest",
        "url": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados",
        "descricao": "Series temporais: Selic, IPCA, cambio, juros.",
        "exemplos": {"Selic": 432, "IPCA": 433, "Cambio": 1, "PIB": 4380},
    },
    "tesouro": {
        "nome": "Tesouro Nacional - Dados Abertos",
        "dominio": "financeiro", "tipo": "api_rest",
        "url": "https://www.tesourotransparente.gov.br/ckan/dataset/",
        "descricao": "Execucao orcamentaria, gastos publicos, divida.",
    },
    "cvm": {
        "nome": "CVM - Dados de Companhias Abertas",
        "dominio": "financeiro", "tipo": "ckan",
        "url": "http://dados.cvm.gov.br/api/",
        "descricao": "Demonstracoes financeiras, fundos, registros.",
    },
    "bndes_abertos": {
        "nome": "BNDES - Dados Abertos (CKAN)",
        "dominio": "financeiro", "tipo": "ckan",
        "url": "https://dadosabertos.bndes.gov.br/api/3/action/",
        "descricao": "Operacoes de financiamento, consultas, produtos.",
    },
    "siconfi": {
        "nome": "SICONFI - Dados Financeiros Municipais/Estaduais",
        "dominio": "financeiro", "tipo": "portal",
        "url": "https://siconfi.tesouro.gov.br/",
        "descricao": "Balancos municipais e estaduais, RGF, RREO.",
    },
    "bcb_estatisticas": {
        "nome": "Banco Central - Estatisticas Economicas",
        "dominio": "financeiro", "tipo": "portal",
        "url": "https://www.bcb.gov.br/estatisticas",
        "descricao": "Estatisticas: credito, moeda, financas, expectativas.",
    },

    # --- AMBIENTAL ---
    "inpe_queimadas": {
        "nome": "INPE - Programa Queimadas",
        "dominio": "ambiental", "tipo": "api_rest",
        "url": "https://queimadas.dgi.inpe.br/queimadas/api/",
        "descricao": "Focos de queimadas em tempo real, historico.",
    },
    "inpe_prodes": {
        "nome": "INPE - PRODES (Desmatamento Amazonia)",
        "dominio": "ambiental", "tipo": "portal",
        "url": "http://www.obt.inpe.br/OBT/",
        "descricao": "Taxas de desmatamento da Amazonia Legal.",
    },
    "ana": {
        "nome": "ANA - Agencia Nacional de Aguas",
        "dominio": "ambiental", "tipo": "portal_ckan",
        "url": "https://dadosabertos.ana.gov.br/",
        "descricao": "Recursos hidricos, estacoes pluviometricas, reservatorios.",
    },
    "mapbiomas": {
        "nome": "MapBiomas - Cobertura do Solo",
        "dominio": "ambiental", "tipo": "api_rest",
        "url": "https://mapbiomas.org/api",
        "descricao": "Mapeamento anual de cobertura do solo, transicoes 1985-2023.",
    },
    "icmbio": {
        "nome": "ICMBio - Unidades de Conservacao",
        "dominio": "ambiental", "tipo": "portal",
        "url": "https://www.gov.br/icmbio/",
        "descricao": "UCs federais, planos de manejo, biodiversidade.",
    },
    "gov_clima": {
        "nome": "Governo Federal - Dados Climaticos",
        "dominio": "ambiental", "tipo": "api_rest",
        "url": "https://clima.dados.gov.br/api",
        "descricao": "Dados climaticos historicos e projecoes para o Brasil.",
    },

    # --- GEOGRAFICO ---
    "ibge_malhas": {
        "nome": "IBGE - Malhas Territoriais",
        "dominio": "geografico", "tipo": "api_rest",
        "url": "https://servicodados.ibge.gov.br/api/v3/malhas/",
        "descricao": "Malhas municipais, estaduais, regionais em GeoJSON.",
    },
    "ibge_localidades": {
        "nome": "IBGE - Localidades",
        "dominio": "geografico", "tipo": "api_rest",
        "url": "https://servicodados.ibge.gov.br/api/v1/localidades/",
        "descricao": "Municipios, estados, regioes, distritos.",
    },
    "cprm": {
        "nome": "CPRM - Servico Geologico do Brasil",
        "dominio": "geografico", "tipo": "portal",
        "url": "https://www.cprm.gov.br/",
        "descricao": "Dados geologicos, hidrogeologicos, recursos minerais.",
    },
    "inpe_catalogo": {
        "nome": "INPE - Catalogo de Imagens de Satelite",
        "dominio": "geografico", "tipo": "portal",
        "url": "http://www.dgi.inpe.br/catalogo/",
        "descricao": "Imagens Landsat, CBERS, Amazonia-1.",
    },

    # --- ECONOMICO ---
    "ibge_sidra": {
        "nome": "IBGE - SIDRA",
        "dominio": "economico", "tipo": "api_rest",
        "url": "https://servicodados.ibge.gov.br/api/v3/agregados/",
        "descricao": "PIB, emprego, industria, servicos, agropecuaria.",
    },
    "ipeadata": {
        "nome": "IPEADATA - Series Macroeconomicas",
        "dominio": "economico", "tipo": "api_rest",
        "url": "http://www.ipeadata.gov.br/api/",
        "descricao": "Series historicas macroeconomicas, sociais, regionais.",
    },
    "dados_gov_br": {
        "nome": "Portal Brasileiro de Dados Abertos",
        "dominio": "economico", "tipo": "ckan",
        "url": "https://dados.gov.br/api/3/action/",
        "descricao": "Catalogo central de datasets governamentais.",
    },
    "banco_mundial": {
        "nome": "Banco Mundial - Indicadores",
        "dominio": "economico", "tipo": "api_rest",
        "url": "https://api.worldbank.org/v2/",
        "descricao": "Indicadores globais: PIB, Gini, educacao, saude.",
    },
    "rais": {
        "nome": "RAIS - Relacao Anual de Informacoes Sociais",
        "dominio": "economico", "tipo": "portal",
        "url": "https://bi.mte.gov.br/rais/",
        "descricao": "Empregos formais, salarios, vinculos por municipio/CNAE.",
    },

    # --- INSTITUCIONAL ---
    "camara": {
        "nome": "Camara dos Deputados - Dados Abertos",
        "dominio": "institucional", "tipo": "api_rest",
        "url": "https://dadosabertos.camara.leg.br/api/v2/",
        "descricao": "Proposicoes, deputados, votacoes, orcamento.",
    },
    "senado": {
        "nome": "Senado Federal - Dados Abertos",
        "dominio": "institucional", "tipo": "api_rest",
        "url": "https://legis.senado.leg.br/dadosabertos/",
        "descricao": "Materias legislativas, senadores, tramitacao.",
    },
    "tse": {
        "nome": "TSE - Dados Eleitorais",
        "dominio": "institucional", "tipo": "portal",
        "url": "https://dadosabertos.tse.jus.br/",
        "descricao": "Resultados eleitorais, candidatos, partidos.",
    },
    "datasus": {
        "nome": "DATASUS - Dados de Saude",
        "dominio": "institucional", "tipo": "portal",
        "url": "https://datasus.saude.gov.br/",
        "descricao": "Morbidade, mortalidade, producao ambulatorial.",
    },
    "ans": {
        "nome": "ANS - Saude Suplementar",
        "dominio": "institucional", "tipo": "portal",
        "url": "https://dadosabertos.ans.gov.br/",
        "descricao": "Operadoras de planos de saude, beneficiarios, indicadores.",
    },
    "anatel": {
        "nome": "ANATEL - Telecomunicacoes",
        "dominio": "institucional", "tipo": "portal",
        "url": "https://dados.anatel.gov.br/",
        "descricao": "Banda larga, telefonia, outorgas, indicadores do setor.",
    },
    "aneel": {
        "nome": "ANEEL - Setor Eletrico",
        "dominio": "institucional", "tipo": "portal_ckan",
        "url": "https://dadosabertos.aneel.gov.br/",
        "descricao": "Geracao, transmissao, distribuicao de energia eletrica.",
    },

    # --- INTERNACIONAL (NOVO) ---
    "fmi": {
        "nome": "FMI - Fundo Monetario Internacional (IMF DataMapper)",
        "dominio": "internacional", "tipo": "api_rest",
        "url": "https://www.imf.org/external/datamapper/api/v1/",
        "descricao": "Indicadores macroeconomicos globais: PIB, inflacao, contas externas.",
    },
    "onu_undata": {
        "nome": "ONU - UN Data (UNSD)",
        "dominio": "internacional", "tipo": "api_rest",
        "url": "https://data.un.org/ws/",
        "descricao": "Estatisticas globais: populacao, comercio, meio ambiente, ODS.",
    },
    "ocde": {
        "nome": "OCDE - OECD Data Explorer",
        "dominio": "internacional", "tipo": "api_rest",
        "url": "https://stats.oecd.org/sdmx-json/",
        "descricao": "Indicadores OCDE: PIB per capita, educacao, inovacao, emprego.",
    },
    "oms": {
        "nome": "OMS - World Health Organization (GHO)",
        "dominio": "internacional", "tipo": "api_rest",
        "url": "https://www.who.int/data/gho",
        "descricao": "Indicadores globais de saude: mortalidade, doencas, sistemas de saude.",
    },
    "brics": {
        "nome": "BRICS - Dados do Bloco",
        "dominio": "internacional", "tipo": "portal",
        "url": "https://infra.brics.org/api/",
        "descricao": "Indicadores comparativos: Brasil, Russia, India, China, Africa do Sul.",
    },
    "unctad": {
        "nome": "UNCTAD - Comercio e Desenvolvimento",
        "dominio": "internacional", "tipo": "portal",
        "url": "https://unctadstat.unctad.org/",
        "descricao": "Estatisticas de comercio internacional, investimento, desenvolvimento.",
    },
    "fao": {
        "nome": "FAO - Organizacao das Nacoes Unidas para Alimentacao e Agricultura (FAOSTAT)",
        "dominio": "internacional", "tipo": "api_rest",
        "url": "https://www.fao.org/faostat/en/#data/",
        "descricao": "Producao agricola, alimentos, seguranca alimentar, uso da terra, emissoes agropecuarias.",
        "dominios_dados": ["producao", "comercio", "seguranca_alimentar", "uso_solo", "emissoes", "precos"],
    },
    "oit": {
        "nome": "OIT - Organizacao Internacional do Trabalho (ILOSTAT)",
        "dominio": "internacional", "tipo": "api_rest",
        "url": "https://ilostat.ilo.org/data/",
        "descricao": "Estatisticas globais de trabalho: emprego, desemprego, salarios, condicoes de trabalho.",
        "indicadores": ["EMP_TEMP", "UNEMP", "EARNINGS", "LABOUR_FORCE", "WORKING_POOR", "CHILD_LABOUR"],
    },
    "unesco": {
        "nome": "UNESCO - Instituto de Estatisticas (UIS)",
        "dominio": "internacional", "tipo": "api_rest",
        "url": "https://uis.unesco.org/",
        "descricao": "Estatisticas de educacao, ciencia, tecnologia, cultura e comunicacao mundial.",
        "indicadores": ["EDUCATION", "SCIENCE", "CULTURE", "SDG4"],
    },
    "adb": {
        "nome": "ADB - Banco Asiatico de Desenvolvimento (Data Library)",
        "dominio": "internacional", "tipo": "api_rest",
        "url": "https://data.adb.org/",
        "descricao": "Indicadores economicos, projetos de desenvolvimento, pobreza, infraestrutura Asia-Pacifico.",
        "indicadores": ["GDP_GROWTH", "POVERTY", "INFRASTRUCTURE", "TRADE", "ENERGY"],
    },
}


def listar_fontes(dominio: str = "") -> List[dict]:
    """Lista fontes disponiveis, opcionalmente filtrando por dominio."""
    resultados = []
    for chave, meta in FONTES.items():
        if dominio and meta["dominio"] != dominio:
            continue
        resultados.append({
            "id": chave, "nome": meta["nome"], "dominio": meta["dominio"],
            "tipo": meta["tipo"], "descricao": meta["descricao"], "url": meta["url"],
        })
    return sorted(resultados, key=lambda x: (x["dominio"], x["id"]))


# =============================================================================
# CACHE
# =============================================================================

def _cache_key(prefix: str, *args) -> str:
    raw = f"{prefix}|{'|'.join(str(a) for a in args)}"
    return hashlib.md5(raw.encode()).hexdigest()

def _cache_get(key: str) -> Optional[Any]:
    p = CACHE_DIR / f"{key}.json"
    if p.exists():
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            if time.time() - d["ts"] < CACHE_TTL:
                return d["data"]
        except: pass
    return None

def _cache_set(key: str, data: Any):
    (CACHE_DIR / f"{key}.json").write_text(
        json.dumps({"ts": time.time(), "data": data}, ensure_ascii=False), encoding="utf-8")

def _fetch_json(url: str, timeout: int = 15) -> Optional[Any]:
    """Faz requisicao HTTP GET e retorna JSON."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"[erro] {url[:80]}: {e}", file=sys.stderr)
        return None


# =============================================================================
# EXTRATORES POR FONTE — FINANCEIRO
# =============================================================================

def extrair_bcb_sgs(codigo: int) -> Optional[List[dict]]:
    ck = _cache_key("bcb_sgs", codigo)
    cached = _cache_get(ck)
    if cached: return cached
    url = FONTES["bcb_sgs"]["url"].format(codigo=codigo)
    data = _fetch_json(f"{url}?formato=json")
    if data:
        _cache_set(ck, data)
    return data

def extrair_bndes_ckan(dataset_id: str = "aprovacoes") -> List[dict]:
    ck = _cache_key("bndes_ckan", dataset_id)
    cached = _cache_get(ck)
    if cached: return cached
    url = f"https://dadosabertos.bndes.gov.br/api/3/action/package_show?id={dataset_id}"
    data = _fetch_json(url)
    resultados = []
    if data:
        resources = data.get("result", {}).get("resources", [])
        for r in resources[:20]:
            resultados.append({
                "nome": r.get("name", ""), "url": r.get("url", ""),
                "formato": r.get("format", ""), "descricao": r.get("description", ""),
            })
    if not resultados:
        resultados = [
            {"nome": "BNDES Operacoes de Financiamento",
             "url": "https://dadosabertos.bndes.gov.br/dataset/aprovacoes", "formato": "CSV"},
            {"nome": "BNDES Linhas de Financiamento",
             "url": "https://www.bndes.gov.br/wps/portal/site/home/financiamento", "formato": "HTML"},
        ]
    _cache_set(ck, resultados)
    return resultados

def extrair_tesouro() -> List[dict]:
    return [
        {"nome": "Execucao Orcamentaria", "url": "https://www.tesourotransparente.gov.br/ckan/dataset/execucao-orcamentaria", "formato": "CSV"},
        {"nome": "Gastos por Orgao", "url": "https://www.tesourotransparente.gov.br/ckan/dataset/gastos-orgao", "formato": "CSV"},
        {"nome": "Divida Publica", "url": "https://www.tesourotransparente.gov.br/ckan/dataset/divida-publica", "formato": "CSV"},
        {"nome": "Transferencias a Estados e Municipios", "url": "https://www.tesourotransparente.gov.br/ckan/dataset/transferencias", "formato": "CSV"},
    ]


# =============================================================================
# EXTRATORES — AMBIENTAL
# =============================================================================

def extrair_inpe_queimadas(estado: str = "SP", dias: int = 7) -> Optional[dict]:
    ck = _cache_key("inpe_queimadas", estado, dias)
    cached = _cache_get(ck)
    if cached: return cached
    url = f"https://queimadas.dgi.inpe.br/queimadas/api/focos?estado={estado}&dias={dias}"
    data = _fetch_json(url)
    if data: _cache_set(ck, data)
    return data

def extrair_mapbiomas() -> List[dict]:
    return [
        {"nome": "Colecao MapBiomas - Cobertura do Solo", "url": "https://mapbiomas.org/download",
         "descricao": "Mapeamento anual 1985-2023"},
        {"nome": "MapBiomas Fogo", "url": "https://fogo.mapbiomas.org/download",
         "descricao": "Area queimada por ano"},
        {"nome": "MapBiomas Agua", "url": "https://agua.mapbiomas.org/download",
         "descricao": "Superficie de agua anual"},
    ]

def extrair_ana() -> List[dict]:
    return [
        {"nome": "Estacoes Pluviometricas", "url": "https://dadosabertos.ana.gov.br/dataset/estacoes-pluviometricas",
         "descricao": "Dados de precipitacao em todo Brasil"},
        {"nome": "Reservatorios do SIN", "url": "https://dadosabertos.ana.gov.br/dataset/reservatorios-sin",
         "descricao": "Niveis de reservatorios do Sistema Interligado Nacional"},
        {"nome": "Qualidade da Agua", "url": "https://dadosabertos.ana.gov.br/dataset/qualidade-agua",
         "descricao": "Indices de qualidade da agua por estacao"},
    ]

def extrair_gov_clima() -> List[dict]:
    return [
        {"nome": "Dados Climaticos Historicos", "url": "https://clima.dados.gov.br/dados-historico",
         "descricao": "Series historicas de temperatura e precipitacao"},
        {"nome": "Projecoes Climaticas", "url": "https://clima.dados.gov.br/projecoes",
         "descricao": "Cenarios climaticos futuros para o Brasil"},
    ]


# =============================================================================
# EXTRATORES — GEOGRAFICO
# =============================================================================

def extrair_ibge_localidades(nivel: str = "municipios") -> Optional[List[dict]]:
    ck = _cache_key("ibge_localidades", nivel)
    cached = _cache_get(ck)
    if cached: return cached
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/{nivel}"
    data = _fetch_json(url)
    if data and isinstance(data, list):
        resumo = []
        for item in data:
            resumo.append({
                "id": item.get("id"), "nome": item.get("nome"),
                "microrregiao": item.get("microrregiao", {}).get("nome") if isinstance(item.get("microrregiao"), dict) else None,
                "uf": item.get("UF", {}).get("sigla") if isinstance(item.get("UF"), dict) else
                      (item.get("microrregiao", {}).get("UF", {}).get("sigla") if isinstance(item.get("microrregiao"), dict) else None),
            })
        _cache_set(ck, resumo)
        return resumo
    return None

def extrair_ibge_malha(uf: str = "SP") -> dict:
    return {"tipo": "GeoJSON", "url": f"https://servicodados.ibge.gov.br/api/v3/malhas/estados/{uf}?formato=application/vnd.geo+json", "uf": uf}


# =============================================================================
# EXTRATORES — ECONOMICO
# =============================================================================

def extrair_ibge_sidra(agregado: int = 5938) -> Optional[list]:
    ck = _cache_key("ibge_sidra", agregado)
    cached = _cache_get(ck)
    if cached: return cached
    url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{agregado}/periodos/-4/variaveis?local=N1[all]"
    data = _fetch_json(url)
    if data: _cache_set(ck, data)
    return data

def extrair_banco_mundial(indicador: str = "NY.GDP.MKTP.CD", pais: str = "BR") -> Optional[List[dict]]:
    ck = _cache_key("banco_mundial", indicador, pais)
    cached = _cache_get(ck)
    if cached: return cached
    url = f"https://api.worldbank.org/v2/country/{pais}/indicator/{indicador}?format=json&per_page=20"
    data = _fetch_json(url)
    if data and len(data) > 1:
        valores = []
        for item in data[1]:
            if item.get("value"):
                valores.append({"ano": item.get("date"), "valor": item.get("value")})
        _cache_set(ck, valores)
        return valores
    return None

def extrair_dados_gov_br(query: str = "economia") -> List[dict]:
    ck = _cache_key("dados_gov_br", query)
    cached = _cache_get(ck)
    if cached: return cached
    url = f"https://dados.gov.br/api/3/action/package_search?q={urllib.parse.quote(query)}&rows=10"
    data = _fetch_json(url)
    resultados = []
    if data:
        for pkg in data.get("result", {}).get("results", []):
            resultados.append({
                "titulo": pkg.get("title", ""), "descricao": pkg.get("notes", "")[:200],
                "url": pkg.get("landing_page", ""),
                "orgao": pkg.get("organization", {}).get("title") if isinstance(pkg.get("organization"), dict) else "",
            })
    _cache_set(ck, resultados)
    return resultados

def extrair_rais() -> List[dict]:
    return [
        {"nome": "RAIS Vinculos Empregaticios", "url": "https://bi.mte.gov.br/rais/",
         "descricao": "Base de vinculos formais por ano, municipio e CNAE"},
        {"nome": "CAGED - Cadastro Geral de Empregados e Desempregados",
         "url": "https://www.gov.br/trabalho-e-previdencia/pt-br/assuntos/caged",
         "descricao": "Admissoes e demissoes mensais por setor"},
    ]


# =============================================================================
# EXTRATORES — INSTITUCIONAL
# =============================================================================

def extrair_camara(sigla: str = "PL", ano: int = 2026) -> Optional[List[dict]]:
    ck = _cache_key("camara", sigla, ano)
    cached = _cache_get(ck)
    if cached: return cached
    url = f"https://dadosabertos.camara.leg.br/api/v2/proposicoes?siglaTipo={sigla}&ano={ano}&itens=10"
    data = _fetch_json(url)
    if data:
        props = data.get("dados", [])
        resumo = [{"id": p.get("id"), "ementa": p.get("ementa", "")[:150],
                    "autor": p.get("autor", {}).get("nome") if isinstance(p.get("autor"), dict) else "",
                    "situacao": p.get("situacao", "")} for p in props]
        _cache_set(ck, resumo)
        return resumo
    return None

def extrair_ans() -> List[dict]:
    return [
        {"nome": "Beneficiarios de Planos de Saude",
         "url": "https://dadosabertos.ans.gov.br/dataset/beneficiarios",
         "descricao": "Beneficiarios por operadora, faixa etaria e UF"},
        {"nome": "Indicadores de Qualidade",
         "url": "https://dadosabertos.ans.gov.br/dataset/indicadores",
         "descricao": "Indicadores assistenciais e economicos das operadoras"},
    ]

def extrair_anatel() -> List[dict]:
    return [
        {"nome": "Banda Larga Fixa",
         "url": "https://dados.anatel.gov.br/dataset/banda-larga-fixa",
         "descricao": "Acessos de banda larga por municipio e velocidade"},
        {"nome": "Telefonia Movel",
         "url": "https://dados.anatel.gov.br/dataset/telefonia-movel",
         "descricao": "Acessos de telefonia movel por operadora e UF"},
    ]

def extrair_aneel() -> List[dict]:
    return [
        {"nome": "Geracao de Energia",
         "url": "https://dadosabertos.aneel.gov.br/dataset/geracao",
         "descricao": "Dados de geracao eletrica por fonte e usina"},
        {"nome": "Consumo de Energia",
         "url": "https://dadosabertos.aneel.gov.br/dataset/consumo",
         "descricao": "Consumo de energia por classe e regiao"},
    ]


# =============================================================================
# EXTRATORES — INTERNACIONAL (NOVO v2.0)
# =============================================================================

def extrair_fmi(indicador: str = "NGDPD", pais: str = "BR") -> Optional[dict]:
    """Extrai dados do FMI DataMapper.

    Indicadores comuns:
        NGDPD - PIB nominal (US$)
        NGDP_R - PIB real (crescimento %)
        PCPI - Inflacao (IPC)
        BCA - Conta corrente (US$)
        LUR - Taxa de desemprego
    """
    ck = _cache_key("fmi", indicador, pais)
    cached = _cache_get(ck)
    if cached: return cached
    url = f"https://www.imf.org/external/datamapper/api/v1/{indicador}/{pais}"
    data = _fetch_json(url)
    if data:
        valores = (data.get("values", {}) or data.get("data", {}))
        if not valores:
            valores = data
        resultado = {"indicador": indicador, "pais": pais, "dados": valores}
        _cache_set(ck, resultado)
        return resultado
    return {"indicador": indicador, "pais": pais, "dados": {}, "nota": "Fallback - FMI pode exigir URL especifica"}

def extrair_onu(indicador: str = "POP") -> Optional[List[dict]]:
    """Extrai dados da ONU (UN Data).

    Indicadores comuns:
        POP - Populacao
        GDP - PIB
        TRD - Comercio
        ENV - Meio ambiente
    """
    ck = _cache_key("onu", indicador)
    cached = _cache_get(ck)
    if cached: return cached
    url = f"https://data.un.org/ws/rest/data/UNSD,{indicador},1.0/.all?format=jsondata"
    data = _fetch_json(url)
    if data:
        _cache_set(ck, data)
        return data
    return [{"nome": "ONU UNData API", "nota": f"Indicador: {indicador}. Consulte https://data.un.org para detalhes."}]

def extrair_ocde(indicador: str = "GDP", pais: str = "BRA") -> Optional[dict]:
    """Extrai dados da OCDE via SDMX-JSON.

    Indicadores comuns:
        GDP - PIB
        UNEMP - Desemprego
        EDU - Educacao
        INNO - Inovacao
    """
    ck = _cache_key("ocde", indicador, pais)
    cached = _cache_get(ck)
    if cached: return cached
    url = f"https://stats.oecd.org/sdmx-json/data/{indicador}/{pais}/all?contentType=json"
    data = _fetch_json(url)
    resultado = {"indicador": indicador, "pais": pais, "dados": data}
    if not data:
        resultado["nota"] = f"OCDE SDMX fallback. Dataset: {indicador}. Tente dataset completo em https://stats.oecd.org"
        resultado["url_referencia"] = f"https://stats.oecd.org/index.aspx?DataSetCode={indicador}"
    _cache_set(ck, resultado)
    return resultado

def extrair_oms(indicador: str = "WHOSIS_000001") -> Optional[List[dict]]:
    """Extrai indicadores da OMS (GHO).

    Indicadores comuns:
        WHOSIS_000001 - Expectativa de vida
        WHOSIS_000003 - Mortalidade infantil
        WHOSIS_000015 - Diabetes prevalence
    """
    ck = _cache_key("oms", indicador)
    cached = _cache_get(ck)
    if cached: return cached
    url = f"https://ghoapi.azureedge.net/api/{indicador}"
    data = _fetch_json(url)
    if data:
        valores = []
        for item in (data.get("value", []) or [])[:20]:
            valores.append({
                "ano": item.get("TimeDim", ""),
                "pais": item.get("SpatialDim", ""),
                "valor": item.get("NumericValue"),
                "fator": item.get("Dim1", ""),
            })
        _cache_set(ck, valores)
        return valores
    return [{"indicador": indicador, "nota": "Consulte https://www.who.int/data/gho para datasets"}]

def extrair_brics() -> List[dict]:
    """Retorna dados do BRICS."""
    return [
        {"nome": "BRICS Infrastructure Data", "url": "https://infra.brics.org/",
         "descricao": "Dados de infraestrutura dos paises BRICS"},
        {"nome": "New Development Bank (NDB)", "url": "https://www.ndb.int/",
         "descricao": "Projetos financiados pelo Banco do BRICS"},
        {"nome": "BRICS Science and Technology", "url": "https://brics-sti.org/",
         "descricao": "Indicadores de Ciencia, Tecnologia e Inovacao BRICS"},
    ]

def extrair_unctad() -> List[dict]:
    """Retorna dados UNCTAD."""
    return [
        {"nome": "UNCTAD Stat - Trade", "url": "https://unctadstat.unctad.org/datacentre/",
         "descricao": "Estatisticas de comercio internacional por pais e produto"},
        {"nome": "World Investment Report", "url": "https://unctad.org/fdi",
         "descricao": "Fluxos de investimento estrangeiro direto (FDI)"},
        {"nome": "UNCTAD Technology and Innovation",
         "url": "https://unctad.org/topic/science-technology-and-innovation",
         "descricao": "Indicadores de tecnologia e inovacao para desenvolvimento"},
    ]


# =============================================================================
# EXTRATORES — NOVAS FONTE INTERNACIONAIS (FAO, OIT, UNESCO, ADB) v2.1
# =============================================================================

def extrair_fao(dominio: str = "producao") -> List[dict]:
    """Retorna dados da FAO (FAOSTAT).

    Dominios FAOSTAT:
        producao - Producao agricola por cultura e pais
        comercio - Comercio internacional de alimentos
        seguranca_alimentar - Indicadores de seguranca alimentar
        uso_solo - Uso e cobertura do solo
        emissoes - Emissoes de gases de efeito estufa da agropecuaria
        precos - Precos de alimentos ao produtor e consumidor
    """
    ck = _cache_key("fao", dominio)
    cached = _cache_get(ck)
    if cached:
        return cached
    base_url = f"https://fenixservices.fao.org/faostat/api/v1/en/{dominio}"
    data = _fetch_json(base_url, timeout=20)
    if data and isinstance(data, dict):
        itens = data.get("data", []) or list(data.values())
        resumo = []
        for item in (itens if isinstance(itens, list) else [])[:15]:
            resumo.append({
                "area": item.get("Area", "") or item.get("area", ""),
                "produto": item.get("Item", "") or item.get("item", ""),
                "ano": item.get("Year", "") or item.get("year", "") or item.get("Time", ""),
                "valor": item.get("Value", "") or item.get("value", ""),
                "unidade": item.get("Unit", "") or item.get("unit", ""),
            })
        if resumo:
            _cache_set(ck, resumo)
            return resumo
    return [
        {"dominio": dominio,
         "url_referencia": f"https://www.fao.org/faostat/en/#data/{dominio.upper()}",
         "descricao": f"Dados FAOSTAT sobre {dominio}. Consulte a pagina oficial para datasets completos.",
         "formatos": ["CSV", "JSON", "SDMX"],
         "atualizacao": "Anual"},
    ]


def extrair_oit(indicador: str = "EMP_TEMP") -> Optional[List[dict]]:
    """Extrai dados da OIT (ILOSTAT).

    Indicadores comuns:
        EMP_TEMP - Emprego total (milhares)
        UNEMP - Taxa de desemprego (%)
        EARNINGS - Rendimentos medios (US$)
        LABOUR_FORCE - Forca de trabalho
        WORKING_POOR - Trabalhadores pobres (%)
        CHILD_LABOUR - Trabalho infantil (%)
    """
    ck = _cache_key("oit", indicador)
    cached = _cache_get(ck)
    if cached:
        return cached
    url = f"https://www.ilo.org/shinyapps/bulkexport/Stat/datos/df='{indicador}'?format=json"
    data = _fetch_json(url, timeout=20)
    if data:
        observacoes = []
        for obs in (data.get("obs", []) if isinstance(data, dict) else data)[:20]:
            observacoes.append({
                "pais": obs.get("Geographic area", "") or obs.get("area", ""),
                "ano": obs.get("Time", "") or obs.get("year", ""),
                "valor": obs.get("Observation value", "") or obs.get("value", ""),
                "sexo": obs.get("Sex", "") or obs.get("sex", ""),
            })
        if observacoes:
            _cache_set(ck, observacoes)
            return observacoes
    return [
        {"indicador": indicador,
         "url_referencia": f"https://ilostat.ilo.org/data/?indicator={indicador}",
         "descricao": f"Indicador ILOSTAT: {indicador}. Consulte https://ilostat.ilo.org para series completas.",
         "cobertura": "Global (190+ paises)",
         "frequencia": "Anual/Trimestral"},
    ]


def extrair_unesco(indicador: str = "EDUCATION") -> List[dict]:
    """Retorna dados da UNESCO (UIS).

    Indicadores comuns:
        EDUCATION - Indicadores educacionais (matriculas, conclusao, alfabetizacao)
        SCIENCE - Gasto em P&D, pesquisadores, publicacoes
        CULTURE - Patrimonio cultural, industrias criativas
        SDG4 - Indicadores ODS 4 (educacao de qualidade)
    """
    ck = _cache_key("unesco", indicador)
    cached = _cache_get(ck)
    if cached:
        return cached
    url = f"https://api.uis.unesco.org/api/indicator/{indicador}?format=json"
    data = _fetch_json(url, timeout=20)
    if data:
        indicadores = []
        for item in (data if isinstance(data, list) else data.get("data", []) or data.get("results", []))[:15]:
            indicadores.append({
                "pais": item.get("country", "") or item.get("COUNTRY", ""),
                "ano": item.get("year", "") or item.get("YEAR", "") or item.get("TIME_PERIOD", ""),
                "valor": item.get("value", "") or item.get("VALUE", ""),
                "indicador": item.get("indicator", "") or item.get("INDICATOR", ""),
            })
        if indicadores:
            _cache_set(ck, indicadores)
            return indicadores
    return [
        {"indicador": indicador,
         "url_referencia": "https://uis.unesco.org/",
         "descricao": f"Dados UNESCO UIS sobre {indicador}. Consulte https://uis.unesco.org para downloads.",
         "fontes": ["UIS API", "SDG Global Database", "UNESCO DataHub"],
         "cobertura": "Global (200+ paises)"},
    ]


def extrair_adb(indicador: str = "GDP_GROWTH") -> Optional[List[dict]]:
    """Extrai dados do ADB (Banco Asiatico de Desenvolvimento).

    Indicadores comuns:
        GDP_GROWTH - Crescimento do PIB (%)
        POVERTY - Taxa de pobreza (%)
        INFRASTRUCTURE - Indice de infraestrutura
        TRADE - Comercio como % do PIB
        ENERGY - Acesso a energia eletrica (%)
    """
    ck = _cache_key("adb", indicador)
    cached = _cache_get(ck)
    if cached:
        return cached
    url = f"https://data.adb.org/api/indicator/{indicador}?format=json&per_page=20"
    data = _fetch_json(url, timeout=20)
    if data:
        itens = []
        for item in (data if isinstance(data, list) else data.get("data", []) or data.get("result", []))[:20]:
            itens.append({
                "economia": item.get("economy", "") or item.get("country", ""),
                "ano": item.get("year", "") or item.get("TIME", ""),
                "valor": item.get("value", "") or item.get("VALUE", ""),
                "unidade": item.get("unit", "") or item.get("UNIT", ""),
            })
        if itens:
            _cache_set(ck, itens)
            return itens
    return [
        {"indicador": indicador,
         "url_referencia": f"https://data.adb.org/search?keywords={indicador.lower()}",
         "descricao": f"Dados ADB sobre {indicador}. Consulte https://data.adb.org para datasets.",
         "regiao": "Asia-Pacifico (49 economias membros)",
         "formatos": ["CSV", "JSON", "XLSX"]},
    ]


# =============================================================================
# ORQUESTRADOR PRINCIPAL
# =============================================================================

EXTRATORES = {
    # Financeiro
    "bcb_sgs": lambda q, k: extrair_bcb_sgs(int(q) if q and q.isdigit() else 432),
    "bndes_abertos": lambda q, k: extrair_bndes_ckan(q or "aprovacoes"),
    "tesouro": lambda q, k: extrair_tesouro(),
    # Ambiental
    "inpe_queimadas": lambda q, k: extrair_inpe_queimadas(q or "SP"),
    "mapbiomas": lambda q, k: extrair_mapbiomas(),
    "ana": lambda q, k: extrair_ana(),
    "gov_clima": lambda q, k: extrair_gov_clima(),
    # Geografico
    "ibge_localidades": lambda q, k: extrair_ibge_localidades(q or "municipios"),
    "ibge_malha": lambda q, k: extrair_ibge_malha(q or "SP"),
    # Economico
    "ibge_sidra": lambda q, k: extrair_ibge_sidra(int(q) if q and q.isdigit() else 5938),
    "banco_mundial": lambda q, k: extrair_banco_mundial(q or "NY.GDP.MKTP.CD"),
    "dados_gov_br": lambda q, k: extrair_dados_gov_br(q or "economia"),
    "rais": lambda q, k: extrair_rais(),
    # Institucional
    "camara": lambda q, k: extrair_camara(q or "PL"),
    "ans": lambda q, k: extrair_ans(),
    "anatel": lambda q, k: extrair_anatel(),
    "aneel": lambda q, k: extrair_aneel(),
    # Internacional
    "fmi": lambda q, k: extrair_fmi(q or "NGDPD"),
    "onu_undata": lambda q, k: extrair_onu(q or "POP"),
    "ocde": lambda q, k: extrair_ocde(q or "GDP"),
    "oms": lambda q, k: extrair_oms(q or "WHOSIS_000001"),
    "brics": lambda q, k: extrair_brics(),
    "unctad": lambda q, k: extrair_unctad(),
    "fao": lambda q, k: extrair_fao(q or "producao"),
    "oit": lambda q, k: extrair_oit(q or "EMP_TEMP"),
    "unesco": lambda q, k: extrair_unesco(q or "EDUCATION"),
    "adb": lambda q, k: extrair_adb(q or "GDP_GROWTH"),
}


def buscar_por_dominio(dominio: str, query: str = "", max_resultados: int = 10) -> List[dict]:
    """Busca dados em todas as fontes de um dominio."""
    resultados = []
    fontes = listar_fontes(dominio)
    for fonte in fontes:
        fid = fonte["id"]
        extrator = EXTRATORES.get(fid)
        if not extrator:
            continue
        try:
            dados = extrator(query, max_resultados)
            if dados:
                resultados.append({
                    "fonte": fonte["nome"], "fonte_id": fid, "dominio": dominio,
                    "dados": dados if isinstance(dados, list) else [dados],
                    "total": len(dados) if isinstance(dados, list) else 1,
                })
        except Exception as e:
            resultados.append({"fonte": fonte["nome"], "fonte_id": fid, "dominio": dominio, "erro": str(e)})
    return resultados


def extrair_url_para_dataset(url: str) -> Optional[dict]:
    """Tenta identificar e extrair dados de uma URL publica."""
    url_lower = url.lower()
    match = re.search(r'bcb\.gov\.br.*sgs.*codigo[=/](\d+)', url_lower)
    if match:
        dados = extrair_bcb_sgs(int(match.group(1)))
        return {"fonte": "bcb_sgs", "dados": dados}
    if "ibge.gov.br" in url_lower and "localidades" in url_lower:
        nivel = "municipios"
        for n in ["municipios", "estados", "regioes", "distritos"]:
            if n in url_lower: nivel = n; break
        dados = extrair_ibge_localidades(nivel)
        return {"fonte": "ibge_localidades", "dados": dados}
    if "dadosabertos.bndes.gov.br" in url_lower:
        match = re.search(r'dataset/(\w+)', url_lower)
        did = match.group(1) if match else "aprovacoes"
        dados = extrair_bndes_ckan(did)
        return {"fonte": "bndes_abertos", "dados": dados}
    if "dados.gov.br" in url_lower:
        query = re.search(r'q=([^&]+)', url_lower)
        q = urllib.parse.unquote(query.group(1)) if query else "dados"
        dados = extrair_dados_gov_br(q)
        return {"fonte": "dados_gov_br", "dados": dados}
    if "worldbank.org" in url_lower:
        match = re.search(r'indicador[/.]([\w.]+)', url_lower)
        ind = match.group(1) if match else "NY.GDP.MKTP.CD"
        dados = extrair_banco_mundial(ind)
        return {"fonte": "banco_mundial", "dados": dados}
    if "imf.org" in url_lower:
        match = re.search(r'/(\w+)/(\w+)', url_lower)
        ind = match.group(1) if match else "NGDPD"
        dados = extrair_fmi(ind)
        return {"fonte": "fmi", "dados": dados}
    return {"erro": "URL nao reconhecida. Use buscar() para encontrar datasets primeiro."}


def buscar_multidominio(query: str, dominios: Optional[List[str]] = None) -> Dict[str, list]:
    """Busca em multiplos dominios simultaneamente."""
    if dominios is None:
        dominios = ["financeiro", "ambiental", "geografico", "economico", "institucional", "internacional"]
    resultados = {}
    for d in dominios:
        resultados[d] = buscar_por_dominio(d, query)
    return resultados


# =============================================================================
# SERVIDOR HTTP
# =============================================================================

def iniciar_servidor(porta: int = 8082):
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            if self.path == "/":
                self._respond(200, json.dumps({
                    "servico": "extrator-dados-publicos", "versao": "2.1",
                    "dominios": ["financeiro", "ambiental", "geografico", "economico", "institucional", "internacional"],
                    "fontes": len(FONTES),  # 38
                    "endpoints": {
                        "/fontes": "Lista todas as fontes",
                        "/fontes?dominio=internacional": "Filtra por dominio",
                        "/buscar?dominio=financeiro&q=selic": "Busca dados",
                        "/extrair?url=https://...": "Extrai de URL",
                        "/multidominio?q=pib": "Busca em todos os dominios",
                    }
                }, ensure_ascii=False).encode())
            elif self.path == "/fontes":
                dominio = params.get("dominio", [""])[0]
                fontes = listar_fontes(dominio)
                self._respond(200, json.dumps(fontes, ensure_ascii=False).encode())
            elif self.path.startswith("/buscar"):
                dominio = params.get("dominio", [""])[0]
                q = params.get("q", [""])[0]
                if not dominio: self._respond(400, b'{"erro":"parametro dominio obrigatorio"}'); return
                resultados = buscar_por_dominio(dominio, q)
                self._respond(200, json.dumps(resultados, ensure_ascii=False).encode())
            elif self.path.startswith("/extrair"):
                url = params.get("url", [""])[0]
                if not url: self._respond(400, b'{"erro":"parametro url obrigatorio"}'); return
                resultado = extrair_url_para_dataset(url)
                self._respond(200, json.dumps(resultado, ensure_ascii=False).encode())
            elif self.path.startswith("/multidominio"):
                q = params.get("q", [""])[0]
                resultados = buscar_multidominio(q)
                self._respond(200, json.dumps(resultados, ensure_ascii=False).encode())
            else:
                self._respond(404, b'{"erro":"endpoint nao encontrado"}')
        def _respond(self, code, body):
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
    print(f"[extrator v2.0] Servidor em http://localhost:{porta}")
    HTTPServer(("0.0.0.0", porta), Handler).serve_forever()


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse
    p = argparse.ArgumentParser(description="Extrator de Dados Publicos v2.1")
    p.add_argument("comando", nargs="?", default="listar-fontes",
                   choices=["listar-fontes", "buscar", "extrair", "servidor", "multidominio"])
    p.add_argument("--dominio", help="Filtrar por dominio")
    p.add_argument("--q", "--query", help="Termo de busca")
    p.add_argument("--url", help="URL para extracao")
    p.add_argument("--porta", type=int, default=8082, help="Porta do servidor")
    p.add_argument("--json", action="store_true", help="Saida JSON")
    args = p.parse_args()

    if args.comando == "servidor":
        return iniciar_servidor(args.porta)

    if args.comando == "listar-fontes":
        fontes = listar_fontes(args.dominio or "")
        if args.json:
            print(json.dumps(fontes, ensure_ascii=False, indent=2))
        else:
            print(f"\n=== FONTES DE DADOS PUBLICOS v2.1 ({len(fontes)} encontradas) ===\n")
            ant_d = ""
            for f in fontes:
                if f["dominio"] != ant_d:
                    print(f"\n--- {f['dominio'].upper()} ---")
                    ant_d = f["dominio"]
                print(f"  [{f['id']}] {f['nome']}")
                print(f"         {f['descricao'][:100]}")
                print(f"         Tipo: {f['tipo']}")
        return

    if args.comando == "buscar":
        if not args.dominio: print("Erro: --dominio obrigatorio para busca"); return
        resultados = buscar_por_dominio(args.dominio, args.q or "")
        if args.json:
            print(json.dumps(resultados, ensure_ascii=False, indent=2))
        else:
            print(f"\n=== BUSCA: {args.dominio} / '{args.q or ''}' ===\n")
            for r in resultados:
                fonte = r["fonte"]; dados = r.get("dados", []); erro = r.get("erro")
                print(f"[{fonte}] {len(dados)} resultados" if dados else f"[{fonte}] ERRO: {erro}")
                for d in (dados or [])[:3]:
                    nome = d.get("nome") or d.get("titulo") or d.get("ano", "")
                    url = d.get("url", "")
                    print(f"  - {str(nome)[:80]}")
                    print(f"    {str(url)[:90]}")
        return

    if args.comando == "extrair":
        if not args.url: print("Erro: --url obrigatorio"); return
        resultado = extrair_url_para_dataset(args.url)
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return

    if args.comando == "multidominio":
        resultados = buscar_multidominio(args.q or "")
        print(json.dumps(resultados, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
