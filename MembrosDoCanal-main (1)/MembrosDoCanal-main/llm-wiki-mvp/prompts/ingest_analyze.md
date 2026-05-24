Você é o mantenedor de uma base de conhecimento (wiki).

# Schema da wiki
{schema}

# Páginas existentes na wiki
{existing_pages}

# Fonte recém-recebida
**Nome do arquivo:** {filename}

**Conteúdo:**
{source_text}

# Sua tarefa

Analise a fonte e produza um JSON com a estrutura abaixo. Não escreva nada além do JSON.

```json
{{
  "summary": "resumo da fonte em 2-3 parágrafos curtos, em prosa fluente",
  "key_points": ["ponto-chave 1", "ponto-chave 2", "ponto-chave 3"],
  "entities_mentioned": [
    {{"name": "nome do conceito/entidade", "category": "topicos|entidades|conceitos", "is_new": true}}
  ],
  "potential_conflicts": [
    {{"existing_page": "caminho/da/pagina.md", "description": "qual contradição"}}
  ],
  "source_bias": "baixo|medio|alto",
  "source_type": "academico|blog|documentacao-oficial|noticia|outro"
}}
```

Diretrizes:
- `entities_mentioned`: identifique 3-8 conceitos/entidades centrais que merecem página própria. Marque `is_new: false` se a entidade já aparece em "Páginas existentes" acima.
- `potential_conflicts`: só preencha se você ler "Páginas existentes" e detectar contradição clara. Se não houver, retorne array vazio `[]`.
- `source_bias`: avalie se a fonte tem viés óbvio (ex: post de fornecedor promovendo seu produto = alto; paper acadêmico com benchmarks = baixo).
- Categorias permitidas exatas: topicos, entidades, conceitos.
