---
name: pesquisa-jurisprudencia
description: "Skill do ecossistema OpenCode - pesquisa-jurisprudencia"
category: juridico
version: "1.0.0"
kind: prompt
---

# Pesquisa Jurisprudencial — Brasil



## Principio Central

Pesquisar jurisprudencia requer metodo: tema claro, busca em multiplas
bases, filtro de relevancia e citacao responsavel. Nunca inventar precedentes;
sempre verificar existencia real.


> *Detalhes de "Preparacao da Pesquisa" em `references/`*


> *Detalhes de "Protocolo de Pesquisa" em `references/`*



## Citacao Responsavel

### Formato de Citacao para Pecas

```
EMENTA: [trecho integral da ementa exatamente como no tribunal]
[Identificacao completa: Tribunal, numero, relator, data, DJe]
```

### Regras de Integridade

- **Nunca resumir** ementa de forma que altere o sentido
- **Nunca citar** precedent without verificar existencia real
- **Sempre informar** quando pesquisa nao encontrar resultado
- **Sempre distinguir** caso concreto do precedente



## Integracao com MCPs

- **websearch (mcp-fetch-server --duckduckgo):** pesquisa primaria em todas bases
- **wikipedia:** conceito juridico base antes de pesquisa em tribunal
- **context7:** busca contextualizada por tema juridico
- **fetch:** acessar base especifica do tribunal



## Casos de Uso Comum

| Situacao | Pesquisa recomendada |
|----------|----------------------|
| Honorarios advogado | STJ + "honorarios sucumbenciais" + ano > 2015 |
| Prisao domiciliar | STF + "prisao domiciliar" + "maiores 80" |
| Responsabilidade civil | TJSP + "responsabilidade civil" + "dano moral" |
| Horas extras | TRT + "horas extras" + "intervalo" |
| Contrato bancario | STJ + "contrato bancario" + "clausula abusiva" |

