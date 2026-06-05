# API Reference — Reasoning Orchestrator

Documentacao de referencia para integracao programatica.

## Uso via Checkpoint Nexus

```python
checkpoint = {
    "depth": "L3",
    "reasoning_types": ["bayesian", "systemic", "falsificationist"],
    "domain": "IA & LLMs",
    "barrier": "falsificationist"
}
```

## Integracao com Sequential Thinking MCP

O Reasoning Orchestrator combina com o MCP `sequential-thinking` para:

1. Definir profundidade (L1-L4) antes de iniciar a cadeia de pensamento
2. Selecionar tipos de raciocinio como lentes analiticas
3. Aplicar barreiras de sincronizacao ao final

## Integracao com Agentes

| Agente | Raciocinio Primario | Nivel |
|--------|-------------------|-------|
| code-reviewer | Falsificacionista | L3 |
| architect | Sistemico | L3 |
| debugger | Abdutivo | L3 |
| story-mapper | Analogico | L2 |
| prioritization-engine | Custo de Oportunidade | L2 |
