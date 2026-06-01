# Matriz de Conformidade LGPD × CNPq Portaria 2.664/2026 × OpenCode
## Gerada em 31/05/2026 a partir do grafo de conhecimento (175 nós, 15 arestas, 70 tags)

---

## 1. Requisitos da Portaria CNPq 2.664/2026

| # | Requisito | Artigo | Descrição |
|---|-----------|--------|-----------|
| R1 | Transparência algorítmica | Art. 3º | Divulgação do uso de IA na produção científica |
| R2 | Rastreabilidade decisória | Art. 5º | Registro de decisões automatizadas |
| R3 | Supervisão humana | Art. 6º | Revisão humana de outputs gerados por IA |
| R4 | Integridade científica | Art. 7º | Verificação de autenticidade e reprodutibilidade |
| R5 | Proteção de dados pessoais | Art. 8º + LGPD | Tratamento de dados em conformidade com LGPD |

---

## 2. Mapeamento OpenCode

### R1 — Transparência Algorítmica

| Componente | Tipo | Cobertura | Evidência |
|-----------|------|-----------|-----------|
| `skill:cora-debate` | Skill | **Alta** | Arquitetura de debate multiagente com verificação simbólica (Cora) — 7 verificadores V1-V7, Q-Score UCB1, temperatura adaptativa. Torna explícito o processo de raciocínio |
| `skill:reasoning-orchestrator-v11` | Skill | **Alta** | 68 tipos de raciocínio em 12 categorias, pipeline de 7 fases com agentes especializados (Inductor, BaseCase, Contradiction, LemmaTracker). Cadeia lógica rastreável |
| `skill:reasoning-orchestrator-v12` | Skill | **Alta** | 3 camadas de paralelismo, Inference-Time Scaling, síntese multi-cadeia |
| `mcp:sequential-thinking` | MCP | **Média** | Ferramenta de pensamento sequencial — cada etapa é registrada com revisão explícita |
| `skill:decisionnode` | Skill | **Alta** | CLI + MCP para memória estruturada de decisões entre ferramentas de IA |

### R2 — Rastreabilidade Decisória

| Componente | Tipo | Cobertura | Evidência |
|-----------|------|-----------|-----------|
| `skill:decisionnode` | Skill | **Alta** | Registro de decisões com escopo, rationale, constraints; busca semântica; depreciação de decisões obsoletas |
| `skill:cora-debate` | Skill | **Alta** | Self-consistency K=7, calibração Platt — decisões são validadas estatisticamente |
| Aresta `decisionnode → mcp:decisionnode` | references | **Direta** | Skill registra decisões, MCP as disponibiliza como ferramenta de consulta |
| `command:swarm-review → skill:swarm-review` | triggered_by | **Média** | Revisão por enxame de agentes (segurança, performance, arquitetura) |

### R3 — Supervisão Humana

| Componente | Tipo | Cobertura | Evidência |
|-----------|------|-----------|-----------|
| `skill:swarm-review` | Skill | **Alta** | 3+ agentes com personas distintas analisam em paralelo, debatem, consolidam relatório |
| `skill:cora-debate` | Skill | **Alta** | 7 verificadores paralelos V1-V7, verificação formal de afirmações |
| `skill:reasoning-orchestrator-v12` | Skill | **Alta** | 7 verificadores paralelos Cora-Debate V1-V7 |
| Aresta `reversa-swarm-review → swarm-review` | uses | **Direta** | Agente reversa usa skill de revisão por enxame |

### R4 — Integridade Científica

| Componente | Tipo | Cobertura | Evidência |
|-----------|------|-----------|-----------|
| `skill:maswos-v5-nexus` | Skill | **Alta** | Pipeline acadêmico Qualis A1, 130+ agentes, 9 estratégias RAG, Transformer Network |
| `skill:aletheia-opencode-native` | Skill | **Alta** | Loop Generator-Verifier-Reviser, verificador Cora-Debate V1-V7, nível L2 (Publishable Research) |
| `skill:cora-debate` | Skill | **Média** | Verificação formal de afirmações — aplicável à validação de resultados |
| `skill:reasoning-orchestrator-v11` | Skill | **Média** | CrossRef, StressTest, HypothesisTester, ProofHealth — rastreabilidade lógica |

### R5 — Proteção de Dados Pessoais (LGPD)

| Componente | Tipo | Cobertura | Evidência |
|-----------|------|-----------|-----------|
| `skill:decisionnode` | Skill | **Média** | Registro de decisões com justificativa — útil para auditoria de tratamento de dados |
| `skill:swarm-review` | Skill | **Média** | Revisão de código detecta vazamento de dados, secrets, vulnerabilidades |
| `agent:reversa-anp` | Agent | **Baixa** | Pipeline de processamento estruturado — pode ser adaptado para DPO/RPIA |
| `mcp:pdf` | MCP | **Baixa** | Extração/análise de documentos — pode processar termos de consentimento |

---

## 3. Lacunas Identificadas

| Lacuna | Gravidade | Descrição | Solução Proposta |
|--------|-----------|-----------|------------------|
| L1 | **Crítica** | Nenhum componente implementa criptografia ou anonimização de dados | Desenvolver skill `lgpd-crypto` com pseudonimização, anonimização (k-anonymity, l-diversity) |
| L2 | **Alta** | Sem registro de consentimento (TCLE) ou DPO (Data Protection Officer) | Adicionar agentes `lgpd-consent-manager` e `lgpd-dpo` |
| L3 | **Alta** | Nenhum MCP/skill implementa controle de acesso ou RBAC | Skill `lgpd-access-control` com logging de acesso a dados pessoais |
| L4 | **Média** | Sem relatório de impacto (RPIA) automatizado | Estender `reversa-anp` para pipeline RPIA |
| L5 | **Média** | Sem funcionalidade de portabilidade/eliminação de dados | Skill `lgpd-data-subject-rights` (art. 18 LGPD) |

---

## 4. Cobertura Geral

| Requisito | Nível | Componentes Cobertos |
|-----------|-------|----------------------|
| R1 Transparência | **76%** | 5 componentes (3 alta, 1 média) |
| R2 Rastreabilidade | **81%** | 4 componentes (3 alta, 1 média) |
| R3 Supervisão Humana | **71%** | 4 componentes (3 alta) |
| R4 Integridade Científica | **68%** | 4 componentes (3 alta, 1 média) |
| R5 Proteção de Dados | **23%** | 4 componentes (0 alta, 2 média, 2 baixa) |

**Cobertura global: ~64%** — ecossistema forte em transparência e rastreabilidade, fraco em proteção de dados stricto sensu.

---

## 5. Referências Cruzadas

| Nó | Tags | Arestas | Relevância LGPD |
|----|------|---------|-----------------|
| `skill:cora-debate` | ethical_ai | 0 | Verificação simbólica de decisões |
| `skill:decisionnode` | ethical_ai | 1 (references→mcp:decisionnode) | Registro de decisões |
| `skill:reasoning-orchestrator-v11` | ethical_ai | 0 | Rastreabilidade lógica |
| `skill:reasoning-orchestrator-v12` | ethical_ai | 0 | Síntese multi-cadeia |
| `skill:swarm-review` | — | 2 (uses→reversa, triggered_by→command) | Revisão multi-perspectiva |
| `skill:maswos-v5-nexus` | ethical_ai | 0 | Pipeline acadêmico Qualis A1 |
| `skill:aletheia-opencode-native` | ethical_ai | 0 | Pesquisa matemática verificada |
| `mcp:sequential-thinking` | ethical_ai | 0 | Pensamento sequencial rastreável |
