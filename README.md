<div align="center">

# OpenCode Ecosystem v4.6.1

### Multi-Agent AI Platform for Assisted Scientific Research

**Ultima atualizacao: 2026-05-30** · 17 Iteracoes · 79 Agentes · 38 MCPs · 104 Skills · **CORA-Score 3.04 (M4)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Node.js 20+](https://img.shields.io/badge/Node.js-20+-green.svg)](https://nodejs.org/)
[![Agents](https://img.shields.io/badge/Agents-79-6366f1?style=flat-square)](agents/)
[![MCPs](https://img.shields.io/badge/MCP_Servers-38-0ea5e9?style=flat-square)](opencode.json)
[![Skills](https://img.shields.io/badge/Skills-104-10b981?style=flat-square)](skills/)
[![Tests](https://img.shields.io/badge/Testes-154/156-22c55e?style=flat-square)](https://github.com/MarceloClaro/CORA-Eval-Dissertacao)
[![CORA-Score](https://img.shields.io/badge/CORA--Score-3.04_M4-e11d48?style=flat-square)](https://github.com/MarceloClaro/CORA-Eval-Dissertacao)

</div>

---

## Sobre

O **OpenCode Ecosystem** e uma plataforma multi-agente para pesquisa cientifica assistida. Diferente de sistemas que dependem de um unico modelo, este ecossistema coordena **79 agentes especializados**, **38 servidores MCP** e **104 skills** que colaboram, debatem e verificam resultados entre si.

A arquitetura de 6 camadas com injecao de dependencia suporta um pipeline academico que vai da busca autonoma em fontes academicas (arXiv, PubMed, OpenAlex, Semantic Scholar, CORE, Sci-Hub) ate a geracao de artigos com exportacao LaTeX/PDF, passando por revisao simulada por pares e verificacao formal multi-agente.

Este projeto e um trabalho em andamento. Muitos componentes estao em estagio experimental e as metricas reportadas sao auto-avaliadas pelo proprio sistema, nao por auditores externos.

---

## CORA-Eval — Maturidade Cientifica

O ecossistema e validado pelo **CORA-Eval**, benchmark de 150 tarefas em 10
dimensoes × 4 niveis (Basico a Pesquisa). Resultados da execucao real:

| Metrica | Valor |
|---------|:-----:|
| CORA-Score bruto | **3.04** (Pesquisa, M4) `[auto-reportado]` |
| Validacao externa (Project Euler + Rosalind) | **34/34 (100%)** |
| Testes internos (11 suites) | **154/156 (98.7%)** |
| Calibracao V1-V7 (F1 medio) | **95.5%** (466 testes) |
| Cross-Validation K=10 | **CV=2.2%** |
| Dimensoes em N4 (Pesquisa) | **5** (D1, D2, D3, D7, D10) |

> **Repositorio:** [CORA-Eval-Dissertacao](https://github.com/MarceloClaro/CORA-Eval-Dissertacao)

### SPECs Ativas (11)

| SPEC | Descricao | CTs | TDD |
|:----:|-----------|:---:|:---:|
| SPEC-001 | Orchestration Pipeline | 9 | ✅ |
| SPEC-002 | Academic Output (MASWOS) | 9 | ✅ |
| SPEC-003 | MCP Integration | 9 | ✅ |
| SPEC-004 | Quantum Computing | 8 | ✅ |
| SPEC-005 | Reverse Engineering | 8 | ✅ |
| SPEC-006 | Data Orchestration | 9 | ✅ |
| SPEC-007 | Evolution Engine | 8 | ✅ |
| SPEC-008 | Triangulacao Anti-Circularidade | 9 | 14/14 ✅ |
| SPEC-009 | D1 — Raciocinio Matematico | 8 | 12/12 ✅ |
| SPEC-010 | D2 — Modelagem Fisica | 8 | 8/8 ✅ |
| SPEC-011 | D9 — Metodologia Experimental | 8 | 15/15 ✅ |

---

## Componentes

### Agentes (79 arquivos em `agents/`)

| Grupo | Quantidade | Descricao |
|-------|:----------:|-----------|
| Core | 56 | Orquestracao, debugging, revisao, documentacao |
| MASWOS (criador-artigo) | — | 49 agentes definidos em `criador-artigo/agents/` |
| SEEKER (basis-research) | — | 12 agentes definidos em `basis-research/agents/` |
| Reversa + Corretor | 8 | Engenharia reversa e correcao linguistica |
| Utilitarios | 15 | Browser, imagem, busca, dados |

> **Nota:** Os 125 agentes mencionados em documentacao interna referem-se ao total incluindo definicoes distribuidas em `criador-artigo/agents/` e `basis-research/agents/`. O diretorio `agents/` contem 79 definicoes diretas.

### MCP Servers (38 configurados em `opencode.json`)

| Categoria | Quantidade | Exemplos |
|-----------|:----------:|----------|
| Infraestrutura | 12 | filesystem, github, sqlite, sequential-thinking |
| Busca | 8 | websearch, gh_grep, context7, scihub |
| Codigo | 6 | eslint, diff, code-runner, playwright |
| Dados | 8 | fetch, pdf, time, node-sandbox |
| Dominio | 4 | memory, decisionnode, antigravity |

### Skills (104 diretorios em `skills/`)

| Categoria | Quantidade | Destaques |
|-----------|:----------:|-----------|
| Research | 25 | academic-export-abnt, editais-br, academic-ml-pipeline |
| System | 18 | code-review, reasoning-orchestrator, pypi-scout |
| Juridico | 7 | edicao-cirurgica, pecas-juridicas-html, triagem-juridica |
| Agente | 8 | agent-forum, cora-debate, coder-agent, ws-coder |
| Tooling | 16 | mcp-builder, log-analyzer, browser-use |
| Dados | 8 | graph-builder-pipeline, entity-ner-reader, fs-ipc |
| Workflows | 6 | plan-protocol, planning-with-files |
| Outros | 16 | frontend, social, marketing, superpowers |

---

## Pipeline Academico (MASWOS + SEEKER)

```
SEEKER (pesquisa) --> MASWOS (escrita, 49 agentes, 8 estagios)
  --> Anti-AI (TSAC, 87 palavras banidas)
  --> Banca simulada (5 revisores + 4 orientadores)
  --> Correcao iterativa (loop ate score >= 95/100)
  --> Exportacao LaTeX/PDF
  --> Verificacao CJK (ptbr_corrector.py)
```

### Cora-Debate V1-V7 (verificacao simbolica interna)

| Verificador | Funcao | Confianca (auto-reportada) |
|:-----------:|--------|:--------------------------:|
| V1 | Consistencia Logica | 0.98 |
| V2 | Coerencia Semantica | 0.95 |
| V3 | Validacao de Referencias | 0.97 |
| V4 | Rigor Estatistico | 0.96 |
| V5 | Correlacao Cruzada | 0.94 |
| V6 | Completude | 0.93 |
| V7 | Originalidade | 0.99 |

> **Nota:** As pontuacoes de confianca acima sao metricas internas do sistema, calculadas pelo proprio Cora-Debate via self-consistency (K=7) com calibracao Platt. Nao representam validacao externa independente.

### PhD Auditor (modulo de verificacao estatistica)

- **NashSolver:** Equilibrio Nash em jogos NxM (algoritmo Lemke-Howson)
- **StatisticalRigor:** Cohen's d, correcao Bonferroni, power analysis (1-beta)
- **QualisA1Auditor:** Motor interno de pontuacao baseado em 7 criterios academicos
- **SensitivityAnalyzer:** Analise de sensibilidade OAT (One-At-a-Time)
- **IMRADFormatter:** Formatacao IMRAD canonica com filtro anti-AI

> **Nota sobre o score Qualis A1:** A pontuacao 96/100 e gerada pelo motor interno `AUTO_SCORE_QUALIS.py` e nao por uma banca Qualis/CAPES real. E uma metrica de auto-avaliacao usada como criterio de parada no loop de correcao iterativa. O threshold de 95/100 e uma meta interna do pipeline.

---

## Ciclos de Desenvolvimento (17 iteracoes)

O ciclo de desenvolvimento do ecossistema e incremental: cada iteracao adiciona capacidades com base nos resultados da iteracao anterior. Scores abaixo sao auto-atribuidos pelo motor `AUTO_SCORE_QUALIS.py`.

### Iteracao 1 — Integracao com World Bank API
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 85/100 |
| Skills adicionadas | cross-validation-quantitativa, world-bank-data-analysis |
| Resultado | 27 indicadores analisados em 50 paises; bootstrap com 10.000 reamostragens |
| Observacao | Educacao r=-0,03 (correlacao quase nula com inovacao); P&D privado r=+0,73 |

### Iteracao 2 — Pipeline de Artigo
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 90/100 |
| Skills adicionadas | pipeline-artigo-academico |
| Resultado | Artigo 35 paginas ABNT com 26 referencias e DOIs; exportacao LaTeX |

### Iteracao 3 — TSAC + Sci-Hub
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 92/100 |
| Skills adicionadas | tsac-rastreabilidade, scihub-paper-downloader |
| Resultado | Sistema de citacao rastreavel (DOI + hash SHA256); 46 anotacoes TSAC; 87 palavras banidas |

### Iteracao 4 — Sci-Hub MCP
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 88/100 |
| Skills adicionadas | scihub-mcp-server, scihub-search-enhanced |
| Resultado | Servidor MCP para Sci-Hub; busca paralela arXiv + Sci-Hub |

### Iteracao 5 — Cross-Validation
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 92/100 |
| Skills adicionadas | cross-validation-quantitativa v2 |
| Resultado | Pearson, Spearman, Kendall; 50 indicadores (World Bank, WHO, FAO, UNESCO) |

### Iteracao 6 — Correcao Iterativa
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 95/100 |
| Skills adicionadas | iterative-correction-loop |
| Resultado | Banca simulada: 5 revisores + 4 orientadores; score 86,5 -> 92,7 apos 3 iteracoes |

### Iteracao 7 — Detector CJK
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 96/100 |
| Skills adicionadas | ptbr-corrector, token-efficiency |
| Resultado | ptbr_corrector.py; deteccao CJK zero-tolerance; 8 regras de eficiencia de tokens |

### Iteracao 8 — Progressive Disclosure
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 98/100 |
| Skills adicionadas | progressive-disclosure-design, agent-observability-monitor |
| Resultado | Padrao SKILL.md <= 2.5KB; health score 96/100; 89/104 skills em conformidade |

### Iteracao 9 — SDD+TDD Pipeline
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 94/100 |
| Skills adicionadas | sdd-tdd-pipeline, simulacao-arguicao |
| Resultado | 7 specs; 9 CTs; 3 ADRs DecisionNode; 16 perguntas de banca simuladas |

### Iteracao 10 — LaTeX Refino
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 96/100 |
| Skills adicionadas | latex-refino, framework-docs |
| Resultado | 4 overfulls eliminados; fix_history catalog; docstrings expandidas |

### Iteracao 11 — Menu Adaptativo
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 96/100 |
| Skills adicionadas | menu-adaptativo, plugin-system |
| Resultado | Menu de 11 opcoes fixas para auto-descoberta; .menu_registry.json |

### Iteracao 12 — Antigravity Bridge
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 98/100 |
| Skills adicionadas | antigravity-integration, antigravity-bridge.ts |
| Resultado | Delegacao de imagem, browser, busca web para Google DeepMind |

### Iteracao 13 — PyPI Scout
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 95/100 |
| Skills adicionadas | pypi-scout, ecosystem-hooks |
| Resultado | CLI 7 comandos; catalogo 22+ bibliotecas; matriz de afinidade |

### Iteracao 14 — DataOrchestrator
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 97/100 |
| Skills adicionadas | data-orchestrator, multi-domain-hooks |
| Resultado | 8 dominios de dados; 30+ bibliotecas; QueryIntent com 80+ keywords |

### Iteracao 15 — Auditoria + UX
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 95/100 |
| Skills adicionadas | auditoria-caixa-branca, ux-refinamento |
| Resultado | 9 componentes de auditoria; scorecards; alertas de orcamento |

### Iteracao 16 — Teoria dos Jogos
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 96/100 |
| Skills adicionadas | reasoning-orchestrator-v9, game-theory-agents |
| Resultado | 10 estrategias de teoria dos jogos (Nash, Minimax, Shapley, etc.) |

### Iteracao 17 — CORA-Eval Benchmark
| Metrica | Valor |
|---------|-------|
| Score auto-atribuido | 97/100 |
| Skills adicionadas | cora-eval-benchmark, cora-benchmark-tracker |
| Resultado | 150 tarefas em 10 dimensoes; baseline CORA-Score 0.67 |

---

## Progressao (auto-reportada)

| Metrica | Inicio (~v1.0) | Atual (~v4.6.1) | Variacao |
|---------|:--------------:|:---------------:|:--------:|
| Skills | 20 | 104 | +84 |
| Agentes em agents/ | ~25 | 79 | +54 |
| MCPs configurados | 12 | 38 | +26 |
| Testes | ~200 | 557 passando | +357 |
| Iteracoes de desenvolvimento | 1 | 17 | +16 |

---

## Limitacoes Conhecidas

- **Scores auto-atribuidos:** As pontuacoes Qualis A1 e confianca Cora-Debate sao geradas internamente. Nao ha validacao externa independente.
- **Cobertura de testes:** Reportada em 97.7% com base em metricas internas. A suite de testes cobre principalmente o Container DI e servicos core.
- **Estagio experimental:** Varios componentes (quantum, evolucao autonoma, MiroFish/BettaFish) estao em estagio inicial de desenvolvimento.
- **Dependencia de modelo externo:** O sistema depende do modelo `deepseek-v4-pro` (gratuito) como backend LLM. Mudancas no modelo podem afetar resultados.
- **Plataforma principal Windows 11:** Suporte para Linux/macOS e experimental.
- **Repositorio contem artefatos:** Diretorios como `OpenCode_Ecosystem-main/`, `.reversa/`, `MembrosDoCanal-main/` contem copias e artefatos de desenvolvimento que aumentam o tamanho do repositorio.

---

## Estrutura do Repositorio

| Diretorio/Arquivo | Descricao |
|-------------------|-----------|
| `agents/` | 79 definicoes de agentes em Markdown com frontmatter YAML |
| `skills/` | 104 skills com padrao progressive disclosure |
| `nexus/` | Orquestrador multi-agente Nexus (scripts Python, core, dashboard) |
| `quantum/` | Modulo de computacao quantica — VQC, QML, ZNE/PEC |
| `criador-artigo/` | Pipeline academico MASWOS — 49 agentes em `agents/` |
| `basis-research/` | Subsistema SEEKER de pesquisa autonoma |
| `core/` | Infraestrutura core — Container DI, gerenciadores, bridges |
| `plugins/` | Plugins TypeScript — AutoEvolve, sync, bridges |
| `commands/` | 29 definicoes de comandos slash |
| `diagrams/` | 11 diagramas SVG de arquitetura |
| `evolution/` | Registros das 17 iteracoes de desenvolvimento |
| `docs/` | Documentacao de engenharia de software |
| `tdd-docs/` | Documentacao de TDD academico |
| `tests/` | Suite de testes (25 arquivos, `core/` + `nexus/`) |
| `opencode.json` | Configuracao principal (556 linhas, 38 MCPs, agentes, skills) |
| `AGENTS_PTBR.md` | Documentacao de agentes em Portugues Brasileiro |
| `OPENCODE_ECOSYSTEM.md` | Documentacao tecnica completa (1.289 linhas) |

---

## Documentacao

| Documento | Conteudo |
|-----------|----------|
| [ENGENHARIA_DE_SOFTWARE.md](docs/ENGENHARIA_DE_SOFTWARE.md) | SDD, TDD, CI/CD, SWEBOK, Git Safety, ADR, arquitetura 6 camadas |
| [SPEC_COVERAGE.md](docs/SPEC_COVERAGE.md) | 186 componentes documentados, matriz por especificacao |
| [TDD Academico](tdd-docs/README.md) | 557 testes, 25/25 validacoes, pipeline de validacao |
| [Cora-Debate](tdd-docs/CORA_DEBATE.md) | Verificacao simbolica V1-V7, self-consistency K=7 |
| [PhD Auditor](tdd-docs/PHD_AUDITOR.md) | NashSolver, StatisticalRigor, QualisA1Auditor |
| [TSAC](tdd-docs/TSAC_RASTREABILIDADE.md) | Sistema de citacao rastreavel, 87 palavras banidas |
| [Score Qualis](tdd-docs/SCORE_QUALIS.md) | Motor de pontuacao, 7 criterios, historico |
| [Primeiros Passos](GETTING_STARTED.md) | Guia de instalacao e primeiro uso |
| [Contribuicao](CONTRIBUTING.md) | Guia para contribuidores |
| [Roadmap](ROADMAP.md) | Planejamento futuro |
| [Tutoriais](TUTORIALS.md) | Tutoriais praticos |
| [Glossario](GLOSSARY.md) | Termos tecnicos |
| [Projetos](PROJECTS.md) | Painel de projetos |
| [Diagramas](diagrams/) | 11 diagramas SVG |
| [Doc. Tecnica Completa](OPENCODE_ECOSYSTEM.md) | 1.289 linhas de documentacao |
| [Referencias](REFERENCIAS.md) | 50 referencias com DOIs reais e verificaveis (13 categorias) |
| [Integridade e Auditabilidade](INTEGRIDADE.md) | Principio obrigatorio — 8 raciocinios, 5 faces, 25 regras |
| [Avaliacao de Maturidade](https://github.com/MarceloClaro/CORA-Eval-Dissertacao/blob/main/AVALIACAO_MATURIDADE_20260530.md) | Resultados da execucao real — 154/156 testes (98.7%) |
| [Triangulacao Anti-Circularidade](https://github.com/MarceloClaro/CORA-Eval-Dissertacao/blob/main/TRIANGULACAO_ANTI_CIRCULARIDADE.md) | Framework SPEC-008 — 15 refs com DOI |
| [Dissertacao CORA-Eval](https://github.com/MarceloClaro/CORA-Eval-Dissertacao) | Repositorio completo — artigos, TDD, avaliacoes, PDF 142p |

---

## Instalacao

```bash
git clone https://github.com/MarceloClaro/OpenCode_Ecosystem.git
cd OpenCode_Ecosystem
bun install
pip install -r requirements.txt
opencode init
```

### Pre-requisitos

| Dependencia | Versao |
|-------------|--------|
| Node.js | 20+ |
| Bun | 1.3+ |
| Python | 3.12+ |
| OpenCode CLI | 1.14+ |

### Comandos principais

```bash
opencode run /artigo    # Pipeline academico
opencode run /reversa   # Engenharia reversa
opencode run /quantum   # Computacao quantica
opencode run /evolve    # Evolucao autonoma
```

---

## Licenca

MIT License — veja [LICENSE](LICENSE).

Copyright (c) 2026 Marcelo Claro Laranjeira · marceloclaro@gmail.com · Prefeitura Municipal de Crateus/CE — [ORCID: 0000-0001-8996-2887](https://orcid.org/0000-0001-8996-2887).

---

## Citacao

```bibtex
@software{OpenCode_Ecosystem2026,
  author = {Marcelo Claro Laranjeira},
  orcid = {0000-0001-8996-2887},
  affiliation = {Secretaria de Educacao, Prefeitura Municipal de Crateus, Ceara, Brasil},
  title = {OpenCode Ecosystem: Multi-Agent AI Platform for Assisted Scientific Research},
  year = {2026},
  version = {4.6.1},
  url = {https://github.com/MarceloClaro/OpenCode_Ecosystem}
}
```

---

<div align="center">

**OpenCode Ecosystem v4.6.1** · 17 Iteracoes de Desenvolvimento · 79 Agentes · 38 MCPs · 104 Skills

Trabalho em andamento — metricas auto-reportadas

Autor: Marcelo Claro Laranjeira — [ORCID: 0000-0001-8996-2887](https://orcid.org/0000-0001-8996-2887)

Professor / Pedagogo — Secretaria de Educacao, Prefeitura Municipal de Crateus, Ceara, Brasil

Contato: marceloclaro@gmail.com | +55 (88) 981587145

</div>
