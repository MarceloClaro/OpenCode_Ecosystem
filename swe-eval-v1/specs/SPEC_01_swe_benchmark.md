# SPEC-01: SWE Process Benchmarks (P2)

> Lacuna 1: Benchmark que avalia o ciclo completo de engenharia de software com agentes

## Dimensoes do Benchmark

| Dimensao | Metrica | Peso |
|----------|---------|------|
| D1: Specification Completeness | % de requisitos cobertos pela spec | 20% |
| D2: Artifact Consistency | % de artefatos consistentes entre si (spec↔plan↔tasks) | 20% |
| D3: Phase Correction Rate | correcoes / fase (quantas iteracoes ate acertar) | 15% |
| D4: Decision Stability | % de decisoes que permanecem inalteradas | 15% |
| D5: Audit Trail Quality | % de decisoes rastreaveis a uma spec/ADR | 15% |
| D6: Implementation Fidelity | % de codigo que implementa exatamente o que a spec define | 15% |

## Tarefas do Benchmark

```json
{
  "tasks": [
    {
      "id": "SWE-001",
      "name": "REST API CRUD",
      "description": "Implementar API REST para gerenciamento de usuarios com autenticacao JWT",
      "difficulty": "N1",
      "expected_artifacts": ["spec.md", "plan.md", "tasks.md", "api.py", "test_api.py"],
      "validation": {
        "endpoints": ["POST /auth/login", "GET /users", "POST /users", "PUT /users/:id", "DELETE /users/:id"],
        "constraints": ["JWT expiration <= 24h", "password min 8 chars", "email unique"],
        "test_coverage_min": 80
      }
    },
    {
      "id": "SWE-002",
      "name": "Database Migration",
      "description": "Migrar schema de SQLite para PostgreSQL mantendo compatibilidade",
      "difficulty": "N2",
      "expected_artifacts": ["spec.md", "plan.md", "migration.sql", "test_migration.py"]
    },
    {
      "id": "SWE-003",
      "name": "Refactoring com Spec",
      "description": "Refatorar modulo legado de 500 linhas para 5 modulos com spec-driven",
      "difficulty": "N3"
    },
    {
      "id": "SWE-004",
      "name": "Greenfield com SDD+TDD",
      "description": "Construir sistema de notificacoes do zero usando SDD+TDD completo",
      "difficulty": "N3"
    },
    {
      "id": "SWE-005",
      "name": "Bug Fix com Traceability",
      "description": "Corrigir 3 bugs criticos com rastreabilidade completa bug→spec→fix→test",
      "difficulty": "N2"
    }
  ],
  "levels": {
    "N1": "Basico -- 1-2 artefatos, baixa complexidade",
    "N2": "Intermediario -- 3-4 artefatos, dependencias entre modulos",
    "N3": "Avancado -- 5+ artefatos, multiplos agentes, CI/CD gate",
    "N4": "Pesquisa -- cenario real, time simulado, metricas longitudinais"
  }
}
```

## Pipeline de Avaliacao

```
Tarefa SWE-N submetida ao agente
      │
      ▼
[FASE 1] SPEC: agente produz spec.md
      │   avalia: D1 (completeness)
      ▼
[FASE 2] PLAN: agente produz plan.md a partir da spec
      │   avalia: D2 (consistency spec→plan)
      ▼
[FASE 3] TASKS: agente decompoe em tasks.md
      │   avalia: D2 (consistency plan→tasks), D3 (corrections)
      ▼
[FASE 4] IMPLEMENT: agente implementa codigo
      │   avalia: D6 (fidelity), D4 (decision stability)
      ▼
[FASE 5] TEST: agente escreve e executa testes
      │   avalia: D3 (corrections), coverage
      ▼
[FASE 6] REVIEW: agente revisa contra spec original
      │   avalia: D5 (audit trail), D1 (re-check completeness)
      ▼
SCORE final = soma ponderada das 6 dimensoes
```

## Integracao com CORA-Eval

O SWE-Eval complementa o CORA-Eval:
- CORA-Eval: raciocinio cientifico (D1-D11)
- SWE-Eval: processo de engenharia (D1-D6)

Juntos formam o **CORA-SWE-Score**: metrica unificada de competencia do ecossistema.
