"""
P15 — Document Composer

Composicao de documentos com dedup de ancoras, ordenacao de blocos e
geracao de indice de referencias cruzadas.
Extraido do BettaFish ReportEngine (core/stitcher.py).

Uso:
    from composer import compose, DocumentComposer
    doc = compose(blocks, anchors, title="Meu Documento")
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from schema import Block, BlockType, Anchor, Document, block_to_dict, asdict


# ─── Config ───────────────────────────────────────────────────────────────────

COMPOSER_VERSION = "1.0"

# Estrategia de dedup
DEDUP_KEEP_FIRST = "keep_first"
DEDUP_KEEP_LAST = "keep_last"


# ─── Document Composer ────────────────────────────────────────────────────────

@dataclass
class ComposerConfig:
    """Configuracao do composer."""
    dedup_strategy: str = DEDUP_KEEP_FIRST
    generate_toc: bool = True
    validate_anchors: bool = True
    sort_blocks: bool = True


class DocumentComposer:
    """Compoe documento final a partir de blocos e ancoras."""
    
    def __init__(self, config: Optional[ComposerConfig] = None):
        self.config = config or ComposerConfig()
    
    def compose(self,
                blocks: list[Block],
                anchors: list[Anchor],
                title: str,
                metadata: Optional[dict] = None,
                template: str = "default") -> Document:
        """Compoe documento completo."""
        blocks = list(blocks)
        anchors = list(anchors)
        
        # 1. Dedup ancoras
        anchors = self._dedup_anchors(anchors)
        
        # 2. Ordenar blocos por posicao
        if self.config.sort_blocks:
            blocks.sort(key=lambda b: b.position)
        
        # 3. Validar ancoras referenciadas
        if self.config.validate_anchors:
            self._validate_cross_refs(blocks, anchors)
        
        # 4. Remover blocos orfaos (se houver ancora invalida)
        blocks = self._remove_orphan_anchors(blocks, anchors)
        
        # 5. Gerar indice de referencias
        ref_index = self._build_reference_index(blocks, anchors)
        
        # 6. Construir documento
        all_metadata = {
            "composer_version": COMPOSER_VERSION,
            "dedup_strategy": self.config.dedup_strategy,
            "total_blocks": len(blocks),
            "total_anchors": len(anchors),
            "reference_index": ref_index,
            **(metadata or {}),
        }
        
        if self.config.generate_toc:
            toc = self._generate_toc(blocks)
            all_metadata["table_of_contents"] = toc
        
        doc = Document(
            title=title,
            blocks=blocks,
            anchors=anchors,
            metadata=all_metadata,
            template=template,
        )
        
        return doc
    
    def compose_from_dicts(self,
                           block_dicts: list[dict],
                           anchor_dicts: list[dict],
                           title: str,
                           metadata: Optional[dict] = None,
                           template: str = "default") -> Document:
        """Compoe documento a partir de dicts (uteis para desserializacao)."""
        from schema import block_from_dict
        
        blocks = [block_from_dict(bd) for bd in block_dicts]
        anchors = [Anchor(**ad) for ad in anchor_dicts]
        
        return self.compose(blocks, anchors, title, metadata, template)
    
    # ─── Privado ───────────────────────────────────────────────────────────
    
    def _dedup_anchors(self, anchors: list[Anchor]) -> list[Anchor]:
        """Remove ancoras duplicadas."""
        seen: set[str] = set()
        result: list[Anchor] = []
        
        if self.config.dedup_strategy == DEDUP_KEEP_LAST:
            anchors = list(reversed(anchors))
        
        for anchor in anchors:
            if anchor.anchor_id not in seen:
                seen.add(anchor.anchor_id)
                result.append(anchor)
        
        if self.config.dedup_strategy == DEDUP_KEEP_LAST:
            result.reverse()
        
        return result
    
    def _validate_cross_refs(self, blocks: list[Block], anchors: list[Anchor]):
        """Verifica se todas as ancoras referenciadas existem."""
        anchor_ids = {a.anchor_id for a in anchors}
        refs = set()
        
        for block in blocks:
            if block.anchor_id and block.anchor_id in anchor_ids:
                refs.add(block.anchor_id)
        
        orphan_refs = anchor_ids - refs
        if orphan_refs:
            print(f"[Composer] Aviso: ancoras nao referenciadas: {orphan_refs}")
    
    def _remove_orphan_anchors(self, blocks: list[Block],
                                anchors: list[Anchor]) -> list[Block]:
        """Remove blocos cuja ancora de origem nao existe mais."""
        active_ids = {a.anchor_id for a in anchors}
        
        # So remove blocos ANCHOR que referenciam algo inexistente
        cleaned: list[Block] = []
        for block in blocks:
            if block.type == BlockType.ANCHOR and block.anchor_id:
                if block.anchor_id not in active_ids:
                    continue
            cleaned.append(block)
        
        return cleaned
    
    def _build_reference_index(self, blocks: list[Block],
                                anchors: list[Anchor]) -> dict:
        """Constroi indice de referencia: ancora → lista de blocos que a usam."""
        index: dict[str, list[int]] = {}
        
        anchor_map = {a.anchor_id: a for a in anchors}
        
        for block in blocks:
            if block.anchor_id and block.anchor_id in anchor_map:
                if block.anchor_id not in index:
                    index[block.anchor_id] = []
                index[block.anchor_id].append(block.position)
        
        return index
    
    def _generate_toc(self, blocks: list[Block]) -> list[dict]:
        """Gera tabela de conteudo baseada em headings."""
        toc: list[dict] = []
        
        for block in blocks:
            if block.type in (BlockType.HEADING1, BlockType.HEADING2, BlockType.HEADING3):
                level = {
                    BlockType.HEADING1: 1,
                    BlockType.HEADING2: 2,
                    BlockType.HEADING3: 3,
                }[block.type]
                
                toc.append({
                    "level": level,
                    "title": block.content,
                    "position": block.position,
                    "anchor_id": block.anchor_id or "",
                })
        
        return toc


# ─── Funcao de conveniencia ───────────────────────────────────────────────────

def compose(blocks: list[Block],
            anchors: list[Anchor],
            title: str,
            metadata: Optional[dict] = None,
            template: str = "default") -> Document:
    """Compoe documento com configuracao padrao."""
    composer = DocumentComposer()
    return composer.compose(blocks, anchors, title, metadata, template)


def demo():
    """Demonstracao do composer."""
    from schema import Block, BlockType, Anchor
    
    blocks = [
        Block(type=BlockType.HEADING1, content="Introducao", position=0),
        Block(type=BlockType.PARAGRAPH, content="Este e um documento de exemplo.", position=1),
        Block(type=BlockType.HEADING2, content="Analise", position=2),
        Block(type=BlockType.METRIC_CARD, content="Precisao: 95%", position=3, anchor_id="metric-acc"),
        Block(type=BlockType.HEADING1, content="Conclusao", position=4),
        Block(type=BlockType.QUOTE, content="Resultados promissores.", position=5),
    ]
    
    anchors = [
        Anchor(anchor_id="metric-acc", target="#precisao", block_type=BlockType.METRIC_CARD),
    ]
    
    doc = compose(blocks, anchors, title="Relatorio de Exemplo")
    
    print(f"Documento: {doc.title}")
    print(f"Blocos: {doc.word_count} palavras")
    print(f"TOC: {len(doc.metadata.get('table_of_contents', []))} entradas")
    print(f"Ancoras: {len(doc.anchors)}")
    
    return doc


if __name__ == "__main__":
    demo()
