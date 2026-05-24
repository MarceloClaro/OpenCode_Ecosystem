<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%).
  Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)
  Genesis-Writer: integrado ao ecossistema v4.0
-->

# 120+ Sync Barriers e 500+ Constraints (Genesis-Writer v2.0)

O Genesis-Writer v2.0 utiliza um sistema robusto de barreiras de sincronização e constraints para garantir a qualidade 10/10 em cada operação atômica, integrando os princípios do Nexus-v6 e Claude Code Architecture.

## 1. Camada L0: Input & Meta-Coordination (20 Barriers)
- **SB0.1-0.4: User Interface & Session Management** (Constraints: 30) - Gerencia entradas do usuário, inicia/persiste sessões e retoma estados.
- **SB0.5-0.8: Permission Gate & Access Control** (Constraints: 25) - Valida permissões de execução e acesso a recursos, baseado em regras de 3 níveis (Deny, Allow, Approve).
- **SB0.9-0.12: Meta-Orchestration & Goal Alignment** (Constraints: 35) - Alinha objetivos globais, decompõe tarefas e define o escopo.
- **SB0.13-0.20: Harness de Veracidade (Nexus L0)** (Constraints: 40) - Verifica autenticidade e relevância de fontes iniciais, prevenindo a progressão com dados falsos ou de baixa qualidade.

## 2. Camada L1: Knowledge & Domain Discovery (25 Barriers)
- **SB1.1-1.5: Skill Registry & Injection** (Constraints: 45) - Armazena, injeta e gerencia habilidades sob demanda, otimizando o uso de recursos.
- **SB1.6-1.10: Context Compressor & Coherence** (Constraints: 50) - Gerencia o tamanho do contexto (limite de 92%), garantindo coerência em sessões longas e evitando perda de informações.
- **SB1.11-1.15: Task Graph & Dependency Management** (Constraints: 40) - Organiza tarefas com base em dependências e prioridades, otimizando o fluxo de trabalho.
- **SB1.16-1.20: Memory Store & Knowledge Persistence** (Constraints: 35) - Fornece persistência de memória entre sessões, mantendo o conhecimento adquirido e evoluindo a base de dados.
- **SB1.21-1.25: Domain Discovery Engine** (Constraints: 50) - Extrai conceitos, mapeia relações e infere leis do domínio, construindo um grafo de conhecimento.

## 3. Camada L2: Autonomous Reasoning (20 Barriers)
- **SB2.1-2.4: Análise de Características** (Constraints: 80) - Define o perfil do problema e as nuances do tópico.
- **SB2.5-2.8: Seleção de Raciocínio (38 Sub-tipos)** (Constraints: 90) - Escolhe dinamicamente o sub-tipo de raciocínio mais adequado (dedutivo, indutivo, causal, etc.).
- **SB2.9-2.12: Configuração de Parâmetros** (Constraints: 70) - Ajusta a sensibilidade e profundidade da análise.
- **SB2.13-2.17: Validação de Estratégia** (Constraints: 100) - Testa a eficácia do raciocínio selecionado para o problema em questão.
- **SB2.18-2.20: Self-Reflection & Bias Detection** (Constraints: 60) - Realiza crítica interna do processo de pensamento e identifica possíveis vieses.

## 4. Camada L3: Fractional Execution & Multi-Agent (30 Barriers)
- **SB3.1-3.5: Subagent Spawner & Delegation** (Constraints: 50) - Cria e delega tarefas a subagentes especializados com contextos isolados.
- **SB3.6-3.10: Teammate Mailboxes & FSM Protocol** (Constraints: 40) - Facilita a comunicação inter-agente via pub/sub e protocolo de máquina de estados finitos.
- **SB3.11-3.15: Autonomous Board & Atomic Locking** (Constraints: 30) - Gerencia autoatribuição de tarefas com bloqueio atômico para coordenação.
- **SB3.16-3.20: Worktree Isolator & Environment Management** (Constraints: 35) - Garante execução em ambientes isolados (branches por tarefa), minimizando conflitos.
- **SB3.21-3.30: Micro Sync Barriers (120+) & Fractional Content** (Constraints: 150) - Divide o conteúdo em unidades atômicas (parágrafos, seções MD) e valida cada uma antes da integração, prevenindo timeouts.

## 5. Camada L4: Specialization & Content Generation (30 Barriers)
- **SB4.1-4.10: Emergent Specialization** (Constraints: 150) - Adapta e refina as capacidades dos agentes com base em padrões de sucesso e feedback.
- **SB4.11-4.20: Adaptive Capabilities & Style/Tone** (Constraints: 140) - Ajusta o estilo, tom e complexidade da escrita para diferentes tipos de publicação e público.
- **SB4.21-4.30: MASWOS Writing Agents & Content Synthesis** (Constraints: 130) - Agentes especializados na geração de conteúdo textual, garantindo fluidez, coesão e aderência às normas acadêmicas.

## 6. Camada L5: Scientific Audit & Validation (40 Barriers)
- **SB5.1-5.10: Micro Validation (500+ Constraints)** (Constraints: 120) - Aplica todas as constraints numéricas, de padrão e de tipo para cada operação atômica.
- **SB5.11-5.20: Qualis A1 Auditor & Academic Rigor** (Constraints: 110) - Avalia o conteúdo contra critérios Qualis A1, garantindo profundidade teórica e relevância.
- **SB5.21-5.30: Citation Validator & Authenticity** (Constraints: 130) - Verifica DOIs, URLs, trechos originais e traduções de citações, prevenindo referências fictícias.
- **SB5.31-5.40: Consistency Checker & Logical Cohesion** (Constraints: 100) - Garante que o argumento principal seja mantido, que as perguntas sejam respondidas e que não haja contradições internas.

## 7. Camada L6: Observability & Evolutionary Feedback (40 Barriers)
- **SB6.1-6.10: Event Bus & Monitoring** (Constraints: 50) - Monitora eventos do ciclo de vida, permitindo interceptação e depuração de operações.
- **SB6.11-6.20: Background Executor & Non-Blocking Tasks** (Constraints: 40) - Executa threads daemon e tarefas em segundo plano de forma não bloqueante.
- **SB6.21-6.30: Micro Feedback Loop (120+ points)** (Constraints: 60) - Coleta feedback granular após cada operação atômica para otimização contínua.
- **SB6.31-6.40: Meta-Learning Engine & Self-Improvement** (Constraints: 50) - Gera otimizações para ciclos futuros, permitindo que o sistema aprenda e evolua.

## 8. Camada L7: Output & Deliverables (10 Barriers)
- **SB7.1-7.3: Final Integrator & Document Assembly** (Constraints: 20) - Consolida todos os arquivos MD fracionados em um documento final, com verificação de links cruzados e formatação.
- **SB7.4-7.7: Report Generator & Quality Metrics** (Constraints: 25) - Produz relatórios detalhados sobre a qualidade do documento, aderência a normas e pontuação de auditoria.
- **SB7.8-7.10: Task Result & Verified Delivery** (Constraints: 15) - Entrega o resultado final verificado ao usuário, com a memória do sistema atualizada.

---
**Total de Sync Barriers:** 225+
**Total de Constraints:** 1000+
