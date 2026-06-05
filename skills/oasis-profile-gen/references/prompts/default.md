# Template de Prompt Padrão — OASIS Profile Generator

## Instruções

Gere um perfil de agente para simulação baseado na entidade abaixo.
Analise o nome, resumo, atributos e relações para inferir uma personalidade
coerente e realista.

## Dados da Entidade

**Nome:** {name}
**Resumo:** {summary}
**Atributos:** {attributes}

## Relações no Grafo

{related_edges}

## Contexto (Nós Relacionados)

{related_nodes}

## Perfil Requerido

Gere um objeto JSON **válido** (sem texto adicional) com os seguintes campos:

```json
{
  "bio": "Biografia de 2-3 frases baseada nos dados da entidade",
  "persona": "Voz em primeira pessoa (1 parágrafo) expressando personalidade",
  "interests": ["interesse1", "interesse2", "interesse3", ...],
  "mbti": "TIPO_MBTI",
  "topics": ["topico1", "topico2", ...],
  "speaking_style": "Descrição do estilo de fala",
  "twitter_behavior": {
    "post_frequency": "alta|media|baixa",
    "content_types": ["opiniao", "compartilhamento", "pergunta", "analise", "critica"],
    "interaction_style": "engajador|observador|influenciador|provocador"
  },
  "reddit_behavior": {
    "post_frequency": "alta|media|baixa",
    "subreddits_preference": ["topico1", "topico2"],
    "comment_style": "analitico|humoristico|informativo|debatedor"
  }
}
```

## Regras

1. A `bio` deve ser factual, baseada no resumo e atributos da entidade
2. A `persona` deve refletir a personalidade implícita nos dados
3. Os `interests` devem ser inferidos das relações e atributos
4. O `mbti` deve ser consistente com a persona descrita
5. Os `topics` devem refletir o domínio de conhecimento da entidade
6. O `speaking_style` deve ser coerente com o tipo de entidade
7. Responda **APENAS** com o JSON, sem texto introdutório ou conclusivo
