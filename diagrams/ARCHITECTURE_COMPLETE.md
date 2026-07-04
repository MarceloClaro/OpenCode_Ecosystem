# 🏗️ OpenCode Ecosystem — Mapa Arquitetônico Completo

> **Versão:** v7.2.0 | **CTs:** 537 | **Evoluções:** R1→R45 | **Atualização:** 2026-07-04  
> **Graphify:** 7.099 nós · 13.717 arestas · 376 comunidades  
> **FlowZap Interativo:** [Arquitetura Completa](https://flowzap.xyz/playground/4683567e-9809-4132-b774-9c496e86ee40?view=architecture)  
> **Árvore Interativa:** `graphify-out/GRAPH_TREE.html` (536KB)  
> **Call-Flow HTML:** `graphify-out/OpenCode_Ecosystem-callflow.html` (17 seções · 16 diagramas Mermaid)  
> **Grafo JSON:** `graphify-out/graph.json` (para consultas com `graphify query "..."`)

---

## Sumário

1. [Visão Geral — Arquitetura em Camadas L0–L6](#1-visão-geral--arquitetura-em-camadas-l0l6)
2. [Pipeline de Scanners (Evolução R19–R45)](#2-pipeline-de-scanners)
3. [Pipeline Acadêmico (MASWOS + SEEKER + Qualis A1)](#3-pipeline-acadêmico)
4. [MiroFish / BettaFish (P14–P18 + PhD Auditor)](#4-mirofish--bettafish)
5. [Motores de Raciocínio Multi-Paradigma](#5-motores-de-raciocínio-multi-paradigma)
6. [Hierarquia de Agentes (128 Agentes)](#6-hierarquia-de-agentes)
7. [Trust Engine — N3.5 Completo (SPEC-038)](#7-trust-engine)
8. [Token Economy (SPEC-022-024)](#8-token-economy)
9. [Ciclos Evolutivos R1→R45](#9-ciclos-evolutivos)
10. [5 Pilares — Marcelo Claro](#10-os-5-pilares)
11. [Resumo de Componentes](#11-resumo-de-componentes)
12. [Mapa de Fluxo da Informação](#12-mapa-de-fluxo-da-informação)
13. [Descobertas do Graphify](#13-descobertas-do-graphify)

---

## 1. 🌐 Visão Geral — Arquitetura em Camadas L0–L6

**Legenda:** L0 = Infraestrutura (base) → L6 = Interface e comando (topo).  
Cada camada depende dos serviços da camada imediatamente inferior.

```mermaid
%%{init: {"theme": "dark", "themeVariables": {"fontSize": "14px"}}}%%
graph TB
    subgraph L6["L6 - Interface e Comando"]
        CLI["OpenCode CLI / Antigravity CLI"]
        CMDS["Comandos: /evolve /reversa /plan /auto /artigo /quantum"]
        PLUGINS["15 Plugins (npm + .ts + bridge)"]
        MCP_GW["MCP Gateway (46 servidores)"]
    end

    subgraph L5["L5 - Orquestracao e Governanca"]
        MARCELO["/marceloclaro (Orquestrador Supremo)"]
        MASTER["master-orchestrator"]
        STAGE["stage-orchestrator"]
        ANTIGRAVITY["antigravity-orchestrator"]
        TRUST["Trust Engine (SPEC-038)"]
        TOKEN["Token Economy (SPEC-022-024)"]
    end

    subgraph L4["L4 - Auditores e Scanners"]
        PHD_AUDIT["PhD Auditor (Nash + Qualis + Bonferroni)"]
        SCANNERS["Pipeline Scanners (6 modulos)"]
        META["Metacognition (SPEC-036)"]
        SNS["Structural Noise Scanner (SPEC-037)"]
        POTENTIALITY["Potentiality Estimator v2 (SPEC-045)"]
    end

    subgraph L3["L3 - Motores de Raciocinio e Ciencia"]
        REASONING["4 Reasoning Engines"]
        SCIENCE["38 Science Skills"]
        MIROFISH["MiroFish/BettaFish (11 modulos)"]
        GAME_THEORY["10 Jogos Classicoss"]
        QUANTUM["Quantum Nexus (146 arquivos)"]
    end

    subgraph L2["L2 - Agentes Especializados"]
        CORE_AGENTS["56 Agentes Core"]
        CRIADOR["49 Agentes MASWOS"]
        SEEKER["12 SEEKER Agents"]
        REVERSA["18 Reversa Agents"]
        LINGUISTIC["1 Linguistic Corrector"]
    end

    subgraph L1["L1 - Habilidades (Skills)"]
        SKILLS_SYS["12 System Skills"]
        SKILLS_JUR["7 Juridico"]
        SKILLS_RESEARCH["18 Research"]
        SKILLS_SCIENCE["38 Science"]
        SKILLS_REASON["4 Reasoning"]
        SKILLS_OUTROS["149 Outras"]
    end

    subgraph L0["L0 - Infraestrutura"]
        MCP_LOCAL["44 MCPs Locais"]
        MCP_REMOTE["2 MCPs Remotos"]
        LSP["1 LSP (TypeScript)"]
        CORRECTOR["ptbr_corrector.py"]
    end

    L6 --> L5
    L5 --> L4
    L4 --> L3
    L3 --> L2
    L2 --> L1
    L1 --> L0
```

---

## 2. ⚙️ Pipeline de Scanners

**Legenda:** O pipeline encadeia 7 scanners que transformam código/SPECs em roadmaps estratégicos.  
Cada scanner alimenta o seguinte, com análise cruzada no meio.

```mermaid
%%{init: {"theme": "dark"}}%%
graph LR
    subgraph INPUT["Entrada"]
        A["Codigo / SPECs / Artefatos"]
    end

    subgraph SCAN["Pipeline de Scanners"]
        S1["Scanner Noologico - 92 categorias - 100% cobertura"]
        S2["Scanner Teleologico - Alinhamento Estrategico"]
        S3["Scanner Evolutivo - Maturidade do Ecossistema"]
        S4["Potentiality Scanner - Oportunidades Latentes"]
        S5["Social Impact Scanner - Impacto Social e ESG"]
    end

    subgraph ANALYZE["Analise Cruzada"]
        CD["Cognitive Diversity Scanner - Homogeneity Index: 0.61"]
        ET["Epistemic Topology Mapper - Ilhas, Pontes, Buracos"]
        RP["Rupture Potential Index - RPI: 70.9"]
    end

    subgraph OUTPUT["Saidas"]
        ROADMAP["Roadmap de Pesquisa - 3 Rotas Estrategicas"]
        GAPS["Gaps Epistemicos - Detectados e Priorizados"]
        DNA["DNA Match - Viabilidade Tecnica"]
    end

    A --> S1
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> S5
    S5 --> CD
    CD --> ET
    ET --> RP
    RP --> ROADMAP
    RP --> GAPS
    RP --> DNA
```

---

## 3. 🧪 Pipeline Acadêmico

**Legenda:** Fluxo completo de produção acadêmica desde a pesquisa até a exportação Qualis A1.  
Cada fase tem validação cruzada e correção iterativa.

```mermaid
%%{init: {"theme": "dark"}}%%
graph TB
    subgraph PHASE1["Fase 1 - Pesquisa"]
        SK["SEEKER - 12 Agentes - 10+ Fontes Academicas"]
        ARGS["Arvore de Argumentacao - Evidencias Verificaveis"]
    end

    subgraph PHASE2["Fase 2 - Escrita (MASWOS)"]
        MW["49 Agentes Especialistas - 00-44 + Scheduling"]
        STAGES["8 Estagios - Diagnostico ate Conclusao"]
    end

    subgraph PHASE3["Fase 3 - Revisao"]
        PR["Revisao por Pares - 5 Revisores"]
        ADV["4 Consultores Doutores"]
        CORR["Correcao Iterativa - Score 86.5 para 92.7"]
    end

    subgraph PHASE4["Fase 4 - Qualis A1"]
        QS["AUTO_SCORE_QUALIS - 10 Criterios"]
        TSAC["Anti-AI Writing - 87 Palavras Proibidas"]
        PEARSON["Cross-Validation Pearson - 3 Niveis"]
    end

    subgraph PHASE5["Fase 5 - Exportacao"]
        LATEX["LaTeX / PDF - Template ABNT"]
        CJK["ptbr_corrector - CJK Detection"]
        EVOLVE["Manus Evolve - Aprendizado Continuo"]
    end

    PHASE1 --> PHASE2
    PHASE2 --> PHASE3
    PHASE3 --> PHASE4
    PHASE4 --> PHASE5
```

---

## 4. 🧬 MiroFish / BettaFish (P14–P18)

**Legenda:** Componentes do ecossistema de auditoria acadêmica multi-agente.  
P14-P17 alimentam o P18 (PhD Auditor) que produz validação Qualis A1.

```mermaid
%%{init: {"theme": "dark"}}%%
graph TB
    subgraph MF["MiroFish Ecosystem"]
        OASIS["P14 - OASIS - Multi-Agent Forum"]
        DOCIR["P15 - DocIR - Documentacao Estruturada"]
        ANP["P16 - ANP - Agent Node Pipeline"]
        MW_G["P17 - MW - Monitoramento"]
    end

    subgraph PHD["PhD Auditor (P18)"]
        NASH["Nash Equilibrium Solver - Equilibrio de Estrategias"]
        STATS["Statistical Rigor - Cohen + Bonferroni"]
        QUALIS["Qualis A1 Auditor - Periodicos Qualificados"]
        SENS["Sensitivity Analyzer - Robustez"]
        IMRAD["IMRAD Formatter - Relatorio Cientifico"]
    end

    subgraph BF["BettaFish"]
        FORUM["Agent Forum Engine - 4 Estagios - Moderador LLM"]
        DEBATE["Debate Strategies - 212+ Raciocinios - 27 Categorias"]
    end

    OASIS --> FORUM
    FORUM --> DEBATE
    DEBATE --> NASH
    NASH --> STATS
    STATS --> QUALIS
    QUALIS --> SENS
    SENS --> IMRAD
```

---

## 5. 🧠 Motores de Raciocínio Multi-Paradigma

**Legenda:** 4 motores independentes conectados por bridge cross-paradigma.  
Self-Repair System mantém saúde dos motores com heartbeat e fallback.

```mermaid
%%{init: {"theme": "dark"}}%%
graph TB
    subgraph ENGINES["4 Motores de Raciocinio"]
        Z3["Z3 4.16 - Verificacao Formal - SMT Solver"]
        SYMPY["SymPy 1.14 - Matematica Simbolica - Calculo, Algebra"]
        KANREN["miniKanren - Programacao Logica - Relacoes, Consultas"]
        CRITICAL["Critical Engine - 15 Falacias Logicas - Vieses Cognitivos"]
    end

    subgraph INTEGRATION["Integracao Cross-Paradigma"]
        BRIDGE["Paradigm Bridge - Auto, Formal, Symbolic, Logic, Critical, All"]
        REPAIR["Self-Repair System - Heartbeat, Pipeline, Fallback, Audit Trail SHA-256"]
    end

    subgraph SCIENCE["38 Science Skills"]
        AF["AlphaFold, PubMed, OpenAlex"]
        UC["ChEMBL, UniProt, ClinVar"]
        VAR["gnomAD, GTEx, Ensembl"]
        STRUCT["PDB, PyMOL, FoldSeek, STRING"]
    end

    Z3 --> BRIDGE
    SYMPY --> BRIDGE
    KANREN --> BRIDGE
    CRITICAL --> BRIDGE
    BRIDGE --> REPAIR
    SCIENCE --> BRIDGE
```

---

## 6. 🧭 Hierarquia de Agentes

**Legenda:** 128 agentes em 4 categorias principais, orquestrados por Marcelo Claro.  
Cada categoria tem especialização vertical.

```mermaid
%%{init: {"theme": "dark"}}%%
graph TB
    subgraph TOP["Orquestracao Suprema"]
        MC["/marceloclaro - Criador e Orquestrador"]
    end

    subgraph ORCH["Orquestradores"]
        MO["master-orchestrator"]
        SO["stage-orchestrator"]
        AO["antigravity-orchestrator"]
        BO["bernstein-orchestrator"]
    end

    subgraph CORE["56 Agentes Core"]
        CODER["coder-agent, opencoder"]
        REVIEW["code-reviewer, reviewer"]
        DEBUG["debugger, test-engineer"]
        DEV["web-developer, frontend-specialist"]
        SEC["security-auditor, devops-specialist"]
        DOC["docs-writer, technical-writer"]
        EXPLORE["explore, architect"]
    end

    subgraph MASWOS["49 Agentes MASWOS"]
        DIA["00-diagnostico-escopo"]
        BUSCA["02-busca-curadoria"]
        EVID["03-evidencias-citacoes"]
        ESTRUT["04-estrutura-argumentativa"]
        REV["05-revisao-literatura"]
        METODO["06-metodologia"]
        ESTAT["07-estatistica"]
        VIZ["08-visualizacao"]
        RES["09-resultados"]
        DISC["10-discussao"]
        CONC["11-conclusao"]
        ABNT["12-auditoria-bibliografica"]
        QA["13-qa-qualis"]
        MAIS["14-44 - Demais especialistas"]
    end

    subgraph SEEKER["12 SEEKER Agents"]
        S_SEARCH["searcher, grounder"]
        S_VALID["validator, cross-ref"]
    end

    subgraph REVERSA["18 Reversa Agents"]
        R_ARCH["archaeologist, architect"]
        R_DET["detective, scout"]
        R_SYNTH["synthesis, writer"]
        R_GRAPH["graph-builder, graphrag"]
        R_FORUM["agent-forum, anp"]
    end

    MC --> ORCH
    ORCH --> CORE
    ORCH --> MASWOS
    ORCH --> SEEKER
    ORCH --> REVERSA
```

---

## 7. 🤝 Trust Engine (N3.5 Completo — SPEC-038)

**Legenda:** N3.5 = N3 completo (forecasting, introspection, boundary, causal) + gate preventivo.  
O TrustScorer usa blend 70/30 e shadow mode para detecção de desvios em menos de 15ms.

```mermaid
%%{init: {"theme": "dark"}}%%
graph TB
    subgraph TRUST["Trust Engine (N3.5)"]
        SCORER["TrustScorer - Blend 70/30 - Shadow Mode - Rollback"]
        GATE["BehavioralGate - Safe, Moderate, Risky, Blocked"]
        FORGET["NaturalForgetting - Atkinson-Shiffrin"]
        TRACKER["OutcomeTracker - Resultados Historicos"]
    end

    subgraph PREVENT["Preventive Guardrails"]
        GOAL["Goal Drift Detection - abaixo de 15ms Response"]
        BEHAV["Behavioral Containment - Alucinacao, Desvio"]
        BARRIER["Cognitive Barriers - Auto-monitoramento"]
    end

    subgraph N3["N3 Completo"]
        FORECAST["Forecasting - Predicao de Estado"]
        INTROSPECT["Source Introspection - Autoanalise"]
        BOUNDARY["Self/Other Boundary - Limites Epistemicos"]
        CAUSAL["Root Cause Causal - Granger + Bayes"]
    end

    TRUST --> PREVENT
    TRUST --> N3
    PREVENT --> GATE
    N3 --> SCORER
```

---

## 8. 💰 Token Economy (SPEC-022-024)

**Legenda:** Tripé economia: ledger imutável + fee market dinâmico + auditoria SHA-256.  
Três planos (Bronze/Silver/Gold) com staking 7d e slashing.

```mermaid
%%{init: {"theme": "dark"}}%%
graph LR
    subgraph ECON["Token Economy Core"]
        LEDGER["Ledger Congelado - Dataclass Imutavel"]
        FEE["Fee Market - Dinamico por Demanda"]
        STAKING["Staking 7d Lock - Slashing Stake-First"]
    end

    subgraph TIERS["Planos"]
        BRONZE["Bronze - Diario"]
        SILVER["Silver - Semanal"]
        GOLD["Gold - Ilimitado"]
    end

    subgraph AUDIT["Auditoria"]
        TRAIL["Audit Trail SHA-256 - Imutavel"]
        ALLOWANCE["Allowance - Diario/Semanal"]
    end

    LEDGER --> FEE
    FEE --> STAKING
    STAKING --> TIERS
    TIERS --> AUDIT
    AUDIT --> TRAIL
```

---

## 9. 📈 Ciclos Evolutivos R1→R45

**Legenda:** Score evoluiu de 85 (R1) para 100 (R20-R45).  
Cada ciclo adiciona nova capacidade ao ecossistema.

```mermaid
%%{init: {"theme": "dark"}}%%
xychart-beta
    title "Evolucao OpenCode - Score por Ciclo"
    x-axis "Ciclo" ["R1", "R5", "R8", "R11", "R14", "R17", "R20", "R23", "R26", "R35", "R40", "R45"]
    y-axis "Score (%)" 0 --> 100
    bar [85, 92, 94, 97, 97, 99, 100, 100, 100, 100, 100, 100]
    line [85, 88, 91, 93, 95, 96, 98, 99, 100, 100, 100, 100]
```

```mermaid
%%{init: {"theme": "dark"}}%%
graph LR
    subgraph EVO["Evolucao Temporal"]
        R1["R1 - Score 85 - World Bank Data Analysis"]
        R5["R5 - Score 92 - Editais BR v7.1 - Busca Paralela"]
        R8["R8 - Score 94 - SDD+TDD Pipeline Academico"]
        R11["R11 - Score 97 - CORA-Eval Benchmark - 150 Tarefas"]
        R14["R14 - Score 97 - 227 Skills - 128 Agentes - 46 MCPs"]
        R17["R17 - Score 99 - Gartner Hype Cycle 2026 - 3 Gaps"]
        R20["R20 - Score 100 - Unit Knowledge Composition - SPEC-033"]
        R23["R23 - Score 100 - Trust Engine N3.5 - SPEC-038"]
        R26["R26 - Score 100 - Marcelo Claro Orchestration TDD"]
        R35["R35 - Score 100 - Science + Reasoning Full Integration"]
        R40["R40 - Score 100 - MCP Discovery - 46/46 Ativos"]
        R45["R45 - Score 100 - Megaciclo ARCHE+OQS+ASDE+Academic+Refine"]
    end

    R1 --> R5 --> R8 --> R11 --> R14 --> R17 --> R20 --> R23 --> R26 --> R35 --> R40 --> R45
```

---

## 10. 🎯 Os 5 Pilares

**Legenda:** Cada pilar é um pilar arquitetônico do ecossistema, validado por 537 CTs.

```mermaid
%%{init: {"theme": "dark"}}%%
graph TB
    subgraph PILARES["5 Pilares do Ecossistema"]
        P1["P1 - Rigor Cientifico e Engenharia - TDD, SDD, Qualis A1"]
        P2["P2 - Contencao de Desvios - TrustEngine, Guardrails, SPEC-038"]
        P3["P3 - Viabilidade de Negocio SaaS - Token Economy, TaaS"]
        P4["P4 - Unificacao CLIs e Motores - Ollama, OpenCode, Antigravity"]
        P5["P5 - Potenciais Latentes - Potentiality Scanner, SPEC-043/045"]
    end

    subgraph VALIDATION["Validacao Cruzada"]
        CTS["537 CTs - 100% GREEN"]
        AUDIT["PhD Auditor (Nash + Qualis A1)"]
        COVERAGE["Spec Coverage: 100% (186/186)"]
        GRAPH["Graphify: 7.099 nos - 13.717 arestas"]
    end

    P1 & P2 & P3 & P4 & P5 --> VALIDATION
```

---

## 11. 📊 Resumo de Componentes

**Legenda:** Distribuição dos 600+ componentes integrados no ecossistema.

```mermaid
%%{init: {"theme": "dark"}}%%
pie title OpenCode Ecosystem - 600+ Integracoes
    "MCPs (46)" : 46
    "Skills (228)" : 228
    "Agentes (128)" : 128
    "Plugins (15)" : 15
    "Modulos Python (24)" : 24
    "Suites TDD (18)" : 18
    "SPECs (88)" : 88
    "ADRs (10)" : 10
    "Quantum (146)" : 146
    "Nexus (488)" : 488
    "MiroFish/BettaFish (11)" : 11
    "Science Skills (38)" : 38
    "Reasoning Engines (4)" : 4
    "Criador-artigo (91)" : 91
    "SEEKER (78)" : 78
```

---

## 12. 🔄 Mapa de Fluxo da Informação

**Legenda:** Ciclo completo: entrada → orquestração → pipeline → geração → revisão → saída → evolução.

```mermaid
%%{init: {"theme": "dark"}}%%
flowchart TB
    subgraph ENTRADA["Entrada"]
        USER["Usuario / Pesquisador"]
        GIT["GitHub Repository"]
        WEB["Web / APIs Externas"]
    end

    subgraph ORQUESTRACAO["Orquestracao"]
        MARC["/marceloclaro"]
        POT["Potentiality Scanner"]
        TRUST["Trust Engine"]
    end

    subgraph PIPELINE_PRINCIPAL["Pipeline Principal"]
        SEEK["SEEKER Research"]
        SCAN["Scanners Pipeline"]
        DEBATE["Agent Forum Debate"]
        PHD["PhD Auditor"]
    end

    subgraph GERACAO["Geracao"]
        MASWOS["MASWOS 49 Agents"]
        ACADEMIC["Academic Pipeline"]
        QUANTUM["Quantum Nexus"]
    end

    subgraph REVISAO["Revisao"]
        PEER["Peer Review 5"]
        CORR["Iterative Correction"]
        CJK_CORR["ptbr_corrector.py"]
    end

    subgraph SAIDA["Saida"]
        LATEX["LaTeX / PDF"]
        CLI["OpenCode CLI"]
        ANTIG["Antigravity CLI"]
        DASH["Dashboard HTTP"]
    end

    subgraph EVOLUCAO["Evolucao"]
        MANUS["Manus Evolve"]
        AUTOE["AutoEvolve"]
        LEARN["Pattern Learning"]
    end

    ENTRADA --> ORQUESTRACAO
    ORQUESTRACAO --> PIPELINE_PRINCIPAL
    PIPELINE_PRINCIPAL --> GERACAO
    GERACAO --> REVISAO
    REVISAO --> SAIDA
    SAIDA --> EVOLUCAO
    EVOLUCAO -.->|Feedback Loop| ORQUESTRACAO
```

---

## 13. 🔍 Descobertas do Graphify

O Graphify extraiu **7.099 nós** e **13.717 arestas** de 245 arquivos Python, organizados em **376 comunidades**.

### Nós Centrais (God Nodes)

| Nó | Grau | Função |
|----|------|--------|
| `Container` | 98 | DI container singleton |
| `AuditEntry` | 61 | Auditoria SHA-256 |
| `NexusIntegrationFacade` | 57 | Fachada de integração |
| `MCPRouter` | 56 | Roteamento MCP |
| `SocialAlgorithms` | 56 | Algoritmos sociais |
| `initialize_core()` | 55 | Inicialização do core |
| `KnowledgeGraph` | 54 | Grafo de conhecimento |
| `DoclingAdapter` | 51 | Adaptador PDF |
| `GranularSyncManager` | 47 | Barreiras de sincronização |

### Conexões Surpreendentes (Graphify INFERRED)

- `GameTheorySolver` → `PeirceType` (Raciocínio lógico aplicado a jogos)
- `convert_game_to_rlt()` → `RLTNode` (ARCHE integrado à teoria dos jogos)
- `GameTheorySolver` → `RLTNode` (Bridge entre teoria dos jogos e lógica peirceana)
- `TestAutoSwarm` → `AgentSpec` (Testes conectados à especificação de agentes)

### Top 10 Tipos de Arestas

| Tipo | Quantidade | Descrição |
|------|-----------|-----------|
| `calls` | 2.979 | Chamadas de função |
| `rationale_for` | 2.439 | Justificativa de design |
| `method` | 2.259 | Definição de método |
| `contains` | 2.081 | Contém/Agrega |
| `uses` | 1.474 | Utiliza/referencia |
| `imports` | 769 | Importação direta |
| `references` | 636 | Referência entre módulos |
| `imports_from` | 606 | Importação de submódulo |
| `indirect_call` | 407 | Chamada indireta |
| `inherits` | 67 | Herança de classe |

### Top 15 Comunidades (376 total)

| ID | Nós | Foco |
|----|-----|------|
| 0 | 106 | Micro Reasoning Types + Enumerações |
| 1 | 95 | Aletheia Engine (Raciocínio Formal) |
| 2 | 92 | Knowledge Graphs (Relações + Entidades) |
| 3 | 85 | Ecosystem Capabilities Server (MCP tools) |
| 4 | 70 | Evolution Loop (Feedback + Learning) |
| 5 | 69 | Sync Orchestrator (Scoring + Descoberta) |
| 6 | 65 | Token Economy SPEC-022 |
| 7 | 65 | Domain Shift Audit (Jaccard + Bootstrap) |
| 8 | 64 | Nexus Evolution Loop (clonagem R4) |
| 9 | 59 | Witness Pattern (R28 Validação) |
| 10 | 59 | OQS Scanner (Optimal Question) |
| 11 | 59 | Audit Integration SPEC-024 |
| 12 | 58 | MCP Real Adapters (Execução) |
| 13 | 58 | Estatística (Testes D3) |
| 14 | 55 | ASDE Engine (Descoberta Científica) |

---

## Anexos

### Ferramentas de Consulta

```bash
# Graphify: consultar o grafo de conhecimento
graphify query "Como funciona o pipeline academico?"
graphify path "SEEKER" "QualisA1Auditor"
graphify explain "TrustEngine"

# FlowZap: diagrama interativo
# https://flowzap.xyz/playground/4683567e-9809-4132-b774-9c496e86ee40?view=architecture

# Graphify HTML tree (navegável no browser)
# file:///mnt/c/Users/marce/Documents/OpenCode_Ecosystem/graphify-out/GRAPH_TREE.html

# Graphify callflow (17 seções Mermaid)
# file:///mnt/c/Users/marce/Documents/OpenCode_Ecosystem/graphify-out/OpenCode_Ecosystem-callflow.html
```

### Arquivos Gerados

| Arquivo | Tamanho | Descrição |
|---------|---------|-----------|
| `graphify-out/graph.json` | 2,1 MB | Grafo completo (7.099 nós, 13.717 arestas) |
| `graphify-out/GRAPH_REPORT.md` | 15 KB | Relatório com 376 comunidades |
| `graphify-out/GRAPH_TREE.html` | 536 KB | Árvore interativa D3.js |
| `graphify-out/OpenCode_Ecosystem-callflow.html` | 37 KB | Call-flow com 17 seções Mermaid |
| `diagrams/ARCHITECTURE_COMPLETE.md` | Este arquivo | Mapa arquitetônico completo |

---

> **Criado por:** Marcelo Claro — Orquestrador Supremo do OpenCode Ecosystem  
> **Graphify v0.9.6** · **7.099 nós** · **376 comunidades** · **13.717 arestas**  
> **Qualis A1** · **537 CTs** · **100% GREEN**
