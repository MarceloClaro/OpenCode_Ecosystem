# SWE-EVAL v1.0 -- Framework de Evolucao do Ecossistema OpenCode

> Derivado de: Manuscrito 1 "Engenharia de Software com Agentes Inteligentes" + Manuscrito 2 "From Prompt to Process" (arXiv:2606.04967v1)
> Auditoria: 04/06/2026 -- 9 lacunas identificadas, 0 componentes completos
> Objetivo: Elevar OpenCode de "ecossistema de pesquisa" para "infraestrutura de producao auditavel"

---

## Arquitetura de Implementacao

```
swe-eval-v1/
├── FRAMEWORK.md                          # esta spec-mestra
├── specs/                                # especificacoes por componente
│   ├── SPEC_01_swe_benchmark.md
│   ├── SPEC_02_supply_chain.md
│   ├── SPEC_03_spec_drift.md
│   ├── SPEC_04_context_grounding.md
│   ├── SPEC_05_artifact_sync.md
│   ├── SPEC_06_permission_tiers.md
│   ├── SPEC_07_registry_v2.md
│   ├── SPEC_08_eval_lab.md
│   └── SPEC_09_cross_platform.md
├── benchmarks/                           # SWE Process Benchmarks (L1)
├── supply_chain/                         # Supply Chain Security (L2+7)
├── spec_drift/                           # SpecDriftDetector (L3)
├── context_grounding/                    # API Hallucination Detection (L4)
├── artifact_sync/                        # ArtifactSyncEngine (L5)
├── permission_tiers/                     # PermissionTiers + Audit (L6)
├── eval_lab/                             # EvalLab Framework (L8)
├── cross_platform/                       # CrossPlatformValidator (L9)
└── tests/                                # TDD suites para todos os componentes
```

## Matriz de Prioridade

| ID | Componente | Status Atual | Meta | Prioridade | Esforco |
|----|-----------|-------------|------|------------|---------|
| L1 | SWE Process Benchmarks | 0% | 100% | P2 | Alto |
| L2 | Supply Chain Security | 0% | 100% | P0 | Medio |
| L3 | Spec Drift Detection | 25% | 100% | P1 | Alto |
| L4 | Context Grounding Metrics | 35% | 100% | P1 | Alto |
| L5 | Living Artifacts Sync | 0% | 100% | P2 | Medio |
| L6 | Permission Tiers + Audit | 60% | 100% | P0 | Baixo |
| L7 | Agent Registry v2.0 | 30% | 100% | P2 | Medio |
| L8 | EvalLab Framework | 10% | 100% | P3 | Alto |
| L9 | Cross-Platform Validator | 0% | 100% | P3 | Baixo |

## Dependencias entre Componentes

```
L7 (Registry v2.0) ──────► L2 (Supply Chain Security)
                                    │
L6 (Permission Tiers) ──────────────┤
                                    ▼
L3 (Spec Drift) ◄──────── L5 (Artifact Sync)
       │                        │
       ▼                        ▼
L4 (Context Grounding)    L1 (SWE Benchmarks)
       │                        │
       └────────┬───────────────┘
                ▼
         L8 (EvalLab)
                │
                ▼
         L9 (Cross-Platform)
```

## Metrica de Sucesso

Cada componente deve atingir cobertura TDD >= 85%, integracao com pelo menos 2 componentes existentes do ecossistema, e documentacao de uso em 3 cenarios reais.
