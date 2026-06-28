---
name: react-agent-loop
version: "1.0.0"
kind: python
category: system
affinity: {agent-forum: 0.95, reasoning-orchestrator: 0.90, cora-debate: 0.85}
description: React Agent Loop skill for the OpenCode ecosystem
---

# ReAct Agent Loop — Ciclo Thought -> Action -> Observation

## Origem
Extraido de **SandeClaw** (specs/agent-loop.md, PRD.md secao 6.2).
E a engrenagem central do SandeClaw: recebe input bruto, submete ao LLM
(Thought), executa ferramentas (Action+Observation), repete ate resposta final.

## Como Funciona
Loop com hard limit de iteracoes que evita loops infinitos:

```
User Input ──> [System Prompt + Tools]
                    |
               ┌────────────────────┐
               │  LLM.chat()        │<──┐
               │  Thought/Action    │   │
               └───────┬────────────┘   │
                       │                │
               ┌───────▼────────────┐   │
               │  Tool call?        │   │
               │  SIM: executa tool │   │ Observation
               │  NAO: resposta     │   │ injetada no
               │  final             │   │ contexto
               └───────┬────────────┘   │
                       │                │
               ┌───────▼────────────┐   │
               │  iter >= MAX?      │───┘
               │  SIM: break        │
               │  NAO: continua     │
               └────────────────────┘
```

Cada iteracao registra log estruturado:
```
[Iter 1] ACTION: write_file({"path": "teste.txt", "content": "Ola"})
[Iter 1] OBSERVATION: Arquivo 'teste.txt' criado (3 bytes)
[Iter 2] FINAL: Arquivo criado com sucesso!
```

**Hard limit**: `MAX_ITERATIONS` (default 5) impede billing infinito. Se atingido,
retorna mensagem de erro controlada em vez de quebrar.

**Tratamento de erros**:
- JSON malformado do LLM → observacao pede correcao
- Tool lanca excecao → mensagem de erro vai como observacao
- MAX_ITERATIONS nulo no env → fallback para 5

## Valor para OpenCode
- **Motor unificado**: Substitui loops ReAct ad-hoc em agent-forum,
  reasoning-orchestrator, cora-debate, etc.
- **Tool registry plugavel**: Qualquer skill pode expor tools via `BaseTool`
- **Seguranca**: Hard limit impede gasto excessivo de tokens
- **Rastreabilidade**: Log detalhado de cada iteracao para auditoria

## Uso
```python
from skills.react_agent_loop.scripts.agent_loop import (
    AgentLoop, ToolRegistry, FileWriterTool, BashTool
)
from skills.provider_factory.scripts.provider_factory import ProviderFactory

llm = ProviderFactory.from_env("LLM_")
tools = ToolRegistry()
tools.register(FileWriterTool(base_dir="workspace"))

# Registre BashTool apenas para entradas confiaveis e com allowlist explicita.
# tools.register(BashTool(allowed_commands={"ls", "pwd"}, base_dir="workspace"))

loop = AgentLoop(llm_client=llm, tool_registry=tools, max_iterations=5)
answer = loop.run("Liste os arquivos .py no diretorio atual")
print(answer)
```

`FileWriterTool` rejeita caminhos absolutos, path traversal e sobrescrita por
padrao. `BashTool` nao permite nenhum comando por padrao; integracoes devem
fornecer uma allowlist minima de comandos e manter o `base_dir` restrito ao
workspace da tarefa.

## Ficheiros
- `scripts/agent_loop.py` — implementacao completa (260 linhas)
  - `AgentLoop` — engine ReAct com hard limit
  - `ToolRegistry` — registro plugavel de ferramentas
  - `BaseTool` — classe base para qualquer ferramenta
  - `FileWriterTool` / `BashTool` — exemplos funcionais
