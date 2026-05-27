---
name: docling-pdf-extraction
description: "Extracao avancada de documentos via Docling (IBM Research)"
user-invocable: true
license: MIT
compatibility: OpenCode, Claude Code, Cursor, Gemini CLI
metadata:
  author: OpenCode Ecosystem
  version: "2.0.0"
  openclaw:
        emoji: "📄"
    homepage: https://github.com/anomalyco/opencode
allowed-tools: Read Edit Write Glob Grep Bash Pdf Docling
---

<!--
  SAIDA OBRIGATORIA: PORTUGUES BRASILEIRO FORMAL
  Toda resposta DEVE ser em portugues do Brasil formal.
  Contexto em chines para eficiencia de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# docling-pdf-extraction

## Visao Geral
Skill que utiliza Docling (IBM Research, LF AI and Data) para extracao avancada de documentos. Substitui o pipeline PDF legacy do ecossistema com capacidades superiores de entendimento de documento.

## Quando Usar
- Converter PDFs com extracao de layout e reading order
- Extrair estrutura de tabelas de documentos
- Processar PDFs escaneados via OCR nativo
- Converter multi-formatos (DOCX, PPTX, XLSX, HTML, imagens)
- Gerar skills automaticas a partir de conteudo extraido
- Alimentar evolution loop com conhecimento rico

## Formatos Suportados
- PDF (com layout understanding via Heron model)
- DOCX, PPTX, XLSX (Office documents)
- HTML
- Imagens: PNG, TIFF, JPEG

## Outputs
- Markdown (com estrutura preservada)
- HTML
- DocTag (formato Docling)
- JSON estruturado (DoclingDocument schema)

## Integracao com Ecossistema
- Evolution Loop (fase INTEGRATE)
- Context Offload (armazenamento de conhecimento)
- Skill Generator (geracao automatica de skills)
- Manus Evolve Bridge (feedback loop)

## Uso via Python
from docling_adapter import DoclingAdapter, DoclingSkillGenerator
adapter = DoclingAdapter(enable_ocr=True, enable_tables=True)
extraction = adapter.extract_knowledge(documento.pdf)
generator = DoclingSkillGenerator()
skill_path = generator.generate_from_extraction(extraction, documento.pdf)

## Arquitetura
1. DETECT: Detectar formato do documento
2. CONVERT: Docling converte com layout understanding
3. EXTRACT: Extrair topics, findings, citations, tables
4. INDEX: Indexar para evolution loop
5. OFFLOAD: Armazenar no context offload
6. GENERATE: Criar skills automaticas

## Vantagens vs Pipeline Legacy
- Layout understanding com modelo Heron
- Extracao de estrutura de tabelas
- OCR nativo (RapidOCR)
- Multi-formato (nao apenas PDF)
- DoclingDocument schema unificado
