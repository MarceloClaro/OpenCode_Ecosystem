"""
P15 — Document IR Schema

16 tipos de bloco para documentos estruturados, com validacao JSON Schema.
Extraido do ReportEngine do BettaFish (ir/schema.py).

Uso:
    from schema import Block, BlockType, validate_block, SCHEMA_REGISTRY
"""

import json
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


# ─── Block Types ──────────────────────────────────────────────────────────────

class BlockType(Enum):
    """16 tipos de bloco do Document IR."""
    HEADING1 = "heading1"
    HEADING2 = "heading2"
    HEADING3 = "heading3"
    PARAGRAPH = "paragraph"
    BULLET_LIST = "bullet_list"
    NUMBERED_LIST = "numbered_list"
    CODE_BLOCK = "code_block"
    TABLE = "table"
    QUOTE = "quote"
    CALL_TO_ACTION = "call_to_action"
    METRIC_CARD = "metric_card"
    ANCHOR = "anchor"
    DIVIDER = "divider"
    IMAGE_PLACEHOLDER = "image_placeholder"
    FOOTNOTE = "footnote"
    RAW_HTML = "raw_html"


# ─── JSON Schema Registry ────────────────────────────────────────────────────

BLOCK_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": [bt.value for bt in BlockType]},
        "content": {"type": "string", "minLength": 1},
        "metadata": {"type": "object"},
        "position": {"type": "integer", "minimum": 0},
        "anchor_id": {"type": "string", "pattern": "^[a-zA-Z_][a-zA-Z0-9_-]*$"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": ["type", "content"],
    "additionalProperties": False,
}

ANCHOR_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "anchor_id": {"type": "string", "minLength": 1},
        "target": {"type": "string", "minLength": 1},
        "block_type": {"type": "string"},
        "source": {"type": "string"},
    },
    "required": ["anchor_id", "target", "block_type"],
    "additionalProperties": False,
}

DOCUMENT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "minLength": 1},
        "blocks": {"type": "array", "items": BLOCK_JSON_SCHEMA},
        "anchors": {"type": "array", "items": ANCHOR_JSON_SCHEMA},
        "metadata": {"type": "object"},
        "template": {"type": "string"},
        "created_at": {"type": "string"},
        "word_count": {"type": "integer", "minimum": 0},
    },
    "required": ["title", "blocks", "anchors", "metadata", "template", "created_at"],
    "additionalProperties": False,
}

SCHEMA_REGISTRY = {
    "block": BLOCK_JSON_SCHEMA,
    "anchor": ANCHOR_JSON_SCHEMA,
    "document": DOCUMENT_JSON_SCHEMA,
}


# ─── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class Block:
    """Bloco de conteudo do documento."""
    type: BlockType
    content: str
    metadata: dict = field(default_factory=dict)
    position: int = 0
    anchor_id: str = ""
    confidence: float = 0.5


@dataclass
class Anchor:
    """Âncora de referencia cruzada entre blocos."""
    anchor_id: str
    target: str
    block_type: BlockType
    source: str = ""


@dataclass
class Document:
    """Documento completo composto por blocos + ancoras."""
    title: str
    blocks: list[Block]
    anchors: list[Anchor]
    metadata: dict
    template: str
    created_at: str = ""
    word_count: int = 0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        self.word_count = sum(len(b.content.split()) for b in self.blocks)


# ─── Validacao ─────────────────────────────────────────────────────────────────

def validate_block(block: dict) -> tuple[bool, list[str]]:
    """Valida dict de bloco contra JSON Schema."""
    try:
        import jsonschema
        try:
            jsonschema.validate(block, BLOCK_JSON_SCHEMA)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [str(e)]
    except ImportError:
        # Fallback: validacao basica sem jsonschema
        errors = []
        if "type" not in block or "content" not in block:
            errors.append("Campos obrigatorios: type, content")
        if "type" in block and block["type"] not in [bt.value for bt in BlockType]:
            errors.append(f"Tipo invalido: {block.get('type')}")
        return (len(errors) == 0, errors)


def validate_anchor(anchor: dict) -> tuple[bool, list[str]]:
    """Valida dict de ancora."""
    try:
        import jsonschema
        try:
            jsonschema.validate(anchor, ANCHOR_JSON_SCHEMA)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [str(e)]
    except ImportError:
        errors = []
        for field in ("anchor_id", "target", "block_type"):
            if field not in anchor:
                errors.append(f"Campo obrigatorio: {field}")
        return (len(errors) == 0, errors)


def validate_document(document: dict) -> tuple[bool, list[str]]:
    """Valida dict de documento completo."""
    try:
        import jsonschema
        try:
            jsonschema.validate(document, DOCUMENT_JSON_SCHEMA)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [str(e)]
    except ImportError:
        errors = []
        for field in ("title", "blocks", "anchors", "metadata", "template", "created_at"):
            if field not in document:
                errors.append(f"Campo obrigatorio: {field}")
        return (len(errors) == 0, errors)


# ─── Helpers ───────────────────────────────────────────────────────────────────

def block_to_dict(block: Block) -> dict:
    """Converte Block para dict serializavel."""
    d = asdict(block)
    d["type"] = block.type.value
    return d


def block_from_dict(data: dict) -> Block:
    """Reconstroi Block de dict."""
    data = dict(data)
    data["type"] = BlockType(data.pop("type"))
    return Block(**data)


def anchor_to_dict(anchor: Anchor) -> dict:
    """Converte Anchor para dict serializavel."""
    d = asdict(anchor)
    d["block_type"] = anchor.block_type.value
    return d


def document_to_dict(doc: Document) -> dict:
    """Converte Document para dict serializavel."""
    return {
        "title": doc.title,
        "blocks": [block_to_dict(b) for b in doc.blocks],
        "anchors": [anchor_to_dict(a) for a in doc.anchors],
        "metadata": doc.metadata,
        "template": doc.template,
        "created_at": doc.created_at,
        "word_count": doc.word_count,
    }


def document_to_json(doc: Document, indent: int = 2) -> str:
    """Serializa Document para JSON string."""
    return json.dumps(document_to_dict(doc), ensure_ascii=False, indent=indent)
