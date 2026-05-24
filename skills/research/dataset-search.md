---
name: dataset-search
description: "Busca de datasets abertos em múltiplas fontes: catálogo curado local (200 datasets), data.gov CKAN API, HuggingFace Datasets Hub. Filtros por categoria, cloud, vintage e tema semântico. Use quando precisar de: 'buscar dataset', 'dados abertos', 'dataset público', 'data.gov', 'repositório de dados', 'HuggingFace dataset', 'fonte de dados para pesquisa'."
version: "1.1.0"
author: "OpenCode Ecosystem v4.2.2"
category: research
updated_at: "2026-05-24"
allowed-tools: Read Edit Write Bash
---

# Skill: Dataset Search v1.1

Descoberta de datasets abertos com busca unificada em **3 fontes** + catálogo curado de **200 datasets**.

## Fontes Integradas

| Fonte | Tipo | Acesso | Datasets disponíveis |
|---|---|:---:|:---:|
| **Catálogo local** | CSV curado | Offline | 200 |
| **data.gov** | CKAN REST API | Online, sem auth | 300k+ |
| **HuggingFace Hub** | REST API | Online, sem auth | 100k+ |

## Uso via CLI

```bash
# Busca full-text (todas as fontes)
python basis-research/core/seeker_datasets_search.py -q "climate temperature"

# Filtro por tema semântico
python basis-research/core/seeker_datasets_search.py -t nlp
python basis-research/core/seeker_datasets_search.py -t transport

# Apenas catálogo local (offline)
python basis-research/core/seeker_datasets_search.py -q "taxi" --no-datagov --no-hf

# Estatísticas do catálogo
python basis-research/core/seeker_datasets_search.py --stats

# Exportar como tabela Markdown (para artigo)
python basis-research/core/seeker_datasets_search.py -q "social network" --markdown

# Exportar JSON para pipeline SEEKER
python basis-research/core/seeker_datasets_search.py -q "energy" --export results.json
```

## Temas Semânticos Disponíveis

| Tema | Categorias mapeadas |
|---|---|
| `biology` | Biology, Healthcare, Agriculture |
| `nlp` | Natural Language, Social Networks |
| `geo` | GIS, Transportation, Climate/Weather |
| `ml` | Machine Learning, Data Challenges |
| `social` | Social Networks, Social Sciences |
| `gov` | Government, Social Sciences, Energy |
| `transport` | Transportation |
| `energy` | Energy |

## Uso Programático (SEEKER)

```python
from basis_research.core.seeker_datasets_search import search_all, load_catalog, catalog_stats

# Busca unificada
report = search_all("urban mobility", include_datagov=True, include_hf=True)
print(report['total'])  # → N datasets encontrados

# Somente catálogo local
catalog = load_catalog()
stats = catalog_stats(catalog)
# → {'total': 200, 'categories': {'Healthcare': 21, 'Environment': 20, ...}}

# Citação ABNT NBR 6023:2025 para dataset
from basis_research.core.seeker_datasets_search import format_citation_abnt
cit = format_citation_abnt(report['results']['local'][0])
# → NYC TAXI. NYC Taxi Trip Data 2009-. [Dataset]. 2009. Acesso em: <http://...>.
```

## Catálogo Local (200 datasets curados)

O catálogo inclui bases fundamentais para pesquisa acadêmica do Brasil e do mundo:

*   **Brasil:** IBGE, DATASUS, EMBRAPA, INPE, IPEA, BCB, ANA, ANAC, etc.
*   **Internacional:** ONU, World Bank, WHO, FAO, OECD, IMF.
*   **Ciência e Clima:** NASA, NOAA, Copernicus, ESA, USGS.
*   **IA e Dados:** HuggingFace Hub, UCI, Kaggle Datasets, OpenML.
*   **Saúde e Biologia:** CDC, NIH, GBIF, ClinicalTrials.

## Observabilidade (`.evolve/`)

| Arquivo | Conteúdo |
|---|---|
| `dataset-search-observability.jsonl` | Log por busca: query, total, por fonte |
| `dataset-search-{ts}.json` | Resultado completo exportado |

## Integração com Pipeline Acadêmico

```
SEEKER (basis-research/agents/grounder.py)
  → dataset_search.search_all("tema do artigo")
  → datasets relevantes identificados
  → format_citation_abnt() para cada fonte
  → Agente A07 (methodology.md): descreve fontes de dados
  → Artigo LaTeX com seção "Fontes de Dados" auditável
  → Qualis A1: rastreabilidade total da proveniência dos dados
```

## Referência técnica

→ [`basis-research/core/seeker_datasets_search.py`](../../basis-research/core/seeker_datasets_search.py)
→ [`basis-research/data/public_datasets_catalog.csv`](../../basis-research/data/public_datasets_catalog.csv)
