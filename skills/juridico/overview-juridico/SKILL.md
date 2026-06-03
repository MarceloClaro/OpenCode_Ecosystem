---
name: overview-juridico
description: >
  Visao geral das skills juridicas instaladas no ecossistema OpenCode.
  Use para identificar qual skill aplicar a cada demanda.
category: juridico
version: "1.0.0"
kind: prompt
---

# Skills Juridicas — OpenCode Ecosystem

Colecao de skills para advocacia integradas ao ambiente CLAWS.

## Skills Disponiveis

| Skill | Funcao | Trigger |
|-------|--------|---------|
| pecas-juridicas-html | Peticoes, contestacoes, recursos em HTML | gerar peticao, redigir peça, documento HTML |
| edicao-cirurgica | Edicao incremental de artefatos | ajustar, corrigir, editar trecho |
| triagem-juridica | Classificacao de demandas e leads | triar, classificar consulta, qualificar |
| pesquisa-jurisprudencia | Buscar precedentes em tribunais | jurisprudencia, precedente, STJ, TJ |
| gerador-contratos | Contratos, procuracoes, acordos em HTML | gerar contrato, redigir acordo |
| followup-advocacia | Gestao de prazos e produtividade | follow-up, lembrete, prazo, rotina |

## Mapa de Aplicacao

| Situacao | Skill recomendada |
|----------|-------------------|
| Cliente chega com demanda nova | triagem-juridica |
| Demand analysis concluida, gerar peça | pecas-juridicas-html |
| Ajustar paragrafo de peça existente | edicao-cirurgica |
| Precisa de fundamento legal | pesquisa-jurisprudencia |
| Cliente precisa assinar documento | gerador-contratos |
| Revisao semanal de prazos | followup-advocacia |

## Integracao MCP

- **websearch (mcp-fetch-server --duckduckgo):** Pesquisa primaria
- **wikipedia (mcp-wikipedia):** Conceitos juridicos basicos
- **time (mcp-time):** Agendamento de prazos
- **sqlite (mcp-server-sqlite):** Persistencia de dados
- **context7:** Documentacao tecnica
- **gh_grep (mcp.grep.app):** Buscas em codigo/links

## Status

Total: 6 skills juridicas
Versao: 1.0
Data: 16/05/2026
Ecosistema: CLAWS v1.0
