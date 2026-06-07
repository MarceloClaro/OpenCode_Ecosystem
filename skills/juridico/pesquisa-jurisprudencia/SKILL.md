---
name: pesquisa-jurisprudencia
description: "Pesquisa jurisprudencial com CLI automatizada via API Jurisprudencias.ai"
category: juridico
version: "2.0.0"
kind: prompt
---

# Pesquisa Jurisprudencial — Brasil

## Principio Central

Pesquisar jurisprudencia requer metodo: tema claro, busca em multiplas
bases, filtro de relevancia e citacao responsavel. Nunca inventar precedentes;
sempre verificar existencia real.

> *Detalhes de "Preparacao da Pesquisa" em `references/`*

> *Detalhes de "Protocolo de Pesquisa" em `references/`*

## CLI Automatizada — Jurisprudencias.ai

Este skill inclui um cliente PowerShell (`scripts/jurisprudencias.ps1`) para
a API Jurisprudencias.ai com cache JSON local (SHA256, TTL configuravel).

**Setup:**
```powershell
. .\scripts\jurisprudencias.ps1
$env:JURISPRUDENCIAS_API_TOKEN = 'jur_seu_token_aqui'
```

**Uso rapido:**
```powershell
Search-JurDecision -Query "honorarios sucumbenciais" -Court STJ -PageSize 10
Resolve-JurProcess -ProcessNumber "0700834-24.2022.8.02.0001"
Get-JurCourt -CourtSlug "stj"
```

> Cache evita consumir a cota de 5 buscas/dia em repeticoes.
> Consulte `references/snippets.ps1` para patterns prontos.

## Citacao Responsavel

### Formato de Citacao para Pecas

```
EMENTA: [trecho integral da ementa exatamente como no tribunal]
[Identificacao completa: Tribunal, numero, relator, data, DJe]
```

### Regras de Integridade

- **Nunca resumir** ementa de forma que altere o sentido
- **Nunca citar** precedente sem verificar existencia real
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

