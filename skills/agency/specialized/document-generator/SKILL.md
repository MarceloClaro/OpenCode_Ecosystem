---
name: document_generator
category: agency
domain: specialized
version: "1.0.0"
kind: python
---

# Document Generator

Agente especializado em geracao de documentos via templates. Extrai variaveis de placeholders, preenche templates com substituicao e detecta variaveis faltantes antes da geracao.

## Uso
```python
from document_generator_engine import DocumentGenerator, Template
```

## CTs (4)
1. Template variable extraction -- regex {{var}} captura todas
2. Template filling -- substituicao sem residuos
3. Document generation pipeline -- registro + geracao completa
4. Missing variable detection -- check antes de gerar

## Dependencias
Python 3.12, stdlib only (dataclasses, enum, typing, re).
