# -*- coding: utf-8 -*-
"""
PDF RAG Collection System v1.0
Pipeline de ingestão e busca hierárquica para 3000+ PDFs.

Arquitetura:
  Ingestor (paralelo) → SQLite FTS5 (coleções) → Roteador → LLM

Resolve o problema de degradação RAG em bases grandes via coleções isoladas.
"""

__version__ = "1.0.0"
