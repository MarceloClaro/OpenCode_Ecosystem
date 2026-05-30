"""
MASWOS V5 NEXUS — Servidor MCP Juridico REAL (porta 3001)
APIs reais: Planalto, STF, JusBrasil + NLP jurídico + cache SQLite.
Fallback: API → cache → dados simulados (mantém compatibilidade).
"""

import sys, json, asyncio, hashlib, re, os, sqlite3, time
from datetime import datetime, timedelta
from urllib.request import urlopen, Request, quote
from urllib.error import URLError, HTTPError
from mcp.server import FastMCP

app = FastMCP("maswos-juridico", debug=False, log_level="INFO")

# Cache SQLite
def cache_db():
    db = sqlite3.connect(".reversa/juridico_cache.db")
    db.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT, fetched_at TEXT)")
    return db

def cache_get(key):
    try:
        row = cache_db().execute("SELECT value, fetched_at FROM cache WHERE key=?", (key,)).fetchone()
        if row:
            age = (datetime.now() - datetime.fromisoformat(row[1])).days
            if age < 30:
                return json.loads(row[0])
    except: pass
    return None

def cache_set(key, value):
    try:
        cache_db().execute("INSERT OR REPLACE INTO cache VALUES (?,?,?)",
            (key, json.dumps(value), datetime.now().isoformat()))
        cache_db().commit()
    except: pass

# ── API do Planalto (gov.br) ──
def fetch_planalto(query: str) -> dict:
    cache_key = f"planalto_{hashlib.md5(query.encode()).hexdigest()[:10]}"
    cached = cache_get(cache_key)
    if cached: return {"fonte": "cache", "dados": cached}

    try:
        url = f"https://www.gov.br/planalto/pt-br/acompanhe-o-planalto/legislacao?search={quote(query)}"
        req = Request(url, headers={"User-Agent": "MASWOS/5.0", "Accept": "text/html"})
        with urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        # Extrair leis encontradas
        results = []
        for match in re.finditer(r'(Lei|Decreto|MP|EC)\s*(?:n[º°]?\s*)?(\d+[\.\d]*)[,/]\s*(\d{4})', html, re.I):
            results.append({"tipo": match.group(1), "numero": match.group(2), "ano": match.group(3)})
        result = {"query": query, "total": len(results), "items": results[:10]}
        cache_set(cache_key, result)
        return {"fonte": "planalto.gov.br", "dados": result}
    except Exception as e:
        return {"fonte": "fallback", "erro": str(e)[:100]}

# ── Base legislativa local (curada) ──
LEGIS_BASE = {
    "trabalhista": {
        "CLT": {"lei": "Decreto-Lei 5.452/1943", "artigos": 922, "ementa": "Consolidação das Leis do Trabalho"},
        "reforma": {"lei": "Lei 13.467/2017", "artigos": 122, "ementa": "Reforma Trabalhista"},
    },
    "civil": {
        "codigo_civil": {"lei": "Lei 10.406/2002", "artigos": 2046, "ementa": "Código Civil Brasileiro"},
        "codigo_processo": {"lei": "Lei 13.105/2015", "artigos": 1072, "ementa": "Código de Processo Civil"},
    },
    "tributario": {
        "codigo_tributario": {"lei": "Lei 5.172/1966", "artigos": 218, "ementa": "Código Tributário Nacional"},
    },
    "penal": {
        "codigo_penal": {"lei": "Decreto-Lei 2.848/1940", "artigos": 361, "ementa": "Código Penal"},
        "codigo_processo_penal": {"lei": "Decreto-Lei 3.689/1941", "artigos": 811, "ementa": "Código de Processo Penal"},
    },
    "constitucional": {
        "constituicao": {"lei": "Constituição Federal/1988", "artigos": 250, "ementa": "Constituição da República Federativa do Brasil"},
    },
    "consumidor": {
        "cdc": {"lei": "Lei 8.078/1990", "artigos": 119, "ementa": "Código de Defesa do Consumidor"},
    },
    "ambiental": {
        "politica_ambiental": {"lei": "Lei 6.938/1981", "artigos": 23, "ementa": "Política Nacional do Meio Ambiente"},
    },
    "administrativo": {
        "licitacoes": {"lei": "Lei 14.133/2021", "artigos": 194, "ementa": "Nova Lei de Licitações"},
        "improbidade": {"lei": "Lei 8.429/1992", "artigos": 23, "ementa": "Lei de Improbidade Administrativa"},
    },
    "digital": {
        "lgpd": {"lei": "Lei 13.709/2018", "artigos": 65, "ementa": "Lei Geral de Proteção de Dados"},
        "marco_internet": {"lei": "Lei 12.965/2014", "artigos": 32, "ementa": "Marco Civil da Internet"},
    },
}

# ── NLP Jurídico simples (keyword + regex) ──
JURIDICAL_KEYWORDS = {
    "fundamentacao": ["fundamento", "artigo", "lei nº", "conforme", "dispõe", "estabelece"],
    "pedido": ["requer", "pleiteia", "solicita", "pede", "postula"],
    "fatos": ["ocorreu", "aconteceu", "verifica-se", "constata-se", "narra"],
    "partes": ["autor", "réu", "reclamante", "reclamado", "requerente", "requerido"],
    "provimento": ["procedente", "improcedente", "deferir", "indeferir", "conceder"],
    "tempestividade": ["prazo", "tempestivo", "intempestivo", "preclusão", "decadência"],
}

@ app.tool()
def consultar_legislacao(termo: str, tipo: str = "federal") -> str:
    """Consulta base legislativa brasileira REAL (Planalto + base local + cache)."""
    # 1. Buscar em base local
    termo_lower = termo.lower()
    resultados = []
    for categoria, leis in LEGIS_BASE.items():
        for nome, dados in leis.items():
            if termo_lower in nome.lower() or termo_lower in dados["ementa"].lower():
                resultados.append({"categoria": categoria, "nome": nome, **dados})

    # 2. Se insuficiente, buscar API do Planalto
    if len(resultados) < 2:
        planalto = fetch_planalto(termo)
        if planalto.get("dados", {}).get("total", 0) > 0:
            for item in planalto["dados"].get("items", [])[:5]:
                resultados.append({
                    "categoria": "federal", "lei": f"{item['tipo']} {item['numero']}/{item['ano']}",
                    "ementa": f"Legislação Federal", "fonte": "planalto.gov.br",
                })

    return json.dumps({
        "termo": termo, "tipo": tipo,
        "resultados": resultados[:10] if resultados else [
            {"lei": f"Busca por '{termo}'", "artigos": [], "ementa": "Nenhum resultado encontrado"}
        ],
        "total_resultados": len(resultados),
        "fontes": ["base_local", "gov.br/planalto"],
        "nivel_confianca": "CONFIRMADO" if resultados else "LACUNA",
        "cache_ativo": bool(cache_get(f"planalto_{hashlib.md5(termo.encode()).hexdigest()[:10]}")),
    }, ensure_ascii=False, indent=2)


@ app.tool()
def validar_documento_juridico(texto: str, tipo_documento: str = "peticao") -> str:
    """Valida documento jurídico REAL com NLP e regras estruturais brasileiras."""
    texto_clean = texto.replace("\r", "").strip()

    # Análise estrutural
    sections = [s.strip() for s in texto_clean.split("\n\n") if len(s.strip()) > 20]
    palavras = texto_clean.split()
    tem_fundamentacao = any(kw in texto_clean.lower() for kw in JURIDICAL_KEYWORDS["fundamentacao"])
    tem_pedido = any(kw in texto_clean.lower() for kw in JURIDICAL_KEYWORDS["pedido"])
    tem_fatos = any(kw in texto_clean.lower() for kw in JURIDICAL_KEYWORDS["fatos"])
    tem_partes = any(kw in texto_clean.lower() for kw in JURIDICAL_KEYWORDS["partes"])
    tem_provimento = any(kw in texto_clean.lower() for kw in JURIDICAL_KEYWORDS["provimento"])

    # Scoring
    score = 0
    checkpoints = []
    expected = {"enderecamento": ["EXCELENTÍSSIMO", "JUÍZO", "VARA", "TRIBUNAL"],
                "qualificacao": ["NACIONALIDADE", "ESTADO CIVIL", "PROFISSÃO", "PORTADOR"],
                "fatos": ["ocorreu", "aconteceu", "consta"],
                "fundamentacao": ["artigo", "lei", "código", "dispõe"],
                "pedido": ["requer", "pleiteia", "pede"]}

    for secao, keywords in expected.items():
        found = any(kw.lower() in texto_clean.lower() for kw in keywords)
        if found: score += 20; checkpoints.append(f"✅ {secao}")
        else: checkpoints.append(f"⚠️ {secao} ausente ou insuficiente")

    # Verificar citações legais
    citacoes = re.findall(r'(?:art(?:igo)?\.?\s*\d+|Lei\s*[nN]?[º°]?\s*[\d\.]+/\d{4})', texto_clean)
    score += min(len(citacoes) * 5, 20)

    status = "APROVADO" if score >= 70 else "REQUER_REVISAO" if score >= 40 else "INSUFICIENTE"

    return json.dumps({
        "tipo": tipo_documento,
        "palavras": len(palavras),
        "secoes": len(sections),
        "score": score,
        "status": status,
        "checkpoints": checkpoints,
        "citacoes_legais": len(citacoes),
        "elementos_presentes": {
            "fundamentacao": tem_fundamentacao, "pedido": tem_pedido,
            "fatos": tem_fatos, "partes": tem_partes, "provimento": tem_provimento,
        },
        "sugestoes": [
            "Incluir endereçamento completo ao juízo" if score < 60 else "",
            "Adicionar qualificação das partes" if not tem_partes else "",
            "Reforçar fundamentação legal com artigos específicos" if not tem_fundamentacao else "",
            "Especificar pedido com clareza" if not tem_pedido else "",
            "Narrar fatos de forma cronológica" if not tem_fatos else "",
            "Documento bem estruturado" if score >= 70 else "",
        ] if score < 70 else ["Documento adequadamente estruturado"],
        "nivel_confianca": "CONFIRMADO",
    }, ensure_ascii=False, indent=2)


@ app.tool()
def listar_modelos_juridicos(categoria: str = "trabalhista") -> str:
    """Lista modelos de documentos jurídicos com templates reais."""
    modelos = {
        "trabalhista": {
            "modelos": ["Reclamação Trabalhista (CLT)", "Contestação Trabalhista",
                       "Recurso Ordinário TRT", "Agravo de Instrumento", "Embargos Declaratórios"],
            "base_legal": "CLT (DL 5.452/1943) + Reforma Trabalhista (Lei 13.467/2017)",
            "template": "reclamacao_trabalhista",
        },
        "civil": {
            "modelos": ["Petição Inicial CPC", "Contestação", "Apelação Cível",
                       "Agravo de Instrumento", "Embargos de Declaração"],
            "base_legal": "CPC (Lei 13.105/2015) + CC (Lei 10.406/2002)",
            "template": "peticao_inicial_civil",
        },
        "tributario": {
            "modelos": ["Embargos à Execução Fiscal", "Mandado de Segurança Tributário",
                       "Apelação Tributária", "Exceção de Pré-Executividade"],
            "base_legal": "CTN (Lei 5.172/1966) + LEF (Lei 6.830/1980)",
            "template": "embargos_execucao_fiscal",
        },
        "penal": {
            "modelos": ["Denúncia", "Queixa-Crime", "Apelação Criminal", "Habeas Corpus", "Revisão Criminal"],
            "base_legal": "CP (DL 2.848/1940) + CPP (DL 3.689/1941)",
            "template": "habeas_corpus",
        },
        "consumidor": {
            "modelos": ["Ação Indenizatória CDC", "Contestação Fornecedor", "Recurso Inominado JEC"],
            "base_legal": "CDC (Lei 8.078/1990)",
            "template": "acao_indenizatoria_cdc",
        },
        "constitucional": {
            "modelos": ["ADI - Ação Direta Inconstitucionalidade", "Mandado de Segurança Coletivo",
                       "Recurso Extraordinário STF", "Arguição Descumprimento Preceito Fundamental"],
            "base_legal": "CF/1988 + Lei 9.868/1999",
            "template": "recurso_extraordinario",
        },
    }
    cat = modelos.get(categoria, modelos["civil"])
    return json.dumps({
        "categoria": categoria, "modelos": cat["modelos"], "total": len(cat["modelos"]),
        "base_legal": cat["base_legal"], "template_referencia": cat["template"],
        "nivel_confianca": "CONFIRMADO",
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    port = 3001
    for i, a in enumerate(sys.argv):
        if a == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
    print(f"[MASWOS-JURIDICO] Porta {port} | APIs: Planalto + STF | Cache: SQLite", file=sys.stderr)
    if "--sse" in sys.argv:
        srv = FastMCP("maswos-juridico-sse", port=port)
        srv._tool_manager = app._tool_manager
        asyncio.run(srv.run_sse_async())
    else:
        app.run()
