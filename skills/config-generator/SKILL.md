---
name: config-generator
description: >
  Gera configurações complexas usando LLM em múltiplas etapas com fallback
  heurístico. Inspirado pelo SimulationConfigGenerator do MiroFish-Offline
  (simulation_config_generator.py). Divide a geração em etapas menores
  (tempo -> eventos -> agentes em lote -> plataforma) para evitar falhas
  de contexto e truncamento.
  Inclui retry com temperatura decrescente, reparo de JSON truncado,
  fallback baseado em regras por tipo de entidade e mapeamento de aliases.
  Use quando precisar de configurações geradas por IA com fallback confiável.
license: MIT
compatibility: opencode
allowed-tools: Read, Grep, Glob, Bash, Write
metadata:
  author: Reversa Engine (padrão MiroFish-Offline SimulationConfigGenerator)
  version: "1.0.0"
  domain: simulation
  triggers: config, configuração, gerar, simulação, parâmetros, LLM
  role: generator
  scope: application
  output-format: json
  related-skills: oasis-profile-gen, process-lifecycle
  inspired-by: MiroFish-Offline simulation_config_generator.py
---

# P13 Config Generator — Step-by-step LLM Config Generator

## Arquitetura: Step-by-Step Generation

```
Requirement + Entities
        |
        v
  [Build Context]  <-- requirement + entities + document_text
        |
    +---+---+
    |       |
 Step 1   Step 2
 Time     Event
 Config   Config
    |       |
    +---+---+
        |
 Step 3a  Step 3b  Step 3c ...
 Agent   Agent    Agent
 Batch   Batch    Batch
 (1-15)  (16-30)  (31-45)
        |
        v
 Step 4
 Platform
 Config
        |
        v
 SimulationParameters
```

Cada etapa chama o LLM com um prompt específico. Se o LLM falha ou retorna JSON inválido, o fallback heurístico entra em ação para aquela etapa específica.

## Dataclasses

```python
@dataclass
class TimeSimulationConfig:
    total_rounds: int                      # Rounds totais da simulação
    round_interval_minutes: int            # Intervalo entre rounds (minutos)
    activity_timezone: str                 # Fuso horário
    timezone_dead_hours: List[int]         # Horas mortas (0-5)
    timezone_peak_hours: List[int]         # Horas de pico (19-22)
    peak_activity_probability: float       # Probabilidade de atividade no pico
    base_activity_probability: float       # Probabilidade base fora do pico
    scheduled_posts_per_peak_hour: int     # Posts programados por hora de pico
    scheduled_posts_per_regular_hour: int  # Posts programados por hora regular
    random_activity_ratio: float           # Razão de atividade aleatória
    dead_hour_noise: float                 # Ruído mínimo em horas mortas

@dataclass
class EventConfig:
    initial_posts: List[Dict]              # Posts iniciais (até 25)
    trending_topic: str                    # Tópico principal
    narrative_tags: List[str]              # Tags de narrativa
    event_intensity: str                   # Baixa, Média, Alta
    controversy_level: float               # 0.0 - 1.0
    polarization_expected: float           # 0.0 - 1.0
    ai_influence_expected: float           # 0.0 - 1.0
    external_factors: List[str]            # Fatores externos
    simulation_objective: str              # Objetivo da simulação

@dataclass
class AgentActivityConfig:
    entity_type: str                       # Official, MediaOutlet, Student, Professor, Alumni, Person
    name: str
    summary: str
    post_frequency: float                  # Posts por round
    activity_hours: List[int]              # Horas de atividade
    topics: List[str]                      # Tópicos de interesse
    writing_style: str                     # Formal, Casual, Técnico, Emocional
    credibility_score: float               # 0.0 - 1.0
    influence_score: float                 # 0.0 - 1.0
    stance: str                            # Apoio, Neutro, Oposição
    interaction_targets: List[str]         # Alvos de interação
    ai_usage_probability: float            # Probabilidade de usar IA
    platform_weights: Dict[str, float]     # Pesos por plataforma

@dataclass
class PlatformConfig:
    algorithm_weights: Dict[str, float]    # Pesos do algoritmo
    content_moderation_threshold: float    # Threshold de moderação
    virality_threshold: float              # Threshold de viralidade
    echo_chamber_factor: float             # Fator de câmara de eco
    cross_platform_boost: float            # Boost entre plataformas
    trending_noise: float                  # Ruído em trending topics
    recommendation_sensitivity: float      # Sensibilidade da recomendação

@dataclass
class SimulationParameters:
    simulation_id: str
    requirement: str
    timestamp: str
    time_config: TimeSimulationConfig
    event_config: EventConfig
    agent_configs: List[AgentActivityConfig]
    platform_config: PlatformConfig
    confidence_score: float
    generation_steps: List[str]
```

## BRAZIL_TIMEZONE_CONFIG

5 faixas horárias com multiplicadores de atividade:

| Faixa | Horas | Multiplicador | Descrição |
|-------|-------|---------------|-----------|
| dead_hours | 0-5 | 0.05 | Madrugada |
| morning_hours | 6-8 | 0.40 | Manhã |
| work_hours | 9-18 | 0.70 | Trabalho |
| peak_hours | 19-22 | 1.50 | Pico noturno |
| night_hours | 23 | 0.50 | Noite alta |

## Etapas de Geração

### Step 1: Time Config

Prompt envia: resumo do requisito, número de entidades, contexto do documento.
LLM retorna: parâmetros de tempo (rounds, intervalo, multiplicadores).
Fallback: `_get_default_time_config(num_entities)`.

### Step 2: Event Config

Prompt envia: requisito completo, lista de entidades, time config gerado.
LLM retorna: posts iniciais, tópico principal, tags de narrativa.
Fallback: eventos genéricos baseados no requisito.

### Step 3: Agent Configs (Lotes de 15)

Para cada lote:
1. Preparar prompt com contexto + entidades do lote + regras de tipo
2. Chamar LLM com retry
3. Se falhar, usar `_generate_agent_config_by_rule(entity)` para cada entidade
4. Acumular configurações

Regras por tipo de entidade:
- **Official**: post_frequency=0.3-0.5, horário comercial, formal, credibility alto
- **MediaOutlet**: post_frequency=0.6-1.0, cobertura total, formal/neutro
- **Student**: post_frequency=0.4-0.8, evenings+weekends, casual/emocional
- **Professor**: post_frequency=0.2-0.4, horário comercial, técnico
- **Alumni**: post_frequency=0.1-0.3, esporádico, variado
- **Person**: post_frequency=0.3-0.6, variado, casual

### Step 4: Platform Config

Prompt envia: resumo, time config, event config, número de agentes.
LLM retorna: pesos de algoritmo, thresholds.
Fallback: valores default com base na intensidade do evento.

## Call LLM with Retry

```
def _call_llm_with_retry(prompt, system_prompt, max_attempts=3):
    temperatures = [0.7, 0.5, 0.3]  # Decrescente
    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model=model, prompt=prompt,
                system=system_prompt, temperature=temperatures[attempt]
            )
            result = _try_fix_config_json(response)
            if result: return result
        except Exception:
            if attempt == max_attempts - 1: raise
            time.sleep(1)
    raise RuntimeError("LLM failed after retries")
```

## JSON Repair

`_try_fix_config_json(content)`:
1. Tentar `json.loads()` direto
2. Se falhar, tentar `_fix_truncated_json()`:
   - Completar chaves/colchetes faltantes
   - Fechar strings quebradas
   - Remover trailing commas
3. Se ainda falhar, tentar extrair JSON com regex `({.*}|\[.*\])`
4. Se tudo falhar, retornar None (fallback)

`_fix_truncated_json(content)`:
- Contar `{` vs `}` e `[` vs `]` e fechar os faltantes
- Remover caracteres após o último `}` ou `]` válido
- Substituir `\n` em strings por `\\n`

## Type Alias Matching

Quando o LLM não retorna type para uma entidade, usar alias matching:
```python
TYPE_ALIASES = {
    "official": "Official", "gov": "Official", "government": "Official",
    "media": "MediaOutlet", "news": "MediaOutlet", "press": "MediaOutlet",
    "student": "Student", "undergrad": "Student", "graduate": "Student",
    "professor": "Professor", "prof": "Professor", "teacher": "Professor",
    "alumni": "Alumni", "alum": "Alumni", "former": "Alumni",
    "person": "Person", "individual": "Person", "user": "Person",
}
```

## Escala de Confiança

| Score | Significado |
|-------|-------------|
| 0.90-1.00 | LLM gerou todas as etapas com sucesso |
| 0.70-0.89 | LLM + fallback em 1-2 etapas |
| 0.50-0.69 | LLM + fallback em 3+ etapas |
| 0.30-0.49 | Fallback heurístico predominante |
| 0.00-0.29 | Apenas fallback (sem LLM disponível) |

## Exemplos

### Básico
```python
gen = ConfigGenerator()
params = gen.generate("demo-001", "Debate sobre reforma universitária", entities)
print(params.to_json())
```

### Com LLM
```python
gen = ConfigGenerator(api_key="sk-...", model="gpt-4o")
params = gen.generate("sim-001", "Eleições estudantis", entities,
                      progress_callback=lambda msg: print(f"[{msg}]"))
```
