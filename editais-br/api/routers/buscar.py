"""Rota de busca sob demanda — pesquisa editais em tempo real."""

import logging
import os
import time

import httpx
from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from api.database import SessionLocal
from api.models.edital import Edital
from extractors.html import HTMLExtractor
from extractors.pdf_markdown import PDFMarkdownExtractor
from worker.discovery import EditalClassifier, SearchEngine

logger = logging.getLogger(__name__)
router = APIRouter(tags=["buscar"])
jinja_env = Environment(loader=FileSystemLoader("templates"))


def render(name: str, context: dict) -> HTMLResponse:
    from pathlib import Path

    template_path = Path("templates") / name
    source = template_path.read_text()
    template = jinja_env.from_string(source)
    return HTMLResponse(template.render(context))


@router.get("/buscar", response_class=HTMLResponse)
async def buscar(request: Request, q: str = Query("", description="Termo de busca")):
    """Busca editais sob demanda usando SerpAPI."""
    if not q.strip():
        return render("buscar.html", {"request": request, "q": "", "resultados": [], "total": 0, "tempo": 0})

    start = time.time()
    serpapi_key = os.getenv("SERPAPI_KEY", "")

    engine = SearchEngine(backend="serpapi" if serpapi_key else "duckduckgo", api_key=serpapi_key)
    classifier = EditalClassifier()
    pdf_extractor = PDFMarkdownExtractor()

    query = f'"{q}" edital fomento 2026'
    logger.info(f"🔍 Buscando: {query}")
    results = engine.search(query, max_results=8)

    fomento_kw = [
        "fomento", "bolsa", "pesquisa", "inovação", "edital",
        "subvenção", "financiamento", "chamada", "auxílio", "energia",
    ]

    editais_encontrados = []
    for item in results:
        try:
            with httpx.Client(timeout=15, headers={"User-Agent": "Mozilla/5.0"}) as client:
                resp = client.get(item["url"])
                html = resp.text

            classification = classifier.classify(html)
            titulo_lower = item.get("title", "").lower()
            tem_keyword = any(kw in titulo_lower for kw in fomento_kw)

            if classification["tipo"] == "edital" or (tem_keyword and classification["tipo"] != "outro"):
                pdf_links = pdf_extractor.find_pdf_links(html, item["url"])
                raw_text = ""
                if pdf_links:
                    raw_text = pdf_extractor.extract(pdf_links[0])
                if not raw_text:
                    raw_text = HTMLExtractor().extract(html)

                # Salva no banco
                db = SessionLocal()
                try:
                    from api.models.portal import Portal

                    portal = db.query(Portal).first()
                    existente = db.query(Edital).filter(Edital.url_original == item["url"]).first()
                    if not existente and portal:
                        edital = Edital(
                            portal_id=portal.id,
                            titulo=item["title"],
                            url_original=item["url"],
                            pdf_url=pdf_links[0] if pdf_links else None,
                            raw_text=raw_text,
                            status="extraido",
                        )
                        db.add(edital)
                        db.commit()
                finally:
                    db.close()

                editais_encontrados.append({
                    "titulo": item["title"],
                    "url": item["url"],
                    "resumo": raw_text[:400] if raw_text else "",
                    "chars": len(raw_text),
                })

            if len(editais_encontrados) >= 5:
                break

        except Exception as e:
            logger.warning(f"Erro ao processar {item.get('url', '')[:60]}: {e}")
            continue

    tempo = round(time.time() - start, 1)
    logger.info(f"✅ Busca concluída: {len(editais_encontrados)} editais em {tempo}s")

    return render("buscar.html", {
        "request": request, "q": q, "resultados": editais_encontrados,
        "total": len(editais_encontrados), "tempo": tempo,
    })
