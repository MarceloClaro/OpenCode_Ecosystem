# OpenCode Ecosystem — Painel de Projetos (v4.2.3)

Este documento apresenta o planejamento, o status de desenvolvimento e a rastreabilidade das tarefas do **OpenCode Ecosystem v4.2.1**, estruturado na forma de um painel **Kanban de Projetos**. Cada seção é detalhada didaticamente, associando as atividades aos agentes, skills e diagramas arquiteturais correspondentes.

---

## 🗺️ Mapa de Roteiro (Roadmap Visual)

O ecossistema é guiado por uma arquitetura de 6 camadas que conecta desde a infraestrutura de baixo nível até os ciclos evolutivos de IA. Os dois diagramas abaixo fornecem a base visual para as tarefas listadas no painel:

<div align="center">
  <figure>
    <img src="diagrams/architecture-overview.svg" alt="Visão Geral da Arquitetura OpenCode" width="100%" style="max-width: 900px; border-radius: 8px; margin: 12px 0;"/>
    <figcaption><i>Figura 1: Visão Geral da Arquitetura em 6 Camadas (L1 a L6)</i></figcaption>
  </figure>

  <figure>
    <img src="diagrams/architectural-patterns.svg" alt="10 Padrões Arquiteturais OpenCode" width="100%" style="max-width: 900px; border-radius: 8px; margin: 12px 0;"/>
    <figcaption><i>Figura 2: Os 10 Padrões Arquiteturais Mapeados por Camada</i></figcaption>
  </figure>
</div>

---

## 📊 Quadro Kanban (Status dos Projetos)

| 📥 Backlog (Futuro) | 📋 A Fazer (To Do) | ⚙️ Em Progresso | 🔍 Em Revisão (Quality) | ✅ Concluído (Done) |
| :--- | :--- | :--- | :--- | :--- |
| [DATA-ORCH-01] Expansão para dados de Saúde e Genômica | [MISH-02] Otimização de reconexões SSE no MiroFish Local | [CORR-03] Otimização da velocidade de processamento do Corrector CJK | [AUD-05] Validação de NashSolver N-Dimensional com 50 indicadores | [DI-MIG-01] Migração Completa do Container DI (Fases 1-7) |
| [VQC-100] Expansão para VQC de 100 Qubits | [TS-BRIDGE-02] Roteamento Dinâmico de Eventos no EventBus | [EVO-LOOP-04] Mecanismo de Ejeção de Skills Inativas no AutoEvolve | [QUAL-A1-09] Auditoria Estatística Cohen's d e Bonferroni no MASWOS | [SAN-BOM-02] Limpeza estrutural de arquivos de Agentes (BOM/YAML) |
| [AGENT-LAW-01] Geração Autônoma de Petições com RAG Jurídico | [CLI-05] Interface Gráfica Interativa para o Terminal | [LLM-PARSER-01] Substituir parser de keywords por LLM local | [HEAL-03] Teste de Resiliência e Autocura com Injeção de Falhas | [DIAG-10] Geração e Validação de 10 Diagramas Arquiteturais SVGs |
| | | | | **[PYPI-SCOUT-01]** PyPI Scout + Catálogo Curado ✅ |
| | | | | **[DATA-ORCH-00]** DataOrchestrator + 10 Hooks ✅ |

---

## 🔍 Detalhamento Didático dos Projetos (Cards & Issues)

Abaixo, cada tarefa importante do quadro é explicada didaticamente, conectando seus objetivos técnicos aos recursos visuais, agentes e skills do ecossistema.

---

### 1. ⚙️ Em Progresso — Otimização de Reconexões SSE no MiroFish Local `[MISH-02]`

* **Status:** Em Progresso  
* **Objetivo:** Resolver o erro `ConnectionAbortedError 10053` que ocorre no backend MiroFish quando o painel desconecta abruptamente do fluxo Server-Sent Events (SSE).
* **Explicação Didática:** O MiroFish simula um ambiente multiagente baseado na Teoria dos Jogos. O servidor local transmite métricas em tempo real para a interface via SSE. A tarefa foca em implementar um tratamento de exceções robusto no loop assíncrono para liberar os recursos da porta local quando um cliente se desconecta sem finalizar o socket.
* **Agentes Envolvidos:** `reversa-architect`, `debugger`
* **Skills Utilizadas:** `reasoning-orchestrator`, `test-driven-dev`
* **Diagrama Arquitetural Associado:**

<div align="center">
  <img src="diagrams/mirofish-phd-auditor.svg" alt="MiroFish & PhD Auditor Pipeline" width="100%" style="max-width: 850px; border-radius: 8px; margin: 12px 0;"/>
  <p><i>Figura 3: Pipeline P14-P18 de debate multiagente, integração DocIR e PhD Auditor</i></p>
</div>

---

### 2. 🔍 Em Revisão — Validação Estatística de Rigor Acadêmico no MASWOS `[QUAL-A1-09]`

* **Status:** Em Revisão (Quality Gate Final)  
* **Objetivo:** Auditar os artigos gerados pelo ecossistema para certificar que cumprem o score Qualis A1 (≥ 95/100).
* **Explicação Didática:** O pipeline de escrita MASWOS gera o manuscrito e o submete a uma banca simulada (5 revisores e 4 orientadores). O script `AUTO_SCORE_QUALIS.py` avalia critérios como o tamanho de efeito de Cohen (Cohen's d) e o ajuste de Bonferroni para evitar falsos positivos em testes estatísticos de hipóteses múltiplos. Se o score ponderado for menor que 95, o loop é acionado novamente para correção cirúrgica automática.
* **Agentes Envolvidos:** 49 agentes MASWOS (A00-A45, scheduler e revisores)
* **Skills Utilizadas:** `academic-export-abnt`, `edicao-cirurgica`
* **Diagrama Arquitetural Associado:**

<div align="center">
  <img src="diagrams/academic-pipeline.svg" alt="MASWOS Academic Pipeline" width="100%" style="max-width: 850px; border-radius: 8px; margin: 12px 0;"/>
  <p><i>Figura 4: Os 8 estágios de produção científica com loop de validação</i></p>
</div>

---

### 3. 📥 Backlog — Expansão para Variational Quantum Circuits de 100 Qubits `[VQC-100]`

* **Status:** Backlog (Pesquisa de Longo Prazo)  
* **Objetivo:** Expandir a simulação VQC / QML de 50 qubits para 100 qubits utilizando a otimização de Matrix Product State (MPS) com menor bond dimension.
* **Explicação Didática:** Atualmente, o módulo `quantum/` processa imagens médicas (dataset HAM10000) com alta precisão simulando 50 qubits quânticos. Para dobrar a quantidade de qubits sem estourar a memória RAM (limitação física do hardware local), é necessário otimizar a contração de tensores do MPS, fixando a dimensão de ligação (bond dimension $\chi$) em no máximo 32 ou 64 e empregando técnicas avançadas de mitigação de erro (Zero-Noise Extrapolation e Probabilistic Error Cancellation).
* **Agentes Envolvidos:** `quantum-nexus-phd`, `optimizer`
* **Skills Utilizadas:** `academic-ml-pipeline`
* **Definição de Pronto (DoD):** Acurácia final no dataset dermatológico ≥ 89.5% e tempo de contração por circuito ≤ 50ms por camada.

---

### 4. 📋 A Fazer — Roteamento Dinâmico de Eventos no EventBus `[TS-BRIDGE-02]`

* **Status:** A Fazer (Próxima Sprint)  
* **Objetivo:** Implementar o roteamento dinâmico de eventos entre componentes TypeScript (plugins) e scripts Python através do barramento de eventos central do Container DI.
* **Explicação Didática:** O ecossistema opera em um modelo híbrido (Node.js/Bun e Python). Para que uma alteração no estado gerido por um plugin TS seja notificada instantaneamente ao orquestrador Python (Nexus NMA v6.2), o `CommandRegistry` e a ponte de infraestrutura do DI precisam mapear dinamicamente os payloads de eventos serializados em JSON sobre sockets IPC ou streams stdio.
* **Agentes Envolvidos:** `architect`, `docs-writer`
* **Skills Utilizadas:** `mcp-builder`, `agentic-mcp`
* **Diagrama Arquitetural Associado:**

<div align="center">
  <img src="diagrams/mcp-architecture.svg" alt="Arquitetura de Comunicação MCP" width="100%" style="max-width: 850px; border-radius: 8px; margin: 12px 0;"/>
  <p><i>Figura 5: Arquitetura de comunicação Host-Client-Server via JSON-RPC</i></p>
</div>

---

### 5. ✅ Concluído — Migração Completa do Container de Injeção de Dependência `[DI-MIG-01]`

* **Status:** Concluído e Validado (Fases 1 a 7)  
* **Objetivo:** Centralizar o gerenciamento de estado, cache, barramento de eventos e gerenciamento de skills sob um único container singleton IoC (Inversion of Control).
* **Explicação Didática:** Anteriormente, os scripts do Nexus instanciavam de forma isolada e acoplada seus gerentes de contexto (como o `SkillManager` e `PluginManager`). A migração implementou o padrão DI, permitindo que qualquer parte do sistema consuma instâncias compartilhadas por meio da factory `from_container()`, garantindo consistência, facilidade de mock em testes unitários e modularidade máxima.
* **Agentes Envolvidos:** `reversa-architect`, `reversa-scout`, `security-auditor`
* **Skills Utilizadas:** `test-driven-dev`, `reasoning-orchestrator`
* **Resultados:** 88/88 testes integrados aprovados e total compatibilidade com códigos legados preservada.

---

### 6. ⚙️ Em Progresso — Mecanismo de Ejeção de Skills no AutoEvolve `[EVO-LOOP-04]`

* **Status:** Em Progresso  
* **Objetivo:** Prevenir o inchaço (context bloat) do modelo base removendo ou migrando para referências externas as skills geradas automaticamente que possuem baixa taxa de ativação.
* **Explicação Didática:** O motor `manus-evolve.ts` gera novas skills em `evolution/` a partir de iterações anteriores de sucesso (ciclo PLAN-ACT-REFLECT-EXTRACT-EVOLVE). No entanto, o limite de skills ativas deve ser controlado para não estourar o limite de 2.500 bytes por arquivo. Esta tarefa desenvolve um coletor de lixo (garbage collector) de skills que analisa logs históricos e move as menos utilizadas para arquivos secundários em `references/`.
* **Agentes Envolvidos:** `optimizer`, `docs-writer`
* **Skills Utilizadas:** `token-efficiency`, `writing-plans`
* **Diagrama Arquitetural Associado:**

<div align="center">
  <img src="diagrams/agent-orchestration.svg" alt="Orquestração de Agentes e AutoEvolve" width="100%" style="max-width: 850px; border-radius: 8px; margin: 12px 0;"/>
  <p><i>Figura 6: Ciclo ReAct dos subagentes integrado ao motor evolutivo AutoEvolve</i></p>
</div>

---

### 7. ✅ Concluído — Ciclo de Autocura do Ecossistema `[HEAL-01]`

* **Status:** Concluído e Estabilizado  
* **Objetivo:** Implementar o loop de detecção e autocura contínua de anomalias operacionais (como contaminações CJK e erros de parsing YAML).
* **Explicação Didática:** O script `self_healer.py` atua como um sistema imunológico, rodando varreduras programadas nas configurações do repositório. Ao encontrar anomalias estruturais, ele as resolve por meio de correções cirúrgicas locais, assegurando que o ecossistema mantenha um score de integridade elevado e previna falhas em tempo de execução.
* **Agentes Envolvidos:** `security-auditor`, `debugger`
* **Skills Utilizadas:** `token-efficiency`
* **Diagrama Arquitetural Associado:**

<div align="center">
  <img src="diagrams/self-healing.svg" alt="Ciclo de Autocura do Ecossistema" width="100%" style="max-width: 750px; border-radius: 8px; margin: 12px 0;"/>
  <p><i>Figura 7: O ciclo de 5 fases da Autocura Contínua</i></p>
</div>

---

## 🛠️ Critérios Gerais de Conclusão de Tarefas (Quality Gates)

Para que uma tarefa saia da coluna "Em Revisão" para "Concluído", ela deve passar com sucesso por 4 portões de qualidade (Quality Gates):

1. **G0 — Detecção de Intenção (100%):** O barramento de comandos valida que a intenção do comando coincide com o objetivo da tarefa.
2. **GR — Roteamento Adequado (≥ 85%):** Os agentes corretos são ativados via Container DI.
3. **GE — Execução Correta (≥ 90%):** Testes unitários e funcionais integrados executam sem levantar exceções.
4. **GF — Validação Final (≥ 95%):** O PhD Auditor valida a saída sob critérios estatísticos rigorosos e garante que não há qualquer leak de caracteres indesejados.

---

> **Ecosystem Project Board v4.2.1** — Documentação gerada dinamicamente com base nas metas do Reversa Framework e do Nexus PhD Strategist.
