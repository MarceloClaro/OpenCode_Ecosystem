---
name: document-ir
description: "Skill do ecossistema OpenCode - document-ir"
---

# P15 — Document IR Report Pipeline

Skill de pipeline de relatório documentado em 7 estágios, com 16 tipos de bloco
e composição inteligente com dedup de âncoras. Extraído e generalizado do
ReportEngine do BettaFish (666ghj/BettaFish) — `ir/schema.py`, `core/stitcher.py`,
`agent.py`.

## Visão Geral

```
Template Selection
  → Layout Planning
    → Word Budget Allocation
      → Chapter Generation
        → Quality Control
          → Document Composer
            → Render
```

Cada estágio produz artefatos intermediários que alimentam o próximo.
Documentos podem ser renderizados em markdown, JSON ou formatos customizados.

## 1. 16 Tipos de Bloco (BlockType)

| # | Bloco | Descrição | Template |
|---|-------|-----------|----------|
| 1 | `HEADING1` | Título de capítulo | `# {text}` |
| 2 | `HEADING2` | Título de seção | `## {text}` |
| 3 | `HEADING3` | Título de subseção | `### {text}` |
| 4 | `PARAGRAPH` | Parágrafo de texto | `{text}` |
| 5 | `BULLET_LIST` | Lista não ordenada | `- {item}` |
| 6 | `NUMBERED_LIST` | Lista ordenada | `1. {item}` |
| 7 | `CODE_BLOCK` | Bloco de código | ```` ```{lang} ``` ```` |
| 8 | `TABLE` | Tabela | `| col1 \| col2 \|` |
| 9 | `QUOTE` | Citação em destaque | `> {text}` |
| 10 | `CALL_TO_ACTION` | Chamada para ação | `⚠️ {text}` |
| 11 | `METRIC_CARD` | Cartão de métrica | `**{label}**: {value}` |
| 12 | `ANCHOR` | Âncora de referência cruzada | `[id]: {target}` |
| 13 | `DIVIDER` | Divisor visual | `---` |
| 14 | `IMAGE_PLACEHOLDER` | Placeholder de imagem | `![{alt}]({src})` |
| 15 | `FOOTNOTE` | Nota de rodapé | `[^{id}]: {text}` |
| 16 | `RAW_HTML` | HTML bruto (renderização avançada) | `{html}` |

## 2. Pipeline de 7 Estágios

### Stage 1: Template Selection

Seleciona template baseado no tipo de documento e público-alvo.

```
select_template(document_type: str, audience: str) → Template
```

- `document_type`: "report", "proposal", "analysis", "manual"
- `audience`: "executive", "technical", "general", "academic"

### Stage 2: Layout Planning

Planeja layout: seções, ordem, hierarquia.

```
plan_layout(template: Template, sections: list[str]) → Layout
```

- Define ordem das seções
- Atribui níveis de heading
- Estima densidade de blocos por seção

### Stage 3: Word Budget

Aloca orçamento de palavras por seção.

```
allocate_budget(layout: Layout, total_words: int) → Budget
```

- Distribui palavras proporcionalmente
- Reserva 15% para introdução + conclusão
- Espaço extra para seções com tabelas/código

### Stage 4: Chapter Generation

Gera conteúdo de cada capítulo via LLM ou template.

```
generate_chapter(section: str, budget: int, context: dict) → list[Block]
```

- Cada capítulo é uma lista de blocos
- Contexto pode conter dados, pesquisas anteriores, referências
- Modo LLM: geração por agente especializado
- Modo template: preenchimento de placeholders

### Stage 5: Quality Control (QC)

Valida blocos gerados contra regras de qualidade.

```
qc_pass(blocks: list[Block]) → list[Block]
```

Regras de QC:
- **Completude**: todos os campos obrigatórios preenchidos
- **Consistência**: âncoras referenciadas existem
- **Tamanho**: blocos dentro do orçamento
- **Formato**: tipos de bloco válidos
- **Links**: URLs bem formadas

### Stage 6: Document Composer

Compõe documento final com dedup de âncoras.

```
compose(blocks: list[Block], anchors: list[Anchor]) → Document
```

- Remove âncoras duplicadas (keep first)
- Ordena blocos por posição
- Aplica template de formatação
- Gera índice de referências cruzadas

### Stage 7: Render

Renderiza em formato de saída.

```
render(document: Document, format: str) → str
```

Formatos suportados:
- `markdown`: markdown padrão com frontmatter
- `json`: JSON estruturado com metadados
- `html`: HTML formatado (raw_html blocks enabled)
- `custom`: formato customizado via callback

## 3. Schemas

### Block

```python
@dataclass
class Block:
    type: BlockType          # Tipo do bloco
    content: str             # Conteúdo principal
    metadata: dict = None    # Metadados (lang, align, id, etc.)
    position: int = 0        # Ordem no documento
    anchor_id: str = ""     # ID para referência cruzada
    confidence: float = 0.5  # CONFIRMADO/INFERIDO/LACUNA
```

### Anchor

```python
@dataclass
class Anchor:
    anchor_id: str           # Identificador único
    target: str              # Referência alvo
    block_type: BlockType    # Tipo do bloco alvo
    source: str = ""         # Documento de origem
```

### Document

```python
@dataclass
class Document:
    title: str
    blocks: list[Block]
    anchors: list[Anchor]
    metadata: dict
    template: str
    created_at: str
    word_count: int = 0
```

## 4. Escala de Confiança

| Nível | Valor | Quando usar |
|-------|-------|-------------|
| CONFIRMADO | 1.0 | Bloco extraído de fonte verificada |
| INFERIDO | 0.7 | Bloco gerado por LLM com contexto |
| LACUNA | 0.3 | Bloco com placeholders ou dados parciais |
| DESCONHEC | 0.0 | Bloco sem fonte identificável |

## 5. Integração com Ecossistema Reversa

| Skill | Tipo | Uso |
|-------|------|-----|
| P5 (Pipeline Orchestrator) | dependência formal | Execução dos 7 estágios |
| P3 (Machine States) | dependência opcional | Estado do pipeline |
| P9 (Swarm Review) | dependência opcional | QC colaborativo |
| P13 (Config Generator) | dependência opcional | Geração de templates |

## 6. Modos de Operação

### Modo LLM Completo

Pipeline completo com geração LLM em Stage 4. Requer:
- API key configurada
- Modelo com contexto suficiente (8K+ tokens)
- Rate limiting para batches grandes

### Modo Template

Geração via placeholders sem LLM. Útil para:
- Documentos estruturados previsíveis
- Testes e validação
- Ambientes offline

### Modo Híbrido

Mistura LLM + template:
- Estrutura e metadados via template
- Conteúdo narrativo via LLM
- Tabelas e dados via template

## 7. Tratamento de Erros

| Erro | Ação |
|------|------|
| BudgetExceeded | Rebalancear orçamento entre seções |
| AnchorConflict | Dedup automático (keep first) |
| QCFail | Logar falha com bloco + regra |
| RenderUnsupported | Fallback para markdown |
| LLMUnavailable | Usar modo template |

