# -*- coding: utf-8 -*-
import json, sys, time, hashlib, logging
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

from ecosystem_config import ECO_ROOT; BASE_DIR = ECO_ROOT
EVOLVE_DIR = BASE_DIR / ".evolve"
DOCLING_INDEX_PATH = EVOLVE_DIR / "docling_index.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions


class DoclingAdapter:
    SUPPORTED_FORMATS = {
        "pdf": InputFormat.PDF, "docx": InputFormat.DOCX,
        "pptx": InputFormat.PPTX, "xlsx": InputFormat.XLSX,
        "html": InputFormat.HTML, "png": InputFormat.IMAGE,
        "jpg": InputFormat.IMAGE, "jpeg": InputFormat.IMAGE, "tiff": InputFormat.IMAGE,
    }

    def __init__(self, enable_ocr=True, enable_tables=True):
        self.converter = DocumentConverter()
        self.index = self._load_index()

    def _load_index(self):
        if DOCLING_INDEX_PATH.exists():
            try:
                return json.loads(DOCLING_INDEX_PATH.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"processed": [], "pending": [], "errors": [], "stats": {}}

    def _save_index(self):
        EVOLVE_DIR.mkdir(parents=True, exist_ok=True)
        DOCLING_INDEX_PATH.write_text(json.dumps(self.index, indent=2, ensure_ascii=False), encoding="utf-8")

    def _compute_hash(self, file_path):
        return hashlib.md5(file_path.read_bytes()).hexdigest()

    def convert_to_markdown(self, source):
        result = self.converter.convert(source)
        return result.document.export_to_markdown()

    def convert_to_html(self, source):
        result = self.converter.convert(source)
        return result.document.export_to_html()

    def convert_to_json(self, source):
        result = self.converter.convert(source)
        return result.document.model_dump()

    def convert_to_doctag(self, source):
        result = self.converter.convert(source)
        return result.document.export_to_doctag()

    def extract_knowledge(self, source):
        start = time.time()
        source_path = Path(source)
        try:
            result = self.converter.convert(source)
            doc = result.document
            metadata = {"title": doc.name or source_path.stem, "source": str(source), "format": source_path.suffix.lower(), "num_pages": len(doc.pages) if hasattr(doc, "pages") else 0, "processed_at": datetime.now().isoformat()}
            markdown_content = doc.export_to_markdown()
            tables = []
            if hasattr(doc, "tables"):
                for i, table in enumerate(doc.tables):
                    tables.append({"index": i, "num_rows": len(table.data) if hasattr(table, "data") else 0, "caption": table.caption.text if hasattr(table, "caption") and table.caption else ""})
            topics = self._extract_topics(markdown_content)
            findings = self._extract_findings(markdown_content)
            citations = self._extract_citations(markdown_content)
            duration = time.time() - start
            extraction = {"metadata": metadata, "content": markdown_content[:50000], "topics": topics, "key_findings": findings, "citations": citations, "tables": tables, "structure": {"sections": len([l for l in markdown_content.split("\n") if l.startswith("#")]), "paragraphs": len([l for l in markdown_content.split("\n\n") if l.strip()]), "tables_count": len(tables)}, "duration_ms": round(duration * 1000, 2)}
            doc_hash = self._compute_hash(source_path)
            self.index["processed"].append({"path": str(source_path), "hash": doc_hash, "metadata": metadata, "processed_at": metadata["processed_at"], "duration_ms": extraction["duration_ms"]})
            self._save_index()
            # Hook: alimentar PDF RAG Collections automaticamente
            try:
                from pdf_rag.bridge import EcosystemBridge
                bridge = EcosystemBridge()
                bridge.hook_docling_extraction(str(source_path), extraction)
                logger.info(f"[pdf_rag] {source_path.name} indexado nas coleções")
            except Exception as bridge_err:
                logger.debug(f"[pdf_rag] Bridge indisponível: {bridge_err}")
            return extraction
        except Exception as e:
            logger.error(f"Erro ao extrair conhecimento de {source}: {e}")
            self.index["errors"].append({"path": str(source_path), "error": str(e), "timestamp": datetime.now().isoformat()})
            self._save_index()
            return {"metadata": {"title": source_path.stem, "source": str(source), "error": str(e)}, "content": "", "topics": [], "key_findings": [], "citations": [], "tables": [], "structure": {}, "duration_ms": 0}

    def _extract_topics(self, content):
        topics = []
        for line in content.split("\n"):
            if line.startswith("## ") and len(line) < 100:
                topics.append(line.replace("## ", "").strip())
        return list(set(topics))[:20]

    def _extract_findings(self, content):
        findings = []
        for p in content.split("\n\n")[:15]:
            p_clean = p.strip()
            if len(p_clean) > 100 and not p_clean.startswith("#"):
                findings.append(p_clean[:300])
        return findings[:10]

    def _extract_citations(self, content):
        citations = []
        for line in content.split("\n"):
            if any(kw in line.lower() for kw in ["et al", "doi:", "arxiv", "isbn", "https://doi.org"]):
                citations.append({"title": line.strip()[:200], "raw": line.strip()})
        return citations[:20]

    def get_index_summary(self):
        return {"total_processed": len(self.index.get("processed", [])), "total_errors": len(self.index.get("errors", [])), "recent": self.index.get("processed", [])[-5:], "stats": self.index.get("stats", {})}

    def scan_directory(self, directory):
        dir_path = Path(directory)
        if not dir_path.exists():
            return []
        docs = []
        for ext in self.SUPPORTED_FORMATS:
            docs.extend(dir_path.rglob(f"*.{ext}"))
        results = []
        processed_hashes = {item["hash"] for item in self.index.get("processed", [])}
        for doc_path in docs:
            doc_hash = self._compute_hash(doc_path)
            status = "processed" if doc_hash in processed_hashes else "pending"
            results.append({"path": str(doc_path), "format": doc_path.suffix.lower(), "size": doc_path.stat().st_size, "status": status, "hash": doc_hash})
        return results


class DoclingSkillGenerator:
    def __init__(self, skills_dir=None):
        self.skills_dir = Path(skills_dir or BASE_DIR / "skills" / "evolution")
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def generate_from_extraction(self, extraction, source):
        metadata = extraction.get("metadata", {})
        topics = extraction.get("topics", [])
        findings = extraction.get("key_findings", [])
        if not topics and not findings:
            return None
        skill_name = f"docling-{Path(source).stem}-{int(time.time())}"
        skill_path = self.skills_dir / f"{skill_name}.md"
        skill_path.write_text(f"Generated skill from: {source}", encoding="utf-8")
        return str(skill_path)
