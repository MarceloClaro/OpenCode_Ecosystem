# Documentação Completa do Ecossistema OpenCode

> **Versão:** 3.5 | **Ciclo:** 8 | **Modelo:** deepseek-v4-pro (OpenCode Zen)
> **Atualizado em:** 2026-05-09

---

## Sumário

1. [Visão Geral da Arquitetura](#1-visao-geral-da-arquitetura)
2. [Camadas do Ecossistema](#2-camadas-do-ecossistema)
3. [Skills (Habilidades)](#3-skills-habilidades)
4. [Agentes SEEKER (Pesquisa Acadêmica)](#4-agentes-seeker)
5. [Criador de Artigo v2 (MASWOS)](#5-criador-de-artigo-v2)
6. [Quantum Nexus PhD](#6-quantum-nexus-phd)
7. [Plugins OpenCode](#7-plugins-opencode)
8. [Nexus Multi-Agentes v6.2](#8-nexus-multi-agentes-v62)
9. [Pipelines de Evolução e Auto-Cura](#9-pipelines-de-evolucao)
10. [MCPs (Model Context Protocols)](#10-mcps)
11. [editais-br — Busca Inteligente de Fomento](#11-editais-br)
12. [Comandos Rápidos](#12-comandos-rapidos)
13. [Métricas do Ecossistema](#13-metricas-do-ecossistema)

---

## 1. Visão Geral da Arquitetura

O ecossistema OpenCode é um **sistema operacional de agentes autônomos** organizado em camadas, projetado para pesquisa acadêmica, desenvolvimento de software agentic, computação quântica, e produção científica Qualis A1.

### Princípios Fundamentais

| Princípio | Descrição |
|-----------|-----------|
| **Token Efficiency** | Contexto em chinês (densidade +40%), saída em PT-BR formal obrigatória |
| **Evolução Autônoma** | Ciclos scan → heal → learn → evolve sem intervenção humana |
| **Cross-Validation** | Matriz de afinidade entre 172 conexões entre componentes |
| **Zero CJK na saída** | Correção linguística obrigatória via ptbr_corrector.py |
| **Auto-Cura** | Detecção e correção automática de anomalias no ecossistema |

### Diagrama de Arquitetura

```
┌──────────────────────────────────────────────────────────────┐
│                      INTERFACE (CLI / Plugin)                │
├──────────────────────────────────────────────────────────────┤
│                    ORQUESTRAÇÃO (Nexus L0-L6)                │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│  SEEKER  │ CRIADOR  │ QUANTUM  │ EDI-TAIS │   AUDITORIA     │
│ (10 ag.) │ (49 ag.) │ (26 sc.) │(3 scripts)│  (evals/tests) │
├──────────┴──────────┴──────────┴──────────┴─────────────────┤
│                    PLUGINS (manus-evolve, ecosystem-sync)    │
├──────────────────────────────────────────────────────────────┤
│                    MCPs (17 conectores)                      │
├──────────────────────────────────────────────────────────────┤
│              EVOLUÇÃO AUTO-CURA (scanner + healer + engine)  │
└──────────────────────────────────────────────────────────────┘
```

### Fluxo de Dados Principal

```
Usuário → Comando → Plugin → Agente → MCP → Dados → Resultado
                                  ↓
                           Nexus Validation (120+ barriers)
                                  ↓
                           Feedback → Evolution → Learning
```

---

## 2. Camadas do Ecossistema

### 2.1 Camada 0 — Meta-Coordenação (Nexus L0)
Gerencia sessão, permissões e alinhamento de objetivos globais.
- 5 barreiras de sincronização
- Mandato de Auditoria Científica Qualis A1

### 2.2 Camada 1 — Domain Discovery (Nexus L1)
Extrai conceitos e gerencia conhecimento.
- 15 barreiras de sincronização
- Skill Registry, Context Compressor

### 2.3 Camada 2 — Autonomous Reasoning (Nexus L2)
Seleciona entre 38 sub-tipos de raciocínio granular.
- 20 barreiras de sincronização

### 2.4 Camada 3 — MCP Organization (Nexus L3)
Auto-organização de ferramentas e coordenação multiagente.
- 25 barreiras de sincronização
- Subagent Spawner, FSM Protocol, Worktree Isolator

### 2.5 Camada 4 — Specialization (Nexus L4)
Adaptação de capacidades emergentes.
- 30 barreiras de sincronização

### 2.6 Camada 5 — Self-Healing (Nexus L5)
Monitoramento e recuperação automática.
- 40 barreiras de sincronização
- Event Bus, Background Executor

### 2.7 Camada 6 — Feedback & Evolution (Nexus L6)
Meta-aprendizado e otimização contínua.
- 120 feedback points
- Protocolo de Simulação de Banca Examinadora

### 2.8 Pipeline de Token Efficiency

```
Contexto (chinês) → Processamento → ptbr_corrector.py → PT-BR Formal
   ↑ 40% densidade                    ↓
   └─────────────── CJK Zero Tolerance
```

---

## 3. Skills (Habilidades)

### 3.1 Lista Completa (9 skills)

| Skill | Arquivo | Tamanho | Descrição |
|-------|---------|---------|-----------|
| **editais-br** | `skills/research/editais-br/SKILL.md` | 2.5KB | Busca inteligente de editais de fomento no Brasil |
| **docling-pdf-extraction** | `skills/docling-pdf-extraction/SKILL.md` | 2.5KB | Extração avançada de PDFs via Docling (IBM) |
| **code-philosophy** | `skills/system/code-philosophy/SKILL.md` | 618B | 5 Leis da Defesa Elegante |
| **code-review** | `skills/system/code-review/SKILL.md` | 1.3KB | Metodologia de revisão de código |
| **plan-protocol** | `skills/workflows/plan-protocol/SKILL.md` | 1.5KB | Criação de planos de implementação |
| **plan-review** | `skills/system/plan-review/SKILL.md` | 1.2KB | Critérios de revisão de planos |
| **reasoning-orchestrator** | `skills/system/reasoning-orchestrator/SKILL.md` | 2.0KB | Orquestração de 58 tipos de raciocínio |
| **token-efficiency** | `skills/system/token-efficiency/SKILL.md` | 1.0KB | Otimização de tokens (chinês + PT-BR) |
| **frontend-philosophy** | `skills/frontend/frontend-philosophy/SKILL.md` | 639B | 5 Pilares da UI Intencional |

### 3.2 editais-br (Busca de Fomento)

**Scripts associados:**
- `scripts/edital_search.py` — Motor principal: busca web (DuckDuckGo), curadoria 52 editais, scoring 0-100, cache versionado v7.1, feedback SQLite, servidor HTTP
- `scripts/extracao_profunda.py` — Extração de PDF: pdfplumber (rápido) + docling OCR (fallback)
- `scripts/buscar_editais.py` — Busca via DuckDuckGo com parsing HTML

**Comandos:**
```bash
python scripts/edital_search.py "ia saude" --tipo pesquisa
python scripts/edital_search.py --servidor --porta 8080
python scripts/edital_search.py --feedback 1 "http://..." 1
python scripts/extracao_profunda.py edital.pdf
```

### 3.3 docling-pdf-extraction

**Propósito:** Extração avançada de documentos via IBM Docling.
- Suporte a PDFs complexos com tabelas, figuras e layouts
- OCR para documentos escaneados
- Exportação em múltiplos formatos

### 3.4 skills de Sistema

| Skill | Propósito |
|-------|-----------|
| **code-philosophy** | Filosofia de lógica interna: 5 Leis da Defesa Elegante (defesa em profundidade, responsabilidade única, efeitos colaterais visíveis, imutabilidade visível, tolerância a falhas explícita) |
| **code-review** | Metodologia abrangente com classificação de gravidade (P1-P3) e limites de confiança |
| **plan-protocol** | Protocolo de planos com citações, versões e rastreabilidade |
| **plan-review** | Critérios para revisão de planos (completude, viabilidade, riscos) |
| **reasoning-orchestrator** | Meta-orquestração de 58 tipos de raciocínio, profundidade L1-L4, matriz de interseção |
| **token-efficiency** | Regras de compressão: chinês para contexto, PT-BR para saída, deepseek-v4-pro |
| **frontend-philosophy** | 5 Pilares da UI Intencional: hierarquia visual, consistência, feedback, acessibilidade, performance |

---

## 4. Agentes SEEKER

### 4.1 Pipeline de Pesquisa (10 agentes)

```
Concept Mapper → Break 0 (confirmação de temas)
  → Grounder (decompõe problema → busca → árvore de argumentos)
  → Social (contemporâneo + pontes → estende árvore)
  → Historian (audita árvore → busca histórica → fatores externos)
  → Gaper (mapeamento estrutural + analítico de lacunas)
  → Break 1 (revisão de fundamentos e lacunas)
  → Vision (implicações lógicas)
  → Theorist (propostas de pesquisa)
  → Rude (avaliação de viabilidade — adversarial)
  → Synthesizer (narrativa de pesquisa)
  → Break 2 (definição de trajetória)
  → Thinker (novas direções)
  → Scribe (mapa de entendimento + outputs)
```

### 4.2 Agentes Implementados

| Agente | Arquivo | Linhas | Funções | Propósito |
|--------|---------|--------|---------|-----------|
| **grounder** | `agents/grounder.py` | 837 | 9 | Decompõe problema, busca fontes, constrói árvore |
| **social** | `agents/social.py` | 1245 | 8 | Fontes contemporâneas, pontes, coleta passiva |
| **historian** | `agents/historian.py` | 325 | 3 | Auditoria histórica, fatores externos |
| **gaper** | `agents/gaper.py` | 629 | 6 | Mapeamento de lacunas na árvore |
| **vision** | `agents/vision.py` | 202 | 3 | Implicações lógicas e cenários |
| **theorist** | `agents/theorist.py` | 237 | 3 | Propostas de pesquisa |
| **rude** | `agents/rude.py` | 154 | 2 | Adversário de viabilidade |
| **synthesizer** | `agents/synthesizer.py` | 204 | 2 | Narrativa de pesquisa |
| **thinker** | `agents/thinker.py` | 170 | 2 | Novas direções |
| **scribe** | `agents/scribe.py` | 570 | 5 | Mapa de entendimento + outputs |
| **breaks** | `agents/breaks.py` | 409 | 11 | Pontos de decisão do pesquisador |

### 4.3 Core Modules

| Módulo | Linhas | Funções | Propósito |
|--------|--------|---------|-----------|
| `core/argument_tree.py` | 673 | 1 | Árvore de argumentos persistente |
| `core/concept_mapper.py` | 813 | 12 | Expansão de conceitos |
| `core/database.py` | 586 | 32 | SQLite + operações de banco |
| `core/context.py` | 360 | 17 | Contexto para cada agente |
| `core/references.py` | 611 | 26 | Gerenciamento de referências |
| `core/consensus_mcp.py` | 459 | 3 | Consenso entre agentes |
| `core/llm.py` | 321 | 2 | Integração LLM |
| `core/keys.py` | 138 | 15 | Gerenciamento de chaves/.env |
| `core/rate_limiter.py` | 217 | 2 | Rate limiting de chamadas |

### 4.4 Comandos SEEKER

```bash
python main.py run --problem "Seu problema de pesquisa"
python main.py run --problem "..." --run-id RUN-20260509-XXXX
python main.py collect
python main.py recheck
python main.py status --run-id RUN-20260509-XXXX
python main.py bank
```

### 4.5 editais_hook — Ponte Nativa SEEKER ↔ editais-br

```python
from tools.editais_hook import buscar_editais, extrair_edital, classificar_edital

resultados = buscar_editais("ia saude", tipo="pesquisa", perfil="pesquisador")
extracao = extrair_edital("edital.pdf")
classificacao = classificar_edital("Chamada Universal CNPq")
```

---

## 5. Criador de Artigo v2 (MASWOS)

### 5.1 Arquitetura

**Multi-Agent Scientific Writing Operating System (MASWOS V4.2)**
45+ agentes especializados, 110+ páginas, Qualis A1.

```
Agentes 00-44 → Dispatcher → Handoff → Template → Banca
                                              ↓
                                     auto_score_qualis.py
                                              ↓
                                    ptbr_corrector.py (CJK)
                                              ↓
                                       LaTeX / PDF / DOCX
```

### 5.2 Agentes de Escrita (44 especialistas + 1 scheduler)

| Faixa | Agentes | Especialidade |
|-------|---------|---------------|
| 00 | Editor-Chefe PhD | Coordenação editorial |
| 01-04 | Diagnóstico, Busca, Evidências, Estrutura | Fundação |
| 05-10 | Literatura, Metodologia, Estatística, Visualização, Resultados, Discussão | Corpo |
| 11-16 | Conclusão, Bibliografia, QA, Consistência, Resumo, Integração | Revisão |
| 17-22 | Framework, Dados, Auditoria, Estatística Avançada, Matemática, ML/DL | Técnico |
| 23-28 | Bioinfo, Quimioinfo, Ciências Sociais, Visão Computacional, Computação Quântica, Benchmarking | Especializado |
| 29-34 | Conformidade, Tradução, Peer Review, Ética, Multi-Norma, Similaridade | Qualidade |
| 35-38 | Coleta Dados, LaTeX/PDF, Slides, Entrega Final | Produção |
| 39-44 | Multi-Paradigma, Marcos Teóricos, GIS, Desenvolvedor, Bioinfo Satélite, Correção | Avançado |

### 5.3 Pontuação Qualis A1

```bash
python auto_score_qualis.py output/artigo.md          # Avaliação completa
python auto_score_qualis.py output/artigo.md --score  # Apenas pontuação
```

### 5.4 Correção Linguística

```bash
python banca/ptbr_corrector.py output/artigo.md       # Remove CJK + PT-BR
```

---

## 6. Quantum Nexus PhD

### 6.1 Capacidades

| Área | Descrição | Status |
|------|-----------|--------|
| **QML Médico** | HAM10000 (89.52% acurácia), 50 qubits MPS | Validado |
| **Error Mitigation** | ZNE, PEC, Dynamical Decoupling | Híbrido |
| **Grad-CAM** | Interpretabilidade em imagens médicas | Implementado |
| **Validação** | Testes estatísticos, bootstrap, robustez | Avançada |
| **Artigos Qualis A1** | 30+ referências, formatação acadêmica | Template |

### 6.2 Scripts (26 arquivos)

```
quantum/scripts/
├── quantum_nexus_maestro.py     — Orquestrador principal
├── quantum_master_controller.py  — Controle global
├── qml_medical:
│   ├── ham10000_integration.py   — Dataset real HAM10000
│   ├── quantum_classifier.py     — Classificador quântico
│   └── generate_professional_grad_cam.py
├── error_mitigation:
│   ├── zne_qiskit_implementation.py
│   ├── pec_pennylane_implementation.py
│   ├── hybrid_zne_pec.py
│   └── qubit_stabilization.py
├── validation:
│   ├── advanced_validation.py
│   ├── qml_scientific_benchmarking.py
│   └── quantum_unit_tests.py
├── infrastructure:
│   ├── vqc_50qubits_training.py
│   ├── quantum_processor.rs      — Rust
│   ├── quantum_embeddings.py
│   └── quantum_applications.py
├── research:
│   ├── academic_search.py        — Busca acadêmica
│   ├── scihub_downloader.py      — Sci-Hub
│   └── phd_forensic_auditor.py   — Auditoria
└── utils:
    ├── main_menu.py
    ├── learning_roadmap.py
    └── benchmarking.py
```

### 6.3 Comandos

```bash
# Pesquisa completa
python scripts/quantum_nexus_maestro.py --mode full-research --domain medical-imaging

# QML médico
python scripts/quantum_nexus_maestro.py --mode qml-medical --dataset HAM10000

# Estabilização
python scripts/qubit_stabilization.py --mode hybrid --circuit vqc_50qubits

# Validação
python scripts/advanced_validation.py --mode full-validation --model qml-50qubits
```

---

## 7. Plugins OpenCode

### 7.1 ecosystem-sync (v3.5) — 473 linhas

**Propósito:** Sincronização unificada entre todos os componentes do ecossistema.

**Capacidades:**
- Validação cruzada entre MCPs, Skills, Agentes, Plugins, Corretores
- Matriz de afinidade (172 conexões)
- Estado de saúde por componente (active/degraded/offline)
- Roteamento de pipeline (full, seeker-only, etc.)

**Pipeline interno:**
```
VALIDATE → CROSS-CHECK → CORRECT → SCORE → SYNC → EVOLVE
```

**Health Report:** Gera `.evolve/health-report.json` com breakdown por categoria.

### 7.2 manus-evolve (v2.1) — 387 linhas

**Propósito:** Motor de evolução autônoma PlanAct com pipeline Nexus integrado.

**Pipeline:**
```
PLAN → ACT → CORRECT → REFLECT → EXTRACT → EVOLVE → NEXUS
                                           ↑
                                   scan → heal → learn
```

**Capacidades:**
- Rastreamento de padrões de ferramentas (tool usage)
- Geração automática de skills em `evolution/`
- Correção CJK + PT-BR tracking
- Token efficiency tracking
- **Novo v2.1:** Pipeline Nexus completo (scanner → healer → evolution engine)
- Score de evolução por round
- Auto-approve para ferramentas confiáveis (≥3 usos)

**State files:** `.evolve/manus-state.json`

**Env vars expostas:**
```
MANUS_ROUND, MANUS_SCORE, MANUS_SKILLS, MANUS_VERSION
MANUS_CORRECTION_PATTERNS, MANUS_TOKEN_PATTERNS
MANUS_HEALTH, MANUS_TOOL_CALLS, MANUS_TOOL_ERRORS, MANUS_ERROR_RATE
MANUS_NEXUS_REPORTS, MANUS_LAST_NEXUS
```

---

## 8. Nexus Multi-Agentes v6.2

### 8.1 Scripts do Core (44 arquivos)

```
nexus/scripts/
├── ecossistema:
│   ├── ecosystem_scanner.py      — Scanner autônomo, manifesto JSON, diff, histórico
│   ├── evolution_engine.py        — Análise de tendências, sugestões, projeção de health
│   └── self_healer.py             — Auto-cura: CJK, frontmatter, oversize, syntax check
├── meta-orquestração:
│   ├── meta_orchestrator.py      — Orquestrador de camadas L0-L6
│   ├── meta_learning_engine.py   — Meta-aprendizado entre ciclos
│   ├── autonomous_reasoning_framework.py
│   └── micro_reasoning_types.py  — 204 tipos de raciocínio (25 categorias)
├── sincronização:
│   ├── micro_sync_barriers.py    — 120+ barreiras
│   ├── micro_validation.py       — 500+ constraints
│   ├── micro_feedback_loop.py    — 120 feedback points
│   └── git_sync_barrier.py      — Integração git
├── MCP:
│   ├── mcp_router.py            — Roteamento de MCPs
│   ├── mcp_real_adapters.py     — Adaptadores reais
│   ├── mcp_self_organization.py — Auto-organização
│   └── aop_service_discovery.py — Descoberta AOP
├── agentes:
│   ├── agent_metamorphosis.py   — Metamorfose de agentes
│   ├── auto_swarm_builder.py    — Swarm automático
│   └── domain_discovery_engine.py
├── integração:
│   ├── ecosystem_bridge.py      — Ponte ecossistema
│   ├── nexus_integration.py     — Integração Nexus
│   ├── manus_evolve_bridge.py   — Ponte Manus Evolve
│   └── granular_sync.py         — Sincronização granular
├── PDF/contexto:
│   ├── pdf_context_offload.py   — Offload de contexto PDF
│   ├── pdf_ecosystem_integration.py
│   └── context_offload.py
└── testes:
    ├── validation_suite.py      — Suíte de validação
    ├── test_ecosystem_full.py   — Teste completo
    └── test_module_coverage.py  — Cobertura de módulos
```

### 8.2 Comandos Nexus

```bash
# Scanner
python nexus/scripts/ecosystem_scanner.py --scan
python nexus/scripts/ecosystem_scanner.py --report  # Gera relatório markdown
python nexus/scripts/ecosystem_scanner.py --diff cache/ecosystem_manifest.json

# Evolution Engine
python nexus/scripts/evolution_engine.py --analyze   # Análise completa
python nexus/scripts/evolution_engine.py --learn     # Aprende com estado atual
python nexus/scripts/evolution_engine.py --suggest   # Sugestões de melhoria
python nexus/scripts/evolution_engine.py --report    # Relatório markdown

# Self-Healer
python nexus/scripts/self_healer.py --check          # Varre anomalias
python nexus/scripts/self_healer.py --fix            # Corrige automático
python nexus/scripts/self_healer.py --auto           # Check + Fix integrado

# Dashboard
python nexus/dashboard_server.py                     # http://localhost:8081
python nexus/dashboard_server.py --porta 9090
python nexus/dashboard_server.py --gerar-only        # HTML estático

# Outros
python nexus/scripts/micro_validation.py --barrier SB1.1 --data output.json
python nexus/scripts/micro_reasoning_types.py --list
```

---

## 9. Pipelines de Evolução e Auto-Cura

### 9.1 Pipeline Nexus (v3.0)

```
Ecosystem Scanner ──→ Self-Healer ──→ Evolution Engine
      ↓                    ↓                  ↓
  Manifest JSON      Anomalias fixadas   Conhecimento acumulado
      ↓                    ↓                  ↓
  └──────────────────────┴──────────────────┘
                      ↓
          Manus-Evolve (session.idle)
                      ↓
           Próximo ciclo evolutivo
```

### 9.2 Scanner (ecosystem_scanner.py)

**Funcionalidades:**
- Descoberta automática de skills (`rglob("SKILL.md")` — encontra 9)
- Varredura de scripts Python (128 arquivos, 42.746 linhas)
- Detecção de imports via `_parse_imports()` linha-por-linha
- Análise de health (frontmatter, CJK, tamanho)
- Histórico de snapshots em `cache/ecosystem_history.json`
- Recomendações de expansão inteligentes
- Modo `--diff` para comparação entre snapshots

### 9.3 Auto-Cura (self_healer.py v2.0)

**Otimizações:**
- **Cache de syntax check** — MD5 hash, apenas arquivos modificados são verificados
- **ThreadPoolExecutor** — 4 workers paralelos
- **Timeout** — 10s por arquivo, evita travamento

**Anomalias detectadas:**
| Tipo | Descrição | Correção |
|------|-----------|----------|
| CJK Leaks | Caracteres chineses em SKILL.md | Remoção automática |
| Frontmatter Ausente | Sem YAML `---` | Inserção automática |
| Oversize | SKILL.md > 2.5KB | Alerta (correção manual) |
| Syntax Error | Erro de compilação Python | Alerta (correção manual) |

### 9.4 Evolution Engine (evolution_engine.py)

**Capacidades:**
- Análise de tendências entre ciclos (melhoria/regressão)
- Detecção de padrões de sucesso e falha
- Sugestões priorizadas (alta/média/baixa)
- Projeção de health score futuro
- Conhecimento acumulado em `cache/evolution_knowledge.json`

### 9.5 Dashboard (dashboard_server.py)

**Endpoints:**
| Rota | Descrição |
|------|-----------|
| `GET /` | Dashboard HTML interativo |
| `GET /api/dados` | JSON com todos os dados do ecossistema |
| `GET /api/scan` | Executa scan e retorna resultado |

**Dados expostos:**
- Stats cards (skills, scripts, plugins, agentes, linhas, anomalias)
- Rounds de evolução (Manus Evolve)
- Relatórios Nexus (scan → heal → learn)
- Histórico de snapshots com barras de tendência
- Recomendações do scanner
- Status do Manus Evolve

---

## 10. MCPs (Model Context Protocols)

### 10.1 Lista Completa (17 ativos)

| Função | MCP | Tipo |
|--------|-----|------|
| **Web Search** | websearch (DuckDuckGo) | Nuvem |
| **Navegador** | playwright, chrome-devtools | Local |
| **Código** | eslint, diff, code-runner | Local |
| **Dados** | sqlite, fetch, pdf, time | Local |
| **Raciocínio** | sequential-thinking, memory | Local |
| **GitHub** | github | Nuvem |
| **Infraestrutura** | filesystem | Local |
| **Pesquisa Acadêmica** | scihub (DOI/title/keyword) | Nuvem |
| **Documentação** | context7 (resolve/query) | Nuvem |
| **Código Exemplo** | gh_grep (searchGitHub) | Nuvem |
| **Supermemory** | memory (persistente) | Local |

### 10.2 Matriz de Afinidade (Top 7)

| Conexão | Afinidade |
|---------|-----------|
| scihub ↔ Criador de Artigo | 0.95 |
| sequential-thinking ↔ code-reviewer | 0.90 |
| code-runner ↔ Quantum Nexus | 0.90 |
| editais-br ↔ websearch | 0.90 |
| academic_search ↔ SEEKER-grounder | 0.85 |
| editais-br ↔ docling-pdf-extraction | 0.85 |
| websearch ↔ SEEKER-searcher | 0.85 |

---

## 11. editais-br — Busca Inteligente de Fomento

### 11.1 Fontes de Dados

| Fonte | Método | Status |
|-------|--------|--------|
| **Curadoria** | 52 editais manuais (CNPq/CAPES/FINEP/FAPs) | Ativo |
| **DuckDuckGo** | curl.exe + Firefox UA (CAPTCHA ~50%) | Parcial |
| **Finep** | Scraping direto | Ativo |
| **BNDES Open Data** | CKAN API (`dadosabertos.bndes.gov.br`) | Ativo |
| **Portais gov.br** | CNPq (404), CAPES (404) | Bloqueado |

### 11.2 Sistema de Scoring (0-100)

| Dimensão | Peso | Descrição |
|----------|------|-----------|
| Query relevance | 0-30 | Correspondência dos termos de busca |
| Área | 0-20 | Match com 12 áreas (ia, saude, biotec, etc.) |
| Perfil | 0-15 | Match com perfil do usuário |
| Mecanismo | 0-10 | Match com tipo de fomento |
| Fonte | 0-10 | Confiabilidade da fonte (curadoria > web) |
| Recência | 0-10 | Data de publicação |
| Feedback | 0-5 | Ajuste por feedback do usuário |

### 11.3 12 Áreas de Classificação

`ia`, `saude`, `biotec`, `energia`, `agro`, `educacao`, `social`, `cultura`, `tech`, `engenharia`, `ambiente`, `ciencia_pura`

### 11.4 25 Dimensões de Classificação

Inclui áreas, perfis (programa_pos, microempresa, ict, osc) e mecanismos (bolsa, subvencao, premio, credito, incentivo_fiscal)

---

## 12. Comandos Rápidos

| Comando | Função |
|---------|--------|
| `/evolve` | autoevolve + ecosystem-sync → descobre e instala |
| `/reversa` | reversa-* agents + filesystem + diff + github |
| `/plan` | writing-plans + sequential-thinking |
| `/auto` | openagent + todos MCPs |
| `/quantum` | quantum-nexus-phd + code-runner + pdf + sequential-thinking |
| `/artigo` | SEEKER + Criador de Artigo + manus-evolve → Qualis A1 |

---

## 13. Métricas do Ecossistema

### 13.1 Componentes Totais

| Componente | Quantidade |
|------------|-----------|
| Skills | 9 |
| Scripts Python | 128 (42.746 linhas) |
| Plugins TypeScript | 2 (860 linhas) |
| Agentes SEEKER | 10 agentes + 14 módulos core |
| Agentes Criador | 45+ agentes |
| Scripts Quantum | 26 |
| Scripts Nexus | 44 |
| MCPs | 17 (11 locais, 6 nuvem) |
| Evals/Docs | 5 relatórios |
| Skills geradas (evo) | 8 + 2 = 10 |

### 13.2 Health Score

| Métrica | Valor |
|---------|-------|
| Skills under 2.5KB | 8/9 (88%) |
| Frontmatter OK | 9/9 (100%) |
| CJK Leaks | 0 (zero) |
| Anomalias ativas | 1 (editais-br SKILL.md 66B acima) |
| Syntax errors | 0 |
| Scripts com main() | 91/128 (71%) |

### 13.3 Evolução

| Ciclo | Aprendizados |
|-------|-------------|
| 7.3 | editais-br v7.1 cache versionado, KeyError fix, BNDES API, feedback SQLite |
| 8 | Pipeline Nexus (scan→heal→learn), self-healer otimizado, editais-br tool nativa, dashboard, scanner 9 skills |

### 13.4 Arquivos Relevantes

| Caminho | Propósito |
|---------|-----------|
| `AGENTS.md` | Definição do ecossistema (chinês) |
| `plugins/manus-evolve.ts` | Motor de evolução autônoma |
| `plugins/ecosystem-sync.ts` | Sincronização cross-ecossistema |
| `nexus/scripts/ecosystem_scanner.py` | Scanner autônomo |
| `nexus/scripts/self_healer.py` | Auto-cura |
| `nexus/scripts/evolution_engine.py` | Motor de aprendizado evolutivo |
| `nexus/dashboard_server.py` | Dashboard web |
| `skills/research/editais-br/scripts/edital_search.py` | Busca de editais (core) |
| `basis-research/tools/editais_hook.py` | Ponte SEEKER ↔ editais-br |
| `cache/ecosystem_manifest.json` | Último manifesto do scanner |
| `cache/ecosystem_history.json` | Histórico de snapshots |
| `cache/evolution_knowledge.json` | Conhecimento acumulado |
| `.evolve/manus-state.json` | Estado do Manus Evolve |
| `evals/DOSSIER_ECOSSISTEMA.md` | Dossiê completo |
| `evals/DOCUMENTACAO_COMPLETA.md` | Este documento |

---

*Documentação gerada em 2026-05-09 pelo ecossistema OpenCode v3.5*
