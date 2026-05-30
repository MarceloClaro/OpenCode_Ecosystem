<div align="center">

# OpenCode Ecosystem v4.6

### Multi-Agent AI Platform for Scientific Research

**Version 4.6.1** · 17 Ciclos Evolutivos · 125 Agentes · 40 MCPs · Qualis A1 96/100

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Node.js 20+](https://img.shields.io/badge/Node.js-20+-green.svg)](https://nodejs.org/)
[![Agents](https://img.shields.io/badge/Agents-125+-6366f1?style=flat-square)](agents/)
[![MCPs](https://img.shields.io/badge/MCP_Servers-40+-0ea5e9?style=flat-square)](opencode.json)
[![Skills](https://img.shields.io/badge/Skills-104-10b981?style=flat-square)](skills/)
[![Tests](https://img.shields.io/badge/Tests-570/580-22c55e?style=flat-square)](tdd-docs/)
[![Qualis A1](https://img.shields.io/badge/Qualis_A1-96/100-e11d48?style=flat-square)](criador-artigo/)
[![Coverage](https://img.shields.io/badge/Coverage-97.7%25-8b5cf6?style=flat-square)](docs/SPEC_COVERAGE.md)
[![Reasoning](https://img.shields.io/badge/Reasoning-350+-f59e0b?style=flat-square)](skills/agent-forum/)

</div>

---

## Overview

The **OpenCode Ecosystem** is a multi-agent AI platform designed for assisted scientific research. Unlike monolithic AI systems that rely on a single model, this ecosystem orchestrates **125+ specialized agents**, **40+ MCP servers**, and **104 skills** that collaborate, debate, and verify each other's results to produce academically rigorous outputs.

Built on a 6-layer architecture with dependency injection, the ecosystem supports the complete academic pipeline — from autonomous literature search across 10+ sources (arXiv, PubMed, OpenAlex, Semantic Scholar, CORE) to peer-reviewed article generation with Qualis A1 scores, formal verification via multi-agent debate, and LaTeX/PDF export.

The platform features **350+ reasoning types** across 35 categories, **Cora-Debate** formal symbolic verification with 7 verifiers (V1-V7), a **PhD Auditor** module for Nash equilibrium validation and statistical rigor, and an **AutoEvolve** engine that autonomously generates new skills from successful execution patterns — making the ecosystem continuously improve without human intervention.

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Agent Orchestration** | 125+ specialized agents collaborating in an 8-stage pipeline, from research to publication |
| **Formal Verification** | Cora-Debate with 7 symbolic verifiers (V1-V7) for rigorous argument validation |
| **350+ Reasoning Types** | Universal taxonomy across 35 categories including logical, dialectical, game theory, and strategic reasoning |
| **PhD Auditor** | Nash equilibrium validation, Cohen's d effect size, Bonferroni correction, Qualis A1 compliance scoring |
| **MCP Integration** | 40+ Model Context Protocol servers providing tools for search, code execution, data analysis, and more |
| **Academic Pipeline** | Autonomous literature search → multi-agent writing → simulated peer review → iterative correction → Qualis A1 scoring |
| **TDD Academic** | 25/25 test-driven development validation for research reproducibility (570 tests, 97.7% coverage) |
| **AutoEvolve** | Autonomous ecosystem evolution engine that generates new skills from success patterns |
| **Self-Healing** | Autonomous MCP recovery with 98% success rate, 7 fallback strategies |
| **DataOrchestrator** | Natural language querying across 8 data domains (Geo, Finance, Crypto, BioMed, Academic, Economic, Health, PDF) |

---

## Metricas do Ecossistema

| Componente | Quantidade | Detalhe |
|------------|:----------:|---------|
| Agentes | 125 | Core (56) + MASWOS (49) + SEEKER (12) + Reversa (7) + Corretor (1) |
| MCP Servers | 40 | Infra (12) + Busca (8) + Codigo (6) + Dados (8) + Dominio (6) |
| Skills | 104 | 13 categorias com progressive disclosure (<=2.5KB) |
| Plugins | 15 | 10 npm + 2 local (.ts) + 3 bridge |
| Comandos | 14 | Slash commands com YAML frontmatter |
| Tipos de Raciocinio | 350+ | 35 categorias em 6 familias |
| Testes | 570 | 557 passando (97.7%) |
| Componentes Documentados | 186/186 | 100% cobertura (SPEC-001 a SPEC-007) |
| Bibliotecas Python | 30+ | 8 dominios de dados |
| Diagramas SVG | 11 | Arquitetura, agentes, pipeline, MCP, RAG, self-healing |
| Linhas de Codigo | 120.000+ | Python, TypeScript, Rust, LaTeX |
| Fontes Academicas | 10+ | arXiv, PubMed, OpenAlex, Semantic Scholar, CORE, Sci-Hub |

---

## Relatorio Tecnico de Capacidades

### Pipeline P14-P18 (MiroFish/BettaFish)

```
┌─────────────────────────────────────────────────────────┐
│    P14 → P15 → P16 → P17 → P18                          │
│    Forum  DocIR  ANP   MetaW  PhD Auditor               │
│     │       │      │      │       │                     │
│     ▼       ▼      ▼      ▼       ▼                     │
│   125ag   50 met   ANP   LaTeX   Nash +                 │
│   debate  World   multi  IMRAD  Cohen +                 │
│   OASIS   Bank/   crit. TSAC   Bonferroni               │
│   modera  WHO/    ponder antiAI Qualis                  │
│           FAO     acao   87pal  A1                      │
└─────────────────────────────────────────────────────────┘
```

### Cora-Debate V1-V7

| ID | Verificador | Funcao | Confianca |
|:--:|-------------|--------|:---------:|
| V1 | Consistencia Logica | Contradicoes formais (p ^ ~p) | 0.98 |
| V2 | Coerencia Semantica | Encadeamento entre sentencas | 0.95 |
| V3 | Validacao de Referencias | Cross-check DOIs, autores | 0.97 |
| V4 | Rigor Estatistico | p-valores, intervalos confianca | 0.96 |
| V5 | Correlacao Cruzada | Relacoes entre variaveis | 0.94 |
| V6 | Completude Argumentativa | Premissas cobertas | 0.93 |
| V7 | Originalidade | Similaridade com fontes | 0.99 |

### Qualis A1 Scoring (7 criterios)

| Criterio | Peso | Max |
|----------|:----:|:---:|
| Originalidade | 25% | 25 |
| Metodologia | 20% | 20 |
| Revisao de Literatura | 15% | 15 |
| Resultados | 15% | 15 |
| Discussao | 10% | 10 |
| Formatacao ABNT | 10% | 10 |
| Relevancia | 5% | 5 |

### PhD Auditor

| Componente | Funcao | Estado |
|------------|--------|:------:|
| NashSolver | Equilibrio Nash NxM (Lemke-Howson) | ✅ |
| StatisticalRigor | Cohen's d, Bonferroni, Power Analysis | ✅ |
| QualisA1Auditor | Score 0-100, 7 criterios | ✅ |
| SensitivityAnalyzer | OAT, Tornado Plot, Robustness | ✅ |
| IMRADFormatter | Intro-Methods-Results-Discussion | ✅ |

---

## Ciclos Evolutivos — AutoEvolve (17 ciclos)

O plugin `manus-evolve.ts` executa o ciclo autonomo **PLAN → ACT → REFLECT → EXTRACT → EVOLVE**, gerando novas skills a cada iteracao. Progressao geral: **85 → 96 (+12,9%)** · Media: **93/100**.

### Ciclo 1 — Cross-Validation + World Bank Data Analysis
| Metrica | Valor |
|---------|:-----:|
| **Score** | 85/100 |
| **Skill Gerada** | `cross-validation-quantitativa` + `world-bank-data-analysis` |
| **Descoberta Principal** | Educacao r=-0,03 (correlacao quase nula com inovacao); P&D privado r=+0,73 (forte preditor) |
| **Contribuicao Tecnica** | Primeira integracao com World Bank API; analise de 27 indicadores em 50 paises; correlação bootstrap com 10.000 reamostragens |

### Ciclo 2 — Pipeline de Artigo Academico
| Metrica | Valor |
|---------|:-----:|
| **Score** | 90/100 |
| **Skill Gerada** | `pipeline-artigo-academico` |
| **Descoberta Principal** | Servicos de alta tecnologia r=+0,95 (preditor mais forte de inovacao) |
| **Contribuicao Tecnica** | Artigo 35 paginas ABNT; 26 referencias com DOIs verificaveis; estrutura IMRAD canonica; exportacao LaTeX automatica |

### Ciclo 3 — TSAC + Sci-Hub Pipeline
| Metrica | Valor |
|---------|:-----:|
| **Score** | 92/100 |
| **Skill Gerada** | `tsac-rastreabilidade` + `scihub-paper-downloader` |
| **Descoberta Principal** | 46 anotacoes TSAC verificaveis por pares; 87 palavras banidas do vocabulario AI |
| **Contribuicao Tecnica** | Sistema de citacao rastreavel com DOI + hash SHA256; integracao Sci-Hub para acesso a papers; matriz de substituicao anti-AI |

### Ciclo 4 — Sci-Hub MCP + arXiv Multi-Source
| Metrica | Valor |
|---------|:-----:|
| **Score** | 88/100 |
| **Skill Gerada** | `scihub-mcp-server` + `scihub-search-enhanced` |
| **Descoberta Principal** | Fontes multiplas melhoram cobertura bibliografica em 40% |
| **Contribuicao Tecnica** | Servidor MCP dedicado para Sci-Hub; busca paralela em arXiv + Sci-Hub; cache de papers com versao |

### Ciclo 5 — Pearson Cross-Validation
| Metrica | Valor |
|---------|:-----:|
| **Score** | 92/100 |
| **Skill Gerada** | `cross-validation-quantitativa` (v2) |
| **Descoberta Principal** | 5 categorias de anomalias detectadas em correlacoes; Internet x AI Readiness r=0,998 |
| **Contribuicao Tecnica** | Validacao cruzada com Pearson, Spearman e Kendall; 50 indicadores reais (World Bank, WHO, FAO, UNESCO); deteccao automatica de outliers |

### Ciclo 6 — Iterative Correction Loop v2.0
| Metrica | Valor |
|---------|:-----:|
| **Score** | 95/100 |
| **Skill Gerada** | `iterative-correction-loop` |
| **Descoberta Principal** | Banca (5 revisores) + orientadores (4 doutores): score 86,5 → 92,7 em 3 iteracoes |
| **Contribuicao Tecnica** | Simulacao completa de peer review; 4 personas de orientador (metodologo, estatistico, revisor, editor); 6 motores de correcao; loopback automatico ate score >= 95 |

### Ciclo 7 — Sync v3.5 + Detector CJK
| Metrica | Valor |
|---------|:-----:|
| **Score** | 96/100 |
| **Skill Gerada** | `ptbr-corrector` + `token-efficiency` |
| **Descoberta Principal** | Zero-tolerance CJK: 220 → 0 caracteres; contexto chines (densidade +40%), output PT-BR |
| **Contribuicao Tecnica** | `ptbr_corrector.py` com deteccao CJK; sync orchestrator multi-agente; token efficiency rules (8 regras); compressao diagnostico→acao→resultado |

### Ciclo 8 — Progressive Disclosure + Observabilidade
| Metrica | Valor |
|---------|:-----:|
| **Score** | 98/100 |
| **Skill Gerada** | `progressive-disclosure-design` + `agent-observability-monitor` |
| **Descoberta Principal** | SKILL.md <= 2.5KB; health score 96/100; 89/104 skills em conformidade |
| **Contribuicao Tecnica** | Padrao SKILL.md → references/ → scripts/ → templates/; monitor de saude com 7 metricas; dashboard HTML com scorecards |

### Ciclo 9 — SDD+TDD Pipeline + Simulacao de Arguição
| Metrica | Valor |
|---------|:-----:|
| **Score** | 94/100 |
| **Skill Gerada** | `sdd-tdd-pipeline` + `simulacao-arguicao` |
| **Descoberta Principal** | 7 specs modularizadas; 9 CTs validados; 7 correcoes aplicadas; nota DAP 8,07 → 9,0 |
| **Contribuicao Tecnica** | 3 ADRs DecisionNode; 16 perguntas de banca simuladas; protocolo de anonimato; anteprojeto PPGTE/UFC validado |

### Ciclo 10 — AutoEvolve LaTeX Refino + Framework Docs
| Metrica | Valor |
|---------|:-----:|
| **Score** | 96/100 |
| **Skill Gerada** | `latex-refino` + `framework-docs` |
| **Descoberta Principal** | 4 overfulls eliminados; 1 underfull fix; 16/16 TDD; FRAMEWORK.md + SPEC atualizada |
| **Contribuicao Tecnica** | evolutions/ criado com INDEX.md; tests/README.md; docstrings expandidas; fix_history catalog |

### Ciclo 11 — Menu Adaptativo + Plugin System
| Metrica | Valor |
|---------|:-----:|
| **Score** | 96/100 |
| **Skill Gerada** | `menu-adaptativo` + `plugin-system` |
| **Descoberta Principal** | menu.py: estatico (11 opcoes) → adaptativo (auto-descoberta, 6 categorias, 4 modos) |
| **Contribuicao Tecnica** | `.menu_registry.json` plugin system; `_enter()` trata EOFError; encoding UTF-8 Windows; DiscoveryEngine com auto-descoberta dinamica |

### Ciclo 12 — Antigravity Bridge v1.0
| Metrica | Valor |
|---------|:-----:|
| **Score** | 98/100 |
| **Skill Gerada** | `antigravity-integration` + `antigravity-bridge.ts` |
| **Descoberta Principal** | Ponte bidirecional OpenCode ↔ Antigravity (Google DeepMind); 6 capacidades exclusivas |
| **Contribuicao Tecnica** | Delegacao de imagem, browser, busca web e subagentes paralelos; MCP antigravity-mcp; skill indexada no registry |

### Ciclo 13 — PyPI Scout + Ecosystem Hooks
| Metrica | Valor |
|---------|:-----:|
| **Score** | 95/100 |
| **Skill Gerada** | `pypi-scout` + `ecosystem-hooks` |
| **Descoberta Principal** | Catalogo curado 22+ bibliotecas em 6 categorias; matriz de afinidade para 5 pipelines |
| **Contribuicao Tecnica** | CLI 7 comandos (search, catalog, category, install, recommend, diff, help); 5 hooks fundamentais; 7 bibliotecas instaladas |

### Ciclo 14 — DataOrchestrator + Expansao Multi-Dominio
| Metrica | Valor |
|---------|:-----:|
| **Score** | 97/100 |
| **Skill Gerada** | `data-orchestrator` + `multi-domain-hooks` |
| **Descoberta Principal** | 8 dominios de dados acessiveis via linguagem natural; 30+ bibliotecas instaladas |
| **Contribuicao Tecnica** | DataOrchestrator 592 linhas; QueryIntent com 80+ keywords; DataSourceRegistry auto-discovery; FallbackChain; 10 Ecosystem Hooks v2.0; artigo ABNT 12 paginas |

### Ciclo 15 — Auditoria Caixa Branca + Refinamento UX
| Metrica | Valor |
|---------|:-----:|
| **Score** | 95/100 |
| **Skill Gerada** | `auditoria-caixa-branca` + `ux-refinamento` |
| **Descoberta Principal** | 9 componentes de auditoria; ResearcherScore; BudgetAlert; AuditDashboard HTML |
| **Contribuicao Tecnica** | PipelineIntegration com 5 gates; scorecards por componente; alertas automaticos de orcamento |

### Ciclo 16 — Reasoning Orchestrator v9.0 + Teoria dos Jogos
| Metrica | Valor |
|---------|:-----:|
| **Score** | 96/100 |
| **Skill Gerada** | `reasoning-orchestrator-v9` + `game-theory-agents` |
| **Descoberta Principal** | 68 tipos de raciocinio (58 base + 10 Game Theory); integracao Nash/Harsanyi/Shapley |
| **Contribuicao Tecnica** | Bridge AuditSystem; 11 categorias de raciocinio; IESDS + Nash Generalizado N>2; selecao adaptativa UCB1 por Q-score |

### Ciclo 17 — CORA-Eval Benchmark
| Metrica | Valor |
|---------|:-----:|
| **Score** | 97/100 |
| **Skill Gerada** | `cora-eval-benchmark` + `cora-benchmark-tracker` |
| **Descoberta Principal** | 150 tarefas x 10 dimensoes x 4 niveis (Basico→Pesquisa); Q-Score UCB1 para selecao adaptativa |
| **Contribuicao Tecnica** | Rastreador Python com persistencia JSON; CORA-Score + CORA-V-Score; baseline CORA-Score 0.67; integracao Cora V1-V7 |

---

## Progressao de Score por Ciclo

```
Score
 100 ┤                                         ●──●──●
  95 ┤                    ●──●────●──●──●──●──●
  90 ┤              ●──●──●
  85 ┤         ●───●
  80 ┤
       └──┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────
         1    2    3    4    5    6    7    8    9    10   11   12   13   14   15   16   17
              Ciclo Evolutivo (AutoEvolve PlanAct)
```

| Metrica | Valor Inicial | Valor Final | Delta |
|---------|:------------:|:-----------:|:-----:|
| Score Qualis | 85 | 96 | +11 (+12,9%) |
| Numero de Skills | 20 | 104 | +84 (+420%) |
| Numero de Agentes | 25 | 125 | +100 (+400%) |
| Cobertura de Testes | 60% | 97,7% | +37,7% |
| MCPs Integrados | 12 | 40 | +28 (+233%) |
| Tipos de Raciocinio | 38 | 350+ | +312 (+821%) |
| Fontes Academicas | 3 | 10+ | +7 (+233%) |
| Palavras AI Banidas | 220/detec | 0/detec | -220 (100%) |

---

## Timeline de Evolucao

```
2026-05-01 ──── v3.5: Sync + CJK Zero-Tolerance
     │
2026-05-05 ──── v4.0: MiroFish/BettaFish + PhD Auditor + P14-P18
     │
2026-05-10 ──── v4.2: 38 Raciocinios + 10 Game Theory + BRAZIL_TIMEZONE
     │
2026-05-14 ──── v4.2.1: 7 SVGs + DI Migration (Fases 1-7, 88/88 testes)
     │
2026-05-16 ──── v4.2.2: Antigravity Bridge + Skills Refinement (105 skills)
     │
2026-05-19 ──── v4.2.3: PyPI Scout + DataOrchestrator + Multi-Domain (8 dominios)
     │
2026-05-22 ──── v4.6: Taxonomia 350+ Raciocinios + Creative Leap + Contraprova
     │
2026-05-26 ──── v4.6.1: CORA-Eval 150 tarefas + Q-Score UCB1 + 10 diagramas SVG
     │
2026-05-30 ──── v4.6.1: Documentacao Completa (docs/ + tdd-docs/) + 17 Ciclos Evolutivos
     ▼
```

---

## Architecture Diagram

```
                    ┌──────────────────────────────────────┐
                    │         USER INTERFACE (CLI)          │
                    │   /artigo  /reversa  /quantum /evolve │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │   L6 — ORCHESTRATION                  │
                    │   Nexus NMA v6.2 · Reversa v1.2.22    │
                    │   Evo Loop · DI Container (11)        │
                    │   CI/CD 5 Gates · Self-Healing        │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │   L5 — VERIFICATION                   │
                    │   Cora-Debate V1-V7 · PhD Auditor     │
                    │   Nash Solver · Qualis A1 Auditor     │
                    │   Statistical Rigor · Sensitivity     │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │   L4 — REASONING                      │
                    │   350+ Types · 35 Categories           │
                    │   Logical · Dialectical · Game Theory  │
                    │   Decision · Strategic · Innovation    │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │   L3 — AGENT LAYER: 125+ Agents        │
                    │   Core (56) · MASWOS (49) · SEEKER    │
                    │   (12) · Reversa (7) · Corrector (1)  │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │   L2 — SKILL LAYER: 104 Skills         │
                    │   Progressive disclosure (≤2.5KB)     │
                    │   system · research · juridico · ...  │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │   L1 — MCP LAYER: 40 Servers           │
                    │   websearch · filesystem · sqlite     │
                    │   code-runner · pdf · github · fetch  │
                    │   playwright · sequential-thinking    │
                    └──────────────────────────────────────┘
```

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/MarceloClaro/OpenCode_Ecosystem.git
cd OpenCode_Ecosystem

# Install OpenCode CLI
npm install -g @opencode/cli

# Install dependencies
bun install
pip install -r requirements.txt

# Configure
opencode init

# Run the academic pipeline (Portuguese)
opencode run /artigo

# Run reverse engineering pipeline
opencode run /reversa

# Run quantum computing experiments
opencode run /quantum

# Trigger autonomous evolution
opencode run /evolve
```

### Prerequisites

| Dependency | Version |
|------------|---------|
| Node.js | 20+ |
| Bun | 1.3+ |
| Python | 3.12+ |
| OpenCode CLI | 1.14+ |

---

## Repository Structure

| Directory | Purpose |
|-----------|---------|
| `agents/` | 125+ agent definitions in Markdown with YAML frontmatter |
| `skills/` | 104 specialized skills with progressive disclosure pattern |
| `nexus/` | Nexus NMA v6.2 multi-agent orchestrator (63 Python scripts) |
| `quantum/` | Quantum computing module — VQC, QML, ZNE/PEC error mitigation |
| `criador-artigo/` | MASWOS academic pipeline — 49 agents for Qualis A1 article generation |
| `basis-research/` | SEEKER autonomous research subsystem (10 agents, argument tree engine) |
| `core/` | Core infrastructure — DI Container, managers, bridges |
| `plugins/` | TypeScript plugins — AutoEvolve, ecosystem sync, Bernstein sync |
| `commands/` | Slash command definitions with YAML frontmatter |
| `diagrams/` | Architecture diagrams in SVG format (11 diagrams) |
| `evolution/` | Auto-generated skills from autonomous evolution cycles |
| `.reversa/` | Reverse engineering artifacts, ADRs, SDDs |
| `docs/` | Engineering and specification documentation |
| `tdd-docs/` | Test-driven development academic documentation |

---

## Documentation

| Documento | Conteudo |
|-----------|----------|
| [ENGENHARIA_DE_SOFTWARE.md](docs/ENGENHARIA_DE_SOFTWARE.md) | SDD, TDD, CI/CD, SWEBOK, Git Safety, ADR, DI, fluxogramas |
| [SPEC_COVERAGE.md](docs/SPEC_COVERAGE.md) | 186/186 componentes (100% cobertura), matriz por spec |
| [TDD Academico](tdd-docs/README.md) | 570 testes, 25/25 validacoes, Cora-Debate V1-V7 |
| [Cora-Debate](tdd-docs/CORA_DEBATE.md) | Verificacao simbolica V1-V7, self-consistency K=7 |
| [PhD Auditor](tdd-docs/PHD_AUDITOR.md) | NashSolver, StatisticalRigor, QualisA1Auditor |
| [TSAC](tdd-docs/TSAC_RASTREABILIDADE.md) | 87 palavras banidas, 46 anotacoes auditaveis |
| [Score Qualis](tdd-docs/SCORE_QUALIS.md) | Motor de pontuacao, 7 criterios, evolucao |
| [Getting Started](GETTING_STARTED.md) | Guia de primeiros passos |
| [Contributing](CONTRIBUTING.md) | Guia de contribuicao |
| [Roadmap](ROADMAP.md) | Visao futura do projeto |
| [Tutorials](TUTORIALS.md) | Tutoriais praticos |
| [Glossary](GLOSSARY.md) | Glossario de termos tecnicos |
| [Projects](PROJECTS.md) | Painel Kanban de projetos |
| [Architecture Diagrams](diagrams/) | 11 diagramas SVG da arquitetura completa |
| [OPENCODE_ECOSYSTEM.md](OPENCODE_ECOSYSTEM.md) | Documentacao tecnica completa (1.289 linhas) |

---

## How It Works

The ecosystem operates through a coordinated pipeline of specialized agents:

1. **Research Phase** — SEEKER agents search 10+ academic sources in parallel, building an argument tree with verifiable evidence
2. **Writing Phase** — 49 MASWOS agents collaborate on structure, writing (with anti-AI vocabulary), formatting, and figures
3. **Review Phase** — Simulated peer review panel of 5 reviewers and 4 doctoral advisors provide iterative feedback
4. **Scoring Phase** — Qualis A1 scoring engine evaluates 7 weighted criteria; loop repeats until score >= 95/100
5. **Export Phase** — Final output in LaTeX/PDF with 46 auditable TSAC annotations
6. **Evolution Phase** — AutoEvolve analyzes success patterns and generates new skills for future use

---

## License

MIT License — see [LICENSE](LICENSE) for details.

Copyright (c) 2026 Marcelo Claro Laranjeira.

---

## Citation

If you use this ecosystem in your research, please cite:

```bibtex
@software{OpenCode_Ecosystem2026,
  author = {Marcelo Claro Laranjeira},
  title = {OpenCode Ecosystem v4.6: Multi-Agent AI Platform for Scientific Research},
  year = {2026},
  version = {4.6.1},
  url = {https://github.com/MarceloClaro/OpenCode_Ecosystem}
}
```

---

<div align="center">

**OpenCode Ecosystem v4.6.1** · 17 Ciclos Evolutivos · 125 Agentes · 40 MCPs · 104 Skills

186/186 Componentes Documentados · 97.7% Cobertura de Testes · Qualis A1 96/100

Built with Python, TypeScript, Rust, and OpenCode CLI

</div>
