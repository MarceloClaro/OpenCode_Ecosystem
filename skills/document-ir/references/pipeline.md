# P15 — Document IR Pipeline

## Visao Geral

Pipeline de 7 estágios para geração de documentos estruturados.
Extraído e generalizado do ReportEngine do BettaFish (666ghj/BettaFish).

## Arquitetura

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Stage 1         │    │  Stage 2         │    │  Stage 3         │
│  Template        │───▶│  Layout          │───▶│  Word Budget     │
│  Selection       │    │  Planning        │    │  Allocation      │
└──────────────────┘    └──────────────────┘    └──────────────────┘
                                                          │
                                                          ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Stage 7         │    │  Stage 6         │    │  Stage 4         │
│  Render          │◀───│  Document        │◀───│  Chapter         │
│  (MD/JSON/HTML)  │    │  Composer        │    │  Generation      │
└──────────────────┘    └──────────────────┘    └──────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌──────────────────┐
                        │  Stage 5         │
                        │  Quality Control │
                        └──────────────────┘
```

## 16 Tipos de Bloco

| Bloco | Uso | Render MD |
|-------|-----|-----------|
| HEADING1 | Capítulo | `# Titulo` |
| HEADING2 | Seção | `## Titulo` |
| HEADING3 | Subseção | `### Titulo` |
| PARAGRAPH | Texto | `texto` |
| BULLET_LIST | Lista | `- item` |
| NUMBERED_LIST | Lista ordenada | `1. item` |
| CODE_BLOCK | Código | ```` ```lang ```` |
| TABLE | Tabela | `\| col1 \| col2 \|` |
| QUOTE | Citação | `> texto` |
| CALL_TO_ACTION | Destaque | `> ⚠️ texto` |
| METRIC_CARD | Métrica | `**label**: valor` |
| ANCHOR | Referência | `[id]: target` |
| DIVIDER | Divisor | `---` |
| IMAGE_PLACEHOLDER | Imagem | `![alt](src)` |
| FOOTNOTE | Nota | `[^id]: text` |
| RAW_HTML | HTML | `<html>` |

## Estagios em Detalhe

### Stage 1: Template Selection

Seleciona template baseado em `document_type` + `audience`.

Templates pre-definidos:
- `report_executive`: Relatório executivo (4 seções, 2000 palavras)
- `report_technical`: Relatório técnico (5 seções, 5000 palavras)
- `analysis_general`: Análise geral (4 seções, 1500 palavras)
- `proposal_executive`: Proposta executiva (4 seções, 3000 palavras)

### Stage 2: Layout Planning

Planeja estrutura do documento: seções, níveis de heading, ordem.

### Stage 3: Word Budget Allocation

Distribui orçamento de palavras:
- 15% reservado para introdução
- 15% reservado para conclusão
- Restante distribuído uniformemente entre seções

### Stage 4: Chapter Generation

Geração de conteúdo por capítulo. Modos:
- **LLM**: geração por agente com contexto
- **Template**: preenchimento de placeholders
- **Híbrido**: LLM para narrativa, template para estrutura

### Stage 5: Quality Control

Regras de qualidade:
1. Conteúdo não vazio
2. Confiança entre 0 e 1
3. Posição não negativa
4. Links bem formados (futuro)
5. Consistência de âncoras (futuro)

### Stage 6: Document Composer

Composição final:
1. Dedup de âncoras (keep first/keep last)
2. Ordenação de blocos por posição
3. Validação de referências cruzadas
4. Geração de tabela de conteúdo
5. Índice de referências

### Stage 7: Render

Formatos de saída:
- **markdown**: com frontmatter YAML + tags de confiança
- **json**: JSON Schema compatível
- **html**: com blocos raw_html habilitados

## Tags de Confiança na Renderização

| Confiança | Tag | Cor |
|-----------|-----|-----|
| 1.0 | (sem tag) | — |
| 0.7-0.99 | `*(inferido)*` | Amarelo |
| 0.0-0.39 | `*(lacuna)*` | Vermelho |

## Integração com Skills Existentes

| Skill | Integração |
|-------|-----------|
| P5 Pipeline Orchestrator | Pipeline de 7 estágios executado como orquestração |
| P9 Swarm Review | QC colaborativo multiagente |
| P13 Config Generator | Geração de templates via LLM config gen |
| P14 Agent Forum | Documento como output de debate |

## Dependências

```python
# Python 3.10+
# Dependências opcionais:
# - jsonschema: validação JSON Schema
# - openai: modo LLM no chapter generation
```
