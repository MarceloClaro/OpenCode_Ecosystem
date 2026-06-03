---
category: agency
kind: python
version: "1.0.0"
---

# DatabaseOptimizer — Otimizador de Banco de Dados

Evolucao Round 14 (Agency Engineering). Motor de analise de banco de dados extraido do agente `engineering-database-optimizer` do repositorio agency-agents.

## Proposito
Analisar schemas SQL, detectar queries N+1, sugerir indices e identificar anti-padroes SQL. Opera offline com Python 3.12 stdlib.

## Uso
```python
from dboptimizer_engine import DatabaseOptimizer

engine = DatabaseOptimizer()
if engine.available:
    schema = engine.analyze_schema(ddl_text)
    n1 = engine.detect_n_plus_one(source_code)
    indexes = engine.suggest_indexes(ddl_text, queries)
    antipatterns = engine.detect_antipatterns(query_text)
```

## Integracao OpenCode
- **MCPs**: sqlite, code-runner, sequential-thinking
- **Skills**: database-optimizer, sql-pro, postgres-pro
- **Categoria**: agency/engineering
