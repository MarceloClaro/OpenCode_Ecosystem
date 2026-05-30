# Ações de Agente Suportadas

## Ações Sociais

### CREATE_POST
- `action_args: {content}`
- Template: `"{agent}: Posted a post: '{content}'"`

### LIKE_POST / DISLIKE_POST
- `action_args: {post_content, post_author_name}`
- Template: `"{agent} Liked {author}'s post: '{content}'"`

### REPOST
- `action_args: {original_content, original_author_name}`
- Template: `"{agent} Reposted {author}'s post: '{content}'"`

### QUOTE_POST
- `action_args: {original_content, original_author_name, quote_content}`
- Template: `"{agent} Quoted {author}'s post '{original}', commented: '{quote}'"`

### FOLLOW
- `action_args: {target_user_name}`
- Template: `"{agent} Followed user '{target}'"`

### CREATE_COMMENT
- `action_args: {content, post_content, post_author_name}`
- Template: `"{agent} Commented on {author}'s post: '{content}'"`

### LIKE_COMMENT / DISLIKE_COMMENT
- `action_args: {comment_content, comment_author_name}`
- Template: `"{agent} Liked {author}'s comment: '{content}'"`

### SEARCH_POSTS / SEARCH_USER
- `action_args: {query}`
- Template: `"{agent} Searched for '{query}'"`

### MUTE
- `action_args: {target_user_name}`
- Template: `"{agent} Muted user '{target}'"`

### DO_NOTHING (ignorado)
- Não enviado ao grafo
- Contabilizado em `skipped_count`

## Sistema de Buffer

```
Plataforma  Buffer  Batch Size  Nome Exibição
──────────  ──────  ──────────  ────────────
twitter      []     5           worldinterface1
reddit       []     5           worldinterface2
```

- Atividades chegam via `Queue` thread-safe
- Worker de background drena a fila e preenche buffers por plataforma
- Quando buffer atinge `BATCH_SIZE` (5), envia lote
- `SEND_INTERVAL` de 0.5s entre lotes
- Retry com backoff: 3 tentativas, delay 2s * (attempt + 1)
