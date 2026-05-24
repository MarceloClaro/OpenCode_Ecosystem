<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%).
  Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)
  Genesis-Writer: integrado ao ecossistema v4.0
-->

# Componentes da Claude Code Architecture Integrados (Genesis-Writer v2.0)

O Genesis-Writer v2.0 incorpora e aprimora os principais componentes da Claude Code Architecture para garantir autonomia, segurança e eficiência no processo de escrita.

## 1. Input Layer (Integrado em L0)
- **User Interface:** Ponto de entrada para o usuário, suportando interfaces CLI e IDE.
- **Session Manager:** Gerencia o ciclo de vida das sessões, permitindo retomar, bifurcar e persistir o estado das operações.
- **Permission Gate:** Mecanismo de segurança que controla as ações que o agente pode executar, baseado em regras YAML de 3 níveis (Deny, Allow, Approve).

## 2. Knowledge Layer (Integrado em L1)
- **Skill Registry:** Armazena e injeta habilidades sob demanda, otimizando o uso de recursos.
- **Context Compressor:** Gerencia o tamanho do contexto do modelo através de um sistema de 3 camadas com um limite de 92%, garantindo a coerência em sessões longas.
- **Task Graph:** Organiza as tarefas com base em dependências e prioridades.
- **Memory Store:** Fornece persistência de memória entre sessões, mantendo o conhecimento adquirido.

## 3. Master Agent Loop (Orquestrador Central)
- O coração do sistema, operando em um ciclo contínuo de **Perception → Action → Observation → Evolution**. Ele observa o estado atual, decide a próxima ação a ser tomada e processa o resultado dessa ação, com a adição de um estágio de evolução contínua.

## 4. Multi-Agent Layer (Integrado em L3)
- **Subagent Spawner:** Permite que o agente mestre crie e delegue tarefas a subagentes com contextos isolados.
- **Teammate Mailboxes:** Facilita a comunicação entre agentes através de um sistema pub/sub com entrega instantânea.
- **FSM Protocol:** Define o protocolo de máquina de estados finitos para a comunicação entre agentes (IDLE → REQUEST → WAIT → RESPOND).
- **Autonomous Board:** Um mecanismo de autoatribuição com bloqueio atômico para coordenação de tarefas.
- **Worktree Isolator:** Garante que as tarefas sejam executadas em ambientes isolados (branches por tarefa), minimizando conflitos.

## 5. Observability Layer (Integrado em L6)
- **Event Bus:** Monitora eventos do ciclo de vida e permite a interceptação de operações.
- **Background Executor:** Executa threads daemon e tarefas em segundo plano de forma não bloqueante.

## 6. Output Layer (Integrado em L7)
- **Task Result:** Fornece o resultado final verificado da tarefa, com a memória do sistema atualizada.
