---
name: sci-hub-mcp-server
description: "Servidor MCP para acesso a literatura acadêmica via Sci-Hub. Permite buscar, baixar e extrair metadados de artigos científicos através de DOI, PMID ou URL. Use para: pesquisa acadêmica, revisão de literatura e validação científica."
---

# Sci-Hub MCP Server

## Visão Geral

O **Sci-Hub MCP Server** é uma ferramenta essencial para o ecossistema de pesquisa, permitindo o acesso direto a artigos científicos que muitas vezes estão atrás de paywalls. Ele integra-se perfeitamente com o framework MASWOS e o BSDT para fornecer evidências reais e fundamentação científica de alto nível (Qualis A1).

## Funcionalidades

*   **Busca por Identificador:** Localiza artigos usando DOI, PMID ou URL direta.
*   **Download de PDF:** Recupera o link direto para o PDF do artigo a partir dos espelhos do Sci-Hub.
*   **Extração de Metadados:** Obtém informações como título, autores e ano de publicação quando disponíveis.
*   **Integração Multi-MCP:** Pode ser invocado por outros agentes ou orquestradores (como o NEXUS-ULTRA).

## Como Usar

O servidor pode ser iniciado via Python ou utilizado através de seus scripts utilitários.

### Uso Programático

```python
from skills.sci_hub_mcp_server.scripts.sci_hub_search import SciHub
sh = SciHub()
result = sh.fetch_article("10.1038/s41586-020-2012-7")
if result["success"]:
    print(f"URL do PDF: {result['pdf_url']}")
```

### Invocação via Orquestrador Nexus

O orquestrador `nexus-ultra-ecosystem` já possui um adaptador para esta skill. Basta enviar uma tarefa contendo "Sci-Hub" ou "baixar artigo" e fornecer o identificador no contexto.

## Recursos

### scripts/

*   `sci_hub_server.py`: Implementação do servidor MCP.
*   `sci_hub_search.py`: Core de busca e extração de dados do Sci-Hub.

### references/

*   `README.md`: Documentação original do servidor Sci-Hub MCP.

### templates/

*   `requirements.txt`: Dependências necessárias para o funcionamento do servidor.
