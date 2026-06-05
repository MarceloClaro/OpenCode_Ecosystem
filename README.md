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
