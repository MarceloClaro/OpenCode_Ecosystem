## Best Practices

1. **Cache de resultados**: Reutilizar descobertas de sessoes anteriores
   para evitar re-buscar o mesmo repositorio
2. **Backup sempre**: Antes de editar opencode.json, copiar para `.backup`
3. **Prefira npx**: Nao instalar MCPs globalmente. `npx -y` baixa sob demanda
4. **Desativado por padrao**: Todo MCP novo comeca `enabled: false` exceto
   quando usuario fornece a API key no momento da instalacao
5. **Tags sao obrigatorias**: Ajudam na organizacao e descoberta futura
6. **Nomes simples**: Nomes curtos (ex: `postgres`, `redis`, `notion`)
   sem prefixo `@org/` no identificador do MCP
7. **Valide o JSON**: Sempre rodar `ConvertFrom-Json` apos editar
8. **Information Density**: Usar formato conciso (tabelas > paragrafos)
