"""Configuração centralizada.

Lê config.yaml se existir; senão, usa defaults. Caminhos são absolutos a partir
da raiz do projeto.
"""
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass, field
import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
WIKI_DIR = DATA_DIR / "wiki"
RAW_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "wiki.db"
SCHEMA_PATH = DATA_DIR / "schema.md"
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


@dataclass
class Config:
    """Configuração runtime do MVP."""
    ollama_host: str = "http://localhost:11434"
    # Modelo principal — usado para ingestão, síntese, queries
    model_main: str = "llama3.1:8b"
    # Modelo leve — usado para tarefas rápidas (classificação, extração)
    model_light: str = "llama3.1:8b"
    # Modelo de embeddings — para busca semântica entre páginas
    embedding_model: str = "all-MiniLM-L6-v2"
    # Temperatura — baixa para tarefas estruturadas
    temperature: float = 0.2
    # Categorias da wiki (definem subpastas em data/wiki/)
    categories: list[str] = field(default_factory=lambda: [
        "topicos", "entidades", "conceitos", "sinteses", "fontes"
    ])
    # Streaming no chat
    enable_streaming: bool = True

    @classmethod
    def load(cls) -> "Config":
        """Carrega config.yaml; cai no default se não existir."""
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        return cls()

    def save(self) -> None:
        """Persiste configuração atual em config.yaml."""
        data = {k: getattr(self, k) for k in self.__dataclass_fields__}
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def ensure_dirs() -> None:
    """Garante que toda a estrutura de pastas existe."""
    cfg = Config.load()
    DATA_DIR.mkdir(exist_ok=True)
    RAW_DIR.mkdir(exist_ok=True)
    WIKI_DIR.mkdir(exist_ok=True)
    for cat in cfg.categories:
        (WIKI_DIR / cat).mkdir(exist_ok=True)
