# Servidor de Busca arXiv

Este é um servidor implementado com FastMCP que fornece uma interface para busca de artigos científicos no arXiv através de uma API HTTP.

## Componentes Principais

### Módulos
- `FastMCP`: Framework para criação do servidor
- `httpx`: Cliente HTTP assíncrono para requisições ao arXiv
- `xml.etree.ElementTree`: Parser XML para processar respostas do arXiv

### Funcionalidades Principais
- Busca assíncrona no arXiv
- Parsing de respostas XML
- Formatação de resultados
- Tratamento de erros
- Gestão de requisições HTTP

## Configuração

### Constantes
```python
ARXIV_API_BASE = "http://export.arxiv.org/api/query"
USER_AGENT = "arxiv-search-app/1.0"
```

### Requisitos
- Python 3.7+
- FastMCP
- httpx
- xml.etree.ElementTree (biblioteca padrão Python)

## API

### Endpoint Principal
`search_arxiv(query: str, max_results: int = 5, start: int = 0)`

#### Parâmetros
- `query`: Termo de busca
- `max_results`: Número máximo de resultados (padrão: 5)
- `start`: Índice inicial para paginação (padrão: 0)

#### Formato de Resposta
```python
{
    'title': str,       # Título do artigo
    'summary': str,     # Resumo do artigo
    'authors': list,    # Lista de autores
    'link': str,        # URL do artigo
    'published': str    # Data de publicação
}
```

## Funções Auxiliares

### make_arxiv_request
- Realiza requisições HTTP ao arXiv
- Inclui tratamento de erros e timeout
- Retorna o texto XML da resposta

### parse_arxiv_response
- Processa o XML retornado pelo arXiv
- Extrai informações relevantes dos artigos
- Organiza dados em dicionários Python

### format_paper
- Formata as informações do artigo para exibição
- Organiza autores, título, resumo e links

## Tratamento de Erros

O servidor inclui tratamento para:
- Falhas de conexão
- Timeouts
- Respostas XML inválidas
- Campos ausentes na resposta

## Boas Práticas

- Uso de User-Agent personalizado
- Timeout configurado para requisições
- Tratamento adequado de namespaces XML
- Validação de dados retornados

## Como Executar

1. Instale as dependências:
```bash
pip install fastmcp httpx
```

2. Execute o servidor:
```bash
python server_arxiv.py
```

## Notas de Implementação

- O servidor utiliza processamento assíncrono para melhor performance
- Respeita as diretrizes da API do arXiv
- Implementa cache básico para otimizar requisições repetidas
- Fornece respostas formatadas e consistentes

## Contribuindo

Contribuições são bem-vindas! Por favor, siga estas etapas:
1. Fork do repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT.
