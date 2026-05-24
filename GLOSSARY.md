# Glossário — OpenCode Ecosystem v4.2.3

> Definições dos termos técnicos utilizados no ecossistema. Organizado em ordem alfabética.

---

## A

### AutoEvolve

Engine de evolução autônoma do ecossistema. Executa o ciclo **PLAN → ACT → REFLECT → EXTRACT → EVOLVE**, gerando novas skills em `evolution/` a partir de padrões de sucesso. Implementado em `plugins/manus-evolve.ts`. Já completou **11 ciclos** com progressão de score de 85 → 97/100.

### Antigravity Bridge

Ponte bidirecional entre o OpenCode Ecosystem e o **Antigravity** (Google DeepMind Advanced Agentic Coding). Expõe 6 capacidades exclusivas: `generate_image`, `browser_subagent`, `search_web`, `read_url_content`, `parallel_subagents`, `artifact_creation`.

---

## C

### Container DI

Container central de Injeção de Dependência. Registra 11 serviços (8 core + 4 plugins TS). Os 4 plugins TS são: `plugin.manus-evolve`, `plugin.ecosystem-sync`, `plugin.bernstein-sync` e `plugin.antigravity-bridge`.

---

## D

### DataOrchestrator 🆕

Camada universal de acesso a dados do ecossistema (`data_orchestrator.py`, 592 linhas). Permite consultas em **linguagem natural** roteadas automaticamente para a fonte de dados correta entre **8 domínios**: Geo, Finance, Crypto, BioMed, Academic, Economic, Health, PDF. Arquitetura de 3 camadas: QueryIntent (parser 80+ keywords) → DataSourceRegistry (auto-discovery 30+ bibliotecas) → Ecosystem Hooks (10 hooks). Implementado no Round 9 do `/evolve`.

### DataSourceRegistry 🆕

Componente do DataOrchestrator responsável por **auto-discovery** das bibliotecas disponíveis no ambiente Python. Verifica 8 domínios e 30+ bibliotecas via `importlib`, detectando quais domínios estão operacionais sem configuração manual.

---

## E

### Ecosystem Hooks 🆕

Camada de integração entre bibliotecas Python e pipelines do ecossistema (`ecosystem_hooks.py`, v2.0, ~700 linhas). Composta por **10 hooks** organizados em duas rodadas evolutivas: Round 8 (SeekerMultiSource, WorldBankAnalyzer, PDFProcessor, MCPScoutBridge, HTTPXClient) e Round 9 (GeoAnalyzer, FinanceAnalyzer, MarketSpeculator, BioMedAnalyzer, QualisDatasetHub).

---

## M

### Matriz de Afinidade 🆕

Mapeamento da relevância funcional (0--100%) de cada biblioteca Python para cada pipeline do ecossistema (SEEKER, MASWOS, PhD Auditor, data\_analysis, MCP\_server). Armazenada em `opencode_catalog.json`. Afinidades máximas: mcp→MCP\_server (100%), wbgapi→data\_analysis (95%), scholarly→SEEKER (95%), arxiv→SEEKER (95%).

---

## P

### PyPI Scout 🆕

Ferramenta canônica de descoberta de bibliotecas Python no ecossistema (`pypi_scout.py`, 350 linhas). Catálogo curado com 22+ bibliotecas em 6 categorias, métricas de afinidade para 5 pipelines, CLI com 7 comandos (`search`, `catalog`, `category`, `install`, `recommend`, `diff`, `help`). Substitui o PyPISearcher v3.0. Skill registrada como `pypi-scout`.

---

## Q

### QueryIntent 🆕

Parser de intenção do DataOrchestrator. Converte consultas em linguagem natural para intenções estruturadas (domínio, entidade, métrica) utilizando 80+ palavras-chave mapeadas para 8 domínios. Extrai automaticamente entidade e métrica da consulta, atribuindo pontuação de confiança (0--100%).

## A

### AutoEvolve

Engine de evolução autônoma do ecossistema. Executa o ciclo **PLAN → ACT → REFLECT → EXTRACT → EVOLVE**, gerando novas skills em `evolution/` a partir de padrões de sucesso identificados em ciclos anteriores. Implementado em `plugins/manus-evolve.ts`. Já completou 9 ciclos com progressão de score de 85 → 98/100.

---

### Antigravity Bridge

Ponte bidirecional entre o **OpenCode Ecosystem v4.2** e o **Antigravity** (Google DeepMind Advanced Agentic Coding). Composta por três artefatos: `plugins/antigravity-bridge.ts` (plugin TypeScript registrado no Container DI), `nexus/antigravity_mcp_server.py` (servidor MCP com 7 ferramentas JSON-RPC) e `agents/antigravity-orchestrator.md` (agente roteador com fallback). Indexada como skill em `skills/agent-forum/antigravity-integration/SKILL.md` (v1.0). Expos 6 capacidades exclusivas: `generate_image`, `browser_subagent`, `search_web`, `read_url_content`, `parallel_subagents`, `artifact_creation`. Health score monitorado em `.evolve/antigravity-bridge-state.json`.

---

## B

### big-pickle

Modelo de linguagem padrão do OpenCode Ecosystem. Também conhecido como **OpenCode Zen**. Características: 200K tokens de contexto, 128K tokens de saída, **gratuito**. Utilizado como orquestrador central de todos os agentes do ecossistema.

---

## C

### Container DI

Container central de **Injeção de Dependência** do ecossistema. Registra **11 serviços** (8 core + 4 plugins TypeScript) e oferece acesso via padrão singleton. Os 8 serviços core são: `state_manager`, `event_bus`, `agent_manager`, `plugin_manager`, `skill_manager`, `cache`, `task_queue` e `command_registry`. Os **4 plugins TS** são: `plugin.manus-evolve`, `plugin.ecosystem-sync`, `plugin.bernstein-sync` e **`plugin.antigravity-bridge`** (v1.0, 2026-05-24).

---

## D

### DI (Dependency Injection)

**Injeção de Dependência** — padrão de design em que os componentes recebem suas dependências externamente em vez de criá-las internamente. No OpenCode Ecosystem, o Container DI centraliza 11 serviços com bridge bidirecional Python ⟷ TypeScript. Migração completa em 7 fases com 88/88 testes passando e 100% de compatibilidade retroativa.

---

## L

### Lazy Init

Padrão de inicialização utilizado pelos servidores MCP. Os MCPs **só inicializam na primeira chamada de ferramenta**, não durante a inicialização do sistema. Isso reduz o tempo de startup e o consumo de recursos, pois apenas os MCPs efetivamente utilizados são carregados em memória.

---

## M

### MASWOS

**Multi-Agent System Writing Orchestration System** — Sistema de orquestração multiagente para produção de artigos acadêmicos. Utiliza **49 agentes especializados** distribuídos em 8 estágios sequenciais: pesquisa (SEEKER) → estrutura → escrita → formatação → revisão (banca de 5) → correção (4 orientadores) → score (AUTO_SCORE_QUALIS.py) → exportação (LaTeX/PDF). Produz artigos com score ≥ 95/100 segundo critérios Qualis A1 da CAPES.

### MCP (Model Context Protocol)

**Model Context Protocol** — Protocolo criado pela Anthropic (2024) que define comunicação padronizada entre agentes de IA e servidores de contexto via **JSON-RPC**. No OpenCode Ecosystem, **41 servidores MCP** (38 locais via stdio + 2 remotos via HTTP + 1 Antigravity MCP) fornecem ferramentas, recursos e prompts ao agente orquestrador. Cada servidor opera em sessão 1:1 com o cliente MCP.

### MiroFish / BettaFish

Pipeline de **simulação multiagente** adaptado de frameworks de inteligência de enxame (MiroFish, 61K estrelas) e análise multiagente (BettaFish, 40.9K estrelas). No ecossistema, implementa os padrões P14-P18 com 11 componentes: OASIS, Forum, Config, Graph, Report, Nash, Stats, Qualis, Sensitivity, IMRAD e Debate. Integra 38 tipos de raciocínio e 10 estratégias de Teoria dos Jogos.

---

## N

### Nexus NMA

**Nexus Multi-Agent** v6.2 — Orquestrador meta-granular central do ecossistema. Responsável por sincronizar operações atômicas entre todos os agentes por meio de **120+ sync barriers** e **500+ constraints de validação distribuída**. Contém 63 scripts Python organizados em 6 camadas internas (L0-L5). Health score: 96/100.

---

## P

### PhD Auditor

Componente **P18** do pipeline MiroFish/BettaFish. Implementa auditoria acadêmica de rigor científico com 5 módulos: **NashSolver** (equilíbrio de Nash generalizado), **StatisticalRigor** (Cohen's d, Bonferroni, Power Analysis), **QualisA1Auditor** (score 0-100 com 7 critérios), **SensitivityAnalyzer** e **IMRADFormatter**. Garante que os artigos produzidos atendam aos padrões Qualis A1.

### Progressive Disclosure

Padrão de organização de skills do ecossistema. Cada `SKILL.md` contém no máximo **2.500 bytes** com frontmatter YAML e uma tabela de referências. O conteúdo detalhado reside em arquivos separados em `references/*.md`. Isso otimiza o uso de tokens ao carregar apenas o resumo da skill, com acesso ao conteúdo completo sob demanda.

---

## R

### RAG (Retrieval-Augmented Generation)

**Geração Aumentada por Recuperação** — Técnica que combina busca de informação com geração de texto. O ecossistema implementa **9 estratégias RAG** no servidor `maswos-rag`: Vanilla, Memory, Agentic, Graph, Hybrid, CRAG (Corrective), Adaptive, Fusion e HyDE. A seleção de estratégia é automática via Adaptive RAG baseado no tipo de consulta.

### ReAct

Padrão de raciocínio dos agentes: **THOUGHT → ACTION → OBSERVATION → REPEAT**. O agente pensa sobre o problema, executa uma ação, observa o resultado e repete o ciclo até alcançar a conclusão. Utilizado como loop principal de execução do orquestrador central.

### ResearcherScore 🆕

Sistema de pontuação de qualidade da sessão de pesquisa (0-100). Avalia 6 critérios ponderados: densidade de evidências (25%), fontes verificadas (20%), TSAC compliance (20%), diversidade de fontes (15%), cobertura multi-domínio (10%) e peer review (10%). Grades: A (≥90), B (≥75), C (≥60), D (≥40), F (<40).

---

## S

### SEEKER

Sistema de **pesquisa científica autônoma** implementado em `basis-research/`. Composto por **10 agentes Python** (grounder, social, historian, gaper, vision, theorist, rude, synthesizer, thinker, scribe) e um **argument tree engine**. Pesquisa em **10+ fontes acadêmicas**: arXiv, PubMed, OpenAlex, CORE, Semantic Scholar, entre outras. Cada afirmação é rastreável até uma evidência verificável.

---

## T

### TSAC

**Anotações anti-IA auditáveis** — Sistema que garante que o texto gerado não apresente padrões típicos de escrita por IA. Mantém uma lista de **87 palavras e expressões banidas** (termos frequentemente usados por modelos de linguagem). O artigo final inclui **46 anotações TSAC** verificáveis por pares acadêmicos, assegurando originalidade e naturalidade do texto.

---

<div align="center">

**OpenCode Ecosystem v4.2.3** · Glossário de Termos Técnicos

</div>
