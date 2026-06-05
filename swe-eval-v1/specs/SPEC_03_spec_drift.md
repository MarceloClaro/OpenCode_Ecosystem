# SPEC-03: SpecDriftDetector (P1)

> Lacuna 3: Deteccao automatica de divergencia spec <-> implementacao

## Arquitetura

```
spec_drift/
├── __init__.py
├── drift_detector.py       # Motor principal de deteccao
├── ast_comparator.py       # Comparacao AST entre spec e codigo
├── contract_extractor.py   # Extrai contratos da spec (dado X, esperado Y)
├── behavior_hasher.py      # Hash de comportamento de funcoes
├── drift_report.py         # Relatorio de divergencias encontradas
├── drift_resolver.py       # Sugestoes de correcao (spec ou codigo?)
├── ci_gate.py              # Gate de CI/CD: bloqueia merge se drift > threshold
└── schema.sql              # Persistencia de deteccoes
```

## Fluxo de Deteccao

```
Spec (markdown) + Codigo (Python/TS)
           │
           ▼
[1] contract_extractor: extrai asserts da spec
    "O endpoint GET /users retorna JSON com campo 'id' e 'name'"
    → {"method": "GET", "path": "/users", "response_fields": ["id", "name"]}
           │
           ▼
[2] ast_comparator: parseia o codigo e compara com contratos
    - Verifica se a rota existe
    - Verifica se os campos de resposta batem
    - Verifica se os tipos sao compativeis
           │
           ▼
[3] behavior_hasher: gera hash do comportamento observado
    - Executa testes contra a implementacao
    - Compara hash com hash esperado da spec
           │
           ▼
[4] drift_report: classifica divergencias
    - CRITICAL: spec diz X, codigo faz Y (comportamento diferente)
    - WARNING: spec menciona campo Z, codigo nao implementa
    - INFO: codigo tem funcionalidade nao documentada na spec
           │
           ▼
[5] ci_gate: decide se bloqueia ou permite
    if critical_drifts > 0: BLOCK
    if warning_drifts > threshold: BLOCK
    else: PASS
```

## Metrica de Drift

```
drift_score = (critical * 10) + (warning * 3) + (info * 1)

0:       spec e codigo alinhados
1-5:     drift leve, requer atencao
6-15:    drift moderado, requer correcao
16+:     drift severo, BLOQUEIA merge
```
