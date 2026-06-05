---
name: pdf-rag-collections
description: "Sistema de busca hierárquica em 3000+ PDFs via coleções isoladas com SQLite FTS5"
---

# PDF RAG Collection System

Resolve degradação de RAG em bases grandes via coleções isoladas.

## Arquitetura

```
Query → Roteador (keywords) → Coleção FTS5 → Top-K chunks → LLM
```

## Comandos

```bash
# Ingerir diretório (auto-classificar)
python -m pdf_rag.cli ingest /path/to/pdfs --auto

# Ingerir com coleção fixa
python -m pdf_rag.cli ingest /path/to/pdfs -c tributario

# Buscar (roteamento automático)
python -m pdf_rag.cli search "prescrição intercorrente"

# Buscar em coleção específica
python -m pdf_rag.cli search "ICMS" -c tributario

# Modo interativo
python -m pdf_rag.cli interactive

# Listar coleções
python -m pdf_rag.cli collections
```

## Dependência

```bash
pip install pdfplumber
```
