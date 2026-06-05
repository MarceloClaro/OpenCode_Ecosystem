---
name: config-generator
description: Gera configuracoes complexas de simulacao usando LLM step-by-step com fallback heuristico
pattern: P13
trigger: /config-generator
aliases:
  - /cfg-gen
  - /cg
usage: |
  /config-generator [subcommand] [args...]
subcommands:
  - name: generate
    args: "<id> <requirement>"
    description: Gera configuracao completa (4 etapas: tempo, eventos, agentes, plataforma)
    example: '/config-generator generate sim-001 "Debate sobre reforma universitaria"'
  - name: time
    args: "<requirement>"
    description: Gera apenas configuracao de tempo
    example: '/config-generator time "Eleicoes estudantis"'
  - name: validate
    args: "<arquivo.json>"
    description: Valida um arquivo de configuracao existente
    example: '/config-generator validate config.json'
  - name: demo
    args: ""
    description: Executa demo com fallback heuristico (sem LLM)
    example: '/config-generator demo'
---

# /config-generator — Step-by-step LLM Config Generator (P13)

Gera configuracoes complexas de simulacao em 4 etapas usando chamadas LLM
step-by-step com fallback heuristico, inspirado pelo SimulationConfigGenerator
do MiroFish-Offline.

## Subcomandos

### `generate <id> "<requirement>"`
Executa o pipeline completo de 4 etapas:
1. **Time**: rounds, intervalos, multiplicadores de atividade (CHINA_TIMEZONE)
2. **Event**: posts iniciais, trending topic, tags narrativas
3. **Agent**: configuracoes por entidade em lotes de 15
4. **Platform**: pesos de algoritmo, thresholds de moderacao/viralidade

Retorna JSON completo com todos os parametros e score de confianca.

### `time "<requirement>"`
Gera apenas a configuracao de tempo. Ideal para testar ou ajustar parametros
temporais antes de gerar o resto.

### `validate <arquivo.json>`
Valida um JSON de configuracao existente:
- Verifica estrutura (5 secoes obrigatorias)
- Verifica ranges de valores
- Verifica tipos de campos
- Retorna relatorio de validacao

### `demo`
Executa o gerador em modo demo sem LLM:
- Usa fallback heuristico para todas as 4 etapas
- Gera 6 entidades de exemplo (Official, Student, Professor, MediaOutlet, Alumni, Person)
- Ideal para testar o pipeline sem dependencias externas

## Exemplos

```
/config-generator generate sim-001 "Debate sobre reforma universitaria"
/config-generator time "Eleicoes estudantis"
/config-generator validate configs/sim-001.json
/config-generator demo
```

## Dependencias

- Python 3.11+
- OpenAI SDK (opcional, para modo com LLM)
- `pip install openai` (se usar LLM)

## Algoritmo

```
Entrada -> Build Context -> Step 1 Time -> Step 2 Event
  -> Step 3 Agents (N batches) -> Step 4 Platform -> SimulationParameters
```

Cada etapa: LLM (3 retries, temp decrescente) -> fallback heuristico se falhar.
