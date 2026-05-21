<div align="center">

<img src="https://img.shields.io/badge/OpenCode_Ecosystem-v4.2.1-6366f1?style=for-the-badge&logo=openai&logoColor=white" alt="version"/>

# OpenCode Ecosystem v4.2.1

### Arquitetura Multiagente Evolutiva + Simulação MiroFish/BettaFish + PhD Auditor

<br/>

[![Agentes](https://img.shields.io/badge/Agentes-125-6366f1?style=flat-square)](agents/)
[![MCPs](https://img.shields.io/badge/MCP_Servers-40-0ea5e9?style=flat-square)](opencode.json)
[![Skills](https://img.shields.io/badge/Skills-104-10b981?style=flat-square)](skills/)
[![Raciocínios](https://img.shields.io/badge/Raciocínios-38_tipos-f59e0b?style=flat-square)](skills/agent-forum)
[![Teoria dos Jogos](https://img.shields.io/badge/Game_Theory-10_estratégias-ef4444?style=flat-square)](skills/agent-forum/scripts/debate_strategies.py)
[![Qualis](https://img.shields.io/badge/Qualis_A1-Auditor_%E2%89%A580%2F100-10b981?style=flat-square)](skills/agent-forum/scripts/phd_auditor.py)
[![DI Migration](https://img.shields.io/badge/DI_Migration-Fases_1–7_✅-22c55e?style=flat-square)](.reversa/DI_MIGRATION.md)
[![BRAZIL_TZ](https://img.shields.io/badge/Timezone-BRAZIL_UTC--3-8b5cf6?style=flat-square)](skills/config-generator)
[![Status](https://img.shields.io/badge/Status-Produção-22c55e?style=flat-square)]()

<br/>

> **Versão:** 4.2.1 · **Autor:** Reversa Framework v1.2.22 + Nexus PhD Strategist · **Atualizado:** 2026-05-21  
> **Classificação:** Arquitetura Multiagente + MiroFish/BettaFish + PhD Auditor · **Modelo:** `opencode/big-pickle` (200K ctx, 128K out)

</div>

---

## Início Rápido

1. **Instalar pré-requisitos:** Node.js 25, Bun 1.3, Python 3.12
2. **Clonar:** `git clone https://github.com/MarceloClaro/OpenCode_Ecosystem.git`
3. **Instalar dependências:** `bun install`
4. **Executar:** Use `/artigo` para gerar artigo Qualis A1, `/reversa` para engenharia reversa, `/quantum` para computação quântica

> Guia completo de instalação: [GETTING_STARTED.md](GETTING_STARTED.md)

---

## Para quem é este projeto

| Perfil | Como usar | Comando principal |
|--------|-----------|-------------------|
| Pesquisador acadêmico | Gerar artigos Qualis A1 com peer-review simulado | `/artigo` |
| Desenvolvedor | Engenharia reversa + autocura de ecossistemas | `/reversa` |
| Estudante de quantum | Experimentos QML com 50 qubits | `/quantum` |
| Contribuidor | Adicionar agentes, skills ou MCPs | Ver [CONTRIBUTING.md](CONTRIBUTING.md) |

---

## Resumo

O **OpenCode Ecosystem** é uma plataforma de inteligência artificial multiagente, autônoma e evolutiva, integrada ao OpenCode CLI. Unifica produção acadêmica Qualis A1, debate multiagente com Teoria dos Jogos, validação estatística, computação quântica e autocura autônoma — tudo com modelo gratuito (200K ctx) e arquitetura que aprende a cada ciclo.

> **Repositório:** `C:\Users\marce\.config\opencode`  
> **Modelo base:** `opencode/big-pickle` — OpenCode Zen, 200K tokens de contexto, 128K tokens de saída

### Detalhes Técnicos

Composta por **125 agentes especializados**, **40 servidores MCP**, **104 skills** e aproximadamente **114.000 linhas de código Python**, a arquitetura operacionaliza de forma unificada:

- **Simulação MiroFish/BettaFish** — Pipeline multiagente com OASIS Profile Gen, Agent Forum (38 raciocínios + Teoria dos Jogos), Config Generator (BRAZIL_TIMEZONE), Graph Builder e Report Agent
- **PhD Auditor (P18)** — NashSolver generalizado, StatisticalRigor (Cohen's d, Bonferroni, Power Analysis), QualisA1Auditor (score 0-100, 7 critérios), SensitivityAnalyzer, IMRADFormatter
- **Injeção de Dependência (DI)** — Container central com 11 serviços + bridge Python ⟷ TypeScript
- **Produção acadêmica Qualis A1** — pipeline de 49 agentes com score ≥ 95/100
- **Pesquisa científica autônoma** — SEEKER com 10+ fontes (arXiv, PubMed, OpenAlex)
- **Computação quântica aplicada** — VQC 50-qubit, QML HAM10000 (89,52% acurácia)
- **Engenharia reversa de sistemas** — Reversa Framework v1.2.22 (confiança 100%)

---

## Índice

- [Arquitetura Geral](#arquitetura-geral)
- [Simulação MiroFish/BettaFish + PhD Auditor](#simulação-mirofishbettafish--phd-auditor)
- [Injeção de Dependência (DI)](#injeção-de-dependência-di)
- [Orquestração Multiagente — Nexus NMA v6.2](#nexus-nma-v62)
- [MCP Servers — 40 Servidores](#mcp-servers)
- [Estratégias RAG](#estratégias-rag)
- [Pipeline Acadêmico Qualis A1](#pipeline-acadêmico-qualis-a1)
- [Autocura do Ecossistema](#autocura-self-healing)
- [Skills Registry](#skills-registry)
- [Módulo Quantum](#módulo-quantum)
- [Reversa Framework](#reversa-framework)
- [Métricas Agregadas](#métricas-agregadas)
- [Comandos Rápidos](#comandos-rápidos)
- [Diagramas Técnicos — 7 SVGs](#diagramas-técnicos--7-svgs)
- [Documentação](#documentação)

---

## Arquitetura Geral

O ecossistema é estruturado em **6 camadas arquiteturais hierárquicas**, do runtime de infraestrutura até a orquestração meta-granular, com **Injeção de Dependência (DI)** transversal a todas as camadas:

| Camada | Nome | Componentes Principais | Tecnologia |
|:------:|------|----------------------|------------|
| **L6** | Orquestração | Nexus NMA v6.2, Reversa v1.2.22, Evo Loop | Python, JSON-RPC |
| **L5** | Agentes | **125 agentes** (core 56 + criação 49 + SEEKER 12 + Reversa 7 + corretor 1) | OpenCode Subagents |
| **L4** | MCP | **40 servidores** (38 local + 2 remote) | MCP SDK, stdio/HTTP |
| **L3** | Skills | **104 skills** · 12 categorias · P14-P18 MiroFish/BettaFish | YAML, Markdown |
| **L2** | Dados | SQLite, Mem0, Quantum (81 arqs), DOCLing | Ollama, SQLite |
| **L1** | Infra | Node.js 25, Bun 1.3, Python 3.12 | Win32 |
| **DI** | Container | 11 serviços + 3 plugins TS + bridge CommandRegistry | Container, from_container() |

---

## Simulação MiroFish/BettaFish + PhD Auditor

<img src="diagrams/mirofish-phd-auditor.svg" alt="Pipeline MiroFish/BettaFish + PhD Auditor P14-P18" width="100%"/>

O ecossistema integra pipeline completo de simulação multiagente adaptado do **MiroFish** (61K ⭐, swarm intelligence) e **BettaFish** (40.9K ⭐, análise multiagente), com rigor acadêmico do **nexus-phd-strategist**:

### Pipeline P1-P18 (18 Padrões Arquiteturais)

| Faixa | Padrões | O que faz |
|-------|---------|-----------|
| **P1-P9** | Entity NER · Hybrid Graph · Graph Builder · Ontology · OASIS Profile · Synthesis · Swarm Review · Code GraphRAG · Machine States | Infraestrutura MiroFish (grafos, entidades, ontologia, estados) |
| **P10-P13** | Graph Memory Updater · Process Lifecycle · FS-IPC · Config Generator | Runtime & Configuração (BRAZIL_TIMEZONE UTC-3) |
| **P14-P18** | Agent Forum · Document IR · ANP · MiddlewareChain · PhD Auditor | Agentes, Debate & Auditoria Qualis A1 |

### 38 Tipos de Raciocínio + 10 Estratégias de Teoria dos Jogos

Os debates são orquestrados com **38 tipos de raciocínio** (Dedutivo, Indutivo, Dialético, Socrático, Nash, Bayesian, etc.) e **10 estratégias de Teoria dos Jogos** (Dilema do Prisioneiro, Equilíbrio de Nash N×M, Tit-for-Tat, Shapley Value, Mechanism Design, etc.).

### Simulação de 50 Indicadores (Brasil)

Simulação integrada com **50 indicadores reais** de fontes verificadas:
- Macroeconomia: PIB per capita, inflação, Gini, desemprego, IED, dívida externa
- Saúde: expectativa de vida, mortalidade infantil, vacinação, gastos em saúde
- Educação: PISA, matrículas, alfabetização, paridade de gênero
- Infraestrutura: eletricidade, água, saneamento, internet, energia renovável
- Social: pobreza, homicídios, proteção social, democracia, AI readiness

**Achados**: Correlação Internet×AI Readiness (r=0.998), Saneamento×Mortalidade (r=-0.947).

---

## Injeção de Dependência (DI)

O Container central do ecossistema foi migrado para **Injeção de Dependência** (Fases 1–7), registrando 11 serviços e garantindo compatibilidade retroativa total.

```
Container (singleton)
├── state_manager       → IStateManager
├── event_bus           → IEventBus  
├── agent_manager       → AgentManager     (container-aware)
├── plugin_manager      → PluginManager    (container-aware)
├── skill_manager       → SkillManager     (container-aware)
├── cache               → TTLCache         (com event_bus)
├── task_queue          → TaskQueue        (com event_bus + cache)
├── command_registry    → CommandRegistry  (bridge 14 comandos)
├── plugin.manus-evolve         → PluginMeta (typescript)
├── plugin.ecosystem-sync       → PluginMeta (typescript)
└── plugin.bernstein-sync       → PluginMeta (typescript)
```

### Bridges Python ⟷ TypeScript

| Bridge | Função | Itens |
|--------|--------|:-----:|
| `CommandRegistry` | Lê 14 comandos de `command/*.md`, espelha TRIGGER_MAP do TS | 14 comandos |
| `PluginManager.discover_ts_plugins()` | Descobre plugins TS como metadados (não executa) | 3 plugins |
| `register_in_container()` | Registra `plugin.<nome>` no Container | 3 chaves |
| `health_summary()` | Painel de saúde dos plugins TS no ecossistema | 3+ plugins |

**Padrões de design:** `from_container()` factory (Nexus) + `container=` opcional no construtor (Managers).  
**Testes:** 88/88 passando (54 F5+6 + 34 F7) · 378/391 testes legado preservados.  
**Backward compatibility:** 100% — `PluginManager()`, `MCPRouter()`, `CommandRegistry()` todos funcionam sem container.

> Documentação completa: [`.reversa/DI_MIGRATION.md`](.reversa/DI_MIGRATION.md)

---

## Nexus NMA v6.2

<img src="diagrams/agent-orchestration.svg" alt="Orquestração Multiagente Nexus NMA v6.2" width="100%"/>

O **Nexus-Multiagents-v6** (NMA) é o orquestrador meta-granular central, responsável por sincronizar operações atômicas entre todos os agentes do ecossistema por meio de **120+ sync barriers** e **500+ constraints de validação distribuída**.

### Arquitetura de 6 Camadas Internas

```
L0 — Meta-Coordenação      → orquestração entre barreiras de sincronização
L1 — Sincronização Micro   → validação atômica de cada operação
L2 — Execução Paralela     → dispatcher de tarefas independentes
L3 — Consolidação          → merge determinístico de resultados parciais
L4 — Auditoria             → validação cruzada com critérios Qualis A1
L5 — Evolução              → ciclo de auto-aprimoramento (Manus Evolve)
```

### Métricas Nexus

| Métrica | Valor |
|---------|:-----:|
| Camadas de orquestração | 6 (L0–L5) |
| Sync Barriers | 120+ |
| Constraints de validação | 500+ |
| Sub-tipos de raciocínio | 38 |
| Feedback points | 120 |
| Scripts Python | 63 |
| Sessões de contexto offload | 55 |
| Health score (evo-7) | 96/100 |

### Scripts Core do Nexus

| Script | Função | DI |
|--------|--------|:--:|
| `sync_orchestrator.py` | Coordenação entre barreiras de sincronização | ✅ |
| `self_healer.py` | Autocura do ecossistema | ✅ |
| `meta_orchestrator.py` | Meta-orquestração L0 | N/A |
| `evolution_loop.py` | Loop evolutivo autônomo | ✅ |
| `mcp_router.py` | Roteamento interno entre MCPs | ✅ (from_container) |
| `context_offload.py` | Offload de contexto (55 sessões) | ✅ (from_container) |
| `mcp_self_healer.py` | Servidor MCP de autocura (registrado) | N/A |

---

## MCP Servers

<img src="diagrams/mcp-architecture.svg" alt="Arquitetura MCP Client-Host-Server" width="100%"/>

O protocolo **Model Context Protocol (MCP)** opera em três zonas: **Host** (OpenCode), **sessões Client** (instâncias de ferramentas) e **servidores** locais e remotos que expõem recursos, ferramentas e prompts via stdio ou HTTP.

### Distribuição dos 17 Servidores

| Categoria | Qt. | Servidores |
|-----------|:--:|-----------|
| Core / Infraestrutura | 12 | `filesystem`, `sqlite`, `github`, `playwright`, `pdf`, `fetch`, `time`, `diff`, `code-runner`, `chrome-devtools`, `desktop-commander`, `shell-server` |
| Busca e Pesquisa | 6 | `websearch`, `context7`, `gh_grep`, `wikipedia`, `hacker-news`, `fetch` |
| Execução e Análise | 6 | `node-sandbox`, `mcp-server-commands`, `run-python`, `eslint`, `sequential-thinking`, `mermaid` |
| Memória e Decisões | 3 | `mem0-mcp`, `decisionnode`, `self-healer` |
| Domínio Jurídico/Acadêmico | 6 | `maswos-juridico`, `maswos-mcp`, `maswos-rag`, `scihub`, `youtube-transcript`, `biomcp` |
| Outros | 5 | `memory`, `github-search`, ... |

O roteamento e validação entre MCPs é gerenciado pelo Container DI (`command_registry`) e pelo `mcp_router.py` (Nexus, DI-ready).

---

## Estratégias RAG

<img src="diagrams/rag-strategies.svg" alt="9 Estratégias RAG do MASWOS" width="100%"/>

O servidor `maswos-rag` expõe **9 estratégias de Retrieval-Augmented Generation**, selecionadas automaticamente de acordo com o tipo de consulta — desde busca semântica densa até RAG híbrido com re-ranking e fusão de múltiplas fontes.

---

## Pipeline Acadêmico Qualis A1

<img src="diagrams/academic-pipeline.svg" alt="Pipeline Acadêmico MASWOS Qualis A1" width="100%"/>

O pipeline **MASWOS** (Multi-Agent Scientific Writing and Orchestration System) executa **8 estágios sequenciais** com 49 agentes especializados para produção de artigos com score ≥ 95/100 segundo critérios Qualis A1 da CAPES.

### Fluxo de 8 Estágios

```
1. SEEKER        → pesquisa autônoma em 10+ fontes (arXiv, PubMed, OpenAlex, CORE)
2. Estrutura     → definição de seções, hipóteses e metodologia
3. Escrita       → redação com vocabulário anti-IA (87 termos proibidos, TSAC)
4. Formatação    → ABNT NBR 6023, LaTeX, figuras e tabelas
5. Revisão       → banca de 5 revisores especializados
6. Correção      → 4 orientadores doutores com feedback iterativo
7. Score         → AUTO_SCORE_QUALIS.py (10 critérios + pesos)
8. Export        → LaTeX/PDF com 46 anotações TSAC auditáveis
```

### Métricas de Execução

| Métrica | Valor |
|---------|:-----:|
| Agentes especialistas | 49 (A00–A45 + scheduler) |
| Templates de artigo | 24 |
| Referências acadêmicas (Qualis A1, ABNT) | 14 |
| Board Score inicial → final | 86,5 → 92,7/100 (+7,1%) |
| Auto Score Qualis inicial → final | 74 → **95/100** (+28,4%) |
| Limiar Qualis A1 | ≥ 95/100 |
| Tempo médio por pipeline | ~10–20 s (automação completa) |

### Ciclos de Evolução AutoEvolve — Manus Evolve

O plugin `manus-evolve.ts` executa o ciclo **PLAN → ACT → REFLECT → EXTRACT → EVOLVE**, gerando novas skills em `evolution/` a partir de padrões de sucesso:

| Ciclo | Skill Principal Gerada | Score |
|:-----:|----------------------|:-----:|
| evo-1 | Cross-validation + World Bank API | 85/100 |
| evo-2 | Pipeline de artigo 35 páginas ABNT | 90/100 |
| evo-3 | TSAC: 46 citações auditáveis | 95/100 |
| evo-4 | Sci-Hub MCP + arXiv multi-source | 88/100 |
| evo-5 | Pearson CV em 27 indicadores | 92/100 |
| evo-6 | Iterative Correction Loop v2.0 | 95/100 |
| evo-7 | Sync v3.5 + detector CJK + token efficiency | 96/100 |
| evo-8 | Progressive disclosure + observabilidade | 98/100 |
| **Média** | Progressão: **85 → 98** (+15,3%) | **91,1** |

---

## Autocura (Self-Healing)

<img src="diagrams/self-healing.svg" alt="Ciclo de Autocura do Ecossistema" width="100%"/>

O ciclo de autocura **Monitorar → Detectar → Diagnosticar → Reparar → Verificar** opera continuamente pelo MCP `self-healer` e script `nexus/scripts/self_healer.py`, garantindo:

- **95,6%** das skills dentro do limite de 2.500B (progressive disclosure)
- **100%** dos MCPs ativos (38/38)
- **Health score geral: 96/100**

---

## Skills Registry

As 45 skills seguem o padrão **progressive disclosure**: cada `SKILL.md` contém no máximo 2.500 bytes com frontmatter YAML e tabela de referências; o conteúdo completo reside em `references/*.md`.

| Categoria | Skills | Exemplos |
|-----------|:------:|---------|
| system | 6 | `code-review`, `reasoning-orchestrator`, `token-efficiency` |
| juridico | 7 | `edicao-cirurgica`, `pecas-juridicas-html`, `gerador-contratos` |
| research | 3 | `academic-export-abnt`, `academic-ml-pipeline`, `editais-br` |
| tooling | 18 | `mcp-builder`, `agentic-mcp` |
| superpowers | 10 | `writing-plans`, `test-driven-dev` |
| Outras | 1 | `frontend-philosophy`, `plan-protocol`, ... |

**Status:** ✅ 43/45 dentro do limite · ⚠️ 1 borderline (2.781B) · 🔴 1 oversize estrutural (nexus/SKILL.md)

---

## Módulo Quantum

Infraestrutura de computação quântica aplicada com resultados validados experimentalmente (40 arquivos `.py`, ~10.088 linhas).

| Experimento | Resultado |
|------------|:---------:|
| QML HAM10000 — 10.015 imagens, 7 classes | Acurácia: **89,52%** |
| VQC 50-qubit MPS — cross-validation 5-fold | **90,54% ± 0,58%** |
| Teste final | Acurácia: 90,6% · F1: 90,57% · **AUC-ROC: 99,98%** |
| ZNE (5 níveis de ruído 1,0×–3,0×) | E_zero_noise: 0,771 |
| PEC (50 qubits, profundidade 6) | Expected accuracy: 89,88% |
| Redução MPS vs. Statevector | **~10¹¹×** menos memória |

### Parâmetros do VQC

| Parâmetro | Valor |
|-----------|:-----:|
| Qubits | 50 |
| Camadas | 6 |
| Parâmetros treináveis | 600 |
| Backend | MPS (Matrix Product State) |
| Bond dimension (χ) | 64 |

---

## Reversa Framework

Pipeline completo de engenharia reversa **v1.2.22** com 9 agentes especializados e confiança de 100/100.

```
Scout → Archaeologist → Detective → Architect → Writer → Reviewer
                                    ↓
                        Visor → Data Master → Design System
```

| Fase | Agente | Artefatos |
|:----:|--------|-----------|
| 1 | `reversa-scout` | `surface.json`, `modules.json` |
| 2 | `reversa-archaeologist` | `code-analysis/` (AST, deps) |
| 3 | `reversa-detective` | `domain/` (UML, fluxos) |
| 4 | `reversa-architect` | `architecture/` (C4, ADRs) |
| 5 | `reversa-writer` | `specs/` (12 SDDs) |
| 6–9 | reviewer, visor, data-master, design-system | 67 artefatos totais |

**Estado:** 12/12 gaps resolvidos · 12 ADRs · 12 SDDs · 3 diagramas C4 · Confiança: **100/100**

---

## Métricas Agregadas

### Linhas de Código Python por Módulo

| Módulo | Arquivos `.py` | Linhas | % |
|--------|:--------------:|:------:|:-:|
| DOCLing | 100+ | ~39.910 | 36,6% |
| Nexus | 63 | ~22.286 | 20,4% |
| Basis Research | 33 | ~13.659 | 12,5% |
| Quantum | 40 | ~10.088 | 9,2% |
| Editais-BR | 73 | ~5.797 | 5,3% |
| Artigo MIT-IA | 46 | ~5.678 | 5,2% |
| Tests | 24 | ~3.996 | 3,7% |
| Core | 21 | ~3.805 | 3,5% |
| Outros | 28+ | ~4.441 | 4,1% |
| **Total** | **~428+** | **~109.660** | **100%** |

### Saúde Geral do Ecossistema

| Indicador | Valor | Status |
|-----------|:-----:|:------:|
| MCPs ativos | 17/17 | 🟢 |
| Container services registered | 11 (8 core + 3 plugin) | 🟢 |
| Bridge commands (Python ⟷ TS) | 14/14 | 🟢 |
| Skills dentro do limite | 72/74 | 🟢 |
| Agentes registrados | 118 | 🟢 |
| Reversa confidence | 100/100 | 🟢 |
| AutoEvolve gerações | 9 | 🟢 |
| DI Migration | Fases 1–7 ✅ (88/88 tests) | 🟢 |
| Gaps abertos | 0 | 🟢 |
| Health score Nexus | 96/100 | 🟢 |

---

## Comandos Rápidos

| Comando | Pipeline Acionado |
|---------|-------------------|
| `/artigo` | SEEKER + 49 agentes MASWOS + manus-evolve → Qualis A1 |
| `/evolve` | AutoEvolve: PLAN→ACT→REFLECT→EXTRACT→EVOLVE |
| `/reversa` | 9 agentes: scout → archaeologist → ... → design-system |
| `/quantum` | quantum-nexus-phd + code-runner + pdf |
| `/plan` | writing-plans + sequential-thinking MCP |
| `/auto` | openagent + todos os 17 MCPs |
| `/ticket` | Jira ticket manager via CommandRegistry bridge |

---

## Diagramas Técnicos — 7 SVGs

O OpenCode Ecosystem v4.2.1 documenta sua arquitetura por meio de **7 diagramas SVG interativos** localizados em `diagrams/`. Cada SVG é gerado e mantido automaticamente pelo pipeline de engenharia reversa (Reversa Framework v1.2.22) e reflete o estado real do ecossistema em produção.

### Por que SVG e não PNG/Mermaid?

| Critério | SVG (este projeto) | Mermaid | PNG estático |
|---------|-------------------|---------|-------------|
| Renderização nativa GitHub | ✅ | ✅ (limitado) | ✅ |
| Escalabilidade vetorial | ✅ infinita | ❌ (raster) | ❌ |
| Gradientes e glassmorphism | ✅ | ❌ | ✅ (fixo) |
| Atualização programática | ✅ (texto puro) | ✅ | ❌ |
| Animações CSS/SMIL | ✅ | ❌ | ❌ |
| Complexidade de layout | Alta (livre) | Média (gramática) | Alta (fixo) |

---

### SVG 1 — `architecture-overview.svg`

<img src="diagrams/architecture-overview.svg" alt="Arquitetura Geral v4.2.1" width="100%"/>

**Aplicação:** Mapa mestre do ecossistema. Apresenta as **6 camadas arquiteturais** (L1-Infra → L6-Orquestração) com contagens reais de todos os componentes v4.2.1.

**Processos representados:**
- Fluxo descendente de camadas: Orquestração → Agentes → MCP → Skills → Dados → Infra
- L5: 125 agentes (core 56 + criação 49 + SEEKER 12 + Reversa 7 + corretor 1)
- L4: 40 servidores MCP (38 local + 2 remoto)
- L3: 104 skills em 12 categorias incluindo P14-P18 MiroFish/BettaFish
- L2: Quantum (81 arqs), DOCLing, Mem0, Basis Research
- Barra de stats: 125 agentes · 40 MCPs · 104 Skills · 38 Raciocínios · 81 arqs Quantum

**Diferença vs similares:** LangChain e AutoGen exibem grafos de execução planos. Este diagrama mostra **hierarquia de 6 camadas com métricas auditadas** — cada número é verificado no código-fonte e atualizado automaticamente.

---

### SVG 2 — `agent-orchestration.svg`

<img src="diagrams/agent-orchestration.svg" alt="Orquestração de Agentes v4.2.1" width="100%"/>

**Aplicação:** Documenta o padrão hierarchical multi-agent com ReAct loop e AutoEvolve.

**Processos representados:**
- Orquestrador Central (big-pickle, 200K ctx) distribui para 4 sub-agentes especializados
- Camada MCP com 40 servidores (JSON-RPC sobre stdio)
- Ciclo ReAct: THOUGHT → ACTION → OBSERVATION → REPEAT (loop até conclusão)
- Pipeline AutoEvolve: PLAN → ACT → REFLECT → EXTRACT → EVOLVE → `evolution/`
- MiroFish/BettaFish P14-P18 integrado no estágio EVOLVE

**Diferença vs similares:** CrewAI usa grafos fixos de agentes. O OpenCode usa **ReAct dinâmico + AutoEvolve**: o orquestrador gera novas skills em tempo de execução baseado em padrões de sucesso, criando um sistema que melhora a cada ciclo.

---

### SVG 3 — `academic-pipeline.svg`

<img src="diagrams/academic-pipeline.svg" alt="Pipeline Acadêmico MASWOS v4.2.1" width="100%"/>

**Aplicação:** Visualiza o pipeline MASWOS de 8 estágios para produção de artigos Qualis A1.

**Processos representados:**
- S01 SEEKER: pesquisa paralela em arXiv, PubMed, OpenAlex, CORE, Semantic Scholar
- S02-S04: Estrutura, Escrita (49 agentes), Formatação ABNT/LaTeX
- S05-S06: Banca (5 revisores) + Orientação (4 doutores) — iteração até score ≥ 95
- S07: AUTO_SCORE_QUALIS.py (10 critérios ponderados)
- Diamond de decisão: score ≥ 95? Se não → loopback para S06
- S08: Export LaTeX/PDF com 46 anotações TSAC auditáveis
- Corretor CJK (`ptbr_corrector.py`) e PhD Auditor (Nash+Bonferroni+Qualis)

**Diferença vs similares:** GPT-Academic e Elicit geram texto linear. O MASWOS aplica **peer-review simulado com 5 revisores + 4 orientadores + loopback iterativo + auditoria estatística** — nenhum framework open-source replica esse nível de verificação.

---

### SVG 4 — `mcp-architecture.svg`

<img src="diagrams/mcp-architecture.svg" alt="Arquitetura MCP v4.2.1" width="100%"/>

**Aplicação:** Documenta a implementação do protocolo MCP (Anthropic, 2024) com 40 servidores.

**Processos representados:**
- Processo Host (OpenCode CLI) contém Agente + Clientes MCP
- Sessões JSON-RPC 1:1 entre cliente e servidor (stdio local / HTTP remoto)
- 3 zonas: Segurança Local (FS, SQLite, PDF), Busca (WebSearch, Context7, gh_grep), Remota (☁️)
- Lazy init: servidores só iniciam na primeira chamada de ferramenta

**Diferença vs similares:** Ferramentas como Cursor e Windsurf usam MCPs de forma monolítica. O OpenCode implementa **40 servidores com lazy init + Container DI**, permitindo adicionar ou remover servidores sem reinicializar o agente.

---

### SVG 5 — `rag-strategies.svg`

<img src="diagrams/rag-strategies.svg" alt="9 Estratégias RAG v4.2.1" width="100%"/>

**Aplicação:** Catálogo das 9 estratégias RAG implementadas no servidor `maswos-rag`.

**Processos representados (9 estratégias):**

| # | Estratégia | Fluxo | Referência |
|---|-----------|-------|------------|
| ① | Vanilla RAG | Query → Embed → Retrieve → Generate | Lewis et al., NeurIPS 2020 |
| ② | Memory RAG | + Redis session memory | Zhong et al., arXiv 2405.14367 |
| ③ | Agentic RAG | + Agent routing dinâmico | Gradientsys, arXiv 2507.06520 |
| ④ | Graph RAG | + Knowledge Graph KG retrieval | Edge et al., Microsoft 2024 |
| ⑤ | Hybrid RAG | Vector + Graph fusion | Wang et al., arXiv 2501.00309 |
| ⑥ | CRAG | Corrective eval → {Correct┃Incorrect┃Ambíguo} | Yan et al., ICLR 2024 |
| ⑦ | Adaptive RAG | Seleção de estratégia por tipo de query | Jeong et al., arXiv 2403.14403 |
| ⑧ | Fusion RAG | Multi-Query → Reciprocal Rank Fusion | Radev et al., arXiv 2402.03367 |
| ⑨ | HyDE | Hypothetical Document Embeddings | Gao et al., NeurIPS 2022 |

**Diferença vs similares:** LlamaIndex e LangChain oferecem RAG modular, mas requerem configuração manual por caso. O `maswos-rag` seleciona automaticamente a estratégia via Adaptive RAG (⑦) baseado no tipo de consulta, combinando Graph+Vector+Correction em um único servidor MCP.

---

### SVG 6 — `self-healing.svg`

<img src="diagrams/self-healing.svg" alt="Ciclo de Autocura v4.2.1" width="100%"/>

**Aplicação:** Visualiza o ciclo contínuo de saúde e reparo automático do ecossistema.

**Processos representados:**
1. **MONITORAR** — varredura contínua: 104 skills, 40 MCPs, CJK leaks, syntax errors
2. **DETECTAR** — anomalias: caracteres CJK, YAML inválido, skills oversize, MCPs inativos
3. **DIAGNOSTICAR** — classificação por severidade (crítico/aviso/info)
4. **REPARAR** — correção automática: remove CJK, corrige frontmatter, progressive disclosure
5. **VERIFICAR** — re-varredura pós-reparo para confirmar resolução

**Métricas v4.2.1:** 104 skills · 12 categorias · 40 MCPs ativos · CJK leaks = 0 (zero-tolerance)

**Diferença vs similares:** AutoGen e CrewAI não possuem monitoramento de saúde do ecossistema. O OpenCode implementa um **MCP dedicado (`self-healer`) + script Python (`self_healer.py`)** que opera de forma autônoma, detectando e corrigindo problemas sem intervenção humana.

---

### SVG 7 — `mirofish-phd-auditor.svg` *(NOVO v4.2.1)*

<img src="diagrams/mirofish-phd-auditor.svg" alt="Pipeline MiroFish/BettaFish + PhD Auditor P14-P18" width="100%"/>

**Aplicação:** Documenta o pipeline P14-P18 completo — a camada de simulação multiagente com rigor científico Qualis A1 — exclusiva do OpenCode Ecosystem v4.2.1.

**Processos representados:**

| Fase | Componente | Função |
|------|-----------|--------|
| P14 | Agent Forum (OASIS) | Debate multiagente estruturado · 38 tipos de raciocínio · 8 perfis |
| P15 | DocIR | Recuperação de 50 métricas reais (World Bank/WHO/FAO/UNESCO) |
| P16 | ANP | Ponderação multi-critério Analytic Network Process |
| P17 | Meta-Writer | Síntese em LaTeX/IMRAD · TSAC anti-AI · 87 palavras banidas |
| P18 | PhD Auditor | NashSolver · StatisticalRigor (Cohen+Bonferroni) · QualisA1Auditor |

**38 tipos de raciocínio em 6 categorias:**
- Lógico (5): Dedutivo, Indutivo, Abdutivo, Analógico, Hipotético-Dedutivo
- Dialético (5): Socrático, Hegeliano, Tese-Antítese, Crítica, Refutação
- Teoria dos Jogos (10): Nash, Minimax, Dominância, Stackelberg, Pareto, Bayesiano, Evolutivo, Cooperativo, Assimétrico, Sinalização
- Decisão (5): Multi-critério, Bayesiano, Árvore, Fuzzy, Heurístico
- Estratégico (5): SWOT, Cenário, Roadmap, Competitivo, Blue Ocean
- Inovação (8): TRIZ, Design Thinking, Lateral, Biomimética, Disruptivo, Frugal, Combinatorial, Ágil

**11 componentes MiroFish/BettaFish:** OASIS · Forum · Config · Graph · Report · Nash · Stats · Qualis · Sensitivity · IMRAD · Debate

**Diferença vs similares:** Nenhum framework open-source combina simulação de debate multiagente com validação estatística acadêmica (Cohen's κ, Bonferroni, Power Analysis, Nash Equilibrium) num único pipeline. GPT-4 research tools, Semantic Scholar e ResearchRabbit fazem busca/sumarização — mas **não auditam, debatem nem validam estatisticamente** o conteúdo gerado.

---

### Por que o OpenCode tem vantagem sobre similares?

| Capacidade | OpenCode Ecosystem v4.2.1 | LangChain | AutoGen | CrewAI | Cursor/Copilot |
|-----------|------------------------|-----------|---------|--------|----------------|
| Agentes especializados | **125** | Configurável | Configurável | ~10-20 | Não |
| Pipeline acadêmico Qualis A1 | **✅ 8 estágios** | ❌ | ❌ | ❌ | ❌ |
| PhD Auditor (Nash+Bonferroni) | **✅** | ❌ | ❌ | ❌ | ❌ |
| RAG multi-estratégia (9) | **✅ auto-select** | Manual | Manual | Manual | ❌ |
| Self-Healing autônomo | **✅ MCP dedicado** | ❌ | ❌ | ❌ | ❌ |
| AutoEvolve (gera skills) | **✅ PLAN→EVOLVE** | ❌ | ❌ | ❌ | ❌ |
| Quantum Computing (50 qubits) | **✅ 89.52% acc** | ❌ | ❌ | ❌ | ❌ |
| MCP Servers nativos | **40 servidores** | Plugin-based | ❌ | ❌ | Limitado |
| Zero-tolerance CJK + PT-BR | **✅ corrector.py** | ❌ | ❌ | ❌ | ❌ |
| Engenharia Reversa autônoma | **✅ 9 agentes** | ❌ | ❌ | ❌ | ❌ |
| Modelo gratuito 200K ctx | **✅ big-pickle** | API paga | API paga | API paga | Assinatura |

> **Vantagem-chave:** O OpenCode Ecosystem é o único framework que **combina produção acadêmica Qualis A1 + debate multiagente com Teoria dos Jogos + validação estatística + quantum computing + autocura autônoma** num ecossistema unificado, com modelo gratuito (200K ctx) e arquitetura evolutiva que aprende a cada ciclo.

---

## Documentação

| Documento | Descrição |
|-----------|-----------|
| [GETTING_STARTED.md](GETTING_STARTED.md) | Guia de instalação e primeiros passos |
| [TUTORIALS.md](TUTORIALS.md) | Tutoriais práticos detalhados *(em breve)* |
| [GLOSSARY.md](GLOSSARY.md) | Glossário de termos técnicos *(em breve)* |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Guia para contribuidores |
| [ROADMAP.md](ROADMAP.md) | Visão futura do projeto |
| [AGENTS_PTBR.md](AGENTS_PTBR.md) | Documentação de agentes em PT-BR *(em breve)* |

---

## Notas Técnicas

1. **DI Migration (Fases 1–7)** — Container central com 11 serviços, bridge Python ⟷ TS via `CommandRegistry` (14 comandos) e `PluginManager` (3 plugins). 88/88 testes passando, 100% backward compat.
2. **Token Efficiency** — Contexto interno em formato compacto (+40% densidade); todo output ao usuário em PT-BR formal; `ptbr_corrector.py` com detecção CJK tolerância zero.
3. **Progressive Disclosure** — `SKILL.md` ≤ 2.500B; conteúdo estendido em `references/*.md`; descoberta via campo `trigger` no frontmatter YAML.
4. **MCP Lazy Init** — Servidores locais auto-inicializam na primeira chamada de ferramenta, sem overhead de startup.
5. **Manus Evolve** — Engine autônoma que aprende de ciclos anteriores e grava novas skills em `evolution/`.
6. **Auditoria Qualis A1** — 10 critérios ponderados + banca de 5 revisores + 4 orientadores, loopback iterativo até score ≥ 95/100.
7. **DecisionNode** — Registro de decisões arquiteturais com busca semântica via embeddings (Ollama), prevenindo duplicação e mantendo histórico de depreciação.
8. **Compilação e Estabilização PDF/LaTeX** — Correção estrutural de numeração ABNT (mapeamento nativo para `\chapter` via `--top-level-division=chapter`), tratamento de exceções de layout (`\tightlist` via `\providecommand`, altura de cabeçalho `\headheight=15pt` e prevenção de colisões de hyperlinks via roman/arabic), e tabelas multidimensionais de 7 colunas autoajustadas via `\scriptsize` + `\tabcolsep=3pt` local.

---

<div align="center">

**OpenCode Ecosystem v4.2.1**

125 agentes · 40 MCPs · 104 skills · 38 raciocínios · MiroFish/BettaFish · PhD Auditor · 81 arqs Quantum

*Documentação atualizada automaticamente — 2026-05-21 · BRAZIL_TIMEZONE UTC-3*

</div>
