### Workflows n8n (JSON)

- Identificar o nó pelo campo `"name"`  -  retornar apenas o objeto do nó alterado
- Se a alteração é no `jsCode` de um Code Tool, retornar apenas o nó com o `jsCode` atualizado
- Se a alteração é em `connections`, retornar apenas o bloco de connections afetado
- **Regra crítica**: nunca alterar o `webhookId` do MCP Server Trigger (`0199517e-f508-4cc9-8dd4-9532ffa42e6c`) em edições parciais  -  isso quebra a URL de conexão Claude ↔ n8n
- Para alterações que afetam nó + connection, entregar dois blocos separados e identificados
