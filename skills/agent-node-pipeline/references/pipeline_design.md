# ANP — Design & Rationale

## Origem

O padrão **Agent Node Pipeline** foi extraído dos três motores de busca
do projeto BettaFish (666ghj/BettaFish):

| Motor | Função | Tools |
|-------|--------|-------|
| **QueryEngine** | Busca textual na web | Tavily News API |
| **MediaEngine** | Busca multimodal | Bocha + Anspire |
| **InsightEngine** | Mineração em BD + sentimento | MediaCrawlerDB + Sentiment |

Apesar de terem tools e APIs diferentes, os três compartilham **exatamente
a mesma arquitetura** de pipeline de nós — provando que o padrão é
reutilizável e independente do domínio.

## Decisões de Design

### 1. BaseNode vs StateMutationNode

- **BaseNode**: Para nós de transformação pura (função in → função out).
  Ex: parsing, validação, encoding.
- **StateMutationNode**: Para nós que precisam ler/escrever no estado
  do pipeline. Ex: buscar dados, chamar LLM, armazenar summary.

*Por que duas classes?* O BettaFish usa apenas StateMutationNode (via
`mutate_state`). Para generalizar, separamos: nós que só transformam
dados não precisam de acesso ao estado completo.

### 2. PipelineState imutável por contrato

`mutate_state()` recebe `state` mas **retorna** um novo state. Isso
permite:
- Checkpoint automático entre nós
- Reejecução de nós falhos
- Auditoria (cada nó produz uma nova versão do estado)

### 3. Fases vs Nós

Fases agrupam nós relacionados. Um nó pode pertencer a uma única fase.
A fase falha se qualquer nó falhar. Isso replica o fluxo do BettaFish:
```
_generate_report_structure  → Fase 1 (StructureNode)
_initial_search_and_summary → Fase 2 (SearchNode + SummaryNode)
_reflection_loop            → Fase 3 (ReflectNode)
_generate_final_report      → Fase 4 (FormatNode)
```

### 4. LLMClient com fallback offline

O BettaFish usa OpenAI diretamente. Generalizamos com:
- Fallback offline quando sem API key
- Suporte a qualquer provedor compatível (via base_url)
- Modo JSON via `invoke_json()`

### 5. Factory method

`AgentNodePipeline.create_search_pipeline()` reproduz o pipeline
completo do BettaFish em uma linha. Útil para:
- Quick-start
- Testes
- Demonstração

## Evolução (P16 → P16+P17)

### P16 — Melhorias do BettaFish Original

| Funcionalidade | BettaFish | P16 | Status |
|---------------|-----------|-----|--------|
| Paralelismo | ❌ Sequencial | ✅ **DAG paralelo** (Kahn + ThreadPoolExecutor) | 🟢 Testado |
| DAG entre nós | ❌ Linear | ✅ **Dependências** com ordenação topológica | 🟢 Testado |
| Streaming | ❌ Não | ✅ Callback `on_node_stream` | 🟢 Testado |
| Checkpoint | ❌ Não | ✅ `save_checkpoint()` / `load_checkpoint()` | 🟢 Testado |
| Resume | ❌ Não | ✅ `_resume()` com `resume_from` | 🟢 Testado |
| Factory | ❌ Fixo | ✅ `create_search_pipeline()` configurável | 🟢 Testado |

### P17 — MiddlewareChain (Novo)

| Funcionalidade | DeerFlow | P17 | Status |
|---------------|----------|-----|--------|
| 8 hooks | ✅ 11-layer pipeline | ✅ **8 hooks** (before/after node, wrap, error, phase, run) | 🟢 63/63 testes |
| 7 pre-built middlewares | ✅ Exemplos | ✅ **Logging, Timing, Validation, Retry, Checkpoint, Summarization, DanglingCall, Stats** | 🟢 Testados |
| wrap_node onion | ✅ wrap_model_call | ✅ **Último adicionado = mais externo** | 🟢 Testado |
| DeerFlow Reducers | ✅ Annotated[list, merge] | ✅ **merge_artifact_list, merge_artifact_dict, merge_viewed_images** | 🟢 13/13 testes |
| Default chain | ✅ Recomendação | ✅ **create_default_chain()** com ordem otimizada | 🟢 Testado |
| Integração ANP | ❌ N/A | ✅ **7 pontos de injeção** no pipeline | 🟢 Testado |

## Limitações Conhecidas (Atual P16+P17)

1. **LLMClient sem streaming assíncrono**: `invoke()` é síncrono. O
   streaming via callback `on_node_stream` funciona, mas não há suporte
   a `async/await` no pipeline principal.
2. **Summarization sem LLM embutido**: O SummarizationMiddleware requer
   função LLM externa para sumarização inteligente; fallback textual é
   básico.
3. **Sem middleware assíncrono**: Todos os hooks são síncronos. Para
   IO-bound, use threads no middleware.

## Comparação com BettaFish Original

| Conceito | BettaFish | ANP (generalizado) |
|----------|-----------|-------------------|
| Base nó | `BaseNode` (mesmo nome) | `BaseNode` + `StateMutationNode` |
| Estado | `State`, `Paragraph`, `Research` | `PipelineState`, `Phase`, `NodeResult` |
| Orquestrador | `DeepSearchAgent.research()` | `AgentNodePipeline.run()` |
| Nó estrutura | `ReportStructureNode` | `StructureNode` |
| Nó busca | `FirstSearchNode` | `SearchNode` |
| Nó sumário | `FirstSummaryNode` | `SummaryNode` |
| Nó reflexão | `ReflectionNode` | `ReflectNode` |
| Nó formatação | `ReportFormattingNode` | `FormatNode` |
| LLM | OpenAI direto | `LLMClient` com fallback |
| Tools | Específicas (Tavily/Bocha/DB) | Função injetada (`search_fn`) |
| Config | `Settings` (TOML/ENV) | `PipelineState.metadata` |
| Saída | Markdown + JSON | FormatNode (MD/JSON/custom) |
| Pipeline fixo | Sim (embutido no agent.py) | Factory method configurável |

## Fluxo de Execução Detalhado

```
run("query")
  │
  ├─ Fase 1: Planejamento
  │   └─ StructureNode.run("query")
  │       → Gera [{"title": "...", "description": "..."}]
  │       → state.artifacts["structure"] = [...]
  │
  ├─ Fase 2: Pesquisa
  │   ├─ SearchNode.run({"query": "...", "context": ""})
  │   │   → state.artifacts["search_results"] = [...]
  │   └─ SummaryNode.run({"query": "...", "results": [...]})
  │       → state.artifacts["summary"] = "texto..."
  │
  ├─ Fase 3: Refinamento
  │   └─ ReflectNode.run({"query": "...", "context": "texto..."})
  │       → Para cada reflection:
  │          1. LLM gera query de lacuna
  │          2. SearchNode executa
  │          3. Acumula resultados
  │       → state.artifacts["reflections"] = [...]
  │
  └─ Fase 4: Entrega
      └─ FormatNode.run(state)
          → state.artifacts["formatted_output"] = "markdown..."
```

## Exemplo de Uso Avançado

```python
from agent_node_pipeline.scripts import *

# Pipeline customizado (sem factory)
pipe = AgentNodePipeline("MeuPipelineAnalítico")

# Nós
llm = LLMClient(model_name="deepseek-chat")
search = SearchNode(minha_funcao_busca, llm_client=llm)
transform = TransformNode(lambda x: x.upper())

pipe.add_node("transforma", transform)
pipe.add_node("busca", search)
pipe.add_node("sumario", SummaryNode(llm))
pipe.add_node("formata", FormatNode(format_type="json"))

pipe.add_phase("Preparação", ["transforma"])
pipe.add_phase("Análise", ["busca", "sumario"])
pipe.add_phase("Saída", ["formata"])

# Hook de callback
pipe.on_node_complete(lambda name, state: print(f"  ✓ {name}"))

state = pipe.run("analisar tendências 2026")
print(state.get_artifact("formatted_output"))
```

## Referências

- BettaFish QueryEngine: https://github.com/666ghj/BettaFish/tree/main/QueryEngine
- BettaFish MediaEngine: https://github.com/666ghj/BettaFish/tree/main/MediaEngine
- BettaFish InsightEngine: https://github.com/666ghj/BettaFish/tree/main/InsightEngine
- DeerFlow (bytedance/deer-flow, MIT): https://github.com/bytedance/deer-flow
- DeerFlow Book (coolclaws/deerflow-book, 504⭐): https://deepwiki.com/coolclaws/deerflow-book/
  - Cap. 2.1: ThreadState Schema (Annotated reducers)
  - Cap. 6: 11-layer Middleware Pipeline
  - Cap. 7: Context Engineering (Summarization, DanglingCall)
- Reversa P16: Padrão extraído em 2026-05-17
- Reversa P17: MiddlewareChain + DeerFlow Reducers adicionados em 2026-05-17
