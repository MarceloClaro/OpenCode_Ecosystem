# SPEC_TOP_react — AgentLoop TDD Specification

**Skill:** react-agent-loop  
**Source:** scripts/agent_loop.py → AgentLoop, ToolRegistry, LoopState  
**Framework:** pytest  
**Status:** Spec-Driven

---

## CT-1: test_init — Inicializacao de AgentLoop e ToolRegistry

**Objetivo:** Verificar que `AgentLoop` armazena `max_iterations` e
`ToolRegistry` corretamente, e que `LoopState` inicia com valores padrao.

**Passos:**
1. Instanciar `AgentLoop(llm, tools, max_iterations=3)`
2. Verificar `loop._max_iterations == 3`
3. Instanciar `LoopState()` e verificar `iterations=0, terminated=False`

**Esperado:** Objetos inicializados com parametros corretos.

---

## CT-2: test_execute_tool — Execucao com sucesso, falha e tool desconhecida

**Objetivo:** Validar que `ToolRegistry.execute()` retorna `ToolResult`
adequado para: tool existente com sucesso, tool que lanca excecao, e
tool nao registrada.

**Passos:**
1. Registrar `EchoTool` e executar → `success=True`, output contem "echo:"
2. Registrar `AlwaysFailTool` e executar → `success=False`, error preenchido
3. Executar tool nao registrada → `success=False`, "desconhecida" no erro

**Esperado:** Tres cenarios de execucao cobertos.

---

## CT-3: test_max_iterations — Hard limit impede loop infinito

**Objetivo:** Confirmar que `AgentLoop.run()` termina ao atingir
`max_iterations` mesmo quando LLM continua gerando tool calls.

**Passos:**
1. Configurar `max_iterations=3`
2. LLM mock sempre retorna tool call
3. Chamar `loop.run("faca algo")`
4. Verificar que resposta contem "limite maximo de iteracoes"

**Esperado:** Loop termina forcadamente apos 3 iteracoes.

---

## CT-4: test_available — Tool registry vazio e preenchido

**Objetivo:** Garantir que `ToolRegistry` comeca vazio e o
`get_system_prompt_addendum()` so retorna prompt de ferramentas
quando ha tools registradas.

**Passos:**
1. `ToolRegistry()` vazio → `get_system_prompt_addendum() == ""`
2. Executar tool desconhecida → `ToolResult.failure`
3. Registrar `EchoTool` → prompt contem "echo" e "Ferramentas Disponiveis"

**Esperado:** Transicao correta de estado vazio para populado.
