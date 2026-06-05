# -*- coding: utf-8 -*-
"""
PDF -> Context Offload Integration
Conecta PDF Knowledge Extraction ao Context Offload Manager para:
- Armazenar conhecimento extraido de PDFs no context offload
- Gerar behavioral fingerprints baseados em conteudo academico
- Criar sessions especializadas por topico de PDF
- Permitir resume consistency com conhecimento academico
"""
import sys
from pathlib import Path
from typing import Any, Optional

from ecosystem_config import ECO_ROOT; BASE_DIR = ECO_ROOT
sys.path.insert(0, str(BASE_DIR / "nexus" / "scripts"))

from context_offload import ContextOffloadManager
try:
    from docling_adapter import DoclingAdapter, DoclingSkillGenerator
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    from pdf_ecosystem_integration import PDFKnowledgeExtractor, PDFPipelineManager


class PDFContextOffloader:
    """
    Integra PDF knowledge extraction com context offload.
    
    Pipeline:
    1. PDF extrai conhecimento -> 2. Armazena no context offload ->
    3. Gera fingerprint academico -> 4. Disponibiliza para evolution loop
    """

    def __init__(self, offload_manager: ContextOffloadManager = None):
        self.offload = offload_manager or ContextOffloadManager()
        if DOCLING_AVAILABLE:
            self.adapter = DoclingAdapter()
            self.skill_gen = DoclingSkillGenerator()
        else:
            self.pdf_extractor = PDFKnowledgeExtractor()
            self.pdf_manager = PDFPipelineManager()

    def offload_pdf_knowledge(self, pdf_path: str, session_id: str = None) -> dict:
        """Extrai conhecimento de PDF e armazena no context offload."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            return {"error": "PDF not found", "path": str(pdf_path)}

        if not session_id:
            session_id = self.offload.create_session(project_id=pdf_path.stem)
        else:
            self.offload.active_session = session_id

        extraction = self.pdf_extractor.extract_knowledge(str(pdf_path))

        metadata = extraction.get("metadata", {})
        self.offload.add_entry(
            content=f"PDF Metadata: {pdf_path.name}\nTitle: {metadata.get('title', 'N/A')}\nAuthors: {metadata.get('authors', 'N/A')}\nYear: {metadata.get('year', 'N/A')}",
            content_type="metadata",
            priority=8
        )

        citations = extraction.get("citations", [])
        if citations:
            self.offload.add_entry(
                content=f"Citations ({len(citations)}):\n" + "\n".join([f"- {c.get('title', c)}" for c in citations[:20]]),
                content_type="intermediate_result",
                priority=7
            )

        topics = extraction.get("topics", [])
        if topics:
            self.offload.add_entry(
                content=f"Main Topics: {', '.join(topics)}",
                content_type="metadata",
                priority=9
            )

        findings = extraction.get("key_findings", [])
        if findings:
            self.offload.add_entry(
                content=f"Key Findings:\n" + "\n".join([f"- {f}" for f in findings[:10]]),
                content_type="intermediate_result",
                priority=10
            )

        structure = extraction.get("structure", {})
        if structure:
            self.offload.add_entry(
                content=f"PDF Structure: {structure}",
                content_type="metadata",
                priority=6
            )

        fingerprint = self.offload.create_behavioral_fingerprint(session_id)

        return {
            "session_id": session_id,
            "pdf_path": str(pdf_path),
            "extraction_summary": {
                "metadata_keys": list(metadata.keys()),
                "citations_count": len(citations),
                "topics_count": len(topics),
                "findings_count": len(findings)
            },
            "fingerprint_terms": len(fingerprint.get("term_frequency", {})),
            "offload_status": "success"
        }

    def get_pdf_knowledge_context(self, session_id: str, max_entries: int = 15) -> dict:
        """Recupera contexto de conhecimento PDF de uma session."""
        context = self.offload.get_session_context(session_id, max_entries)
        summary = self.offload.get_session_summary(session_id)
        fingerprint = self.offload.sessions.get(session_id, {}).behavioral_fingerprint

        return {
            "session_id": session_id,
            "context_entries": len(context),
            "context_preview": context[:3] if context else [],
            "summary": summary[:500] if summary else "",
            "fingerprint_terms": len(fingerprint.get("term_frequency", {})) if fingerprint else 0
        }

    def scan_and_offload_all_pdfs(self) -> list:
        """Escaneia diretorios monitorados e offloada todos os PDFs encontrados."""
        if DOCLING_AVAILABLE:
            pdfs = self.adapter.scan_directory(str(BASE_DIR.parent / "Downloads"))
            pdfs.extend(self.adapter.scan_directory(str(BASE_DIR / "documents")))
            pdfs.extend(self.adapter.scan_directory(str(BASE_DIR / "papers")))
        else:
            pdfs = self.pdf_manager.scan_for_pdfs()
        results = []
        for pdf_info in pdfs:
            pdf_path = pdf_info.get("path")
            if pdf_path:
                result = self.offload_pdf_knowledge(pdf_path)
                results.append(result)
        return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PDF Context Offload Integration")
    parser.add_argument("--pdf", type=str, help="Path to PDF file")
    parser.add_argument("--session", type=str, help="Session ID")
    parser.add_argument("--scan", action="store_true", help="Scan and offload all PDFs")
    parser.add_argument("--context", type=str, help="Get context for session ID")
    args = parser.parse_args()
    offloader = PDFContextOffloader()
    if args.pdf:
        result = offloader.offload_pdf_knowledge(args.pdf, args.session)
        print("PDF Knowledge Offloaded:", result)
    elif args.scan:
        results = offloader.scan_and_offload_all_pdfs()
        print(f"Scanned and offloaded {len(results)} PDFs")
    elif args.context:
        ctx = offloader.get_pdf_knowledge_context(args.context)
        print("PDF Knowledge Context:", ctx)
    else:
        print("Use --pdf, --scan, or --context")
