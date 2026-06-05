<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Gerado: 2026-05-31T22:30 UTC-3
-->

---
name: evo-7-academic-pipeline
description: Pipeline acadêmico LaTeX — compilação, fichamentos, cotejo, status e registro de aprendizado
round: 7
origin: "Ciclo de compilação e documentação do anteprojeto PPGTE/UFC"
score: 94
tags:
  - latex
  - academic
  - pipeline
  - qualis-a1
  - fichamento
  - cotejo
---

# Evo-7: Academic Pipeline

Skill gerada a partir do ciclo de compilação e documentação do anteprojeto UFC (91 pág., 0 erros). Captura o pipeline reutilizável para manutenção de manuscritos acadêmicos LaTeX.

## Pipeline

### Fase 1: Compilação
```
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

### Fase 2: Fichamentos documentais
Fichar artefatos do projeto (STATUS.md, cotejo, PDFs) em `\begin{fichamento}...\end{fichamento}`.

### Fase 3: Cotejo de citações
Extrair `\cite{}`, verificar `[§XX]`, registrar taxa de acerto.

### Fase 4: Status
PopularySTATUS.md, verificar STATUS.md.zip se vazio.

### Fase 5: Evolutions
Registrar aprendizado em `artigo/orchestration/evolutions/insight_YYYYMMDD_tema.md`.

## Aprendizados chave
1. "major issue" != erro — é notificação MiKTeX
2. 3 passagens pdflatex+bibtex é suficiente
3. Fichamentos documentais ≠ bibliográficos

## Uso
```bash
# Load via subagent:
# skill evo-7-academic-pipeline
```
