# Antiprojeto UFC — PPGTE/UFC

**Inteligência Artificial Multiagente no Ensino Superior: Um Guia Prático para Pesquisa Científica Assistida e Ética**

[![Tests](https://img.shields.io/badge/Testes-327/327_100%25-22c55e?style=flat-square)]()
[![SWOT](https://img.shields.io/badge/SWOT-100/100-8b5cf6?style=flat-square)]()
[![CORA-Score](https://img.shields.io/badge/CORA--Score-3.04_M4-e11d48?style=flat-square)]()
[![SPECs](https://img.shields.io/badge/SPECs-12-6366f1?style=flat-square)]()

---

## Sobre

Este repositório contém o **anteprojeto de pesquisa** submetido ao Programa de Pós-Graduação em Tecnologia Educacional (PPGTE/UFC), Edital nº 01/2026, e toda a infraestrutura de desenvolvimento do **OpenCode Ecosystem v4.7.1** que o fundamenta.

A pesquisa propõe o desenvolvimento e validação de um guia prático de uso ético de uma plataforma de **IA multiagente de código aberto** (125 agentes especializados, 212+ tipos de raciocínio, 600+ integrações) como ferramenta de suporte à pesquisa científica assistida, em conformidade com a LGPD e as normativas de integridade acadêmica da UFC.

---

## Eixos de Pesquisa

| Eixo | Descrição | Status |
|------|-----------|--------|
| **Anteprojeto PPGTE** | Guia prático de IA multiagente para pesquisa ética | Submetido (Edital 01/2026) |
| **Monografia (Direito)** | Proteção da Personalidade Humana na era da IA — Contribuições da Encíclica Magnifica Humanitas | Manuscrito completo (91 pág.) |
| **OpenCode Ecosystem** | Plataforma multiagente com raciocínio científico verificável | v4.7.1 — 327/327 testes GREEN |

---

## Funcionalidades Principais

- **125 agentes especializados** — 56 core + 49 criação + 12 SEEKER + 18 Reversa
- **212+ tipos de raciocínio** em 27 categorias (lógico, dialético, estatístico, teoria dos jogos...)
- **CORA-Eval** — Benchmark com 150 tarefas em 10 dimensões x 4 níveis
- **SEEKER** — Agente de pesquisa com varredura em 10+ fontes acadêmicas (arXiv, OpenAlex, PubMed, CORE)
- **PhD Auditor** — Validação estatística (Nash, Cohen, Bonferroni) com padrão Qualis A1
- **Cora-Debate** — Arquitetura de debate multiagente com 7 verificadores simbólicos V1-V7
- **4 Motores de Raciocínio** — Z3 (prova formal), SymPy (simbólico), miniKanren (lógico), Critical (falácias)
- **46 MCPs** — Conectores com GitHub, PubMed, Sci-Hub, Playwright, SQLite, PDF e mais
- **Pesquisa de Editais** — Busca inteligente em 25 subdimensões com 52 editais curados (CNPq/CAPES/FINEP)
- **Pesquisa Jurisprudencial** — CLI automatizada via API Jurisprudencias.ai com cache SHA256 para consultas no STJ, STF e demais tribunais
- **Pipeline de Escrita** — SEEKER → MASWOS → AutoScore → Corretor PT-BR → Banca Simulada

---

## Estrutura do Projeto

```
/
├── anteprojeto_abntex2.tex      # Anteprojeto em LaTeX (ABNT)
├── ANTEPROJETO_PPGTE_2026.md    # Versão markdown do anteprojeto
├── dissertacao_opencode_*.tex   # Dissertação do ecossistema
├── artigo/                      # Submódulo — artigo científico CORA-Eval v4.7.1
├── manuscrito/                  # Monografia de Direito (LaTeX)
├── pesquisa/                    # Fichamentos e materiais de pesquisa
├── docs/                        # Documentação do ecossistema
├── scripts/                     # Scripts de automação
├── specs/                       # Especificações TDD
├── diagrams/                    # Diagramas de arquitetura
├── templates/                   # Templates diversos
├── evolution/                   # Insights do AutoEvolve
├── thoughts/                    # Registro de planejamento e decisões
├── .evolve/                     # Logs de observabilidade do ecossistema
├── .evidence/                   # Evidências de validação
└── .reversa/                    # Pipeline de engenharia reversa
```

---

## Histórico de Commits Recentes

| Commit | Descrição |
|--------|-----------|
| `28bcf7d` | Submodule artigo v4.7.1 — 327/327 GREEN, validação expandida |
| `8eb21d3` | v4.7.1 — SWOT+TDD 100/100, 13 recomendações implementadas |
| `20ae626` | Revisão de redação e conformidade ABNT |
| `224b621` | Finalização da estruturação e redação do manuscrito |
| `fff1bcc` | Cross-correlation: Superhuman/Aletheia x OpenCode — 12 dimensões, 67% vantagem |
| `f0349b9` | Aletheia Math Research — SPEC-012, 71/71 TDD, L2 PUBLISHABLE |
| `9343174` | Sync: evolve log + submodule ref |
| `22a5a45` | Init: Antiprojeto UFC — PPGTE/UFC — OpenCode Ecosystem v4.3.0 |

---

## Como Usar

### Pré-requisitos
- **Node.js** v25+
- **Bun** 1.3+
- **OpenCode CLI** 1.14+
- **LaTeX** (abnTeX2) para compilação dos documentos acadêmicos

### Compilar o Anteprojeto
```bash
pdflatex anteprojeto_abntex2.tex
biber anteprojeto_abntex2
pdflatex anteprojeto_abntex2.tex
```

### Compilar a Dissertação
```bash
pdflatex dissertacao_opencode_ecosystem.tex
biber dissertacao_opencode_ecosystem
pdflatex dissertacao_opencode_ecosystem.tex
```

### Validar o Ecossistema
```bash
python tdd_academic_validator.py    # Validação TDD
python simulacao_cora_debate.py     # Simulação Cora-Debate
python cross_correlation.py         # Correlação cruzada
```

---

## Autor

**Marcelo Claro Laranjeira** — [ORCID: 0000-0001-8996-2887](https://orcid.org/0000-0001-8996-2887)

Professor/Pedagogo — Secretaria de Educação, Prefeitura Municipal de Crateús, Ceará, Brasil

---

## Licença

Este projeto está licenciado sob a licença **MIT** — veja o arquivo LICENSE para detalhes.

---

<div align="center">

# OpenCode Ecosystem — Multi-Agent AI Platform for Scientific Research

**Version 4.6** · Multi-Agent Orchestration · Formal Verification · Autonomous Evolution

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Node.js 20+](https://img.shields.io/badge/Node.js-20+-green.svg)](https://nodejs.org/)
[![Agents](https://img.shields.io/badge/Agents-125+-6366f1?style=flat-square)](agents/)
[![MCPs](https://img.shields.io/badge/MCP_Servers-40+-0ea5e9?style=flat-square)](opencode.json)
[![Skills](https://img.shields.io/badge/Skills-100+-10b981?style=flat-square)](skills/)
[![Qualis A1](https://img.shields.io/badge/Qualis_A1-95/100-22c55e?style=flat-square)](criador-artigo/)
[![Reasoning Types](https://img.shields.io/badge/Reasoning_Types-350+-f59e0b?style=flat-square)](skills/agent-forum/)

</div>

---

## Overview

The **OpenCode Ecosystem** is a multi-agent AI platform designed for assisted scientific research. Unlike monolithic AI systems that rely on a single model, this ecosystem orchestrates **125+ specialized agents**, **40+ MCP servers**, and **100+ skills** that collaborate, debate, and verify each other's results to produce academically rigorous outputs.

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
| **TDD Academic** | 25/25 test-driven development validation for research reproducibility |
| **AutoEvolve** | Autonomous ecosystem evolution engine that generates new skills from success patterns |

---

## Architecture Diagram

```
                    ┌──────────────────────────────────────┐
                    │         USER INTERFACE (CLI)          │
                    │   /artigo  /reversa  /quantum /evolve │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │   MCP LAYER: 40+ Servers              │
                    │   websearch · filesystem · sqlite     │
                    │   code-runner · pdf · github · fetch  │
                    │   playwright · sequential-thinking    │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │   AGENT LAYER: 125+ Agents            │
                    │   Core (56) · MASWOS (49) · SEEKER   │
                    │   (12) · Reversa (7) · Corrector (1) │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │   SKILL LAYER: 100+ Skills            │
                    │   Progressive disclosure (≤2.5KB)     │
                    │   system · research · juridico · ... │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │   REASONING LAYER: 350+ Types         │
                    │   35 categories across 6 families:    │
                    │   Logical · Dialectical · Game Theory │
                    │   Decision · Strategic · Innovation   │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │   VERIFICATION LAYER                  │
                    │   Cora-Debate V1-V7 · PhD Auditor     │
                    │   Nash Solver · Qualis A1 Auditor     │
                    │   Statistical Rigor · Sensitivity     │
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
| `skills/` | 100+ specialized skills with progressive disclosure pattern |
| `nexus/` | Nexus NMA v6.2 multi-agent orchestrator (63 Python scripts) |
| `quantum/` | Quantum computing module — VQC, QML, ZNE/PEC error mitigation |
| `criador-artigo/` | MASWOS academic pipeline — 49 agents for Qualis A1 article generation |
| `basis-research/` | SEEKER autonomous research subsystem (10 agents, argument tree engine) |
| `core/` | Core infrastructure — DI Container, managers, bridges |
| `plugins/` | TypeScript plugins — AutoEvolve, ecosystem sync, Bernstein sync |
| `commands/` | Slash command definitions with YAML frontmatter |
| `diagrams/` | Architecture diagrams in SVG format |
| `evolution/` | Auto-generated skills from autonomous evolution cycles |
| `.reversa/` | Reverse engineering artifacts, ADRs, SDDs |
| `docs/` | Engineering and specification documentation |
| `tdd-docs/` | Test-driven development academic documentation |

---

## Documentation

- [Engineering Documentation](docs/ENGENHARIA_DE_SOFTWARE.md) — Architecture, SDD, TDD, CI/CD, SWEBOK
- [Spec Coverage](docs/SPEC_COVERAGE.md) — 186/186 components (100% coverage)
- [TDD Academic Documentation](tdd-docs/) — Test-driven development for research

---

## How It Works

The ecosystem operates through a coordinated pipeline of specialized agents:

1. **Research Phase** — SEEKER agents search 10+ academic sources in parallel, building an argument tree with verifiable evidence
2. **Writing Phase** — 49 MASWOS agents collaborate on structure, writing (with anti-AI vocabulary), formatting, and figures
3. **Review Phase** — Simulated peer review panel of 5 reviewers and 4 doctoral advisors provide iterative feedback
4. **Scoring Phase** — Qualis A1 scoring engine evaluates 10 weighted criteria; loop repeats until score >= 95/100
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
  title = {OpenCode Ecosystem: Multi-Agent AI Platform for Scientific Research},
  year = {2026},
  url = {https://github.com/MarceloClaro/OpenCode_Ecosystem}
}
```

---

<div align="center">

**OpenCode Ecosystem v4.6** · Built with Python, TypeScript, and OpenCode CLI

</div>
