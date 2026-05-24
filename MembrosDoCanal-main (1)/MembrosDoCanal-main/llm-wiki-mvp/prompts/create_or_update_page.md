Você é o mantenedor de uma wiki. Crie uma página markdown sobre `{entity_name}` na categoria `{category}`.

# Schema da wiki
{schema}

# Fonte que introduziu/atualizou esta entidade
{source_summary}

# Pontos-chave relevantes da fonte sobre `{entity_name}`
{relevant_points}

# Página existente sobre `{entity_name}` (se houver — vazio se for nova)
{existing_content}

# Sua tarefa

Produza o conteúdo completo da página markdown. Estrutura obrigatória:

```
---
tipo: {category_singular}
data_atualizacao: {today}
---

# {entity_name_title}

## (seções em prosa, com wikilinks para outras páginas relevantes)

## Linha do tempo de evidências
- {today} — observação resumida — [[fontes/{source_filename}]]
```

Diretrizes:
- Se já existe uma página, INTEGRE a nova informação preservando o que já estava lá. Adicione uma entrada nova na linha do tempo. Atualize seções existentes se a fonte trouxer dados novos.
- Se for página nova, crie 2-4 seções curtas em prosa fluente, com wikilinks para outras páginas quando mencionar conceitos relacionados.
- Sempre atribua: "Segundo [[fontes/X.md]], ..." em vez de afirmar diretamente.
- Se houver conflito conhecido com outras fontes, adicione um bloco:
  ```
  > [!warning] Conflito entre fontes
  > [[fontes/A.md]] afirma X. [[fontes/B.md]] afirma Y. Posições não foram resolvidas.
  ```
- NÃO use markdown fences (```) ao redor da resposta. Retorne só o conteúdo da página, começando com `---`.
- Mantenha conciso: 200-500 palavras tipicamente.
