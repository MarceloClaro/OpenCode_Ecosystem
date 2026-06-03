---
name: spec-015-d6-geociencias
description: "Suite TDD para D6 (Raciocinio em Geociencias) do CORA-Eval. 3 CTs em nivel N1: Rochas, Temperatura, Atmosfera. Validacao via TDD com classificacao real de rochas e camadas atmosfericas. Use quando precisar validar raciocinio em geociencias do ecossistema OpenCode."
spec: "SPEC-015"
version: "1.0"
category: research
tags: [cora-eval, d6, geociencias, tdd, validacao]
dependencies: [SPEC-001, CORA-Eval]
tdd_suite: "artigo/evaluations/tests/test_d6_geociencias.py"
ct_count: 3
status: active
---

# SPEC-015 — Suite D6: Raciocínio em Geociências

## Objetivo
Validar a capacidade de raciocínio em geociências (D6 do CORA-Eval)
via 3 critérios de teste N1 (Básico) com classificação real de rochas,
conversão de temperatura e identificação de camadas atmosféricas.

## CTs

| CT | Descrição | Nível |
|:--:|-----------|:-----:|
| D6-N1-01 | Classificação de Rochas —ígnea/sedimentar/metamórfica por textura e composição (granito, basalto, calcário, arenito, gnaisse, quartzito) | N1 |
| D6-N1-02 | Conversão de Temperatura — Celsius↔Kelvin↔Fahrenheit com zero absoluto e ponto de fusão/ebulição da água | N1 |
| D6-N1-03 | Camadas Atmosféricas — identificação por altitude: Troposfera, Estratosfera, Mesosfera, Termosfera, Exosfera | N1 |

## Funções Implementadas
`classify_rock`, `celsius_to_kelvin`, `kelvin_to_celsius`, `celsius_to_fahrenheit`, `fahrenheit_to_celsius`, `get_atmospheric_layer`

## Execução
```bash
python artigo/evaluations/tests/test_d6_geociencias.py
```

## Integração CORA-Eval
D6 cobre conceitos fundamentais de geociências em nível N1 (Básico),
utilizando classificações reais (rochas, camadas atmosféricas) e
conversões termométricas padrão da física terrestre.
