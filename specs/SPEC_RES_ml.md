# SPEC_RES_ml — Academic ML Pipeline v1.1

## API Contract (Synthetic — semantic-only skill)

### Skill: `academic-ml-pipeline`

```python
# Pipeline stages (7 etapas documentadas em references/etapa1..7.md):
#   1: Data Loading & Preprocessing
#   2: Exploratory Analysis (descriptive stats, distributions)
#   3: Bootstrap Correlation Matrix
#   4: Classification (ARM — Middle Income Trap)
#   5: Anomaly Detection & Clustering
#   6: Feature Importance (SHAP, permutation)
#   7: Export to Article (figures, tables, ABNT)

# Features (14 total):
#   11 originais: WDI indicators (GDP, education, R&D, tech exports, ...)
#   3 complexidade: knowledge_complexity, export_sophistication, product_density

# Outputs:
#   - Figuras (gerar_figuras.py, seed 42)
#   - Results JSON (results_template.json)
#   - Dataset: WDI + Oxford Insights AIPI + FMI/WEO
```

---

## CT-001: References Completeness (Structural)
**Entrada**: Verificar `references/etapa1.md` a `etapa7.md`
**Esperado**: Todos os 7 arquivos existem com `len(content) > 50`. Feature catalog (`feature_catalog.md`) existe com conteudo.

## CT-002: Results Template Validity (Structural)
**Entrada**: Ler `references/results_template.json`
**Esperado**: Arquivo existe, JSON parse valido (dict ou list)

## CT-003: SKILL.md Metadata (Contract)
**Entrada**: Ler `SKILL.md`
**Esperado**: Contem `"academic-ml-pipeline"`, `"pipeline"`, referencias a Hausmann et al. (2014)

## CT-004: Seed Reproducibility (Design Constraint)
**Entrada**: Documentacao, scripts de figura
**Esperado**: Seed 42 documentado; pipeline deterministico via seed fixing
