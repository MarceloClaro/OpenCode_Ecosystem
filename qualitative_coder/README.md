# QualitativeCoder — Documentação TDD/SDD

## Resumo

Módulo Python para análise qualitativa de dados acadêmicos, substituindo ferramentas proprietárias (NVivo 12, MAXQDA) com código aberto, validável e reproduzível.

## Status

| Componente | Status | CTs | Cobertura |
|------------|--------|-----|-----------|
| SPEC-050 (QualitativeCoder) | DRAFT | - | - |
| SPEC-051 (Autonomia/Metacognição) | DRAFT | - | - |
| Core (coder.py) | IMPLEMENTADO | 15 | 100% |
| Categorizer | IMPLEMENTADO | 9 | 100% |
| Triangulator | IMPLEMENTADO | 8 | 100% |
| Reporter | IMPLEMENTADO | 6 | 100% |
| Integration tests | IMPLEMENTADO | 5 | 100% |
| **TOTAL** | **43 CTs** | **43/43 PASS** | **100%** |

## Estrutura

```
qualitative_coder/
├── __init__.py              # Exportação principal
├── core/
│   ├── coder.py             # Engine principal (15 CTs)
│   ├── categorizer.py       # Categorização temática (9 CTs)
│   ├── triangulator.py      # Triangulação de métodos (8 CTs)
│   └── reporter.py          # Geração de relatórios (6 CTs)
├── algorithms/              # (futuro: TF-IDF, BERT, LDA)
├── io/                      # (futuro: parsers de arquivo)
├── integration/
│   └── mcp_server.py        # MCP server para OpenCode
├── tests/
│   ├── test_coder.py        # 15 CTs
│   ├── test_categorizer.py  # 9 CTs
│   ├── test_triangulator.py # 8 CTs
│   ├── test_reporter.py     # 6 CTs
│   └── test_integration.py  # 5 CTs
├── SKILL.md                 # Skill para OpenCode
└── specs/
    ├── SPEC-050.md          # Especificação principal
    └── SPEC-051.md          # Autonomia e metacognição
```

## TDD (Desenvolvimento Orientado a Testes)

### Ciclo TDD Aplicado
1. **Red**: Testes escritos antes da implementação (43 CTs)
2. **Green**: Implementação mínima para passar nos testes
3. **Refactor**: Melhoria de código mantendo testes verdes

### Testes por Módulo

#### test_coder.py (15 CTs)
- CT-001: Importação do módulo
- CT-002: Idioma padrão (pt-br)
- CT-003: Idioma customizado
- CT-004: Codebook inicia vazio
- CT-005: Categorias iniciam vazias
- CT-006: code() retorna lista
- CT-007: Cada código é dict com code, span, confidence
- CT-008: Confidence entre 0.0 e 1.0
- CT-009: Span válido dentro do texto
- CT-010: Método axial gera códigos relacionais
- CT-011: Método open gera códigos emergentes
- CT-012: Texto vazio retorna lista vazia
- CT-013: add_code adiciona ao codebook
- CT-014: add_code aceita código pai
- CT-015: export_codebook retorna dict serializável

#### test_categorizer.py (9 CTs)
- CT-016: Importação do Categorizer
- CT-017: Inicialização com método padrão
- CT-018: categorize() retorna lista
- CT-019: Categoria contém category, codes, frequency
- CT-020: Frequency conta ocorrências
- CT-021: Lista vazia retorna categorias vazias
- CT-022: Método thematic configurado
- CT-023: cluster() agrupa documentos
- CT-024: get_top_themes() retorna temas ordenados

#### test_triangulator.py (8 CTs)
- CT-025: Importação do Triangulator
- CT-026: Inicialização correta
- CT-027: triangulate() retorna dict com convergence, divergence, gaps
- CT-028: convergence entre 0.0 e 1.0
- CT-029: divergence é lista
- CT-030: gaps é lista
- CT-031: Aceita múltiplos métodos
- CT-032: Dados vazios retornam gaps

#### test_reporter.py (6 CTs)
- CT-033: Importação do Reporter
- CT-034: Inicialização correta
- CT-035: report() LaTeX retorna string
- CT-036: report() Markdown retorna string
- CT-037: report() JSON retorna dict
- CT-038: Dados vazios geram relatório mínimo

#### test_integration.py (5 CTs)
- CT-039: Importação do pacote
- CT-040: Pipeline completo code→categorize→triangulate→report
- CT-041: export_codebook() gera JSON válido
- CT-042: Codebook persiste entre operações
- CT-043: Métodos open e axial geram resultados diferentes

## SDD (Desenvolvimento Orientado a Documentação)

### Especificações
- **SPEC-050**: QualitativeCoder — módulo principal
- **SPEC-051**: Autonomia e Metacognição do Ecossistema

### Documentação
- Docstrings em todos os módulos
- SKILL.md para integração com OpenCode
- MCP server com 5 ferramentas
- Este documento (TDD/SDD)

## Integração com Ecossistema

### Skill
- `qualitative-analysis`: Ativado por "análise qualitativa", "codificação", "NVivo", "MAXQDA"

### MCP Server
- `code_text`: Codifica texto qualitativo
- `categorize_codes`: Categoriza códigos
- `triangulate`: Triangula dados
- `generate_report`: Gera relatório
- `analyze_interview`: Pipeline completo

### Referência na Dissertação
- Cap. 3, §3.4: "Utilizei módulo de análise qualitativa em Python (QualitativeCoder, SPEC-050)..."
- Substitui NVivo 12 e MAXQDA

## Dependências

### Obrigatórias
- Python >= 3.10
- Nenhuma dependência externa (stdlib apenas)

### Opcionais (futuro)
- scikit-learn (clustering avançado)
- sentence-transformers (embeddings BERT)
- bertopic (topic modeling)

## Roadmap

1. **R27** (atual): SPEC + TDD base + Implementação core
2. **R28**: Algoritmos avançados (TF-IDF, BERT)
3. **R29**: Integração OpenCode + MCP server
4. **R30**: Production ready + auto-evolução
