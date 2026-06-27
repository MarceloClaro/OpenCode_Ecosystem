# Skill: qualitative-analysis
# Descrição: Pipeline completo de análise qualitativa em Python
#替代 NVivo 12 e MAXQDA com código aberto validável

## Ativação
- "análise qualitativa"
- "codificação de entrevistas"
- "categorização temática"
- "triangulação de métodos"
- "NVivo" ou "MAXQDA"

## Pipeline

### 1. Codificação
```python
from qualitative_coder import QualitativeCoder

coder = QualitativeCoder(language="pt-br")
codes = coder.code(texto_entrevista, method="axial")
```

### 2. Categorização
```python
categories = coder.categorize(codes)
# -> [{"category": "Barreiras Implementação", "codes": [...], "frequency": 12}]
```

### 3. Triangulação
```python
triang = coder.triangulate(dados_quant, dados_qual)
# -> {"convergence": 0.73, "divergence": [...], "gaps": [...]}
```

### 4. Relatório
```python
report = coder.report({"categories": categories, "triangulation": triang}, format="latex")
# -> String LaTeX pronta para compilar
```

## Validação TDD
- 43 testes unitários (pytest)
- Cobertura >= 90%
- Zero dependências proprietárias

## Referência
- SPEC-050: `specs/SPEC-050_QUALITATIVE-CODER.md`
- Código: `qualitative_coder/`
- Testes: `qualitative_coder/tests/`
