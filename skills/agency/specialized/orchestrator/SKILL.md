# Agents Orchestrator

Agente especializado em orquestracao autonoma de pipelines de desenvolvimento. Gerencia fluxos completos de trabalho com maquina de estados, logica de retry e controle de qualidade.

## Uso
```python
from orchestrator_engine import Pipeline, Stage, Task
```

## CTs (4)
1. Pipeline happy path -- todas tarefas passam
2. Retry logic -- falha seguida de sucesso
3. Max retries exceeded -- falha permanente
4. Status report -- relatorio fiel ao estado real

## Dependencias
Python 3.12, stdlib only (dataclasses, enum, typing).
