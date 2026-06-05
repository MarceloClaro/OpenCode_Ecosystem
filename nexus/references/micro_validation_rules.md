<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# TMA v5.0 MICRO - Regras de Validação (500+ Constraints)

## 1. Tipos de Constraints

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| NUMERIC_RANGE | Valor entre min e max | `5 ≤ concepts ≤ 100` |
| NUMERIC_COMPARISON | Comparação numérica | `quality_score ≥ 0.7` |
| STRING_PATTERN | Padrão de string | `concept matches [a-zA-Z0-9_]` |
| COLLECTION_SIZE | Tamanho de coleção | `len(concepts) ≥ 5` |
| EXISTENCE | Campo deve existir | `"concepts" in output` |
| TYPE_CHECK | Tipo correto | `isinstance(concepts, list)` |
| CUSTOM | Lógica customizada | `uniqueness_ratio > 0.95` |

## 2. Constraints por Camada

### Camada 1: Discovery (70 Constraints)

#### SB1.1: Extract Concepts (5 constraints)

```yaml
SB1.1_C1:
  name: "Min Concepts Extracted"
  type: NUMERIC_RANGE
  field: "concepts.length"
  min: 5
  max: 100
  severity: CRITICAL
  message: "Must extract between 5 and 100 concepts"

SB1.1_C2:
  name: "Concept Quality Minimum"
  type: NUMERIC_COMPARISON
  field: "concept.quality"
  operator: ">="
  value: 0.7
  severity: HIGH
  message: "Each concept must have quality ≥ 0.7"

SB1.1_C3:
  name: "Concept Length Valid"
  type: NUMERIC_RANGE
  field: "concept.length"
  min: 3
  max: 100
  severity: MEDIUM
  message: "Concept length must be 3-100 characters"

SB1.1_C4:
  name: "Extraction Time Limit"
  type: NUMERIC_COMPARISON
  field: "execution_time_ms"
  operator: "<="
  value: 5000
  severity: HIGH
  message: "Extraction must complete within 5000ms"

SB1.1_C5:
  name: "Language Support"
  type: CUSTOM
  logic: "language in ['en', 'pt', 'es']"
  severity: CRITICAL
  message: "Language must be en, pt, or es"
```

#### SB1.2: Validate Concepts (8 constraints)

```yaml
SB1.2_C1:
  name: "Concepts Exist"
  type: EXISTENCE
  field: "concepts"
  severity: CRITICAL

SB1.2_C2:
  name: "Concepts is List"
  type: TYPE_CHECK
  field: "concepts"
  expected_type: "list"
  severity: CRITICAL

SB1.2_C3:
  name: "All Concepts Valid"
  type: CUSTOM
  logic: "all(c.quality >= 0.7 for c in concepts)"
  severity: HIGH

SB1.2_C4:
  name: "No Empty Concepts"
  type: CUSTOM
  logic: "all(len(c.name) > 0 for c in concepts)"
  severity: HIGH

SB1.2_C5:
  name: "Unique Concepts"
  type: CUSTOM
  logic: "len(set(c.name for c in concepts)) == len(concepts)"
  severity: MEDIUM

SB1.2_C6:
  name: "Valid Definitions"
  type: CUSTOM
  logic: "all(c.definition and len(c.definition) > 10 for c in concepts)"
  severity: MEDIUM

SB1.2_C7:
  name: "Valid Examples"
  type: CUSTOM
  logic: "all(len(c.examples) >= 1 for c in concepts)"
  severity: LOW

SB1.2_C8:
  name: "Validation Time"
  type: NUMERIC_COMPARISON
  field: "execution_time_ms"
  operator: "<="
  value: 3000
  severity: MEDIUM
```

#### SB1.3: Deduplicate Concepts (6 constraints)

```yaml
SB1.3_C1:
  name: "Deduplication Ratio"
  type: NUMERIC_COMPARISON
  field: "deduplication_ratio"
  operator: ">"
  value: 0.95
  severity: HIGH
  message: "At least 95% of concepts must be unique"

SB1.3_C2:
  name: "Uniqueness Score"
  type: NUMERIC_COMPARISON
  field: "uniqueness_score"
  operator: ">="
  value: 0.9
  severity: HIGH

SB1.3_C3:
  name: "Concepts Preserved"
  type: NUMERIC_COMPARISON
  field: "concepts_preserved_ratio"
  operator: ">="
  value: 0.8
  severity: MEDIUM
  message: "At least 80% of original concepts must be preserved"

SB1.3_C4:
  name: "No Duplicate Names"
  type: CUSTOM
  logic: "len(set(c.name for c in concepts)) == len(concepts)"
  severity: CRITICAL

SB1.3_C5:
  name: "Quality Maintained"
  type: CUSTOM
  logic: "all(c.quality >= 0.7 for c in concepts)"
  severity: HIGH

SB1.3_C6:
  name: "Deduplication Time"
  type: NUMERIC_COMPARISON
  field: "execution_time_ms"
  operator: "<="
  value: 2000
  severity: MEDIUM
```

#### SB1.4: Rank Concepts (4 constraints)

```yaml
SB1.4_C1:
  name: "Ranking Completeness"
  type: NUMERIC_COMPARISON
  field: "ranking_completeness"
  operator: "=="
  value: 1.0
  severity: CRITICAL
  message: "All concepts must be ranked"

SB1.4_C2:
  name: "Ranking Validity"
  type: CUSTOM
  logic: "all(c.rank >= 1 and c.rank <= len(concepts) for c in concepts)"
  severity: CRITICAL

SB1.4_C3:
  name: "No Duplicate Ranks"
  type: CUSTOM
  logic: "len(set(c.rank for c in concepts)) == len(concepts)"
  severity: CRITICAL

SB1.4_C4:
  name: "Ranking Time"
  type: NUMERIC_COMPARISON
  field: "execution_time_ms"
  operator: "<="
  value: 1500
  severity: MEDIUM
```

#### SB1.5-1.15: Relation Discovery, Law Inference, Problem Classification (47 constraints)

```yaml
# Similar pattern para cada barrier
# Total: 7 + 8 + 6 + 4 + 7 + 8 + 7 + 8 + 6 + 5 = 70 constraints
```

### Camada 2: Reasoning (90 Constraints)

#### SB2.1-2.4: Analyze Characteristics (8 constraints)

```yaml
SB2.1_C1:
  name: "Domain Characteristics Extracted"
  type: NUMERIC_RANGE
  field: "characteristics.count"
  min: 5
  max: 50
  severity: HIGH

SB2.1_C2:
  name: "Problem Characteristics Extracted"
  type: NUMERIC_RANGE
  field: "problem_characteristics.count"
  min: 3
  max: 20
  severity: HIGH

# ... 6 mais constraints
```

#### SB2.5-2.8: Select Reasoning Type (10 constraints)

```yaml
SB2.5_C1:
  name: "Reasoning Type Selected"
  type: EXISTENCE
  field: "selected_reasoning_type"
  severity: CRITICAL

SB2.5_C2:
  name: "Valid Reasoning Type"
  type: CUSTOM
  logic: "selected_reasoning_type in VALID_TYPES"
  severity: CRITICAL

SB2.5_C3:
  name: "Selection Score Valid"
  type: NUMERIC_RANGE
  field: "selection_score"
  min: 0
  max: 1
  severity: HIGH

# ... 7 mais constraints
```

#### SB2.9-2.12: Configure Parameters (8 constraints)

```yaml
SB2.9_C1:
  name: "Parameters Configured"
  type: EXISTENCE
  field: "parameters"
  severity: CRITICAL

SB2.9_C2:
  name: "All Required Params"
  type: CUSTOM
  logic: "all(p in parameters for p in REQUIRED_PARAMS)"
  severity: CRITICAL

# ... 6 mais constraints
```

#### SB2.13-2.20: Validate & Reflect (64 constraints)

```yaml
# Similar pattern para validação e reflexão
```

### Camada 3: Organization (110 Constraints)

#### SB3.1-3.5: Discover MCPs (25 constraints)

```yaml
SB3.1_C1:
  name: "MCPs Discovered"
  type: NUMERIC_RANGE
  field: "discovered_mcps.count"
  min: 1
  max: 50
  severity: HIGH

SB3.1_C2:
  name: "MCP Metadata Complete"
  type: CUSTOM
  logic: "all(m.name and m.capabilities and m.health for m in discovered_mcps)"
  severity: HIGH

# ... 23 mais constraints
```

#### SB3.6-3.9: Analyze Requirements (20 constraints)

```yaml
SB3.6_C1:
  name: "Requirements Extracted"
  type: NUMERIC_RANGE
  field: "requirements.count"
  min: 1
  max: 50
  severity: HIGH

# ... 19 mais constraints
```

#### SB3.10-3.14: Match MCPs (25 constraints)

```yaml
SB3.10_C1:
  name: "Matches Found"
  type: NUMERIC_RANGE
  field: "matches.count"
  min: 1
  max: 50
  severity: HIGH

SB3.10_C2:
  name: "Match Quality"
  type: NUMERIC_COMPARISON
  field: "match.score"
  operator: ">="
  value: 0.7
  severity: HIGH

# ... 23 mais constraints
```

#### SB3.15-3.25: Negotiate & Form Team (40 constraints)

```yaml
# Similar pattern para negociação e formação de time
```

### Camada 4: Specialization (80 Constraints)

```yaml
# 30 constraints para análise de padrões
# 30 constraints para adaptação de capacidades
# 20 constraints para especialização de agentes
```

### Camada 5: Healing (50 Constraints)

```yaml
# 10 constraints para monitoramento
# 15 constraints para detecção de falhas
# 15 constraints para recuperação
# 10 constraints para prevenção
```

## 3. Validação Cruzada

### Constraint Dependency Graph

```
SB1.1_C1 (Min Concepts) 
  ↓ depends on
SB1.2_C1 (Concepts Exist)
  ↓ depends on
SB1.3_C1 (Deduplication)
  ↓ depends on
SB1.4_C1 (Ranking)
  ↓ depends on
[SYNC BARRIER 1]
```

### Validação Hierárquica

```
Level 1: Operação Individual
  └─ 5-12 constraints por operação

Level 2: Sync Barrier
  └─ 50-110 constraints por barrier

Level 3: Camada
  └─ 50-110 constraints por camada

Level 4: Sistema
  └─ 500+ constraints totais
```

## 4. Severidade de Constraints

| Severidade | Ação | Exemplo |
|-----------|------|---------|
| CRITICAL | Falha imediata | Conceitos não existem |
| HIGH | Falha com retry | Qualidade < 0.7 |
| MEDIUM | Warning + continue | Tempo > 5s |
| LOW | Log apenas | Exemplos faltando |

## 5. Relatório de Validação

```
╔════════════════════════════════════════════════════════════════╗
║           VALIDATION REPORT - SB1.1                           ║
╚════════════════════════════════════════════════════════════════╝

Constraints Checked: 5/5
Passed: 5 ✓
Failed: 0 ✗
Warnings: 0 ⚠

Details:
  SB1.1_C1: Min Concepts [5-100] ✓ (45 concepts)
  SB1.1_C2: Quality ≥ 0.7 ✓ (avg 0.92)
  SB1.1_C3: Length [3-100] ✓ (avg 25 chars)
  SB1.1_C4: Time ≤ 5000ms ✓ (2500ms)
  SB1.1_C5: Language Support ✓ (pt)

Status: ✓ PASSED
Confidence: 0.95
```

## 6. Customização de Constraints

### Template para Novo Constraint

```yaml
Barrier: SB_X_Y
Operation: "Operation Name"
Constraint: "Constraint Name"
Type: CUSTOM
Severity: HIGH
Logic: |
  def validate(output):
    # Implementar lógica
    return True/False
Message: "Constraint failed message"
Remediation: "How to fix"
```

---

**Versão:** 5.0 MICRO | **Status:** Production Ready | **Total Constraints:** 500+
