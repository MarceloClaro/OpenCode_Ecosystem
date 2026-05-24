# Cliente de Busca arXiv

Este é um cliente Python que permite realizar buscas de artigos científicos no arXiv usando uma interface simples e eficiente.

## Funcionalidades

- Busca de artigos científicos no arXiv
- Exibição formatada dos resultados incluindo:
  - Título do artigo
  - Autores
  - Data de publicação
  - Link para o artigo
  - Resumo (abstract)

## Requisitos

- Python 3.7+
- Dependências listadas em `requirements.txt`

## Como Usar

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o cliente:
```python
from client import search_arxiv

# Exemplo de busca
query = "machine learning"
results = await search_arxiv(query)
```

### Parâmetros de Busca

- `query` (str): Termo de busca para encontrar artigos
- `max_results` (int, opcional): Número máximo de resultados (padrão: 5)
- `start` (int, opcional): Índice inicial para paginação (padrão: 0)

### Exemplo de Resultado

O resultado será uma lista de artigos, onde cada artigo contém:
```python
{
    'title': 'Título do Artigo',
    'authors': ['Autor 1', 'Autor 2'],
    'published': 'Data de Publicação',
    'link': 'URL do Artigo',
    'summary': 'Resumo do Artigo'
}
```

## Notas

- A API utiliza o serviço oficial do arXiv
- Os resultados são limitados para evitar sobrecarga do servidor
- As buscas são realizadas em todos os campos (título, autores, resumo)

## Contribuindo

Sinta-se à vontade para contribuir com melhorias através de pull requests ou reportar problemas através de issues.

## Licença

Este projeto está sob a licença MIT.
