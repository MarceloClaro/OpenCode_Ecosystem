---
name: mcp_builder
category: agency
domain: specialized
version: "1.0.0"
kind: python
---

# MCP Builder

Agente especializado em construcao de servidores MCP (Model Context Protocol). Valida schemas de ferramentas, registra tools com nomes unicos e formata respostas no padrao MCP.

## Uso
```python
from mcp_builder_engine import ParamDef, ToolDef, ToolRegistry
```

## CTs (4)
1. Parameter validation -- tipos e obrigatoriedade
2. Tool registry uniqueness -- nomes duplicados rejeitados
3. Validate tool call -- validacao completa de chamada
4. Error formatting -- padrao MCP isError + content

## Dependencias
Python 3.12, stdlib only (dataclasses, enum, typing).
