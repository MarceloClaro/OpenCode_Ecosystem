"""Task: extract_edital — extrai texto de um edital (PDF/HTML) e converte para Markdown."""

import logging

import httpx

from api.database import SessionLocal
from api.models.edital import Edital
from extractors.html import HTMLExtractor
from extractors.pdf_markdown import PDFMarkdownExtractor
from worker.celery_app import app
from worker.tasks.analyze import analyze_edital  # noqa: E402

logger = logging.getLogger(__name__)


@app.task(bind=True, name="extract_edital")
def extract_edital(self, edital_id: str):
    """Extrai texto completo de um edital e converte para Markdown.

    Estratégia:
    1. Se tem pdf_url → baixa PDF → converte Markdown
    2. Senão, baixa a página HTML → extrai texto → busca links de PDF na página
    3. Se encontrar PDF na página → baixa e converte

    Args:
        edital_id: UUID do edital no banco de dados.
    """
    db = SessionLocal()
    try:
        edital = db.query(Edital).filter(Edital.id == edital_id).first()
        if not edital:
            logger.error(f"Edital {edital_id} não encontrado")
            return {"error": "Edital não encontrado"}

        raw_text = None
        pdf_extractor = PDFMarkdownExtractor()

        # Estratégia 1: PDF direto (se já tem pdf_url)
        if edital.pdf_url:
            logger.info(f"📥 Baixando PDF: {edital.pdf_url[:80]}")
            raw_text = pdf_extractor.extract(edital.pdf_url)
            if raw_text:
                logger.info(f"PDF convertido: {len(raw_text)} caracteres Markdown")

        # Estratégia 2: Baixa página HTML
        if not raw_text:
            try:
                logger.info(f"📥 Baixando página: {edital.url_original[:80]}")
                response = httpx.get(
                    edital.url_original,
                    timeout=30,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                response.raise_for_status()
                html = response.text

                # Extrai texto limpo do HTML
                html_extractor = HTMLExtractor()
                raw_text = html_extractor.extract(html)

                # Estratégia 3: Busca links de PDF na página
                pdf_links = pdf_extractor.find_pdf_links(html, edital.url_original)
                if pdf_links:
                    logger.info(f"🔗 {len(pdf_links)} PDF(s) encontrados na página")
                    for pdf_url in pdf_links[:3]:  # tenta até 3 PDFs
                        pdf_text = pdf_extractor.extract(pdf_url)
                        if pdf_text and len(pdf_text) > len(raw_text or ""):
                            raw_text = pdf_text
                            edital.pdf_url = pdf_url  # atualiza URL do PDF
                            logger.info(f"✅ PDF convertido: {len(pdf_text)} caracteres")
                            break

            except Exception as e:
                logger.warning(f"Falha ao baixar HTML {edital.url_original[:80]}: {e}")

        if raw_text:
            edital.raw_text = raw_text
            edital.status = "extraido"
            db.commit()
            logger.info(f"Edital {edital_id[:8]}: {len(raw_text)} caracteres extraídos")

            # ⛓️ Pipeline: dispara análise com IA
            analyze_edital.delay(edital_id)
            return {"status": "extraido", "chars": len(raw_text)}
        else:
            edital.status = "erro"
            db.commit()
            return {"status": "erro", "error": "Não foi possível extrair texto"}

    except Exception as e:
        logger.exception(f"Erro na extração do edital {edital_id}: {e}")
        db.rollback()
        raise
    finally:
        db.close()
