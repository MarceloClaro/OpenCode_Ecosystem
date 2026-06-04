# Arquitetura do OpenCode Ecosystem v4.7

**Documento de Onboarding para Desenvolvedores** | **Bus Factor:** 1 → 2+
**Data:** 2026-06-04 | **Versao:** 1.0

---

## 1. Visao Geral

O OpenCode Ecosystem e uma plataforma de inteligencia artificial multiagente que
coordena **125 agentes especializados** com **212 tipos de raciocinio** (27 categorias)
para realizar tarefas complexas de forma autonoma, com verificacao cientifica
quantitativa (CORA-Score 3.04, nivel Pesquisa).

### Principios Arquiteturais

1. **Multiagente sobre Monolitico:** 125 agentes especializados > 1 LLM generico
2. **Auditoria Caixa Branca:** Toda decisao rastreavel a um agente + verificador
3. **TDD como Gate:** Qualidade medida objetivamente, nao por inspecao
4. **AutoEvolve:** O sistema aprende com cada correcao e registra padroes

---

## 2. Diagrama de Arquitetura (ASCII)

```
+====================================================================+
|                     INTERFACE (menu.py)                             |
|  DiscoveryEngine + MenuRenderer + RunnerEngine + PluginSystem       |
+====================================================================+
        |              |              |              |
+-------+------+ +-----+------+ +-----+------+ +-----+------+
|  OPERACIONAR | | REPRODUZIR | | REGISTRAR  | |  AUDITAR   |
+--------------+ +------------+ +------------+ +------------+
        |              |              |              |
+====================================================================+
|                ORCHESTRATOR (Pipeline SENSE->LEARN)                 |
|  refinement_loop.py: SENSE → DIAGNOSE → FIX → VERIFY → EVOLVE → LEARN |
+====================================================================+
        |              |              |
+-------+------+ +-----+------+ +-----+------+
|  Q-Gate 1    | | Q-Gate 2   | | Q-Gate 3   |
| Compilation  | | Structure  | | Quality    |
| (5 tests)    | | (6 tests)  | | (5 tests)  |
+-------+------+ +-----+------+ +-----+------+
        |              |              |
+====================================================================+
|                     AGENT LAYER (125 agents)                        |
|  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  |
|  │ MASWOS   │ │ SEEKER   │ │ CORA     │ │ REVERSA  │ │ QUANTUM  │  |
|  │ 49 agents│ │ 10 agents│ │ 7 verif. │ │ 18 agents│ │ 8 agents │  |
|  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  |
+====================================================================+
        |              |              |
+====================================================================+
|                     SKILL LAYER (106 skills)                        |
|  System(12) | Juridico(7) | Research(18) | Science(38) | Design(90+)|
+====================================================================+
        |              |              |
+====================================================================+
|                      MCP LAYER (41 servers)                         |
|  WebSearch | CodeRunner | SequentialThinking | Fetch | SciHub | ... |
+====================================================================+
        |              |              |
+====================================================================+
|                   EXTERNAL APIs & Services                          |
|  arXiv | PubMed | OpenAlex | CORE | GitHub | DuckDuckGo | Sci-Hub  |
+====================================================================+
```

## 3. Fluxo de Dados (Pipeline Tipico)

```
Usuario (menu.py)
    │
    ▼
DiscoveryEngine: identifica .tex, testes, pipelines
    │
    ├─► OPERACIONAR: pdflatex → TDD → relatorio
    ├─► REPRODUZIR: restaurar backup → recompliar
    ├─► REGISTRAR: registrar correcao → fix_history.json
    └─► AUDITAR: historico, metricas, dependencias
    │
    ▼
Orchestrator (refinement_loop.py)
    │
    ├─► SENSE: compila .tex, extrai metricas
    ├─► DIAGNOSE: parseia .log com regex
    ├─► FIX: aplica correcao seletiva (max 5x)
    ├─► VERIFY: executa suites TDD (16 testes)
    ├─► EVOLVE: registra em fix_history.json
    └─► LEARN: detecta padroes, gera insights
    │
    ▼
PDF final + relatorio JSON
```

---

## 4. Componentes Detalhados

### 4.1 Agentes (125)

| Grupo | Agentes | Funcao |
|-------|:-------:|--------|
| MASWOS | 49 | Pipeline de escrita academica (8 estagios) |
| SEEKER | 10 | Busca e verificacao de fontes academicas |
| Cora-Debate | 7 | Verificadores simbolicos V1-V7 |
| Reversa | 18 | Engenharia reversa de codigo |
| Quantum Nexus | 8 | Computacao quantica e simulacao |
| Agent Forum | 5 | Debate multiagente com moderacao |
| Outros | 28 | AutoEvolve, DecisionNode, corretores |

### 4.2 MCPs (41 servidores, 23 ativos)

| Categoria | MCPs | Exemplos |
|-----------|:----:|----------|
| Busca | 4 | websearch, gh_grep, context7, scihub |
| Browser | 2 | playwright, chrome-devtools |
| Codigo | 3 | eslint, diff, code-runner |
| Dados | 4 | sqlite, fetch, pdf, time |
| Raciocinio | 2 | sequential-thinking, memory |

### 4.3 Skills (106)

| Categoria | Skills | Destaques |
|-----------|:------:|-----------|
| System | 12 | code-review, plan-review, pypi-scout |
| Research | 18 | academic-ml-pipeline, editais-br, aletheia-math |
| Science | 38 | AlphaFold, PubMed, ChEMBL, UniProt, PyMOL |
| Design | 90+ | html-ppt, hyperframes, open-design-landing |

### 4.4 Raciocinios (212, 27 categorias)

| Categoria | Tipos | Exemplos |
|-----------|:-----:|----------|
| Logica | 5 | Dedutivo, Indutivo, Abdutivo, Analogico, Dialetico |
| Dialetica | 5 | Tese-Antitese-Sintese, Hegeliano, Marxista |
| Teoria dos Jogos | 10 | Nash, Pareto, Shapley, MinMax, Stackelberg |
| Estrategia | 5 | First Principles, Inversion, Second Order |
| Cientifico | 8 | Hipotetico-Dedutivo, Falsificacao, Abducao Peirceana |

---

## 5. Pipeline SDD+TDD+AutoEvolve

### 5.1 SDD (Spec-Driven Development)

```
Qualidade definida ANTES da execucao:
  SPEC_ORCHESTRATION.md  →  criterios objetivos
  SPEC_008-011           →  validacao cientifica
  ADRs (6)               →  decisoes arquiteturais
```

### 5.2 TDD (Test-Driven Development)

```
16 testes em 3 gates:
  Gate 1 — Compilacao (5): exit code, erros, refs, PDF, cross-ref
  Gate 2 — Estrutura (6): secoes, labels, refs, numeracao, figuras
  Gate 3 — Qualidade (5): overfull, underfull, viuva/orfa, fontes

Ciclo: RED (falha) → GREEN (corrige) → REFACTOR (aprende)
```

### 5.3 AutoEvolve

```
Loop autonomo:
  SENSE → DIAGNOSE → FIX → VERIFY → EVOLVE → LEARN
  Max 5 iteracoes, backup automatico antes de cada FIX
  1 correcao por iteracao para rastreabilidade
```

---

## 6. Fluxo de Desenvolvimento

### 6.1 Criar Novo Agente

```
1. Definir funcao do agente (documentar em SPEC)
2. Implementar handler em agents/<nome>.py
3. Registrar no AgentRegistry
4. Criar teste TDD: tests/test_<nome>.py
5. Executar suite: pytest tests/ -v
```

### 6.2 Criar Nova Skill

```
1. Criar diretorio: skills/<categoria>/<nome>/
2. Escrever SKILL.md com instrucoes
3. Adicionar referencias em references/
4. Testar com agente existente
```

### 6.3 Criar Novo SPEC

```
1. Modelo: `template SPEC_XXX_NOME.md`
2. Definir criterios de aceitacao (formato TDD)
3. Registrar no project-state.json
4. Implementar suite de teste correspondente
```

---

## 7. Dependencias

### 7.1 Externas

| Dependencia | Funcao | Criticidade |
|-------------|--------|:-----------:|
| deepseek-v4-pro | Modelo LLM principal | Critica |
| arXiv API | Busca de papers | Alta |
| PubMed E-utilities | Literatura biomedica | Media |
| GitHub API | Versionamento e CI | Media |
| PyPI | Pacotes Python | Baixa |

### 7.2 Python

| Pacote | Versao Minima | Funcao |
|--------|:------------:|--------|
| pytest | 8.0+ | Framework TDD |
| numpy | 1.24+ | Computacao cientifica |
| scipy | 1.10+ | Estatistica avancada |
| sympy | 1.12+ | Matematica simbolica |

### 7.3 Sistema

| Ferramenta | Funcao |
|------------|--------|
| pdflatex (TeX Live 2023+) | Compilacao LaTeX |
| Python 3.10+ | Runtime |
| Git 2.40+ | Versionamento |

---

## 8. Como Contribuir

### Primeiros Passos

```bash
git clone https://github.com/MarceloClaro/OpenCode_Ecosystem.git
cd OpenCode_Ecosystem
python -m pytest artigo/evaluations/tests/ -v --tb=short
```

### Estrutura de Diretorios

```
Antiprojeto UFC/
├── artigo/                     # Projeto CORA-Eval
│   ├── evaluations/tests/      # 30+ arquivos de teste TDD
│   ├── orchestration/          # Pipeline AutoEvolve
│   ├── tests/                  # Testes de qualidade LaTeX
│   └── figuras/                # Graficos e diagramas
├── docs/                       # Documentacao unificada
├── .github/workflows/          # CI/CD
├── menu.py                     # Menu adaptativo
└── .menu_registry.json         # Registro de plugins
```

### Convencoes

- Testes: prefixo `test_` com docstring descritiva
- SPECs: formato `SPEC_NNN_NOME.md`
- Commits: Conventional Commits v1.0.0
- Codigo: Python 3.12+, type hints, docstrings

---

## 9. Glossario

| Termo | Definicao |
|-------|-----------|
| **Agente** | Entidade autonoma com funcao especializada (ex: revisor, buscador) |
| **AutoEvolve** | Capacidade do sistema de se auto-corrigir e aprender com padroes |
| **CORA-Eval** | Benchmark de 150 tarefas × 10 dimensoes × 4 niveis |
| **CORA-Score** | Pontuacao agregada de maturidade cientifica (0-4) |
| **DiscoveryEngine** | Motor que varre diretorio e descobre artefatos automaticamente |
| **MCP** | Model Context Protocol — servidor que conecta IA a ferramentas |
| **PCI** | Process Confidence Index — metrica de confianca em resultados |
| **Q-Score** | Qualidade ponderada por verificadores V1-V7 |
| **SDD** | Spec-Driven Development — especificacao precede implementacao |
| **Skill** | Conjunto de instrucoes e workflows para tarefa especifica |
| **SPEC** | Especificacao formal com criterios de aceitacao TDD |
| **TDD** | Test-Driven Development — testes definem qualidade |
| **TSAC** | Protocolo anti-AI com 87 palavras banidas |
| **V1-V7** | Verificadores Cora-Debate (dimensional, algebrico, etc.) |
| **Quality Gate** | Conjunto de testes que bloqueia pipeline se falhar |
| **Overfull** | Caixa horizontal que excede largura do texto (pontos) |
| **Badness** | Metrica LaTeX de qualidade de quebra (0=otimo, 10000=pessimo) |

---

**Arquitetura do Ecossistema** · 2026-06-04 · OpenCode Ecosystem v4.7.1
