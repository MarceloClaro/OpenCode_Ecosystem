---
name: academic-ml-pipeline
description: "Pipeline ML completo para análise acadêmica: correlação bootstrap, classificação ARM, detecção de anomalias, clusterização, feature importance e integração com artigo científico"
user-invocable: true
license: MIT
compatibility: OpenCode, Claude Code
metadata:
  author: OpenCode Ecosystem v4.1
  version: "1.1.0"
  ecossistema: opencode
  categoria: pesquisa-academica
  round: 11
  learning-session: "artigo-ARM-IAG-262-observacoes"
  v3-features: "knowledge_complexity, export_sophistication, product_density"
  v3-date: "2026-05-14"
allowed-tools: Read Edit Write Bash Python Code-Runner
---

# Academic ML Pipeline v1.1

Pipeline de Machine Learning para análise acadêmica, validado em sessão real com dataset de 262 observações × 14 features (11 originais + 3 de complexidade econômica) sobre Armadilha da Renda Média (ARM) e Inteligência Artificial Generativa (IAG).

## Visão Geral

Pipeline integrado que conecta análise quantitativa → geração de figuras → inserção em artigo acadêmico → exportação ABNT multi-formato.

## Workflow Completo (7 Etapas)

> *Detalhes em `references/etapa1.md`*
> *Detalhes em `references/etapa2.md`*
> *Detalhes em `references/etapa3.md`*
> *Detalhes em `references/etapa4.md`*
> *Detalhes em `references/etapa5.md`*
> *Detalhes em `references/etapa6.md`*
> *Detalhes em `references/etapa7.md`*
## Referências

- Script de pipeline v2: `03_ml_pipeline_v2.py` (11 features)
- Script de pipeline v3: `03_ml_pipeline_v3.py` (14 features, 3 novas de complexidade)
- Script de figuras: `gerar_figuras.py` (reproduzível com seed 42)
- Dataset: WDI + Oxford Insights AIPI + FMI/WEO
- Hausmann, R., Hidalgo, C. A., et al. (2014). *The Atlas of Economic Complexity*. MIT Press.
- Hausmann, R., Hwang, J., & Rodrik, D. (2007). What you export matters. *Journal of Economic Growth*, 12(1), 1-25.
- Hidalgo, C. A., Klinger, B., Barabási, A. L., & Hausmann, R. (2007). The product space conditions the development of nations. *Science*, 317(5837), 482-487.

