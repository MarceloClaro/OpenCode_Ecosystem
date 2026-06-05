# -*- coding: utf-8 -*-
"""
PDF ECOSYSTEM INTEGRATION v5.0 - Pipeline Completo
Pipeline: PDF Detection -> Conversion -> Context Extraction -> Skill Feeding

Integrates pdf_to_markdown.py with the full ecosystem:
1. Watch directories for new PDFs
2. Convert PDFs to structured Markdown
3. Extract knowledge and feed into context offload
4. Generate skills from extracted knowledge
5. Update sync orchestrator with new components

Arquitetura:
  Directory Watcher -> PDF Converter -> Text Analyzer
  -> Context Offload -> Skill Generator -> Sync Orchestrator

Autor: Ecossistema OpenCode v5.0
Modelo: big-pickle
"""

import os, sys, json, time, re, hashlib, logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from ecosystem_config import ECO_ROOT; BASE_DIR = ECO_ROOT
EVOLVE_DIR = BASE_DIR / ".evolve"
PDF_INDEX_PATH = EVOLVE_DIR / "pdf_index.json"
PDF_OUTPUT_DIR = BASE_DIR / "documents" / "markdown"
PDF_KNOWLEDGE_DIR = BASE_DIR / "documents" / "knowledge"

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, str(BASE_DIR / "nexus" / "scripts"))

# ============================================================
# PDF Metadata & Knowledge Extraction
# ============================================================

class PDFKnowledgeExtractor:
    """
    Extracts structured knowledge from converted PDF Markdown files.
    Identifies: topics, entities, citations, key findings, action items.
    """

    def __init__(self):
        self.citation_patterns = [
            r'\(?\d{4}[a-z]?\)?',  # Year citations like (2023), (2024a)
            r'(?:et al\.|&|and)\s*[A-Z]',  # Author citations
            r'(?:Fig\.?|Table|Eq\.?|Section)\s*\d+',  # References to figures/tables
            r'(?:doi|DOI)[:.\s]*10\.\d+',  # DOI references
            r'(?:arXiv)[:.\s]*\d+\.\d+',  # arXiv references
        ]
        self.entity_patterns = {
            'concept': r'(?:concept|framework|model|theory|methodology|approach|paradigm)',
            'metric': r'(?:metric|measure|score|index|rate|percentage|r\s*=\s*[-\d.]+)',
            'organization': r'(?:university|institute|company|organization|agency|government)',
        }

    def extract_knowledge(self, markdown_content: str, source_file: str = "") -> dict:
        """Extract structured knowledge from PDF markdown content."""
        knowledge = {
            "source": source_file,
            "timestamp": datetime.now().isoformat(),
            "metadata": self._extract_metadata(markdown_content),
            "topics": self._extract_topics(markdown_content),
            "citations": self._extract_citations(markdown_content),
            "entities": self._extract_entities(markdown_content),
            "key_findings": self._extract_key_findings(markdown_content),
            "structure": self._extract_structure(markdown_content),
            "summary": self._generate_summary(markdown_content),
        }
        return knowledge

    def _extract_metadata(self, content: str) -> dict:
        """Extract YAML frontmatter metadata."""
        meta = {}
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            for line in match.group(1).split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    meta[k.strip()] = v.strip()
        return meta

    def _extract_topics(self, content: str) -> list:
        """Extract main topics from headings and repeated terms."""
        headings = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
        # Remove duplicates and clean
        topics = list(set(h.strip() for h in headings if len(h.strip()) > 3))
        # Also look for frequently occurring terms
        words = re.findall(r'\b[A-Z][a-z]{3,}\b', content)
        from collections import Counter
        freq = Counter(words)
        for word, count in freq.most_common(10):
            if count >= 3 and word.lower() not in [t.lower() for t in topics]:
                topics.append(word)
        return topics[:20]

    def _extract_citations(self, content: str) -> list:
        """Extract citation references."""
        citations = []
        for pattern in self.citation_patterns:
            matches = re.findall(pattern, content)
            citations.extend(matches)
        return list(set(citations))[:50]

    def _extract_entities(self, content: str) -> dict:
        """Extract named entities by category."""
        entities = {}
        for category, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            entities[category] = list(set(matches))[:20]
        return entities

    def _extract_key_findings(self, content: str) -> list:
        """Extract sentences that look like key findings."""
        sentences = re.split(r'[.!?]+', content)
        findings = []
        indicator_words = ['significant', 'important', 'key finding', 'results show',
                          'conclusion', 'demonstrates', 'reveals', 'indicates',
                          'suggests', 'confirms', 'establishes']
        for s in sentences:
            s = s.strip()
            if len(s) > 30 and len(s) < 500:
                if any(ind in s.lower() for ind in indicator_words):
                    findings.append(s[:300])
        return findings[:10]

    def _extract_structure(self, content: str) -> dict:
        """Extract document structure information."""
        h1 = len(re.findall(r'^#\s+', content, re.MULTILINE))
        h2 = len(re.findall(r'^##\s+', content, re.MULTILINE))
        h3 = len(re.findall(r'^###\s+', content, re.MULTILINE))
        tables = len(re.findall(r'\|[-\s|]+\|', content))
        code_blocks = len(re.findall(r'`', content))
        lists = len(re.findall(r'^\s*[-*]\s+', content, re.MULTILINE))
        return {
            "headings": {"h1": h1, "h2": h2, "h3": h3},
            "tables": tables,
            "code_blocks": code_blocks,
            "lists": lists,
            "total_chars": len(content),
            "total_lines": content.count('\n'),
        }

    def _generate_summary(self, content: str) -> str:
        """Generate a brief summary from the content."""
        # Extract first meaningful paragraph after frontmatter
        match = re.match(r'^---\s*\n.*?\n---\s*\n(.+?)(?:\n\n|\n#{1,3} )', content, re.DOTALL)
        if match:
            first_section = match.group(1).strip()
            return first_section[:500]
        # Fallback: first 500 chars
        return content[:500]

# ============================================================
# PDF Skill Generator
# ============================================================

class PDFSkillGenerator:
    """
    Generates skills from extracted PDF knowledge.
    Creates SKILL.md files based on extracted topics and findings.
    """

    def __init__(self):
        self.skills_dir = BASE_DIR / "skills" / "research"

    def generate_skill_from_knowledge(self, knowledge: dict) -> Optional[str]:
        """Generate a skill file from PDF knowledge."""
        if not knowledge.get("topics"):
            return None

        # Create skill name from first topic or source
        source = Path(knowledge.get("source", "unknown")).stem
        skill_name = re.sub(r'[^a-z0-9-]', '-', source.lower()).strip('-')
        skill_file = self.skills_dir / f"{skill_name}.md"

        # Skip if skill already exists
        if skill_file.exists():
            logger.info(f"Skill already exists: {skill_file.name}")
            return None

        title = knowledge["topics"][0] if knowledge["topics"] else skill_name.replace('-', ' ').title()
        summary = knowledge.get("summary", "")[:300]
        topics = knowledge.get("topics", [])[:10]
        findings = knowledge.get("key_findings", [])[:5]

        skill_content = f"""<!-- SAIDA OBRIGATORIA: PORTUGUES BRASILEIRO FORMAL -->
<!-- Modelo: big-pickle -->

---
name: {skill_name}
description: Skill gerada automaticamente a partir de PDF: {source}
version: 1.0.0
author: ecosystem
category: research
inspired_by: pdf-ecosystem-integration
compatibility: big-pickle
source_pdf: {knowledge.get('source', '')}
generated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# {title}

Skill gerada automaticamente a partir da extracao de conhecimento do PDF:
{knowledge.get('source', 'unknown')}

## Resumo

{summary}

## Topicos Principais

{chr(10).join(f"- {t}" for t in topics)}

## Achados Principais

{chr(10).join(f"- {f}" for f in findings)}

## Citacoes Detectadas

{chr(10).join(f"- {c}" for c in knowledge.get('citations', [])[:10])}

## Workflow

### Step 1: Carregar contexto
Utilize o conhecimento extraido do PDF como base.

### Step 2: Aplicar topicos
Use os topicos identificados para guiar a pesquisa.

### Step 3: Validar achados
Cruze os achados com fontes adicionais.

### Step 4: Gerar output
Produza resultado integrando o conhecimento do PDF.

## Best Practices

1. Sempre referenciar o PDF original
2. Cruzar com fontes externas
3. Validar citacoes e referencias
4. Manter rastreabilidade
5. PT-BR formal

## Integration

| Component | Type | Connection |
|-----------|------|------------|
| pdf_to_markdown | Script | Conversao PDF |
| context_offload | Script | Persistencia |
| websearch | MCP | Validacao externa |
"""

        self.skills_dir.mkdir(parents=True, exist_ok=True)
        skill_file.write_text(skill_content, encoding="utf-8")
        logger.info(f"Skill generated: {skill_file.name}")
        return str(skill_file)

# ============================================================
# PDF Pipeline Manager
# ============================================================

class PDFPipelineManager:
    """
    Manages the complete PDF pipeline:
    Detect -> Convert -> Extract -> Generate Skills -> Update Index
    """

    def __init__(self, watch_dirs: list = None):
        self.watch_dirs = watch_dirs or [
            str(BASE_DIR.parent / "Downloads"),
            str(BASE_DIR / "documents"),
            str(BASE_DIR / "papers"),
        ]
        self.extractor = PDFKnowledgeExtractor()
        self.skill_generator = PDFSkillGenerator()
        self.pdf_index = self._load_index()

    def _load_index(self) -> dict:
        """Load PDF processing index."""
        if PDF_INDEX_PATH.exists():
            try:
                return json.loads(PDF_INDEX_PATH.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, KeyError):
                pass
        return {"processed": {}, "pending": [], "errors": {}}

    def _save_index(self):
        """Save PDF processing index."""
        EVOLVE_DIR.mkdir(parents=True, exist_ok=True)
        PDF_INDEX_PATH.write_text(
            json.dumps(self.pdf_index, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def scan_for_pdfs(self) -> list[Path]:
        """Scan watch directories for PDF files."""
        pdfs = []
        for dir_path in self.watch_dirs:
            d = Path(dir_path)
            if d.exists():
                for pdf in d.rglob("*.pdf"):
                    pdf_hash = hashlib.md5(pdf.read_bytes()[:1024]).hexdigest()
                    if pdf_hash not in self.pdf_index.get("processed", {}):
                        pdfs.append(pdf)
        return pdfs

    def process_pdf(self, pdf_path: Path) -> dict:
        """Process a single PDF through the full pipeline."""
        result = {
            "pdf": str(pdf_path),
            "timestamp": datetime.now().isoformat(),
            "status": "processing",
            "steps": {}
        }

        try:
            # Step 1: Convert PDF to Markdown
            logger.info(f"[PDF] Converting: {pdf_path.name}")
            md_path = self._convert_pdf(pdf_path)
            result["steps"]["conversion"] = "success" if md_path else "skipped"
            result["markdown_path"] = md_path

            if md_path and Path(md_path).exists():
                md_content = Path(md_path).read_text(encoding="utf-8")

                # Step 2: Extract knowledge
                logger.info(f"[PDF] Extracting knowledge: {pdf_path.name}")
                knowledge = self.extractor.extract_knowledge(md_content, str(pdf_path))
                result["steps"]["knowledge_extraction"] = "success"
                result["knowledge"] = {
                    "topics_count": len(knowledge["topics"]),
                    "citations_count": len(knowledge["citations"]),
                    "findings_count": len(knowledge["key_findings"]),
                }

                # Step 3: Save knowledge
                knowledge_file = self._save_knowledge(knowledge, pdf_path)
                result["knowledge_path"] = knowledge_file

                # Step 4: Generate skill
                logger.info(f"[PDF] Generating skill: {pdf_path.name}")
                skill_path = self.skill_generator.generate_skill_from_knowledge(knowledge)
                result["steps"]["skill_generation"] = "success" if skill_path else "no_skill"
                result["skill_path"] = skill_path

                # Update index
                pdf_hash = hashlib.md5(pdf_path.read_bytes()[:1024]).hexdigest()
                self.pdf_index["processed"][pdf_hash] = {
                    "pdf": str(pdf_path),
                    "timestamp": result["timestamp"],
                    "markdown": md_path,
                    "knowledge": knowledge_file,
                    "skill": skill_path,
                    "topics": knowledge["topics"][:5],
                }
                result["status"] = "completed"
            else:
                result["status"] = "no_content"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            pdf_hash = hashlib.md5(pdf_path.read_bytes()[:1024]).hexdigest() if pdf_path.exists() else "unknown"
            self.pdf_index["errors"][pdf_hash] = str(e)
            logger.error(f"[PDF] Error processing {pdf_path.name}: {e}")

        self._save_index()
        return result

    def _convert_pdf(self, pdf_path: Path) -> Optional[str]:
        """Convert PDF to Markdown using pdf_to_markdown.py."""
        try:
            from pdf_to_markdown import PDFToMarkdownConverter
            converter = PDFToMarkdownConverter(preserve_structure=True, academic_mode=True)
            output_dir = str(PDF_OUTPUT_DIR)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, pdf_path.stem + ".md")
            result = converter.convert(str(pdf_path), output_path)
            return result
        except ImportError:
            logger.warning("pdf_to_markdown.py not available, creating basic conversion")
            # Fallback: create a basic markdown file with metadata
            try:
                import fitz
                doc = fitz.open(str(pdf_path))
                meta = doc.metadata
                md_content = f"""<!-- SAIDA OBRIGATORIA: PORTUGUES BRASILEIRO FORMAL -->
<!-- Modelo: big-pickle -->

---
title: "{meta.get('title', pdf_path.stem)}"
author: "{meta.get('author', 'Unknown')}"
pages: {len(doc)}
source: {pdf_path.name}
---

# {meta.get('title', pdf_path.stem)}

**Author:** {meta.get('author', 'Unknown')}
**Pages:** {len(doc)}

"""
                for page_num in range(min(len(doc), 10)):  # First 10 pages
                    page = doc[page_num]
                    text = page.get_text("text")
                    md_content += f"\n## Page {page_num + 1}\n\n{text}\n"
                doc.close()

                os.makedirs(str(PDF_OUTPUT_DIR), exist_ok=True)
                output_path = os.path.join(str(PDF_OUTPUT_DIR), pdf_path.stem + ".md")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                return output_path
            except Exception as e:
                logger.error(f"PDF conversion failed: {e}")
                return None

    def _save_knowledge(self, knowledge: dict, pdf_path: Path) -> str:
        """Save extracted knowledge to file."""
        PDF_KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        knowledge_file = PDF_KNOWLEDGE_DIR / f"{pdf_path.stem}_knowledge.json"
        knowledge_file.write_text(
            json.dumps(knowledge, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return str(knowledge_file)

    def process_all_pending(self) -> list[dict]:
        """Process all pending PDFs."""
        pdfs = self.scan_for_pdfs()
        results = []
        for pdf in pdfs:
            logger.info(f"[PDF Pipeline] Processing: {pdf.name}")
            result = self.process_pdf(pdf)
            results.append(result)
        return results

    def get_index_summary(self) -> dict:
        """Get summary of PDF processing index."""
        processed = self.pdf_index.get("processed", {})
        errors = self.pdf_index.get("errors", {})
        return {
            "total_processed": len(processed),
            "total_errors": len(errors),
            "recent": list(processed.values())[-5:],
            "watch_dirs": self.watch_dirs,
        }

# ============================================================
# CLI Entry Point
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="PDF Ecosystem Integration v5.0")
    parser.add_argument("--scan", action="store_true", help="Scan for new PDFs")
    parser.add_argument("--process", action="store_true", help="Process all pending PDFs")
    parser.add_argument("--process-file", type=str, help="Process a specific PDF file")
    parser.add_argument("--status", action="store_true", help="Show PDF pipeline status")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    pipeline = PDFPipelineManager()

    if args.scan:
        pdfs = pipeline.scan_for_pdfs()
        if args.json:
            print(json.dumps({"pending_pdfs": [str(p) for p in pdfs]}, ensure_ascii=False, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"  PDF SCAN - {len(pdfs)} new PDFs found")
            print(f"{'='*60}")
            for p in pdfs:
                print(f"  - {p.name} ({p.stat().st_size / 1024:.0f}KB)")
            print(f"{'='*60}")

    elif args.process:
        results = pipeline.process_all_pending()
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
        else:
            print(f"\n{'='*60}")
            print(f"  PDF PROCESSING RESULTS")
            print(f"{'='*60}")
            for r in results:
                status_icon = "OK" if r["status"] == "completed" else r["status"].upper()
                print(f"  [{status_icon}] {Path(r['pdf']).name}")
                for step, result in r.get("steps", {}).items():
                    print(f"    {step}: {result}")
            print(f"{'='*60}")

    elif args.process_file:
        pdf_path = Path(args.process_file)
        if pdf_path.exists():
            result = pipeline.process_pdf(pdf_path)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
            else:
                print(f"\n{'='*60}")
                print(f"  PDF PROCESSING: {pdf_path.name}")
                print(f"{'='*60}")
                print(f"  Status: {result['status']}")
                for step, res in result.get("steps", {}).items():
                    print(f"  {step}: {res}")
                print(f"{'='*60}")
        else:
            print(f"File not found: {pdf_path}")

    elif args.status:
        summary = pipeline.get_index_summary()
        if args.json:
            print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
        else:
            print(f"\n{'='*60}")
            print(f"  PDF PIPELINE STATUS")
            print(f"{'='*60}")
            print(f"  Processed: {summary['total_processed']}")
            print(f"  Errors: {summary['total_errors']}")
            print(f"  Watch directories: {len(summary['watch_dirs'])}")
            if summary['recent']:
                print(f"\n  Recent:")
                for r in summary['recent']:
                    print(f"    - {Path(r['pdf']).name} ({r['timestamp'][:10]})")
            print(f"{'='*60}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
