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
- [Getting Started Guide](GETTING_STARTED.md) — Detailed setup instructions
- [Contributing Guide](CONTRIBUTING.md) — How to contribute to the ecosystem
- [Architecture Diagrams](diagrams/) — 10 SVG diagrams of the full architecture

---

## How It Works

The ecosystem operates through a coordinated pipeline of specialized agents:

1. **Research Phase** — SEEKER agents search 10+ academic sources in parallel, building an argument tree with verifiable evidence
2. **Writing Phase** — 49 MASWOS agents collaborate on structure, writing (with anti-AI vocabulary), formatting, and figures
3. **Review Phase** — Simulated peer review panel of 5 reviewers and 4 doctoral advisors provide iterative feedback
4. **Scoring Phase** — Qualis A1 scoring engine evaluates 10 weighted criteria; loop repeats until score ≥ 95/100
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
