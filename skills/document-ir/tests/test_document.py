"""
TDD tests for Document IR — Schema, Composer, Render Pipeline.
CT-1: test_init — criacao de Block, Anchor e Document
CT-2: test_compose — DocumentComposer com dedup e ordenacao
CT-3: test_pipeline — DocumentPipeline com 7 estagios
CT-4: test_available — validacao de schema e tipos
"""

import os
import sys
import tempfile
import pytest

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, SCRIPT_DIR)

from schema import (
    Block, Anchor, Document, BlockType,
    block_to_dict, block_from_dict,
    validate_block, validate_anchor, validate_document,
    BLOCK_JSON_SCHEMA, SCHEMA_REGISTRY,
)
from composer import DocumentComposer, compose, ComposerConfig
from renderer import DocumentPipeline, TEMPLATES


class TestDocumentIR:

    def test_init(self):
        block = Block(type=BlockType.HEADING1, content="Introducao", position=0)
        assert block.type == BlockType.HEADING1
        assert block.content == "Introducao"
        assert block.position == 0

        anchor = Anchor(anchor_id="ref-1", target="#intro", block_type=BlockType.HEADING1)
        assert anchor.anchor_id == "ref-1"

        doc = Document(
            title="Teste", blocks=[block], anchors=[anchor],
            metadata={"author": "test"}, template="default",
        )
        assert doc.title == "Teste"
        assert doc.word_count > 0

    def test_compose(self):
        blocks = [
            Block(type=BlockType.HEADING1, content="Intro", position=2),
            Block(type=BlockType.PARAGRAPH, content="Texto", position=1),
        ]
        anchors = [
            Anchor(anchor_id="a1", target="#x", block_type=BlockType.PARAGRAPH),
        ]
        composer = DocumentComposer()
        doc = composer.compose(blocks, anchors, title="Doc Teste")
        assert doc.blocks[0].position <= doc.blocks[1].position
        assert len(doc.anchors) == 1
        assert "reference_index" in doc.metadata

    def test_pipeline(self):
        pipeline = DocumentPipeline()
        blocks = [
            Block(type=BlockType.HEADING1, content="Introducao", position=0, confidence=1.0),
            Block(type=BlockType.PARAGRAPH, content="Analise de dados.", position=1, confidence=0.9),
            Block(type=BlockType.HEADING2, content="Resultados", position=2, confidence=1.0),
            Block(type=BlockType.METRIC_CARD, content="Taxa: 94.7%", position=3, confidence=0.85),
        ]
        anchors = []
        doc = pipeline.run(
            title="Relatorio P15", blocks=blocks, anchors=anchors,
            document_type="report", audience="executive",
            metadata={"max_words": 1000},
        )
        assert doc.title == "Relatorio P15"
        md = pipeline.render_markdown(doc)
        assert "Introducao" in md
        assert "Taxa: 94.7%" in md

    def test_available(self):
        assert len(BlockType) == 16
        assert len(SCHEMA_REGISTRY) == 3
        assert "block" in SCHEMA_REGISTRY
        assert "document" in SCHEMA_REGISTRY

        ok, errors = validate_block({"type": "paragraph", "content": "teste"})
        assert ok is True

        ok2, errors2 = validate_block({"type": "invalid_type", "content": "x"})
        assert ok2 is False

        d = block_to_dict(Block(type=BlockType.PARAGRAPH, content="x"))
        assert d["type"] == "paragraph"
        b = block_from_dict(d)
        assert b.type == BlockType.PARAGRAPH
