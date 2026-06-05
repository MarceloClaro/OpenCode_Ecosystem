# pypi-scout: Buscador Inteligente de Bibliotecas Python para o Ecossistema OpenCode

**Status**: v1.0.0 | **Categoria**: system | **Tipo**: CLI tool

## Descrição

CLI Python que busca, cataloga e instala bibliotecas do PyPI relevantes para o ecossistema OpenCode. Integra-se com o pipeline acadêmico (SEEKER → MASWOS → PhD Auditor), oferecendo curadoria de 24+ bibliotecas em 5 categorias com métricas de afinidade.

## Quando Usar

- Buscar bibliotecas Python para tarefas acadêmicas (Sci-Hub, arXiv, Semantic Scholar)
- Instalar SDKs MCP, adaptadores e servidores
- Acessar dados do Banco Mundial, ONU, OCDE
- Obter recomendações de pacotes por pipeline do ecossistema
- Comparar versões do catálogo curado com PyPI ao vivo

## Uso Rápido

```bash
# Buscar pacotes relacionados a sci-hub
python skills/system/pypi-scout/pypi_scout.py search scihub

# Listar catálogo curado completo
python skills/system/pypi-scout/pypi_scout.py catalog

# Pacotes para artigos acadêmicos
python skills/system/pypi-scout/pypi_scout.py category artigos_academicos

# Recomendar para pipeline SEEKER
python skills/system/pypi-scout/pypi_scout.py recommend SEEKER

# Instalar World Bank API
python skills/system/pypi-scout/pypi_scout.py install wbgapi

# Comparar versão do catálogo com PyPI
python skills/system/pypi-scout/pypi_scout.py diff scholarly
```

## Categorias

| Categoria | Descrição | Pacotes |
|-----------|-----------|---------|
| `artigos_academicos` | Sci-Hub, arXiv, Semantic Scholar, Google Scholar, OpenAlex, Crossref | 8 |
| `dados_mundiais` | World Bank (WDI), ONU (SDG), OCDE | 3 |
| `mcp_ecosystem` | MCP SDK, OpenAI Agents MCP, LangChain MCP | 3 |
| `dados_cientificos` | BioPython, PubMed, NCBI | 1 |
| `infra_ferramentas` | Click, Rich, HTTPX | 3 |

## Afinidade com Componentes OpenCode

| Componente | Top Bibliotecas |
|------------|----------------|
| SEEKER | scholarly, arxiv, semanticscholar, scihub-cn, openalex |
| MASWOS | scihub-cn, scholarly, semanticscholar, pypdf, arxiv |
| PhD Auditor | semanticscholar, openalex, crossrefapi, wbgapi |
| MCP Server | mcp, openai-agents-mcp, langchain-mcp-adapters |
| Data Analysis | wbgapi, pandas-datareader, sdg-indicators |

## Exemplos de Integração

### Busca de artigos no SEEKER

```python
# Usando scihub-cn para baixar artigos
# pip install scihub-cn
import subprocess
result = subprocess.run(
    ["scihub-cn", "-d", "10.1038/s41524-017-0032-0", "-o", "./papers/"],
    capture_output=True
)
```

### Dados do Banco Mundial no PhD Auditor

```python
# pip install wbgapi
import wbgapi as wb
# PIB per capita (US$ corrente) para Brasil
gdp = wb.data.fetch('NY.GDP.PCAP.CD', 'BRA', range(2010, 2024))
```

### Semantic Scholar para validação de citações

```python
# pip install semanticscholar
from semanticscholar import SemanticScholar
sch = SemanticScholar()
paper = sch.get_paper('10.1093/mind/lix.236.433')
print(f"Título: {paper.title}")
print(f"Citações: {paper.citationCount}")
```

## Arquivos

- `pypi_scout.py` — CLI principal (busca, catálogo, instalação)
- `opencode_catalog.json` — Catálogo curado com 24+ pacotes e métricas de afinidade
