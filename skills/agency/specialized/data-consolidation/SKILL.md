---
name: data_consolidation
category: agency
domain: specialized
version: "1.0.0"
kind: python
---

# Data Consolidation Agent

Agente especializado em consolidacao de dados de multiplas fontes. Alinha schemas, faz merge por chave com deteccao de duplicatas e executa funcoes de agregacao (SUM, AVG, COUNT, MIN, MAX).

## Uso
```python
from data_consolidation_engine import DataConsolidator, SourceSchema
```

## CTs (4)
1. Schema registration -- colunas comuns entre fontes
2. Data merging with key -- merge com deduplicacao
3. Aggregation functions -- todas as 5 operacoes
4. Empty and edge cases -- datasets vazios, colunas ausentes

## Dependencias
Python 3.12, stdlib only (dataclasses, enum, typing, collections).
