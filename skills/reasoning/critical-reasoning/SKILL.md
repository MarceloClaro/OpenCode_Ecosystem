---
name: critical-reasoning
version: "1.0.0"
kind: python
category: reasoning
affinity: {cora-debate: 0.95, agent-forum: 0.90, reasoning-orchestrator: 0.85, the-fool: 0.80}
---

# Critical Reasoning — Analise de Argumentos e Falacias

Framework para analise critica de argumentos, deteccao de falacias logicas,
decomposicao de premissas/conclusoes e avaliacao de solidez argumentativa.

## Capacidades

- **Decomposicao de Argumentos**: Premissas, conclusoes, pressupostos ocultos
- **Deteccao de Falacias**: 20+ falacias (ad hominem, straw man, false dilemma, etc.)
- **Avaliacao de Solidez**: Validade logica + verdade factual das premissas
- **Contra-argumentacao**: Geracao de contra-argumentos estruturados
- **Debate Analysis**: Analise de dialogos multi-turno para consistencia logica
- **Vies Cognitivo**: Identificacao de vieses em raciocinios

## Uso

```python
from skills.reasoning.critical_reasoning.scripts.critical_engine import CriticalEngine

engine = CriticalEngine()
result = engine.analyze("If we invest in AI, we will lose jobs. Therefore, we should not invest in AI.")
# result: {
#   "fallacies": ["false_dilemma", "slippery_slope"],
#   "premises": ["Investing in AI leads to job loss"],
#   "hidden_assumptions": ["No new jobs are created by AI"],
#   "strength": "weak"
# }
```

## Ficheiros

- `scripts/critical_engine.py` — Motor de raciocinio critico
- `scripts/fallacy_db.py` — Banco de dados de 20+ falacias logicas
- `scripts/argument_parser.py` — Parser de linguagem natural para estrutura logica
