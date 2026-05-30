# Changelog

Todas as mudancas notaveis do OpenCode Ecosystem documentadas neste arquivo.

---

## [v4.6.1] — 2026-05-30

### Adicionado
- Diretorio `docs/` com documentacao completa de engenharia de software
  - `ENGENHARIA_DE_SOFTWARE.md`: SDD, TDD, CI/CD, SWEBOK, Git Safety, ADR, DI, fluxogramas, tabelas (500+ linhas)
  - `SPEC_COVERAGE.md`: 186/186 componentes documentados (100% cobertura), matriz por subsistema
- Diretorio `tdd-docs/` com documentacao de TDD academico
  - `README.md`: 570 testes, 25/25 validacoes, pipeline de validacao continua
  - `CORA_DEBATE.md`: verificacao simbolica V1-V7, self-consistency K=7, calibracao Platt
  - `PHD_AUDITOR.md`: NashSolver, StatisticalRigor, QualisA1Auditor, SensitivityAnalyzer
  - `TSAC_RASTREABILIDADE.md`: 87 palavras banidas, 46 anotacoes auditaveis, matriz de substituicao
  - `SCORE_QUALIS.md`: motor de pontuacao, 7 criterios ponderados, historico de scores
- Diagrama SVG `engineering-architecture.svg`: arquitetura 6 camadas L1-L6 com gradientes
- README.md expandido com 17 ciclos evolutivos detalhados, metricas do ecossistema, relatorio tecnico, timeline
- CHANGELOG.md expandido com todos os ciclos evolutivos

### Modificado
- README.md: versao 4.6.1, tabela de metricas, relatorio tecnico, 17 ciclos evolutivos, timeline
- Links quebrados corrigidos (docs/ e tdd-docs/ agora existem)

---

## [v4.6.0] — 2026-05-26

### Adicionado — Taxonomia 350+ Raciocinios + Creative Leap + Contraprova
- Taxonomia expandida de 38 para 350+ tipos de raciocinio em 35 categorias
- Creative Leap Generator: geracao autonoma de 4 novos raciocinios (R201-R204)
  - R201: Cost-Benefit (trade-off estruturado com funcao utilidade)
  - R202: Fairness-Rawls (maximin sobre utilidades dos agentes menos favorecidos)
  - R203: Stability-Lyapunov (analise de estabilidade via funcao de Lyapunov)
  - R204: Emergence (propriedades coletivas nao redutiveis a partes individuais)
- Orquestrador definitivo 7 fases (Classify → Select → Activate → Execute → Verify → Calibrate → Learn)
- Validacao IMO: 10 problemas reais, PCI medio 99/100, Cohen's d 5.37
- Contraprova geometria simpletica: PCI 100/100, 4 identidades via calculo exterior
- Artigo ABNT 40 paginas/44 referencias com trilha de auditoria
- Novos agentes: ConsensusEngine, TemperatureController, BellmanEngine, ChemistryAgent, SymPy Physics Engine, 5 GameTheoryAgents
- CORA-Eval Benchmark: 150 tarefas x 10 dimensoes x 4 niveis, baseline CORA-Score 0.67
- Q-Score UCB1 para selecao adaptativa de tarefas pendentes

---

## [v4.2.3] — 2026-05-19
### Adicionado — PyPI Scout + DataOrchestrator + Multi-Domain Hooks
- PyPI Scout: 22+ bibliotecas curadas, matriz de afinidade 5 pipelines, CLI 7 comandos
- DataOrchestrator: linguagem natural → 8 dominios de dados, 592 linhas
- 10 Ecosystem Hooks v2.0 (R8:5 + R9:5)
- 30+ bibliotecas Python instaladas (yfinance, ccxt, fredapi, biopython, pysus, etc.)
- 12 novas bibliotecas em 6 dominios
- 20+ fontes Qualis A1
- Artigo LaTeX ABNT 12 paginas
- 3 fluxogramas SVG

---

## [v4.2.2] — 2026-05-16
### Adicionado — Antigravity Bridge + Skills Refinement
- Plugin `antigravity-bridge.ts` registrado no Container
- Skill `antigravity-integration` indexada no registry (105 skills)
- MCP `antigravity-mcp` (41 total)
- 6 capacidades exclusivas Google DeepMind
- Delegacao de imagem, browser, busca web e subagentes paralelos

---

## [v4.2.1] — 2026-05-14
### Adicionado — 7 SVGs + DI Migration
- 7 diagramas SVG interativos (arquitetura, agentes, pipeline, MCP, RAG, self-healing, MiroFish/PhD)
- Injeção de Dependencia Fases 1-7 (88/88 testes)
- Container com 11 servicos
- Bridge Python <-> TypeScript

---

## [v4.2.0] — 2026-05-10
### Adicionado — P14-P18 + 38 Raciocinios
- Pipeline MiroFish/BettaFish P14-P18 completo
- Agent Forum com 38 raciocinios em 6 categorias
- 10 estrategias de Teoria dos Jogos
- BRAZIL_TIMEZONE (UTC-3)
- 50 indicadores reais (World Bank, WHO, FAO, UNESCO)
- SensitivityAnalyzer, IMRADFormatter
- Estrutura do repositorio refinada e organizada

---

## [v4.0.0] — 2026-05-05
### Adicionado — MiroFish/BettaFish + PhD Auditor
- Pipeline P14-P18: Agent Forum → DocIR → ANP → MetaWriter → PhD Auditor
- NashSolver: equilibrio Nash NxM (Lemke-Howson)
- StatisticalRigor: Cohen's d, Bonferroni, Power Analysis
- QualisA1Auditor: score 0-100 com 7 criterios
- Integracao nexus-phd-strategist
- Consolidacao da arquitetura multi-agente

---

## [v3.5] — 2026-05-01
### Adicionado — Sync + CJK Zero-Tolerance
- `ptbr_corrector.py`: deteccao e remocao de caracteres CJK
- Sync orchestrator multi-agente
- Token efficiency rules (8 regras)
- Contexto em chines (densidade +40%), output em PT-BR
- Zero-tolerance CJK: 220 → 0 caracteres

---

## [v1.0.0] — 2026-05-01
### Adicionado — Lancamento Inicial
- Fundacao do OpenCode Ecosystem
- Estrutura basica da plataforma
- Primeira visao documentada do ecossistema multi-agente coordenado
- 25 agentes, 12 MCPs, 20 skills
