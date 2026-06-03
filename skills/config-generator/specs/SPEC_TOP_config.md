# SPEC_TOP_config — ConfigGenerator TDD Specification

**Skill:** config-generator  
**Source:** scripts/generator.py → ConfigGenerator, TimeSimulationConfig  
**Framework:** pytest  
**Status:** Spec-Driven

---

## CT-1: test_init — Inicializacao e deteccao de LLM disponivel

**Objetivo:** Verificar que `ConfigGenerator` detecta corretamente se
LLM esta disponivel (api_key != None) e armazena o model.

**Passos:**
1. `ConfigGenerator(api_key=None)` → `llm_available is False`
2. `ConfigGenerator(api_key="sk-test")` → `llm_available is True`
3. Verificar `gen.model` armazenado

**Esperado:** Flag `llm_available` reflete presenca de api_key.

---

## CT-2: test_fallback — Geracao completa com fallback heuristico

**Objetivo:** Confirmar que `generate()` produz `SimulationParameters`
completo (time, event, agents, platform) mesmo sem LLM (modo fallback).

**Passos:**
1. `gen.generate("test-001", "Debate sobre educacao", entities)`
2. Verificar `params.simulation_id`, `params.time_config` nao-nulo
3. Verificar `len(params.agent_configs) == len(entities)`
4. Verificar `params.platform_config` nao-nulo

**Esperado:** Parametros completos via fallback heuristico por tipo.

---

## CT-3: test_parse_config — Parsing e validacao de ranges

**Objetivo:** Validar que `_parse_time_config()` e
`_get_default_platform_config()` produzem valores dentro dos ranges
esperados.

**Passos:**
1. `_parse_time_config({}, 10)` → `total_rounds >= 10`
2. `_get_default_platform_config("Media")` → soma dos weights == 1.0

**Esperado:** Valores normalizados e dentro dos limites.

---

## CT-4: test_available — Type rules, aliases e timezone

**Objetivo:** Garantir que `TYPE_RULES`, `TYPE_ALIASES` e `BRAZIL_TIMEZONE`
estao populados e `_resolve_type_alias()` funciona.

**Passos:**
1. `len(TYPE_RULES) >= 5`, `len(TYPE_ALIASES) >= 10`
2. `"dead_hours" in BRAZIL_TIMEZONE`
3. `_resolve_type_alias("prof") == "Professor"`

**Esperado:** Sistema de tipos funcional.
