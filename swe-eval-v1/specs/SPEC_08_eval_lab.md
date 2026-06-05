# SPEC-08: EvalLab Framework (P3)

> Lacuna 8: Infraestrutura para experimentos controlados A/B com analise estatistica

## Arquitetura

```
eval_lab/
├── __init__.py
├── experiment_runner.py    # Executor de experimentos controlados
├── conditions.py           # Definicao de condicoes A/B
├── metrics_collector.py    # Coleta automatizada de metricas
├── statistical_analyzer.py # Analise estatistica (t-test, Cohen's d, ANOVA)
├── report_generator.py     # Geracao de relatorios de experimento
├── container_orchestrator.py # Reproducibilidade via Docker
└── experiment_registry.py  # Registro de experimentos executados
```

## Metricas Automatizadas

| Metrica | Descricao | Coleta |
|---------|-----------|--------|
| `time_to_complete` | Tempo total ate conclusao da tarefa | Wall clock |
| `defect_rate` | Defeitos por 100 linhas de codigo | Test runner |
| `context_coverage` | % de arquivos relevantes que o agente leu | Hook de filesystem |
| `token_cost` | Custo total de tokens da sessao | API tracking |
| `human_interventions` | Quantas vezes o humano precisou intervir | Counter |
| `spec_fidelity` | % de requisitos da spec implementados | SpecDriftDetector |
| `correction_loops` | Quantas iteracoes de correcao por tarefa | Phase tracker |
| `arch_violations` | Violacoes de decisoes arquiteturais | Context grounding |

## Formato do Experimento

```json
{
  "experiment_id": "EXP-2026-001",
  "name": "SDD vs Vibe Coding: Taxa de Defeitos",
  "hypothesis": "SDD produz 50% menos defeitos que vibe coding",
  "conditions": {
    "A": {
      "name": "SDD (treatment)",
      "framework": "spec-driven",
      "config": {"spec_required": true, "tests_required": true}
    },
    "B": {
      "name": "Vibe Coding (control)",
      "framework": "unstructured",
      "config": {"spec_required": false, "tests_required": false}
    }
  },
  "tasks": ["SWE-001", "SWE-004"],
  "repetitions": 10,
  "metrics": ["defect_rate", "time_to_complete", "token_cost"],
  "statistical_tests": ["t_test", "cohens_d"]
}
```

## Analise Estatistica

```python
@dataclass
class ExperimentResult:
    condition_a: list[float]
    condition_b: list[float]
    
    @property
    def t_statistic(self) -> float:
        """Teste t de Student para duas amostras independentes."""
        ...
    
    @property
    def p_value(self) -> float:
        """Valor-p bicaudal."""
        ...
    
    @property
    def cohens_d(self) -> float:
        """Tamanho de efeito: pequeno (0.2), medio (0.5), grande (0.8)."""
        ...
    
    @property
    def is_significant(self) -> bool:
        """p < 0.05 com correcao Bonferroni."""
        ...
```
