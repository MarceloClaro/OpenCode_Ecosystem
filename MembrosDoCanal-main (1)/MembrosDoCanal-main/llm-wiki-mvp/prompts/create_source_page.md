Você é o mantenedor de uma wiki. Crie a página de resumo da fonte ingerida.

# Dados da fonte
- Nome do arquivo: {filename}
- Tipo: {source_type}
- Viés potencial: {source_bias}

# Resumo gerado anteriormente
{summary}

# Pontos-chave
{key_points}

# Páginas que serão atualizadas a partir desta fonte
{updated_pages}

# Sua tarefa

Produza o conteúdo da página markdown que vai em `fontes/{filename_kebab}.md`. Estrutura:

```
---
tipo: fonte
arquivo_original: {filename}
viés: {source_bias}
tipo_fonte: {source_type}
data_ingestao: {today}
---

# {filename_no_ext}

## Origem e viés
1-2 frases descrevendo a origem e o viés potencial.

## Resumo
(o resumo aqui, em 2-3 parágrafos)

## Pontos-chave
- ponto 1
- ponto 2

## Páginas atualizadas a partir desta fonte
- [[topicos/exemplo.md]]
- [[conceitos/exemplo.md]]
```

NÃO use markdown fences ao redor. Retorne começando com `---`.
