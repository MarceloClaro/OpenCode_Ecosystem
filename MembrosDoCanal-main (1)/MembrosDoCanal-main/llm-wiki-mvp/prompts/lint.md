Você é o auditor da wiki. Faça um health-check da wiki e retorne JSON estruturado.

# Páginas existentes (com último update)
{pages_metadata}

# Páginas órfãs detectadas (sem inbound link)
{orphan_pages}

# Links quebrados detectados
{broken_links}

# Páginas estagnadas (sem update há 30+ dias)
{stale_pages}

# Sua tarefa

Produza um relatório em JSON:

```json
{{
  "summary": "frase resumindo a saúde geral da wiki",
  "issues": [
    {{
      "severity": "alta|media|baixa",
      "type": "orfa|link-quebrado|estagnacao|conceito-sem-pagina|sugestao",
      "description": "descrição clara do problema",
      "affected_pages": ["paths"],
      "suggested_action": "o que fazer"
    }}
  ],
  "next_steps": ["sugestão 1", "sugestão 2", "sugestão 3"]
}}
```

Diretrizes:
- Não duplique itens já listados nas seções "órfãs", "links quebrados", "estagnadas" — esses são DADOS PRÉ-CALCULADOS para você. Apenas se houver mais 5 páginas órfãs, agrupe em UM issue de severidade alta.
- Sugira 2-3 next_steps concretos: novos critérios a investigar, fontes que valeria buscar, refatorações que melhorariam a wiki.
- Retorne APENAS o JSON, sem texto antes ou depois.
