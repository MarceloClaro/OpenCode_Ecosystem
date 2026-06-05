---
name: editais-br
description: "Busca inteligente de editais de fomento a pesquisa, inovacao e cultura no Brasil. Classificacao granular em 25 sub-dimensoes, scoring por perfil, extracao profunda, 52 editais curados (CNPq/CAPES/FINEP)"
user-invocable: true
license: MIT
compatibility: OpenCode, Claude Code, Cursor, Gemini CLI
---

# editais-br v7.2 — Busca Inteligente de Editais de Fomento

## Quando Usar

- **Mestrado/Doutorado**: Bolsas CAPES, CNPq, programas de pos, PNPD, PROEX
- **Inovacao**: Subvencao FINEP, SEBRAE, InovAtiva, EMBRAPII, Lei do Bem
- **Pesquisa**: Chamada Universal, INCT, Jovem Pesquisador, FAPs estaduais
- **Cultura**: Lei Rouanet, premios, editais estaduais
- **Impacto Social**: Prosas, Fundo Brasil, termo fomento MROSC

## Scoring (0-100)

| Componente | Peso max | Descricao |
|-----------|----------|-----------|
| Query Relevance | 30 | Quantos termos da busca estao no titulo |
| Tipo Alignment | 30 | Tipo do edital casa com area classificada |
| Perfil Alignment | 20 | Perfil do usuario casa com perfil do edital |
| Mechanism Bonus | 10 | Adequacao do mecanismo de fomento |
| Completeness | 12 | Dimensoes classificadas com sucesso |
| Penalties | -35 | Encerrado(-20), contrapartida(-10), alta competicao(-5) |

## Exemplos

```bash
python scripts/edital_search.py "pesquisa" --tipo pesquisa --curadoria-only
python scripts/edital_search.py "bolsa doutorado" --tipo doutorado --perfil doutorando
python scripts/edital_search.py "startup" --tipo startup --json
python scripts/edital_search.py "ia saude" --tipo pesquisa --no-cache --json | jq .
python scripts/edital_search.py --servidor
python scripts/extracao_profunda.py edital.pdf --json
```

## Pipeline

```
Busca (DuckDuckGo + curadoria 52 editais + portais diretos)
  -> Classificador (25 sub-dimensoes, word-boundary regex)
    -> Scoring por perfil (0-100, query-aware)
      -> Cache LRU (versionado, TTL 1h) + SQLite feedback
        -> [opcional] Servidor HTTP REST
```

## File Reference

| File | Content |
|------|---------|
| `scripts/edital_search.py` | Busca multi-portal, cache, curadoria, servidor HTTP |
| `scripts/extracao_profunda.py` | Extracao de requisitos de PDF via docling/pdfplumber |




