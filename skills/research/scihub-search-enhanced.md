---
name: scihub-search-enhanced
description: "Pipeline de busca acadêmica multi-estratégia: CrossRef → Unpaywall (OA) → Sci-Hub → CORE → arXiv. Use quando precisar de: DOI validation, PDF download, citação ABNT automática, batch de artigos, busca por palavras-chave em fontes abertas. Gatilhos: 'baixar artigo', 'buscar DOI', 'citação ABNT', 'acesso aberto', 'PDF artigo', 'sci-hub', 'scihub'."
version: "2.0.0"
author: "OpenCode Ecosystem v4.6"
category: research
compatibility: deepseek-v4-pro
updated_at: "2026-05-24"
allowed-tools: Read Edit Write Bash
---

# Skill: SciHub Search Enhanced v2.0

Pipeline de acesso a literatura acadêmica com **fallback em cascata** e auditoria completa.

## Hierarquia de Fallback (ordem de prioridade)

```
DOI recebido
  ↓ 1. CrossRef API → metadados + validação (gratuito, sem auth)
  ↓ 2. Unpaywall API → PDF em Acesso Aberto (gratuito, sem auth)
  ↓ 3. Sci-Hub → fallback com rotação de mirrors (se OA indisponível)
  ↓ 4. CORE.ac.uk → repositório OA alternativo
  ↓ 5. arXiv API → preprints (física, math, CS, biomédico)
  ↓ Resultado: PDF + metadados + ABNT NBR 6023:2025
```

## Uso via CLI

```bash
# Busca + download por DOI (cascata automática)
python basis-research/core/seeker_scihub_enhanced.py -d "10.1515/9781400881970-018"

# Batch de DOIs (arquivo com 1 DOI por linha, paralelo)
python basis-research/core/seeker_scihub_enhanced.py -b dois.txt -w 3

# Busca por palavras-chave (CORE + arXiv)
python basis-research/core/seeker_scihub_enhanced.py -s "bayesian optimization gaussian process" -l 10
```

## Uso Programático (SEEKER integration)

```python
from basis_research.core.seeker_scihub_enhanced import SciHubEnhanced

sh = SciHubEnhanced()

# Fetch único com trilha de auditoria
result = sh.fetch("10.2307/1969529")
print(result['abnt'])      # → NASH, John F. Non-Cooperative Games. Annals of Mathematics...
print(result['source'])    # → "Unpaywall (OA)" ou "Sci-Hub" ou None
print(result['audit'])     # → lista de steps para PhD Auditor L5

# Batch paralelo (3 workers, respeita rate limits)
results = sh.fetch_batch([
    "10.2307/1969529",       # Nash 1951
    "10.1515/9781400881970-018",  # Shapley 1953
    "10.1007/BF01448847",    # Von Neumann 1928
], destination="papers/", max_workers=3)
```

## Melhorias v2.0 vs v1.0

| Feature | v1.0 (scihub_downloader.py) | v2.0 (enhanced) |
|---|---|---|
| Verificação DOI | ❌ | ✅ CrossRef API |
| Acesso Aberto | ❌ | ✅ Unpaywall |
| CORE fallback | ❌ | ✅ |
| arXiv fallback | ❌ | ✅ |
| ABNT NBR 6023:2025 | ❌ Manual | ✅ Automático |
| Cache local (TTL 24h) | ❌ | ✅ `.evolve/scihub-cache/` |
| Batch paralelo | ❌ | ✅ ThreadPoolExecutor |
| Verificação PDF | ❌ | ✅ header + tamanho mínimo |
| Log observabilidade | ❌ | ✅ `.evolve/scihub-observability.jsonl` |
| PhD Auditor L5 | ❌ | ✅ trilha de auditoria |

## Integração MCP

```json
// opencode.json — MCP scihub já registrado
"scihub": {
  "command": "python",
  "args": ["sci-hub-mcp-server/scripts/sci_hub_server.py"],
  "tools": [
    "search_scihub_by_doi",
    "search_scihub_by_title",
    "search_scihub_by_keyword",
    "download_scihub_pdf",
    "get_paper_metadata"
  ]
}
```

## Observabilidade (`.evolve/`)

| Arquivo | Conteúdo |
|---|---|
| `scihub-cache/{hash}.json` | Cache de metadados CrossRef/Unpaywall (TTL 24h) |
| `scihub-observability.jsonl` | Log por linha: doi, source, has_pdf, has_meta, err |

## Integração com Pipeline Acadêmico

```
SEEKER (basis-research/agents/grounder.py)
  → seeker_scihub_enhanced.fetch_batch(dois)
  → metadados verificados + PDFs + ABNT formatadas
  → Agente A35 (verificacao_referencias.md)
  → PhD Auditor L5 (audit trail)
  → Artigo LaTeX com citações auditáveis
  → Qualis A1 ≥ 95/100
```

## Referências Técnicas

→ [`references/scihub-enhanced-reference.md`](references/scihub-enhanced-reference.md)
→ [`basis-research/core/seeker_scihub_enhanced.py`](../../basis-research/core/seeker_scihub_enhanced.py)
