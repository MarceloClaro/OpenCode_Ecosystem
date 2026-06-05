<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

---
description: Ativa o framework Reversa para análise de engenharia reversa. Orquestra agentes especializados (Scout, Archaeologist, Detective, Architect, Writer, Reviewer) para gerar especificações executáveis a partir de código legado.
---

# Reversa — Engenharia Reversa de Especificações

Ao ser ativado, o Reversa coordena uma equipe de agentes especializados para analisar o código legado e gerar especificações completas e rastreáveis.

## Comando

```
/reversa
```

## O que o Reversa faz

1. **Reconhecimento** — Scout mapeia estrutura, tecnologias e dependências
2. **Escavação** — Archaeologist analisa código módulo a módulo
3. **Interpretação** — Detective extrai regras de negócio; Architect gera diagramas C4 e ERD
4. **Geração** — Writer produz especificações executáveis
5. **Revisão** — Reviewer valida e classifica confiança das specs

## Estrutura gerada

```
_reversa_sdd/
├── inventory.md
├── code-analysis.md
├── domain.md
├── architecture.md
├── c4-*.md
├── erd-complete.md
├── confidence-report.md
├── sdd/          (specs por componente)
├── adrs/         (decisões arquiteturais)
└── traceability/ (matrizes de rastreabilidade)
```

## Agentes disponíveis

| Agente | Descrição |
|--------|-----------|
| reversa-scout | Mapeamento de superfície do projeto |
| reversa-archaeologist | Análise profunda de código |
| reversa-detective | Extração de regras de negócio |
| reversa-architect | Documentação arquitetural (C4, ERD) |
| reversa-writer | Geração de especificações |
| reversa-reviewer | Revisão e validação |
| reversa-visor | Documentação de interface via screenshots |
| reversa-data-master | Análise completa de banco de dados |
| reversa-design-system | Extração de design tokens |

## Persistência

Todo progresso é salvo em `.reversa/state.json`. Se a sessão for interrompida, basta digitar `/reversa` novamente para continuar de onde parou.
