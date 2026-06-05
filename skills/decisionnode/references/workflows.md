# DecisionNode — Workflows

## 1. Registrar Decisão Arquitetural

```bash
decide add -s "API Gateway" -d "Usar Kong como API Gateway" -r "Já temos experiência com Kong na equipe, suporta plugins customizados" -c "Nenhum"
```

## 2. Buscar Decisões ao Iniciar Tarefa

O agente MCP chama automaticamente `search_decisions` com a descrição da tarefa. Exemplo:
- Tarefa: "adicionar cache no backend"
- Query MCP: "cache backend redis performance"
- Retorna: decisões anteriores sobre cache, estratégias de armazenamento, etc.

## 3. Decisões Globais (Cross-Project)

```bash
decide add --global -s "Segurança" -d "Nunca comitar .env files" -r "Política de segurança da organização"
```

Aparecem em todos os projetos automaticamente.

## 4. Auditoria

```bash
decide history           # ver histórico completo
decide list --status deprecated  # decisões obsoletas
decide export md > docs/decisoes.md  # exportar para documentação
```

## 5. Manutenção

```bash
decide check      # verificar embeddings faltando
decide embed      # gerar embeddings pendentes
decide clean      # remover vetores órfãos
decide delete-scope "Backend"  # remover escopo inteiro
```
