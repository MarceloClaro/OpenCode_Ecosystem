# Indice Unificado — OpenCode Ecosystem v4.7.1

**Documentacao consolidada** | **25+ arquivos indexados** | **2026-06-04**

---

## 1. PROJETO PRINCIPAL (Anteprojeto PPGTE/UFC)

### ANTEPROJETO_PPGTE_2026.md
Anteprojeto de mestrado: IA Multiagente no Ensino Superior — guia pratico para pesquisa cientifica assistida e etica.
`/ANTEPROJETO_PPGTE_2026.md`

### anteprojeto-produto.md
Descricao do produto tecnologico digital (OpenCode Ecosystem v4.6) para o edital PPGTE/UFC 2026.
`/anteprojeto-produto.md`

### anteprojeto_validado.tex
Versao LaTeX compilada do anteprojeto — inclui Apendice TDD SPECs + Apendice B Mapa Taxonomico 150 questoes.
`/anteprojeto_validado.tex`

### anteprojeto_validado.pdf
PDF compilado do anteprojeto (validado, limpo).
`/anteprojeto_validado.pdf`

### 2026-edital-ppgte-ampla-concorrencia.pdf
Edital oficial PPGTE/UFC 2026.
`/2026-edital-ppgte-ampla-concorrencia.pdf`

### 2026-ficha-de-producao-academica-ppgte-ufc.pdf
Ficha de producao academica do PPGTE/UFC para avaliacao de produtos.
`/2026-ficha-de-producao-academica-ppgte-ufc.pdf`

---

## 2. ECOSSISTEMA OPENCODE

### AVALIACAO_SWOT_TDD_ECOSYSTEM.md
Avaliacao completa SWOT+TDD: 263 testes em 4 camadas, nota 86/100, 13 recomendacoes.
`/AVALIACAO_SWOT_TDD_ECOSYSTEM.md`

### .evolve/project-state.json
Estado atual do projeto: health score 100, 5 componentes saudaveis, 5 SPECs ativas.
`/.evolve/project-state.json`

### .menu_registry.json
Plugin system: 7 comandos registrados (audit, build, validate), 5 SPECs mapeadas, resumo TDD 58/58.
`/.menu_registry.json`

### menu.py
Menu adaptativo com DiscoveryEngine, plugin system e 4 modos de execucao.
`/menu.py`

---

## 3. CORA-EVAL (Validacao Cientifica)

### artigo/README.md
README do repositorio CORA-Eval: CORA-Score 3.04, 154/156 testes, 11 suites, 11 SPECs.
`/artigo/README.md`

### artigo/AVALIACAO_MATURIDADE_20260530.md
Resultados da execucao real (hardware): 12 suites, 98.7% taxa de aprovacao, calibracao V1-V7.
`/artigo/AVALIACAO_MATURIDADE_20260530.md`

### artigo/evolucao_completa_opencode.md
Transcricao completa dos 14 rounds de evolucao: score 85→98, M1→M4, 8 snapshots CORA-Eval.
`/artigo/evolucao_completa_opencode.md`

### artigo/TRIANGULACAO_ANTI_CIRCULARIDADE.md
Framework SPEC-008: triangulacao epistemologica com 15 referencias DOI.
`/artigo/TRIANGULACAO_ANTI_CIRCULARIDADE.md`

### artigo/evaluations/tests/ (30 arquivos)
Suites TDD para as 10 dimensoes CORA-Eval + validacao externa + SPEC framework.
`/artigo/evaluations/tests/test_d1_matematica.py` (12/12)
`/artigo/evaluations/tests/test_d2_fisica.py` (8/8)
`/artigo/evaluations/tests/test_d3_estatistica.py` (9/9)
`/artigo/evaluations/tests/test_d4_quimica.py` (9/9)
`/artigo/evaluations/tests/test_d5_biologia.py` (11/11)
`/artigo/evaluations/tests/test_d6_geociencias.py` (15/15)
`/artigo/evaluations/tests/test_d7_codigo.py` (7/7)
`/artigo/evaluations/tests/test_d8_literatura.py` (12/12)
`/artigo/evaluations/tests/test_d9_metodologia.py` (15/15)
`/artigo/evaluations/tests/test_d10_gat.py` (10/10)
`/artigo/evaluations/tests/test_evolucao_m4.py` (7/7)
`/artigo/evaluations/tests/test_exaustivo_final.py` (34/34)
`/artigo/evaluations/tests/test_anticircularidade.py` (14/14)

### artigo/evaluations/ (framework scripts)
Auditoria, dashboard, pipeline, anotacao humana, calibracao.
`/artigo/evaluations/domain_shift_audit.py`
`/artigo/evaluations/cora_benchmark_tracker.py`
`/artigo/evaluations/pipeline_coraeval.py`
`/artigo/evaluations/BENCHMARK_CORA_CIENCIAS_EXATAS.md`

---

## 4. SDD+TDD+AUTOEVOLVE (Qualidade LaTeX)

### artigo/orchestration/SPEC_ORCHESTRATION.md
Especificacao completa do pipeline: 3 quality gates (16 testes), 6 ADRs, menu adaptativo, 10 correcoes catalogadas.
`/artigo/orchestration/SPEC_ORCHESTRATION.md`

### artigo/orchestration/FRAMEWORK.md
Framework conceitual SDD+TDD+AutoEvolve: filosofia, arquitetura, metricas, reutilizacao.
`/artigo/orchestration/FRAMEWORK.md`

### artigo/orchestration/fix_history.json
Historico de correcoes: 4 sessoes, 3 padroes de fix catalogados, convergencia em 1 iteracao.
`/artigo/orchestration/fix_history.json`

### artigo/orchestration/refinement_loop.py
Implementacao do orquestrador AutoEvolve (SENSE→LEARN).
`/artigo/orchestration/refinement_loop.py`

### artigo/tests/
Testes de qualidade LaTeX (3 suites, 16 testes):
`/artigo/tests/test_compile.py` (5 testes, Gate 1)
`/artigo/tests/test_structure.py` (6 testes, Gate 2)
`/artigo/tests/test_quality.py` (5 testes, Gate 3)
`/artigo/tests/run_all_tests.py` (Runner TDD)
`/artigo/tests/README.md` (Documentacao dos testes)

### artigo/orchestration/evolutions/
Insights evolutivos: padroes aprendidos, tendencias, recomendacoes.
`/artigo/orchestration/evolutions/INDEX.md`
`/artigo/orchestration/evolutions/insight_20260528.md`
`/artigo/orchestration/evolutions/insight_cora_eval_20260529.md`

---

## 5. PRODUCAO ACADEMICA (Artigos e Documentos)

### artigo_150_questoes (LaTeX)
Artigo ABNT 24pp — Analise taxonomica de 150 questoes (60 EUF + 90 ENA).
`/artigo/artigo_150_questoes.tex` (fonte)
`/artigo/artigo_150_questoes.pdf` (compilado)

### dissertacao_cora_eval_abnt (LaTeX)
Dissertacao 142pp — Evolucao e Validacao do OpenCode Ecosystem via CORA-Eval.
`/artigo/dissertacao_cora_eval_abnt.tex` (fonte)
`/artigo/dissertacao_cora_eval_abnt.pdf` (compilado)

### jaccard_domain_shift_audit (LaTeX)
Relatorio tecnico 27pp — Auditoria de Domain Shift (SPEC-008-B).
`/artigo/jaccard_domain_shift_audit.tex`
`/artigo/jaccard_domain_shift_audit.pdf`

### modulo_dca_gat (LaTeX)
Modulo didatico — Geometric Arbitrage Theory.
`/artigo/modulo_dca_gat.tex`
`/artigo/modulo_dca_gat.pdf`

### artigos auxiliares
`/artigo_ciclo_evolucao_raciocinio.pdf` — Artigo sobre ciclo de evolucao de raciocinio
`/artigo_completo_qualis_a1.pdf` — Artigo Qualis A1 sobre ecossistema
`/artigo_cora_opencode.pdf` — Artigo CORA-Eval × OpenCode

---

## 6. VALIDACAO CIENTIFICA (SPECs e Auditoria)

### SPECs Ativas (11)

| SPEC | Documento | Status TDD |
|:----:|-----------|:----------:|
| SPEC-001 | Orchestration Pipeline | Documentada |
| SPEC-002 | Academic Output (MASWOS) | Documentada |
| SPEC-003 | MCP Integration | Documentada |
| SPEC-004 | Quantum Computing | Documentada |
| SPEC-005 | Reverse Engineering | Documentada |
| SPEC-006 | Data Orchestration | Documentada |
| SPEC-007 | Evolution Engine | Documentada |
| SPEC-008 | Triangulacao Anti-Circularidade | 14/14 ✅ |
| SPEC-008-B | Domain Shift (Camada 1B) | 9/9 ✅ |
| SPEC-009 | D1 Raciocinio Matematico | 12/12 ✅ |
| SPEC-010 | D2 Modelagem Fisica | 8/8 ✅ |
| SPEC-011 | D9 Metodologia Experimental | 15/15 ✅ |

### Relatorios de Auditoria
`/artigo/evaluations/AUDITORIA_CORA_EVAL_20260528.md`
`/artigo/evaluations/RELATORIO_C6_ANOTACAO.md`
`/artigo/evaluations/RELATORIO_TECNICO_CORA_EVAL_LISTAS_DCA.md`

---

## 7. NOVA INFRAESTRUTURA (v4.7.1)

### CI/CD
`/.github/workflows/ci.yml` — GitHub Actions: Windows+Ubuntu, 206 testes, 15min timeout

### Docker
`/Dockerfile` — Container Python 3.12 + TeX Live para validacao cross-platform

### Documentacao Tecnica
`/docs/ARQUITETURA_ECOSYSTEM.md` — Arquitetura completa para onboarding de novos desenvolvedores
`/docs/CONTINGENCIA_MODELO.md` — Plano de contingencia para descontinuacao do modelo
`/docs/PROTOCOLO_ANONIMIZACAO_LGPD.md` — Protocolo LGPD com script de scanner PII
`/docs/INDICE_UNIFICADO.md` — Este documento: indice de toda a documentacao
`/docs/TUTORIAL_INTERATIVO.md` — Tutorial passo-a-passo para novos usuarios

---

## 8. SUBPROJETOS

### ARMADILHA DA RENDA MEDIA
Artigo cientifico com analise empirica, jogo evolutivo, graficos e LaTeX.
`/ARMADILHA DA RENDA MEDIA/ARTIGO_COMPLETO.md`
`/ARMADILHA DA RENDA MEDIA/artigo_completo.pdf`
`/ARMADILHA DA RENDA MEDIA/SPEC_ARM_IAG_GAME_THEORY.md`

### ARTETERAPIA
Projeto de arteterapia decolonial com validacao clinica.
`/ARTETERAPIA/`

### A Protecao da Personalidade Humana...
Anteprojeto sobre IA, personalidade humana e Enciclica Magnifica Humanitas.
`/A Proteção da Personalidade Humana na Era da Inteligência Artificial.../`

---

## 9. GUIAS E PROTOCOLOS (Novos)

| Documento | Conteudo |
|-----------|----------|
| `docs/ARQUITETURA_ECOSYSTEM.md` | Arquitetura completa + onboarding dev |
| `docs/CONTINGENCIA_MODELO.md` | Plano fallback para descontinuacao do modelo |
| `docs/PROTOCOLO_ANONIMIZACAO_LGPD.md` | Protocolo LGPD + scanner PII |
| `docs/TUTORIAL_INTERATIVO.md` | Tutorial passo-a-passo para novos usuarios |
| `docs/INDICE_UNIFICADO.md` | Este indice |
| `AVALIACAO_SWOT_TDD_ECOSYSTEM.md` | SWOT+TDD completo com recomendacoes |

---

**Indice Unificado** · 2026-06-04 · 52 arquivos indexados · OpenCode Ecosystem v4.7.1
