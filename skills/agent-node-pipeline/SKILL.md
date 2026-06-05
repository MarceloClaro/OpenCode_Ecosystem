---
name: agent-node-pipeline
description: >
  Agent Node Pipeline (ANP) — Framework para construir agentes LLM como
  pipelines de nós tipados e composáveis. Inclui o P17 MiddlewareChain
  (cadeia de middlewares estilo DeerFlow com 7 implementações pré-construídas).
  Inspirado pelos motores QueryEngine, MediaEngine e InsightEngine do
  BettaFish (666ghj/BettaFish) e pelo DeerFlow 11-layer Middleware Pipeline.
  Use quando precisar construir um agente com pipeline de processamento
  estruturado (busca → sumarização → reflexão → formatação) com estado
  rastreável, nós reutilizáveis e middlewares componíveis.
license: MIT
compatibility: opencode
allowed-tools: Read, Grep, Glob, Write, code-runner, Sqlite
metadata:
  author: Reversa Engine (padrão BettaFish + DeerFlow)
  version: "1.1.0"
  domain: agent-framework
  triggers: pipeline, node, agente pipeline, ANP, nó, base node, state mutation, LLM pipeline, search pipeline, reflection loop, middleware, middleware chain, P17, hook, before_node, after_node, wrap_node, on_error, default chain, retry, checkpoint, dangling call, summarization, logging, timing, validation, stats, deerflow reducers, merge artifacts, clear-on-empty
  role: builder
  scope: framework
  output-format: python
  related-skills: report-agent-react, graph-builder-pipeline, synthesis-agent, agent-forum
  inspired-by: BettaFish QueryEngine/MediaEngine/InsightEngine (666ghj/BettaFish), DeerFlow (bytedance/deer-flow, MIT)
  pattern-id: P16+P17
---

# Agent Node Pipeline (ANP) + MiddlewareChain (P17) — Framework de Agentes como Pipelines de Nós

Inspirado pelos motores **QueryEngine**, **MediaEngine** e **InsightEngine**
do BettaFish (666ghj/BettaFish, 40.9k ⭐) — três agentes independentes que
compartilham **a mesma arquitetura** de nós tipados em pipeline.

## O Padrão

```
┌──────────────────────────────────────────────────────────┐
│                    AgentNodePipeline                      │
├──────────────────────────────────────────────────────────┤
│  Fase 1: Planejamento                                    │
│  ┌─────────────────┐                                     │
│  │ StructureNode   │  Gera estrutura a partir da query   │
│  └────────┬────────┘                                     │
│           ▼                                               │
│  Fase 2: Pesquisa                                        │
│  ┌─────────────────┐   ┌─────────────────┐              │
│  │  SearchNode     │▸▸│  SummaryNode     │  Por parágrafo│
│  └────────┬────────┘   └────────┬────────┘              │
│           ▼                     ▼                        │
│  Fase 3: Refinamento                                     │
│  ┌─────────────────┐   Loop de reflexão (× N)           │
│  │  ReflectNode    │▸▸ Gap analysis → nova busca         │
│  └────────┬────────┘                                     │
│           ▼                                               │
│  Fase 4: Entrega                                         │
│  ┌─────────────────┐                                     │
│  │  FormatNode     │  MD / JSON / custom                 │
│  └─────────────────┘                                     │
└──────────────────────────────────────────────────────────┘
```

## Arquitetura (4 Camadas)

### 1. Nós Base (`BaseNode` / `StateMutationNode`)
Contrato abstrato que todo nó deve implementar:
- `run(input_data, **kwargs) → Any` — Lógica principal
- `validate_input(input_data) → bool` — Validação de entrada
- `process_output(output) → Any` — Pós-processamento
- `mutate_state(input_data, state, **kwargs) → PipelineState` — Transformação de estado (StateMutationNode)

### 2. Estado (`PipelineState`)
Estado tipado e serializável que flui pelo pipeline:
- `phases: List[Phase]` — Fases executadas
- `node_results: Dict[str, NodeResult]` — Status por nó
- `artifacts: Dict[str, Any]` — Dados produzidos
- `metadata: Dict[str, Any]` — Configuração e metadados
- Serialização: `to_dict()`, `to_json()`, `save()`, `load()`

### 3. Nós Concretos (`node_types.py`)
7 tipos de nó prontos para uso:
| Nó | Função | Origem |
|----|--------|--------|
| `TransformNode` | Transformação pura de dados | Padrão genérico |
| `LLMQueryNode` | Chamada a LLM com prompt template | BettaFish LLMClient |
| `SearchNode` | Busca externa (web, DB, API) | BettaFish FirstSearchNode |
| `ReflectNode` | Loop de reflexão com gap analysis | BettaFish ReflectionNode |
| `StructureNode` | Geração de estrutura de documento | BettaFish ReportStructureNode |
| `SummaryNode` | Sumarização de resultados | BettaFish FirstSummaryNode |
| `FormatNode` | Formatação de saída (MD/JSON) | BettaFish ReportFormattingNode |

### 4. Orquestrador (`AgentNodePipeline`)
Gerencia o ciclo de vida completo:
- `add_node(name, node)` — Registra nó
- `add_phase(name, [node_names])` — Define fase
- `run(query)` — Executa pipeline completo
- `get_progress()` — Progresso atual
- `get_result(node_name)` — Resultado de nó específico
- `create_search_pipeline(llm, search_fn)` — Factory para pipeline completo

## Interface Padrão

### BaseNode (todos os nós)

```python
class MeuNode(BaseNode):
    def run(self, input_data, **kwargs):
        # Lógica principal
        return resultado
```

### StateMutationNode (nós que transformam estado)

```python
class MeuNodeMutante(StateMutationNode):
    def mutate_state(self, input_data, state, **kwargs):
        # Transforma o estado
        state.store_artifact("chave", valor)
        return state
```

### PipelineState (estado)

```python
state = PipelineState(query="minha consulta")
state.add_phase("Fase 1", ["no1", "no2"])
state.set_phase_status(0, "running")
state.store_artifact("resultado", {"chave": "valor"})
state.register_result("no1", NodeResult(node_name="no1", status="completed"))
state.mark_completed()
state.save("checkpoint.json")
```

## Uso Rápido

```python
from agent_node_pipeline.scripts import (
    AgentNodePipeline, LLMClient,
    StructureNode, SearchNode, SummaryNode, FormatNode
)

# 1. Cliente LLM
llm = LLMClient(model_name="gpt-4o")

# 2. Função de busca
def minha_busca(query, max_results=5):
    return [{"title": "exemplo", "content": "conteúdo", "url": "https://..."}]

# 3. Pipeline completo (factory method)
pipeline = AgentNodePipeline.create_search_pipeline(llm, minha_busca)

# 4. Executa
state = pipeline.run("O que é o padrão ANP?")

# 5. Resultado
print(state.get_artifact("formatted_output"))
```

## Níveis de Confiança

| Nível | Onde se aplica |
|-------|---------------|
| 🟢 **CONFIRMADO** | BaseNode/StateMutationNode — idêntico ao BettaFish base_node.py |
| 🟢 **CONFIRMADO** | PipelineState — generalização direta do State/Paragraph/Research |
| 🟢 **CONFIRMADO** | LLMClient — unificado a partir do llms/base.py |
| 🟢 **CONFIRMADO** | Estrutura de 4 fases — extraída do research() do agent.py |
| 🟢 **CONFIRMADO** | 7 tipos de nó — mapeamento 1:1 dos nós do BettaFish |
| 🟡 **INFERIDO** | Factory method `create_search_pipeline` — combinação dos 3 agentes |
| 🟡 **INFERIDO** | `_resolve_input` automático — adaptado para ser genérico |

## Como este padrão se diferencia

| Skill | Foco | Diferença do ANP |
|-------|------|------------------|
| `report-agent-react` | ReACT + Reflection | ANP é sobre pipeline de nós tipados, não sobre ciclo thought-action |
| `graph-builder-pipeline` | Construção de grafos | ANP é framework genérico, não específico para grafos |
| `synthesis-agent` | Síntese multi-fonte | ANP fornece a infraestrutura de nós, não o conteúdo |
| `agent-forum` | Debate multi-agente | ANP é pipeline single-agent, não fórum |

## Dependências

- Python 3.10+
- `openai` (opcional, para LLMClient online)
- Sem dependências obrigatórias (modo offline/fallback funciona sem API)

## Arquivos

| Arquivo | Função |
|---------|--------|
| `SKILL.md` | Documentação do padrão (este arquivo) |
| `scripts/__init__.py` | Exportações públicas |
| `scripts/base_node.py` | BaseNode + StateMutationNode |
| `scripts/pipeline_state.py` | PipelineState, Phase, NodeResult |
| `scripts/llm_client.py` | LLMClient unificado |
| `scripts/node_types.py` | 7 nós concretos |
| `scripts/pipeline.py` | AgentNodePipeline orquestrador |
| `references/pipeline_design.md` | Design rationale completo |
| `scripts/middleware_chain.py` | P17: BaseMiddleware, MiddlewareChain, 7 pre-built, factory |

---

## P17 — MiddlewareChain (DeerFlow 11-Layer Middleware Pipeline)

Adiciona uma **cadeia de middlewares componíveis** ao ANP, inspirada pelo
DeerFlow 11-layer Middleware Pipeline (cap. 6) e Context Engineering (cap. 7).

### Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        MiddlewareChain                          │
├─────────────────────────────────────────────────────────────────┤
│  execute_before_run() → execute_before_phase() → execute_node() │
│                                      → execute_after_phase()    │
│                                      → execute_after_run()       │
└─────────────────────────────────────────────────────────────────┘
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
     ┌─────────────────┐ ┌─────────┐ ┌──────────────┐
     │    before_node   │ │wrap_node│ │  after_node   │
     │ (modifica input) │ │(cebola) │ │(modifica out) │
     └────────┬────────┘ └────┬────┘ └──────┬───────┘
              │               │              │
              ▼               ▼              ▼
         on_error()    before_phase()   after_phase()
```

### BaseMiddleware — 8 Hooks (interface ABC)

| Hook | Assinatura | Quando executa | DeerFlow equiv. |
|------|-----------|---------------|-----------------|
| `before_node` | `(name, input, state) → dict` | Antes de cada nó | `before_model_call` |
| `after_node` | `(name, result, state) → dict` | Após cada nó | `after_model_call` |
| `wrap_node` | `(name, input, state, run_fn) → Any` | Substitui execução | `wrap_model_call` |
| `on_error` | `(name, error, state) → dict` | Em exceção | `on_error` |
| `before_phase` | `(name, index, nodes, state) → dict` | Antes de cada fase | — |
| `after_phase` | `(name, index, state) → dict` | Após cada fase | — |
| `before_run` | `(query, state) → dict` | Antes do pipeline | — |
| `after_run` | `(state) → None` | Após o pipeline | — |

Cada hook retorna um dicionário opcional com chaves que afetam o fluxo:

| Chave | Hooks | Efeito |
|-------|-------|--------|
| `input_data` | before_node | Substitui a entrada do nó |
| `state` | before/after_node/phase | Substitui o estado do pipeline |
| `skip` | before_node | `True` → pula execução do nó |
| `result` | before_node (skip), after_node, on_error | Resultado alternativo / fallback |
| `retry` | on_error | `True` → solicita retry |

### wrap_node — Onion Ordering (Casca de Cebola)

O último middleware adicionado é o **mais externo** (semântica DeerFlow,
idêntica a decorators Python):

```python
chain.add(WrapA)  # mais interno (próximo ao core)
chain.add(WrapB)  # mais externo (primeiro a executar)

# Fluxo: WrapB → WrapA → core → WrapA → WrapB
```

**IMPORTANTE:** A ordem de adição importa. `create_default_chain()` segue
esta ordem predefinida:

| Ordem | Middleware | Camada |
|-------|-----------|--------|
| 1 (interno) | StatsMiddleware | Medição bruta |
| 2 | LoggingMiddleware | Observabilidade |
| 3 | TimingMiddleware | Temporização |
| 4 | ValidationMiddleware | Contrato |
| 5 | DanglingCallMiddleware | Reparo de estado |
| 6 | SummarizationMiddleware | Gestão de contexto |
| 7 | RetryMiddleware | Resiliência |
| 8 (externo) | CheckpointMiddleware | Persistência |

### 7 Pre-built Middlewares

#### 1. LoggingMiddleware
```python
LoggingMiddleware(logger: Optional[logging.Logger] = None)
```
- Loga início/fim de cada nó + erros (formato `[ANP]`)
- Não altera dados

#### 2. TimingMiddleware
```python
TimingMiddleware()
```
- Registra `node_timings` em `state.metadata["node_timings"]`
- Medição precisa via `time.time()`

#### 3. ValidationMiddleware
```python
ValidationMiddleware(
    input_validators: Dict[str, Callable] = {},
    output_validators: Dict[str, Callable] = {},
    strict: bool = False,
)
```
- Se `strict=True`, levanta `ValueError` em falha de validação
- Caso contrário, loga warning

#### 4. RetryMiddleware
```python
RetryMiddleware(
    max_retries: int = 2,
    retry_delay: float = 1.0,
    retryable_exceptions: Optional[tuple] = None,
)
```
- Retenta até `max_retries+1` vezes
- `retryable_exceptions` filtra quais exceções são retentáveis
- Usa `time.sleep(delay)` entre tentativas

#### 5. CheckpointMiddleware
```python
CheckpointMiddleware(
    dir_path: str = ".reversa/checkpoints",
    interval: int = 1,  # a cada N nós
)
```
- Salva `PipelineState` em disco a cada `interval` nós
- Nomes: `ckpt_{query[:20]}_{phase_status}.json`

#### 6. SummarizationMiddleware (DeerFlow cap. 7)
```python
SummarizationMiddleware(
    trigger_messages: int = 20,
    keep_recent: int = 10,
    llm_summarize_fn: Optional[Callable] = None,
)
```
- Quando `len(state.artifacts) >= trigger_messages`, sumariza artefatos antigos
- Preserva os `keep_recent` mais recentes
- Se `llm_summarize_fn` definida, usa LLM para sumarização inteligente
- Caso contrário, fallback textual com contagem de artefatos

#### 7. DanglingCallMiddleware (DeerFlow cap. 7)
```python
DanglingCallMiddleware()
```
- Marca nós com status `"pending"` ou `"running"` como `"dangling"`
- Insere mensagem de erro: `"[Interrupted — tool call did not return a result.]"`
- Executa como **primeiro hook before_node** (antes de qualquer processamento)

#### 8. StatsMiddleware
```python
StatsMiddleware()
```
- Coleta estatísticas do pipeline: duração total, nós por status, artefatos
- Registra `pipeline_start`, `pipeline_duration_sec`, `pipeline_end` no metadata
- Acumula `nodes_completed` e `artifacts_total`

### Factory: `create_default_chain()`

```python
def create_default_chain(
    checkpoint_dir: str = ".reversa/checkpoints",
    checkpoint_interval: int = 1,
    retry_enabled: bool = True,
    retry_max: int = 2,
    summarization_trigger: int = 20,
    summarization_keep: int = 10,
    **kwargs,
) -> MiddlewareChain:
```

Cria cadeia completa com os 8 middlewares na ordem correta.
Parâmetros `**kwargs` são repassados para `ValidationMiddleware`.

### Integração com ANP (P16)

```python
# Modo 1: Cadeia explícita
pipe = AgentNodePipeline("MeuPipeline")
chain = MiddlewareChain()
chain.add(LoggingMiddleware())
chain.add(CheckpointMiddleware())
pipe.use_middleware(chain)

# Modo 2: Cadeia padrão (factory)
pipe.use_middleware(defaults=True)

# Modo 3: Personalizada
pipe.use_middleware(
    defaults=True,
    checkpoint_dir="./ckpts",
    retry_max=3,
    summarization_trigger=10,
)
```

**7 pontos de injeção** no `AgentNodePipeline`:

| Local | Hook | Efeito |
|-------|------|--------|
| `run()` início | `execute_before_run` | Configuração global |
| `run()` fim | `execute_after_run` | Finalização global |
| `_run_sequential()` início | `execute_before_phase` | Pré-fase |
| `_run_sequential()` fim | `execute_after_phase` | Pós-fase |
| `_run_dag()` início | `execute_before_phase` | Pré-fase paralela |
| `_run_dag()` fim | `execute_after_phase` | Pós-fase paralela |
| `_execute_node()` | `execute_node` | Ciclo completo do nó |

Fluxo completo para cada nó com middleware:

```
AgentNodePipeline._execute_node()
  └── MiddlewareChain.execute_node()
        ├── execute_before_node()    ──── Logging, Timing, Validation,
        │                                   DanglingCall, Summarization
        ├── execute_wrap_node()      ──── Checkpoint → Retry → run_fn()
        ├── execute_on_error()       ──── Logging (se exceção)
        └── execute_after_node()     ──── Checkpoint, Validation, Timing,
                                            Logging, Stats (ordem inversa)
```

### DeerFlow Reducers no PipelineState

Três métodos para merge inteligente de artefatos, inspirados pelos
`Annotated` reducers do LangGraph (DeerFlow cap. 2.1):

#### `merge_artifact_list(key, items)`
- **Dedup ordenado** via `dict.fromkeys()`
- Preserva ordem de inserção, remove duplicatas
- DeerFlow equivalente: `Annotated[list[str], merge_artifacts]`

```python
state.merge_artifact_list("paths", ["a.txt", "b.txt"])
state.merge_artifact_list("paths", ["b.txt", "c.txt"])
# Resultado: ["a.txt", "b.txt", "c.txt"]  ← "b" não duplica
```

#### `merge_artifact_dict(key, values)`
- Merge simples com `dict.update()`
- Útil para acumular resultados parciais de múltiplos nós

```python
state.merge_artifact_dict("scores", {"no1": 0.95})
state.merge_artifact_dict("scores", {"no2": 0.87})
# Resultado: {"no1": 0.95, "no2": 0.87}
```

#### `merge_viewed_images(images)`
- **Clear-on-empty**: se `images = {}`, limpa todo `_viewed_images`
- DeerFlow equivalente: `Annotated[dict, merge_viewed_images]`
- Previne memory bloat de strings base64 em threads longas

```python
state.merge_viewed_images({"img1": "base64..."})
state.merge_viewed_images({"img2": "base64..."})
state.merge_viewed_images({})  # ← limpa tudo!
assert "_viewed_images" not in state.artifacts
```

### Níveis de Confiança (P17)

| Nível | Componente | Justificativa |
|-------|-----------|---------------|
| 🟢 **CONFIRMADO** | 8 hooks do BaseMiddleware | Extraído do DeerFlow cap. 6 (11-layer pipeline) |
| 🟢 **CONFIRMADO** | wrap_node onion ordering | Semântica DeerFlow = Python decorators |
| 🟢 **CONFIRMADO** | 7 pre-built middlewares | Implementação testada (63/63) |
| 🟢 **CONFIRMADO** | create_default_chain | Factory validada em testes de integração |
| 🟢 **CONFIRMADO** | DeerFlow Reducers (3 métodos) | Extraído do DeerFlow cap. 2.1 (LangGraph Annotated) |
| 🟡 **INFERIDO** | P14+P15+P17 cross-validation | Pendente (próximo passo) |

### Dependências (P17)

- Python 3.10+
- Sem dependências externas obrigatórias
- `logging` (stdlib) para LoggingMiddleware
- `json`, `time`, `os`, `threading` (stdlib) para demais middlewares
- Opcional: função LLM externa para SummarizationMiddleware

---

## Atualização de Limitações (P16 + P17)

| Antes | Agora |
|-------|-------|
| ❌ Sem paralelismo | ✅ **DAG paralelo** via Kahn + ThreadPoolExecutor |
| ❌ Sem DAG | ✅ **DAG** com dependências entre nós |
| ❌ Sem middlewares | ✅ **MiddlewareChain** com 8 hooks e 7 middlewares |
| ❌ Sem checkpoint automático | ✅ **CheckpointMiddleware** com intervalo configurável |
| ❌ Sem retry | ✅ **RetryMiddleware** com retentativas configuráveis |
| ❌ Sem validação | ✅ **ValidationMiddleware** com modo strict |
| ❌ Sem sumarização de estado | ✅ **SummarizationMiddleware** com trigger por artefatos |
| ❌ Sem merge inteligente | ✅ **3 DeerFlow Reducers** (artifact list, dict, clear-on-empty) |
