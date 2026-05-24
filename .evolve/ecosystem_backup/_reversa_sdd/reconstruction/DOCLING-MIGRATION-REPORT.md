# Docling Migration Report - Injeção de Dependência (Fase 4)

## Resumo

O diretório `docling/` contém o **IBM Docling SDK v2.68.0 completo** (263+ arquivos, ~60MB) — um SDK externo maduro mantido pela IBM. **Não há refatoração interna do SDK**. Esta fase cria apenas wrappers finos com interfaces `IDocumentBackend` e uma `BackendFactory` para uso via DI no ecossistema OpenCode.

## Decisão Arquitetural

```
┌─────────────────────────────────────────────────────┐
│                   OpenCode Ecosystem                 │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │         DoclingService (DI wrapper)           │   │
│  │  - state_manager: IStateManager               │   │
│  │  - event_bus: IEventBus                       │   │
│  │  - factory: BackendFactory                    │   │
│  └──────────────────┬───────────────────────────┘   │
│                     │                                 │
│  ┌──────────────────▼───────────────────────────┐   │
│  │           BackendFactory                       │   │
│  │  - register(backend)                          │   │
│  │  - get_backend(format, preferred)             │   │
│  │  - list_available()                           │   │
│  │  - health_check()                             │   │
│  └──┬────────────┬────────────┬─────────────────┘   │
│     │            │            │                       │
│  ┌──▼──┐   ┌─────▼──┐   ┌───▼────────┐               │
│  │ IBM │   │ PyMuPDF │   │ Scraping   │               │
│  │SDK  │   │ (rápido)│   │ (fallback) │               │
│  └─────┘   └────────┘   └────────────┘               │
│     │            │                                    │
│  ┌──▼──────────────────────────────┐                  │
│  │  docling/ (SDK IBM, 263+ arquivos)                │
│  │  - NÃO MODIFICADO                                 │
│  │  - Mantido pela IBM                               │
│  │  - Já tem factory pattern interno                 │
│  └───────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────┘
```

## Arquivos Criados (4)

### `docling_backends.py`
Interfaces abstratas + fábrica de backends:
- `DocumentFormat` — enum com 12 formatos (PDF, DOCX, PPTX, HTML, IMAGE, MD, etc.)
- `ConversionStatus` — enum: pending, started, success, partial_success, failure, skipped
- `IDocument` — Protocol duck-typing (text, pages, tables, metadata, export_to_*)
- `IConversionResult` — Protocol (document, status, errors, input_path, duration_ms)
- `IDocumentBackend` — ABC abstrato (name, supports, convert, is_available)
- `BackendFactory` — fábrica com registro dinâmico e seleção automática
- `DoclingService` — wrapper DI com IStateManager/IEventBus

### `docling_ibm_backend.py`
`IbmDoclingBackend` — wrapper sobre o SDK IBM Docling:
- Lazy import do `DocumentConverter` (falha graciosa se SDK não instalado)
- Suporte a pipeline VLM opcional (`SmolDocling-256M-preview`)
- `is_available()` verifica SDK instalado
- Wrappers internos `_DoclingDocumentWrapper` e `_ConversionResultWrapper` duck-typed

### `docling_pymupdf_backend.py`
`PyMuPdfBackend` — extração rápida via PyMuPDF (fitz):
- ~10x mais rápido que IBM Docling para texto puro
- Suporte a seleção de páginas (`"1-5,7,10-12"`)
- Metadados: título, autor, páginas, formato
- Fallback de import: `fitz` → `pymupdf`

### `docling_scraping_backend.py`
`ScrapingBackend` — fallback para scraping web:
- 3 estratégias em cadeia: requests → Playwright → curl.exe
- Auto-detecção de URL vs arquivo local
- Timeout configurável
- Ideal para documentos disponíveis apenas como URL

## Riscos

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| SDK IBM muda API | MÉDIO | BAIXA | Wrapper isola mudanças; versão fixa v2.68.0 |
| PyMuPDF não instalado | BAIXO | MÉDIA | `is_available()` retorna False; fallback para Scraping |
| Scraping quebra com site change | MÉDIO | MÉDIA | 3 estratégias em cadeia; erro reportado |
| DUPLICIDADE: `docling/backend/` já tem AbstractDocumentBackend | BAIXO | ALTA | Decisão consciente: não refatorar SDK externo; wrapper é camada nossa |

## Observações

- **Não confundir**: `docling/backend/abstract_backend.py` (SDK IBM) vs `docling_backends.py` (nosso wrapper). O SDK já tem sua própria hierarquia (`AbstractDocumentBackend`, `PaginatedDocumentBackend`, `PdfDocumentBackend`, etc.) — não a modificamos.
- **PyMuPDF vs IBM Docling**: IBM Docling faz pipeline completo (layout → OCR → tabelas → ordem leitura), enquanto PyMuPDF extrai só texto. Use IBM Docling para qualidade, PyMuPDF para velocidade.
- **Scraping**: Usa `curl.exe` no Windows (estratégia validada em editais-br v7.1).
- **Zero modificações** no diretório `docling/` original.
