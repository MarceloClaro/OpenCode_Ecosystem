"""
P15 — Document IR Pipeline (Renderer)

Pipeline de 7 estagios para geracao de documentos estruturados:
1. Template Selection
2. Layout Planning
3. Word Budget Allocation
4. Chapter Generation
5. Quality Control
6. Document Composer
7. Render

Extraido do BettaFish ReportEngine (agent.py + ir/schema.py).

Uso:
    from renderer import DocumentPipeline
    pipeline = DocumentPipeline()
    doc = pipeline.run(title="Relatorio", blocks=[...], anchors=[...])
    markdown = pipeline.render_markdown(doc)
"""

import json
import re
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Callable

from schema import Block, BlockType, Anchor, Document, block_to_dict
from composer import DocumentComposer, ComposerConfig


# ─── Enums ────────────────────────────────────────────────────────────────────

class DocumentType(Enum):
    REPORT = "report"
    PROPOSAL = "proposal"
    ANALYSIS = "analysis"
    MANUAL = "manual"


class Audience(Enum):
    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    GENERAL = "general"
    ACADEMIC = "academic"


class PipelineStage(Enum):
    TEMPLATE_SELECTION = "template_selection"
    LAYOUT_PLANNING = "layout_planning"
    WORD_BUDGET = "word_budget"
    CHAPTER_GEN = "chapter_generation"
    QC = "quality_control"
    COMPOSER = "composer"
    RENDER = "render"


# ─── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class Template:
    """Template de documento."""
    name: str
    document_type: DocumentType
    audience: Audience
    sections: list[str]
    metadata: dict = field(default_factory=dict)


@dataclass
class Layout:
    """Layout planejado para o documento."""
    sections: list[dict]  # [{"name": str, "level": int, "order": int}, ...]
    total_blocks_estimate: int = 0


@dataclass
class Budget:
    """Orcamento de palavras por secao."""
    section_budgets: dict[str, int]  # secao -> palavras
    total_words: int = 0
    reserved_intro: int = 0
    reserved_conclusion: int = 0


@dataclass
class QCRule:
    """Regra de qualidade."""
    name: str
    description: str
    check: Callable  # (block: Block) -> bool


# ─── Templates pre-definidos ──────────────────────────────────────────────────

TEMPLATES = {
    "report_executive": Template(
        name="Relatorio Executivo",
        document_type=DocumentType.REPORT,
        audience=Audience.EXECUTIVE,
        sections=["Sumario Executivo", "Contexto", "Descobertas", "Recomendacoes"],
        metadata={"max_words": 2000, "include_toc": True},
    ),
    "report_technical": Template(
        name="Relatorio Tecnico",
        document_type=DocumentType.REPORT,
        audience=Audience.TECHNICAL,
        sections=["Introducao", "Metodologia", "Resultados", "Discussao", "Conclusao"],
        metadata={"max_words": 5000, "include_toc": True},
    ),
    "analysis_general": Template(
        name="Analise Geral",
        document_type=DocumentType.ANALYSIS,
        audience=Audience.GENERAL,
        sections=["Visao Geral", "Pontos-Chave", "Implicacoes", "Proximos Passos"],
        metadata={"max_words": 1500, "include_toc": False},
    ),
    "proposal_executive": Template(
        name="Proposta Executiva",
        document_type=DocumentType.PROPOSAL,
        audience=Audience.EXECUTIVE,
        sections=["Problema", "Solucao", "Investimento", "Cronograma"],
        metadata={"max_words": 3000, "include_toc": True},
    ),
}

DEFAULT_TEMPLATE = TEMPLATES["report_executive"]


# ─── Pipeline ─────────────────────────────────────────────────────────────────

class DocumentPipeline:
    """Pipeline de 7 estagios para geracao de documentos."""
    
    def __init__(self):
        self.composer = DocumentComposer()
        self.current_template: Optional[Template] = None
        self.current_layout: Optional[Layout] = None
        self.current_budget: Optional[Budget] = None
        self.stage_results: dict[str, dict] = {}
    
    # ─── API Publica ───────────────────────────────────────────────────────
    
    def run(self,
            title: str,
            blocks: list[Block],
            anchors: list[Anchor],
            document_type: str = "report",
            audience: str = "executive",
            metadata: Optional[dict] = None,
            template_name: str = "") -> Document:
        """Executa pipeline completo."""
        
        # Stage 1
        template = self.select_template(document_type, audience, template_name)
        
        # Stage 2
        layout = self.plan_layout(template)
        
        # Stage 3
        budget = self.allocate_budget(layout, total_words=metadata.get("max_words", 2000) if metadata else 2000)
        
        # Stage 4 — blocks ja sao o output da geracao de capitulos
        # (geracao LLM real seria feita externamente)
        
        # Stage 5
        qc_blocks = self.qc_pass(blocks)
        
        # Stage 6
        doc = self.composer.compose(
            blocks=qc_blocks,
            anchors=anchors,
            title=title,
            metadata={
                "document_type": document_type,
                "audience": audience,
                "template": template.name,
                "layout": {
                    "sections": layout.sections,
                    "total_blocks_estimate": layout.total_blocks_estimate,
                },
                "budget": {
                    "total_words": budget.total_words,
                    "section_budgets": budget.section_budgets,
                },
                **(metadata or {}),
            },
            template=template.name,
        )
        
        return doc
    
    def render_markdown(self, doc: Document) -> str:
        """Renderiza documento em markdown."""
        lines: list[str] = []
        
        # Frontmatter
        lines.append("---")
        lines.append(f"title: {doc.title}")
        lines.append(f"template: {doc.template}")
        lines.append(f"created: {doc.created_at}")
        lines.append(f"words: {doc.word_count}")
        lines.append(f"blocks: {len(doc.blocks)}")
        lines.append("---")
        lines.append("")
        
        # TOC
        toc = doc.metadata.get("table_of_contents", [])
        if toc:
            lines.append("## Sumario")
            for entry in toc:
                indent = "  " * (entry["level"] - 1)
                anchor = f" [#{entry['anchor_id']}]" if entry["anchor_id"] else ""
                lines.append(f"{indent}- {entry['title']}{anchor}")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Blocos
        for block in doc.blocks:
            rendered = self._render_block(block)
            if rendered:
                lines.append(rendered)
                lines.append("")
        
        # Referencias
        refs = doc.metadata.get("reference_index", {})
        if refs:
            lines.append("---")
            lines.append("## Referencias Cruzadas")
            for anchor_id, positions in refs.items():
                lines.append(f"- `{anchor_id}`: blocos nas posicoes {positions}")
        
        return "\n".join(lines)
    
    def render_json(self, doc: Document, indent: int = 2) -> str:
        """Renderiza documento em JSON."""
        from schema import document_to_json
        return document_to_json(doc, indent)
    
    # ─── Stage 1: Template Selection ───────────────────────────────────────
    
    def select_template(self, document_type: str, audience: str,
                        template_name: str = "") -> Template:
        """Seleciona template."""
        if template_name:
            key = template_name.lower().replace(" ", "_")
            if key in TEMPLATES:
                self.current_template = TEMPLATES[key]
                return self.current_template
        
        # Match por tipo + audiencia
        key = f"{document_type}_{audience}"
        self.current_template = TEMPLATES.get(key, DEFAULT_TEMPLATE)
        return self.current_template
    
    # ─── Stage 2: Layout Planning ──────────────────────────────────────────
    
    def plan_layout(self, template: Template) -> Layout:
        """Planeja layout do documento."""
        sections = []
        for i, section in enumerate(template.sections):
            level = 1 if i == 0 else 2
            sections.append({
                "name": section,
                "level": level,
                "order": i,
            })
        
        self.current_layout = Layout(
            sections=sections,
            total_blocks_estimate=len(sections) * 3,  # estimativa
        )
        return self.current_layout
    
    # ─── Stage 3: Word Budget ──────────────────────────────────────────────
    
    def allocate_budget(self, layout: Layout, total_words: int) -> Budget:
        """Aloca orcamento de palavras."""
        n = len(layout.sections)
        if n == 0:
            return Budget(section_budgets={}, total_words=0)
        
        reserved = int(total_words * 0.15)
        remaining = total_words - (reserved * 2)  # intro + conclusion
        
        per_section = remaining // n if n > 0 else 0
        section_budgets = {}
        
        for i, section in enumerate(layout.sections):
            if i == 0:
                section_budgets[section["name"]] = reserved + per_section
            elif i == n - 1:
                section_budgets[section["name"]] = reserved + per_section
            else:
                section_budgets[section["name"]] = per_section
        
        self.current_budget = Budget(
            section_budgets=section_budgets,
            total_words=total_words,
            reserved_intro=reserved,
            reserved_conclusion=reserved,
        )
        return self.current_budget
    
    # ─── Stage 5: Quality Control ──────────────────────────────────────────
    
    def qc_pass(self, blocks: list[Block]) -> list[Block]:
        """Valida blocos e remove/ajusta os que falham."""
        rules: list[QCRule] = [
            QCRule("content_not_empty", "Conteudo nao pode ser vazio",
                   lambda b: bool(b.content.strip())),
            QCRule("valid_confidence", "Confianca entre 0 e 1",
                   lambda b: 0 <= b.confidence <= 1),
            QCRule("valid_position", "Posicao nao negativa",
                   lambda b: b.position >= 0),
        ]
        
        passed: list[Block] = []
        for block in blocks:
            failed_rules = []
            for rule in rules:
                if not rule.check(block):
                    failed_rules.append(rule.name)
            
            if failed_rules:
                print(f"[QC] Bloco #{block.position} falhou: {failed_rules}")
                # Apenas remove blocos completamente vazios
                if "content_not_empty" in failed_rules:
                    continue
            
            passed.append(block)
        
        return passed
    
    # ─── Render Helpers ────────────────────────────────────────────────────
    
    def _render_block(self, block: Block) -> str:
        """Renderiza bloco individual em markdown."""
        confidence_tag = ""
        if block.confidence < 0.4:
            confidence_tag = " *(lacuna)*"
        elif block.confidence < 0.8:
            confidence_tag = " *(inferido)*"
        
        anchor = f" [#{block.anchor_id}]" if block.anchor_id else ""
        
        renderers = {
            BlockType.HEADING1: lambda: f"# {block.content}{anchor}{confidence_tag}",
            BlockType.HEADING2: lambda: f"## {block.content}{anchor}{confidence_tag}",
            BlockType.HEADING3: lambda: f"### {block.content}{anchor}{confidence_tag}",
            BlockType.PARAGRAPH: lambda: f"{block.content}{confidence_tag}",
            BlockType.BULLET_LIST: lambda: self._render_list(block, "- "),
            BlockType.NUMBERED_LIST: lambda: self._render_list(block, "1. "),
            BlockType.CODE_BLOCK: lambda: self._render_code(block),
            BlockType.TABLE: lambda: f"| {block.content} |{confidence_tag}",
            BlockType.QUOTE: lambda: f"> {block.content}{confidence_tag}",
            BlockType.CALL_TO_ACTION: lambda: f"> ⚠️ **{block.content}**{confidence_tag}",
            BlockType.METRIC_CARD: lambda: f"**{block.content}**{confidence_tag}",
            BlockType.ANCHOR: lambda: f"[{block.anchor_id}]: {block.content}",
            BlockType.DIVIDER: lambda: "---",
            BlockType.IMAGE_PLACEHOLDER: lambda: f"![{block.content}](placeholder.png)",
            BlockType.FOOTNOTE: lambda: f"[^{block.anchor_id}]: {block.content}",
            BlockType.RAW_HTML: lambda: block.content if block.content.startswith("<") else f"```html\n{block.content}\n```",
        }
        
        renderer = renderers.get(block.type)
        if renderer:
            return renderer()
        return block.content
    
    def _render_list(self, block: Block, prefix: str) -> str:
        """Renderiza bloco de lista."""
        items = block.content.split("\n")
        return "\n".join(f"{prefix}{item.strip()}" for item in items if item.strip())
    
    def _render_code(self, block: Block) -> str:
        """Renderiza bloco de codigo."""
        lang = block.metadata.get("lang", "") if block.metadata else ""
        return f"```{lang}\n{block.content}\n```"


# ─── Conveniencia ─────────────────────────────────────────────────────────────

def create_pipeline() -> DocumentPipeline:
    """Factory function."""
    return DocumentPipeline()


def demo():
    """Demonstracao do pipeline completo."""
    from schema import Block, BlockType, Anchor
    
    pipeline = create_pipeline()
    
    blocks = [
        Block(type=BlockType.HEADING1, content="Introducao", position=0, confidence=1.0),
        Block(type=BlockType.PARAGRAPH, content="Este relatorio analisa...", position=1, confidence=0.9),
        Block(type=BlockType.HEADING2, content="Resultados", position=2, confidence=1.0),
        Block(type=BlockType.METRIC_CARD, content="Taxa de sucesso: 94.7%", position=3, confidence=0.85, anchor_id="metric-success"),
        Block(type=BlockType.BULLET_LIST, content="Item 1\nItem 2\nItem 3", position=4, confidence=0.8),
        Block(type=BlockType.HEADING1, content="Conclusao", position=5, confidence=1.0),
        Block(type=BlockType.QUOTE, content="Resultado positivo.", position=6, confidence=0.7),
    ]
    
    anchors = [
        Anchor(anchor_id="metric-success", target="#sucesso", block_type=BlockType.METRIC_CARD),
    ]
    
    doc = pipeline.run(
        title="Relatorio de Exemplo P15",
        blocks=blocks,
        anchors=anchors,
        document_type="report",
        audience="executive",
        metadata={"max_words": 2000},
    )
    
    print("=== MARKDOWN ===")
    print(pipeline.render_markdown(doc))
    
    print("\n=== JSON (primeiros 500 chars) ===")
    json_str = pipeline.render_json(doc)
    print(json_str[:500] + "...")
    
    return doc


if __name__ == "__main__":
    demo()
