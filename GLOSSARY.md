# Glossário — OpenCode Ecosystem v4.2.1

> Definições dos termos técnicos utilizados no ecossistema. Organizado em ordem alfabética.

---

## A

### AutoEvolve

Engine de evolução autônoma do ecossistema. Executa o ciclo **PLAN → ACT → REFLECT → EXTRACT → EVOLVE**, gerando novas skills em `evolution/` a partir de padrões de sucesso identificados em ciclos anteriores. Implementado em `plugins/manus-evolve.ts`. Já completou 8 ciclos com progressão de score de 85 → 98/100.

---

## B

### big-pickle

Modelo de linguagem padrão do OpenCode Ecosystem. Também conhecido como **OpenCode Zen**. Características: 200K tokens de contexto, 128K tokens de saída, **gratuito**. Utilizado como orquestrador central de todos os agentes do ecossistema.

---

## C

### Container DI

Container central de **Injeção de Dependência** do ecossistema. Registra **11 serviços** (8 core + 3 plugins TypeScript) e oferece acesso via padrão singleton. Os 8 serviços core são: `state_manager`, `event_bus`, `agent_manager`, `plugin_manager`, `skill_manager`, `cache`, `task_queue` e `command_registry`. Os 3 plugins TS são: `plugin.manus-evolve`, `plugin.ecosystem-sync` e `plugin.bernstein-sync`.

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

**Model Context Protocol** — Protocolo criado pela Anthropic (2024) que define comunicação padronizada entre agentes de IA e servidores de contexto via **JSON-RPC**. No OpenCode Ecosystem, **40 servidores MCP** (38 locais via stdio + 2 remotos via HTTP) fornecem ferramentas, recursos e prompts ao agente orquestrador. Cada servidor opera em sessão 1:1 com o cliente MCP.

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

**OpenCode Ecosystem v4.2.1** · Glossário de Termos Técnicos

</div>
