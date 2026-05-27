# Análise Técnica Consolidada — OpenCode Ecosystem

> **Gerado por:** reversa-archaeologist  
> **Data:** 2026-05-10  
> **Nível de documentação:** detalhado  
> **Modelo:** deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out)  

---

## Sumário

1. [Visão Geral da Arquitetura](#1-visão-geral-da-arquitetura)
2. [Módulo 1: opencode-core (core/)](#2-módulo-1-opencode-core-core)
3. [Módulo 2: basis-research / SEEKER](#3-módulo-2-basis-research--seeker)
4. [Módulo 3: criador-artigo / MASWOS](#4-módulo-3-criador-artigo--maswos)
5. [Módulo 4: docling](#5-módulo-4-docling)
6. [Módulo 5: agents](#6-módulo-5-agents)
7. [Módulo 6: commands](#7-módulo-6-commands)
8. [Módulo 7: plugins](#8-módulo-7-plugins)
9. [Módulo 8: nexus](#9-módulo-8-nexus)
10. [Módulo 9: quantum](#10-módulo-9-quantum)
11. [Módulo 10: evolution](#11-módulo-10-evolution)
12. [Módulo 11: skills](#12-módulo-11-skills)
13. [Módulo 12: editais-br](#13-módulo-12-editais-br)
14. [Dicionário de Dados Central](#14-dicionário-de-dados-central)
15. [Padrões Arquiteturais Identificados](#15-padrões-arquiteturais-identificados)
16. [Alertas e Lacunas](#16-alertas-e-lacunas)

---

## 1. Visão Geral da Arquitetura

O OpenCode é um **ecossistema de agentes multi-módulo** projetado para produção de artigos científicos Qualis A1, pesquisa acadêmica automatizada e computação quântica aplicada. Composto por **12 módulos principais** totalizando **~865+ arquivos** em **Python, TypeScript e Markdown**.

### Diagrama de Contexto (C4 Nível 1)

`scii
┌─────────────────────────────────────────────────────────────┐
│                    OPENCODE ECOSYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  core/       SEEKR      MASWOS      nexus/                   │
│  Runtime  ◄─ Research ─► Articles ─► Orchest.                │
│     │           │           │           │                    │
│  plugins/   skills/    quantum/   evolution                  │
│  ManusEv.   74 skills  VQC/Penn.  8 rounds                   │
│                                                              │
│  editais-br  docling/   agents/    commands/                 │
│  Scraping    PDF ext.   Defin.     Slash                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
`

### Contagem de Componentes

| Tipo | Quantidade | Status |
|------|-----------|--------|
| MCPs | 17* | Ativos |

> *Nota do Reviewer: `opencode.json` contém 20 MCPs. Discrepância documentada no confidence-report.md (Q01).
| Skills | 74 → 76 | Em evolução |
| Agentes | 118 | Ativos |
| Plugins | 12 | Ativos |
| Comandos | 14 | Ativos |
| Corretores | 1 (ptbr_corrector.py) | Ativo |
| Evoluções | 8 rounds | Documentadas |
| Arquivos totais | ~865 | +66% desde última contagem |

---

## 2. Módulo 1: opencode-core (core/)

### Arquivos Analisados

| Arquivo | Propósito | Confiança |
|---------|-----------|-----------|
| __init__.py | Init module | 🟢 CONFIRMADO |
| config.py | Configurações centralizadas (Pydantic v2) | 🟢 CONFIRMADO |
| state.py | Gerenciamento de estado (SQLite WAL) | 🟢 CONFIRMADO |
| events.py | EventBus assíncrono | 🟢 CONFIRMADO |

### Estruturas de Dados

Config (config.py via Pydantic v2):
- ECO_ROOT: Path raiz do ecossistema
- EVOLVE_DIR: Diretório .evolve/ para estado persistente
- CACHE_DIR: Cache temporário
- scoring.*: Pesos do Dynamic Scoring Engine
- health_thresholds: Limiares de saúde (95/85/70)
- state_path(key): Factory para paths de estado

StateManager (state.py singleton):
- Padrão: Pydantic v2 Model + SQLite WAL (Write-Ahead Logging)
- state_manager: instância global singleton
- load_state(key) / save_state(key, data)
- sm.get(key) / sm.set(key, value): acesso style dict

EventBus (events.py):
- event_bus: singleton global
- Publica/assina eventos assíncronos entre componentes

### 🟡 INFERIDO

Core parece ser importado por referência nos scripts nexus, mas não há testes unitários visíveis. A arquitetura de singleton pode ser problemática para testing.

> **Nota do Reviewer:** A contagem de 17 MCPs não reflete os 20 configurados em `opencode.json`. Discrepância documentada no confidence-report.md.

---

## 3. Módulo 2: basis-research / SEEKER

### Arquivos Analisados

| Arquivo | Propósito | Confiança |
|---------|-----------|-----------|
| main.py | Entry point do pipeline SEEKER | 🟢 CONFIRMADO |
| core/llm.py | LLM Router (Claude → Ollama fallback) | 🟢 CONFIRMADO |
| core/database.py | SQLite persistence | 🟢 CONFIRMADO |
| core/argument_tree.py | Árvore de argumentação | 🟢 CONFIRMADO |
| config.json | Configuração do pipeline | 🟢 CONFIRMADO |
| requirements.txt | Dependências Python | 🟢 CONFIRMADO |

### Pipeline de 12 Agentes

1. vision — Definição de escopo da pesquisa
2. theorist — Enquadramento teórico
3. historian — Contexto histórico
4. breaks — Identificação de lacunas
5. thinker — Raciocínio aprofundado
6. grounder — Fundamentação empírica
7. synthesizer — Síntese de descobertas
8. gaper — Identificação de gaps na argumentação
9. rude — Revisão crítica adversarial
10. scribe — Redação acadêmica
11. social — Análise de impacto social
12. vision — Conclusão e direções futuras

### Algoritmos

- LLM Router: Tenta Claude primeiro; se falhar, fallback para Ollama (modelos locais)
- Argument Tree: Estrutura em árvore com claims, evidências, contra-argumentos
- Search Pipeline: 4 eixos temáticos em paralelo com fallback chain (arXiv → Sci-Hub → websearch)
- Score calibration: auto_score_qualis.py com 10 critérios Qualis A1

---

## 4. Módulo 3: criador-artigo / MASWOS

### Arquivos Analisados

| Arquivo | Propósito | Confiança |
|---------|-----------|-----------|
| executor.py | Orquestrador principal MASWOS | 🟢 CONFIRMADO |
| auto_score_qualis.py | Scoring automático Qualis A1 | 🟢 CONFIRMADO |
| seeker_bridge.py | Ponte SEEKER → MASWOS | 🟢 CONFIRMADO |
| SKILL.md | Definição de habilidade MASWOS | 🟢 CONFIRMADO |
| banca/ptbr_corrector.py | Corretor linguístico CJK+PT-BR | 🟢 CONFIRMADO |

### Arquitetura: 49 Agentes em 7 Fases

1. Planejamento: editor-chefe, dispatch, framework teórico
2. Pesquisa: busca, curadoria, citações TSAC
3. Estruturação: metodologia, estatística, visualização
4. Redação: resultados, discussão, conclusão
5. Revisão: auditoria, consistência, peer review (5 revisores)
6. Orientação: 4 advisors PhD com pesos diferenciados
7. Correção: 6 engines (travessões, proibidas, VIF, power analysis)

### Algoritmos

- auto_score_qualis.py: 10 critérios com pesos: TSAC density, referências, DOIs, anti-AI writing, formatação ABNT, escopo, metodologia, resultados, conclusão, impacto
- iterative_correction_loop.py: Board (5 revisores) → Advisors (4 PhD) → Correctors (6 engines) → Score → Repeat até ≥ 95
- ptbr_corrector.py: Scan caractere-a-caractere de 17 blocos Unicode CJK, preservação de code blocks, URLs e HTML comments; corretor ortográfico PT-BR com 50+ regras

### Métricas de Performance

| Indicador | Antes | Depois | Delta |
|-----------|-------|--------|-------|
| Board Score | 86.5 | 92.7 | +7.1% |
| auto_score | 74 | 95 | +28.4% |
| DOIs | 12 | 55 | +358% |
| Travessões | 220 | 0 | -100% |
| TSAC | 35 | 40 | +14.3% |

---

## 5. Módulo 4: docling

### Arquivos Analisados

| Arquivo | Propósito | Confiança |
|---------|-----------|-----------|
| docling/backend/pdf_backend.py | ABCs PdfPageBackend, PdfDocumentBackend | 🟢 CONFIRMADO |

### 🔴 LACUNA

Apenas classes abstratas (ABCs) foram encontradas. Implementações concretas (Docling IBM, pdfplumber, PyMuPDF) não estão neste módulo.

---

## 6. Módulo 5: agents

### Arquivos Analisados

| Arquivo | Propósito | Confiança |
|---------|-----------|-----------|
| reversa-archaeologist.md | Definição do agente Arqueólogo | 🟢 CONFIRMADO |
| Demais agentes reversa | Definições dos 9 agentes reversa | 🟡 INFERIDO |

### Agentes Reversa (9)

- reversa-scout: Mapeamento estrutural
- reversa-archaeologist: Análise profunda de código (este agente)
- reversa-detective: Arqueologia Git e regras de negócio
- reversa-architect: Diagramas C4 e ERD
- reversa-writer: Geração de specs SDD
- reversa-reviewer: Revisão cruzada de specs
- reversa-visor: Análise de interface via screenshots
- reversa-data-master: Análise de banco de dados
- reversa-design-system: Extração de tokens de design

---

## 7. Módulo 6: commands

### Arquivos Analisados

| Arquivo | Propósito | Confiança |
|---------|-----------|-----------|
| reversa.md | Slash command /reversa | 🟢 CONFIRMADO |
| evolve.md | Slash command /evolve | 🟢 CONFIRMADO |

### Fluxo de Controle

/reversa → reversa-scout → reversa-archaeologist → reversa-detective → ...
/evolve → ecosystem-sync.ts → manus-evolve.ts → nexus sync scripts

---

## 8. Módulo 7: plugins

### Arquivos Analisados

| Arquivo | Propósito | Confiança |
|---------|-----------|-----------|
| ecosystem-sync.ts | v3.5 Cross-Validation Engine | 🟢 CONFIRMADO |
| manus-evolve.ts | v2.2 Autonomous Evolution Engine | 🟢 CONFIRMADO |

### ecosystem-sync.ts v3.5

Pipeline: VALIDATE → CROSS-CHECK → CORRECT → SCORE → SYNC → EVOLVE

Interfaces TypeScript:
- ComponentHealth: name, componentType, status, score, errorCount, affinityScore
- TokenEfficiencyState: contextLanguage, outputLanguage, compressionRatio, cjkBlockCount  
- EcosystemState: version, healthScore, total/active components, crossValidationMatrix

Observabilidade: Log em .evolve/ecosystem-observability.jsonl

### manus-evolve.ts v2.2

Pipeline: PLAN → ACT → CORRECT → REFLECT → EXTRACT → EVOLVE → NEXUS

Interfaces:
- ToolMetric: toolName, callCount, successCount, errorCount
- EvolutionRound: roundNumber, generatedSkillPath, score, timestamp
- ManusState: evolutionRounds[], sessionMetrics

---

## 9. Módulo 8: nexus

### Arquivos Analisados (principais)

| Arquivo | Propósito | Confiança |
|---------|-----------|-----------|
| SKILL.md | Definição Nexus-Multiagents-v6.2 | 🟢 CONFIRMADO |
| scripts/sync_orchestrator.py | v4.0 Orquestrador de sincronia | 🟢 CONFIRMADO |
| scripts/context_offload.py | Gerenciamento de contexto offloading | 🟢 CONFIRMADO |
| scripts/ecosystem_bridge.py | Ponte entre 8 componentes | 🟢 CONFIRMADO |
| scripts/evolution_engine.py | Motor de evolução | 🟢 CONFIRMADO |
| scripts/evolution_cycle.py | Ciclo de evolução | 🟢 CONFIRMADO |
| scripts/self_healer.py | v2.1 Auto-cura | 🟢 CONFIRMADO |
| scripts/auto_swarm_builder.py | Criação de pipelines multi-agente | 🟢 CONFIRMADO |
| scripts/micro_reasoning_types.py | 38 sub-tipos de raciocínio | 🟢 CONFIRMADO |
| scripts/meta_orchestrator.py | Camada L0 de meta-coordenação | 🟢 CONFIRMADO |
| scripts/ecosystem_scanner.py | Scanner de componentes | 🟢 CONFIRMADO |
| scripts/agent_metamorphosis.py | Transformação de agentes | 🟢 CONFIRMADO |
| scripts/knowledge_graphs.py | Grafos de conhecimento | 🟢 CONFIRMADO |
| scripts/validation_suite.py | Suite de validação TMA v5.0 | 🟢 CONFIRMADO |
| scripts/mcp_router.py | Roteamento para MCPs | 🟢 CONFIRMADO |
| dashboard_server.py | Dashboard de status | 🟢 CONFIRMADO |

### Arquitetura de 6 Camadas (Nexus-v6.2)

| Camada | Nome | Função | Sync Barriers |
|--------|------|--------|---------------|
| L0 | Meta-Coordination | Orquestração global | 5 |
| L1 | Domain Discovery | Extração de conceitos | 15 |
| L2 | Autonomous Reasoning | 38 sub-tipos de raciocínio | 20 |
| L3 | MCP Organization | Auto-organização de ferramentas | 25 |
| L4 | Specialization | Adaptação de capacidades | 30 |
| L5 | Self-Healing | Monitoramento e recuperação | 40 |
| L6 | Feedback & Evolution | Meta-aprendizado | 120 feedback pts |

### Algoritmos-Chave

SyncOrchestrator:
- ComponentDiscovery: Auto-descoberta por varredura de diretórios
- DynamicScoringEngine: score = max(0, min(100, (sr * SW) + BB - (er/t * EPF) + RB))
- CrossValidationEngine: 172 regras de afinidade entre 97 componentes
- AutoHealingEngine: 4 níveis (healthy >=95, attention >=85, alert >=70, critical <70)
- ConflictDetector: Overlaps conhecidos (websearch/gh_grep, etc.)

context_offload.py:
- Gerenciamento de sessões com offloading para filesystem
- Compression automática ao exceder 50KB
- Summarization a cada 10 entries
- 60+ sessões históricas

self_healer.py:
- check_cjk_leaks(): regex [\u4e00-\u9fff]+ em SKILL.md
- fix_cjk_leaks(): Remove CJK preservando code blocks
- check_frontmatter() / fix_frontmatter(): Valida e corrige YAML

micro_reasoning_types.py:
- 38 sub-tipos em 8 categorias: Deductive (8), Inductive (6), Causal (5), Counterfactual (4), Bayesian (5), Analogical (4), Formal (3), Abductive (3)

---

## 10. Módulo 9: quantum

### Arquivos Analisados

| Arquivo | Propósito | Confiança |
|---------|-----------|-----------|
| quantum_vqc.py | VQC PennyLane (50 qubits, 6 layers, ZNE+PEC) | 🟢 CONFIRMADO |
| frontend/* | React Dashboard + ImageAnalysis + WebSocket | 🟡 INFERIDO |

### Algoritmo Quântico (quantum_vqc.py)

- n_qubits = 50, n_layers = 6
- ansatz: hardware-efficient (PennyLane)
- ZNE: noise_factors = [1, 3, 5], extrapolação linear
- PEC: n_samples = 100, noise_model = depolarizing
- Encoder: amplitude encoding
- Simulador: default.qubit

### Frontend React

Componentes: App, AdminDashboard, Home, ImageAnalysis
Hooks: useQMLAnalysis, useWebSocket
Componentes UI: FeedbackCorrection, GradCAMModal, RetrainingProgress

---

## 11. Módulo 10: evolution

### Arquivos Analisados

| Arquivo | Round | Score | Confiança |
|---------|-------|-------|-----------|
| evo-1-armadilha-renda-media.md | 1 | 85 | 🟢 CONFIRMADO |
| evo-2-artigo-35-paginas.md | 2 | 90 | 🟢 CONFIRMADO |
| evo-3-tsac-citation-system.md | 3 | 95 | 🟢 CONFIRMADO |
| evo-4-scihub-pipeline.md | 3 | 88 | 🟢 CONFIRMADO |
| evo-5-cross-validation-engine.md | 3 | 92 | 🟢 CONFIRMADO |
| evo-6-iterative-correction-mastery.md | 4 | 95 | 🟢 CONFIRMADO |
| evo-7-sync-v3.5.md | 5 | 96 | 🟢 CONFIRMADO |
| evo-8-progressive-disclosure-and-observability.md | 8 | 98 | 🟢 CONFIRMADO |

### Evolução dos Scores: 85 → 90 → 95 → 88 → 92 → 95 → 96 → 98

### Padrões Extraídos (cross-round)

1. Token Efficiency: contexto chinês + saída PT-BR = economia de ~40%
2. Progressive Disclosure: SKILL.md magro (<2.5kt) com referências sob demanda
3. Iterative Correction: Board (5 revisores) → Advisors (4 PhD) → Correctors (6 engines)
4. Cross-Validation: Pearson com n<10 requer interpretação por Cohen, não significância
5. Fallback Chains: scihub → arXiv → websearch → manual
6. Known Overlaps: documentar redundâncias intencionais
7. Atomic Skills: cada skill = exatamente um domínio
8. Observabilidade: health checks por ferramenta com tracking de latência

---

## 12. Módulo 11: skills

### Estrutura de Diretórios

`
skills/
├── content/           image-service.md, video-creator.md, video-stickfigure.md
│                      video-subtitle-remover.md, story-to-scenes.md
├── docling-pdf-extraction/   SKILL.md, scripts/docling_skill.py
├── evolution/         agent-observability-monitor.md, progressive-disclosure-design.md
├── frontend/          frontend-philosophy/ (SKILL.md, the-5-pillars.md, adherence-checklist.md)
└── system/            code-philosophy/, code-review/, reasoning-orchestrator/, token-efficiency/
`

### Categorias: 12 categorias, 13 confirmações em skills/

Skills de Sistema identificadas:
- code-philosophy: 5 Leis da Defesa Elegante
- code-review: Metodologia com classificação de gravidade
- reasoning-orchestrator: Nexus v6.0, 58 tipos de raciocínio
- token-efficiency: Otimização chinês + PT-BR + deepseek-v4-pro

---

## 13. Módulo 12: editais-br

### Arquitetura

Projeto Python independente em C:\Users\marce\editais-local\:

- API: FastAPI com SQLAlchemy + migrations Alembic
- Workers: Celery para tarefas assíncronas
- Extractors: HTML, PDF, PDF→Markdown
- Pipeline: Orchestrator + Deduplicator
- Frontend: Templates HTML server-side (dashboard, buscar, detalhes)
- Tests: Unitários (pytest) e integração
- Docker: Dockerfile + docker-compose.yml + nginx.conf

### Funcionalidades

- Busca inteligente: duckduckgo via curl.exe (httpx bloqueado por CAPTCHA)
- Classificação granular: 25 sub-dimensões com scoring por perfil
- 52 editais curados: 16 FAPs estaduais, 4 exterior, 4 setoriais, 27 UFs
- Extração profunda: contrapartida, prazos, documentos
- Cache versionado: CACHE_VERSION para invalidação controlada

### 🟡 INFERIDO

Diretório externo ao workspace — análise baseada em estrutura e SKILL.md.

---

## 14. Dicionário de Dados Central

### Core State (core/state.py)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| key | str | Sim | Chave do estado |
| value | JSON | Sim | Valor serializado |
| timestamp | datetime | Auto | Momento da persistência |

### SyncOrchestrator

| Classe | Campo | Tipo | Descrição |
|--------|-------|------|-----------|
| SyncComponent | name | str | Nome do componente |
| | component_type | str | agent/skill/plugin/command/mcp |
| | status | str | active/degraded/offline/unknown |
| | score | int | 0-100 |
| | affinity_score | float | 0.0-1.0 |
| DynamicScore | usage_count | int | Total de usos |
| | success_count | int | Total de sucessos |
| | error_count | int | Total de erros |
| | computed_score | float | 0-100 calculado |
| SyncState | health_score | float | 0-100 saúde geral |
| | total_components | int | Total de componentes |
| | active_components | int | Componentes ativos |

### ContextOffload

| Classe | Campo | Tipo | Descrição |
|--------|-------|------|-----------|
| ContextEntry | entry_id | str | Hash MD5 (12 chars) |
| | session_id | str | ID da sessão |
| | content | str | Conteúdo textual |
| | content_type | str | text/intermediate_result/summary/metadata |
| | priority | int | 0-10 |
| SessionState | entry_count | int | Total de entradas |
| | total_size | int | Bytes totais |
| | behavioral_fingerprint | dict | Fingerprint de comportamento |

### MicroReasoningTypes

| Campo | Tipo | Descrição |
|-------|------|-----------|
| name | str | Nome do tipo de raciocínio |
| category | ReasoningCategory | 8 categorias (enum) |
| description | str | Descrição textual |
| formula | str | Representação formal |
| complexity | float | 0.0-1.0 |
| confidence | float | 0.0-1.0 |

### AgentGenome

| Campo | Tipo | Descrição |
|-------|------|-----------|
| agent_id | str | ID único |
| role | AgentRole | A1-A8 (enum) |
| generation | int | Geração evolutiva |
| fitness_score | float | 0.0-1.0 |
| mutation_count | int | Total de mutações |

### MCPServer

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | str | ID único |
| name | str | Nome do servidor MCP |
| capabilities | list[MCPCapability] | Capacidades suportadas |
| health_score | float | 0.0-1.0 |

### Ecosystem Config

| Chave | Tipo | Localização | Descrição |
|-------|------|-------------|-----------|
| mcp | dict | opencode.json | Config dos 17 MCPs |
| scoring.* | float | core.config | Pesos Dynamic Scoring |
| health_thresholds | dict | core.config | Limiares de saúde |
| eco_root | Path | core.config | C:\Users\marce\.config\opencode |

---

## 15. Padrões Arquiteturais Identificados

### 15.1 Production-Grade Framework (core/)
Pydantic v2 + SQLite WAL + EventBus async + Singleton Pattern

### 15.2 Multi-Agent Pipeline (SEEKER + MASWOS)
12+49 agentes, LLM Router Claude→Ollama, TSAC Citations, Iterative Correction

### 15.3 Cross-Validation Engine (ecosystem-sync.ts + sync_orchestrator.py)
97 componentes, 172 regras de afinidade, Dynamic Scoring, AutoHealing 4 níveis

### 15.4 Context Offloading (context_offload.py)
Filesystem-based, compressão automática, summarization, 60+ sessões

### 15.5 Token Efficiency Architecture
Contexto chinês (+40% densidade) + saída PT-BR + headers padronizados + Progressive Disclosure

### 15.6 Autonomous Evolution (manus-evolve.ts + evolution/)
PLAN→ACT→CORRECT→REFLECT→EXTRACT→EVOLVE→NEXUS, 8 rounds, geração automática de skills

### 15.7 Quantum-Classical Hybrid (quantum/)
50 qubits VQC, ZNE+PEC, React Dashboard, Grad-CAM, WebSocket streaming

---

## 16. Alertas e Lacunas

### 🔴 Críticos

| ID | Descrição | Módulo |
|----|-----------|--------|
| LACUNA-1 | Implementação concreta docling não encontrada (apenas ABCs) | docling/ |
| LACUNA-2 | nexus/scripts/pdf_rag/ parcialmente analisado | nexus/ |
| LACUNA-3 | Editais-br em diretório externo ao workspace | editais-br |

### 🟡 Atenção

| ID | Descrição | Módulo |
|----|-----------|--------|
| ALERTA-1 | Arquivos binários/gzip sem documentação em context_offload/ | nexus/ |
| ALERTA-2 | 118 agentes declarados mas ~50 confirmados | agents/ |
| ALERTA-3 | Possível dependência circular core↔nexus | core/ |
| ALERTA-4 | Singletons globais dificultam testes | core/ |
| ALERTA-5 | 74 skills vs ~13 em skills/ | skills/ |
| ALERTA-6 | validation_suite.py parece simulado | nexus/ |

### 🟢 Confirmado (Boas Práticas)

| ID | Descrição |
|----|-----------|
| BOA-1 | Headers padronizados em 210 arquivos |
| BOA-2 | Dynamic Scoring com persistência e lazy compute |
| BOA-3 | Known Overlaps documentados sem penalidade |
| BOA-4 | Progressive Disclosure seguindo padrões indústria |
| BOA-5 | Fallback chains robustas (LLM, busca, MCPs) |
| BOA-6 | Mitigação dupla de erros quânticos (ZNE + PEC) |
| BOA-7 | Corretor CJK com preservação de code blocks |
| BOA-8 | 8 rounds de evolução documentados com métricas |

---

*Documento gerado automaticamente pelo reversa-archaeologist — Fase de Escavação do pipeline de engenharia reversa OpenCode.*
