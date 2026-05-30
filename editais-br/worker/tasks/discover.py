"""Task: discover_editais — busca editais na web e alimenta o pipeline."""

import logging
import os

import httpx

from worker.celery_app import app
from worker.discovery import SearchEngine, EditalClassifier
from worker.tasks.extract import extract_edital  # noqa: E402

logger = logging.getLogger(__name__)

QUERIES_PADRAO = [
    # Fomento governamental
    '"edital de fomento" 2026',
    '"chamada pública" fomento 2026',
    '"edital" "fomento" "pesquisa" 2026',
    # Fomento à inovação e tecnologia
    '"edital" "inovação" "fomento" 2026',
    '"subvenção econômica" edital 2026',
    # Fomento à cultura
    '"edital" "fomento" "cultura" 2026',
    # Agências de fomento
    'fapesp "chamada de propostas" 2026',
    'cnpq "bolsa" "fomento" 2026',
    'finep "chamada pública" "fomento" 2026',
    'confap "edital" fomento 2026',
]


@app.task(bind=True, name="discover_editais")
def discover_editais(self, query: str = "", max_results: int = 20):
    """Busca editais na web e os classifica.

    Args:
        query: Termo de busca. Se vazio, usa queries padrão.
        max_results: Máximo de resultados por query.

    Returns:
        Dict com estatísticas da descoberta.
    """
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    google_api_key = os.getenv("GOOGLE_API_KEY", "")
    search_api_key = os.getenv("SERPAPI_KEY", "")

    engine = SearchEngine(
        backend="serpapi" if search_api_key else "duckduckgo",
        api_key=search_api_key,
        google_api_key=google_api_key,
    )
    classifier = EditalClassifier(api_key=api_key, google_api_key=google_api_key)

    queries = [query] if query else QUERIES_PADRAO
    all_results = []
    editais = []
    portais = []

    for q in queries:
        logger.info(f"🔍 Buscando: {q}")
        results = engine.search(q, max_results=max_results)
        all_results.extend(results)
        logger.info(f"  → {len(results)} resultados")

    # Deduplica URLs
    seen = set()
    unique = []
    for r in all_results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)

    logger.info(f"📊 Total: {len(all_results)} raw, {len(unique)} únicos")

    # Classifica cada URL
    for item in unique[:50]:  # limita processamento (50 URLs)
        try:
            with httpx.Client(timeout=15, headers={"User-Agent": "Mozilla/5.0"}) as client:
                response = client.get(item["url"])
                html = response.text[:10000]  # primeiros 10KB

            classification = classifier.classify(html)
            item["tipo"] = classification["tipo"]
            item["confidence"] = classification["confidence"]

            if classification["tipo"] == "edital":
                # Filtro extra: precisa ter keyword de fomento
                titulo_lower = item.get("title", "").lower()
                fomento_keywords = ["fomento", "bolsa", "pesquisa", "inovação", "subvenção",
                                    "financiamento", "chamada", "edital", "auxílio"]
                if any(kw in titulo_lower for kw in fomento_keywords):
                    editais.append(item)
                    logger.info(f"  📄 Edital: {item['title'][:60]}")
                else:
                    logger.debug(f"  ⏭️ Ignorado (não é fomento): {item['title'][:50]}")
            elif classification["tipo"] == "portal_list":
                portais.append(item)
                logger.info(f"  📋 Portal: {item['title'][:60]}")

                # 🔗 Crawler profundo: extrai links do portal
                sub_links = _extrair_links_de_portal(html, item["url"])
                logger.info(f"    🔗 {len(sub_links)} links extraídos do portal")

                for sub in sub_links[:20]:  # até 20 links por portal
                    if sub["url"] not in seen:
                        seen.add(sub["url"])
                        try:
                            with httpx.Client(timeout=10, headers={"User-Agent": "Mozilla/5.0"}) as client:
                                sub_html = client.get(sub["url"]).text[:10000]
                            sub_class = classifier.classify(sub_html)
                            if sub_class["tipo"] == "edital":
                                sub["tipo"] = "edital"
                                sub["confidence"] = sub_class["confidence"]
                                editais.append(sub)
                                logger.info(f"    📄 Sub-edital: {sub['title'][:60]}")
                        except Exception:
                            pass

        except Exception as e:
            logger.debug(f"  ⚠️ Erro ao classificar {item['url'][:50]}: {e}")
            continue

    # Salva no banco
    salvos = _salvar_no_banco(editais, portais)

    logger.info(
        f"✅ Descoberta concluída: {len(editais)} editais, {len(portais)} portais, {salvos} salvos"
    )

    return {
        "total_encontrados": len(unique),
        "editais": len(editais),
        "portais": len(portais),
        "salvos_no_banco": salvos,
        "resultados": editais + portais,
    }


def _salvar_no_banco(editais: list[dict], portais: list[dict]) -> int:
    """Salva editais e portais descobertos no banco e dispara pipeline."""
    from api.database import SessionLocal
    from api.models.edital import Edital
    from api.models.portal import Portal

    db = SessionLocal()
    salvos = []

    try:
        for item in editais:
            exists = db.query(Edital).filter(Edital.url_original == item["url"]).first()
            if not exists:
                portal = db.query(Portal).first()
                if portal:
                    edital = Edital(
                        portal_id=portal.id,
                        titulo=item["title"],
                        url_original=item["url"],
                        status="pendente",
                    )
                    db.add(edital)
                    db.flush()
                    salvos.append(str(edital.id))

        db.commit()
        logger.info(f"💾 {len(salvos)} editais salvos no banco")

        # ⛓️ Pipeline: dispara extração para cada edital salvo
        for edital_id in salvos:
            logger.info(f"  ⛓️ Enfileirando extração: {edital_id[:8]}...")
            extract_edital.delay(edital_id)

    except Exception as e:
        logger.exception(f"Erro ao salvar no banco: {e}")
        db.rollback()
    finally:
        db.close()

    return len(salvos)


def _extrair_links_de_portal(html: str, base_url: str) -> list[dict]:
    """Extrai links de editais individuais de uma página de portal/lista."""
    from urllib.parse import urljoin, urlparse
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    links = []
    seen = set()

    # Palavras-chave que indicam um edital individual
    edital_keywords = [
        "edital", "chamada", "seleção", "concurso", "fomento",
        "bolsa", "auxílio", "inscrição", "oportunidade",
    ]

    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True).lower()

        # Monta URL absoluta
        url = urljoin(base_url, href)

        # Ignora navegação interna, js, imagens
        if any(x in url.lower() for x in ["#", "javascript:", ".jpg", ".png", ".pdf", "wp-admin", "login", "feed", "rss"]):
            continue

        # Link precisa: ter texto visível E estar no mesmo domínio OU ter keyword de edital
        if not text or len(text) < 10:
            continue

        same_domain = urlparse(base_url).netloc in url
        has_keyword = any(kw in text or kw in href.lower() for kw in edital_keywords)

        if not (same_domain or has_keyword):
            continue

        if url in seen:
            continue

        seen.add(url)
        links.append({"url": url, "title": text})

    return links
