# P13 Config Generator — Pseudocodigo Detalhado

## Visao Geral

```
Entrada: requirement (string), entities (List[Dict]), simulation_id (string)
Saida: SimulationParameters (JSON)
Dependencia opcional: OpenAI-compatible API
```

## Algoritmo Principal

```
FUNCTION generate(simulation_id, requirement, entities):
    params = SimulationParameters(simulation_id, requirement)
    context = build_context(requirement, entities)

    -- Step 1: Time Config
    TRY:
        time_result = generate_time_config(context, len(entities))
        params.time_config = parse_time_config(time_result)
    CATCH:
        params.time_config = get_default_time_config(len(entities))

    -- Step 2: Event Config
    TRY:
        event_result = generate_event_config(context, requirement, entities)
        params.event_config = parse_event_config(event_result)
    CATCH:
        params.event_config = EventConfig(trending_topic=requirement[:80], ...)

    -- Step 3: Agent Configs (batches)
    FOR start = 0 TO len(entities) STEP AGENTS_PER_BATCH:
        TRY:
            batch = generate_agent_configs_batch(context, entities, start, requirement)
        CATCH:
            batch = [generate_agent_config_by_rule(e) FOR e IN batch_entities]
        params.agent_configs.append(batch)

    params.event_config = assign_initial_post_agents(params.event_config, params.agent_configs)

    -- Step 4: Platform Config
    TRY:
        plat_result = generate_platform_config(context, requirement, params.time_config, params.event_config, len(entities))
        params.platform_config = parse_platform_config(plat_result)
    CATCH:
        params.platform_config = get_default_platform_config(params.event_config.event_intensity)

    params.confidence_score = compute_confidence(steps_llm, steps_fallback)
    RETURN params
```

## Sub-rotinas

### build_context
```
FUNCTION build_context(requirement, entities, document_text=None):
    ctx = "Requisito: {requirement}\n\nEntidades ({N}):\n"
    FOR EACH entity IN entities:
        ctx += "  [{i}] {name} ({type}): {summary[:200]}\n"
    IF document_text AND remaining_context > 500:
        ctx += document_text[:remaining_context]
    RETURN ctx
```

### call_llm_with_retry
```
FUNCTION call_llm_with_retry(prompt, system_prompt, max_attempts=3):
    temperatures = [0.7, 0.5, 0.3]
    FOR attempt = 0 TO max_attempts-1:
        TRY:
            response = client.chat.completions.create(
                model=model,
                messages=[{role: "system", content: system_prompt},
                          {role: "user", content: prompt}],
                temperature=temperatures[attempt],
                response_format={type: "json_object"}
            )
            result = try_fix_config_json(response.content)
            IF result IS NOT None: RETURN result
        CATCH error:
            IF attempt == max_attempts-1: RAISE error
            WAIT 1 second
    RAISE "LLM failed after retries"
```

### try_fix_config_json
```
FUNCTION try_fix_config_json(content):
    IF content IS None OR empty: RETURN None

    -- Attempt 1: direct parse
    TRY: RETURN json.loads(content.strip())

    -- Attempt 2: fix truncated JSON
    TRY:
        fixed = fix_truncated_json(content)
        RETURN json.loads(fixed)

    -- Attempt 3: regex extraction
    matches = regex_search(r'(\{.*\}|\[.*\])', content, DOTALL)
    IF matches:
        TRY: RETURN json.loads(matches[0])

    RETURN None
```

### fix_truncated_json
```
FUNCTION fix_truncated_json(content):
    content = content.strip()
    IF empty: RETURN "{}"

    stack = 0
    in_string = False
    escape = False
    last_valid = 0

    FOR i, ch IN enumerate(content):
        IF escape: escape = False; CONTINUE
        IF ch == '\\' AND in_string: escape = True; CONTINUE
        IF ch == '"' AND NOT escape: in_string = NOT in_string; CONTINUE
        IF in_string:
            IF ch == '\n': REPLACE with '\\n'; CONTINUE
            CONTINUE
        IF ch == '{' OR ch == '[': stack += 1
        IF ch == '}' OR ch == ']':
            stack -= 1
            IF stack == 0: last_valid = i + 1

    content = content[:last_valid]
    content = rstrip_trailing_commas(content)
    WHILE stack > 0: content += '}'; stack -= 1
    IF NOT ends_with(content, '}'): content += '}'
    RETURN content
```

### generate_time_config
```
FUNCTION generate_time_config(context, num_entities):
    IF NOT llm_available: RAISE

    prompt = "Com base no contexto abaixo, gere configuracao de tempo
              para simulacao com {num_entities} entidades.
              {context}
              Retorne JSON com: total_rounds, round_interval_minutes,
              activity_timezone, peak_activity_probability,
              base_activity_probability, scheduled_posts_per_peak_hour,
              scheduled_posts_per_regular_hour, random_activity_ratio,
              dead_hour_noise"

    result = call_llm_with_retry(prompt, SYSTEM_PROMPT)
    result.default(timezone_dead_hours = BRAZIL_TIMEZONE.dead_hours)
    result.default(timezone_peak_hours = BRAZIL_TIMEZONE.peak_hours)
    RETURN result
```

### get_default_time_config
```
FUNCTION get_default_time_config(num_entities):
    rounds = min(200, max(80, num_entities * 2))
    RETURN TimeSimulationConfig(
        total_rounds = rounds,
        round_interval_minutes = 15,
        activity_timezone = "Asia/Shanghai",
        peak_activity_probability = 0.85,
        base_activity_probability = 0.35,
        scheduled_posts_per_peak_hour = clamp(num_entities//10, 5, 15),
        scheduled_posts_per_regular_hour = clamp(num_entities//30, 1, 5),
        random_activity_ratio = 0.3,
        dead_hour_noise = 0.02
    )
```

### generate_event_config
```
FUNCTION generate_event_config(context, requirement, entities):
    IF NOT llm_available: RAISE
    entity_summaries = FORMAT entities as "- {name} ({type})"
    prompt = "Gere configuracao de evento para: {requirement}
              Entidades: {entity_summaries}
              Retorne JSON com: initial_posts (array ate 5),
              trending_topic, narrative_tags, event_intensity,
              controversy_level, polarization_expected,
              ai_influence_expected, simulation_objective"
    result = call_llm_with_retry(prompt, SYSTEM_PROMPT)
    RETURN result
```

### generate_agent_configs_batch
```
FUNCTION generate_agent_configs_batch(context, entities, start_idx, requirement):
    IF NOT llm_available: RAISE
    batch = entities[start_idx : start_idx + AGENTS_PER_BATCH]

    entity_block = FORMAT each entity as "[{i}] {name} | {type} | {summary[:100]}"
    prompt = "Gere configuracoes de agente para:
              {entity_block}
              Retorne JSON com chave 'agents' contendo array de objetos.
              Cada objeto: entity_type, post_frequency, activity_hours,
              topics, writing_style, credibility_score, influence_score,
              stance, ai_usage_probability"

    result = call_llm_with_retry(prompt, SYSTEM_PROMPT)
    agents_data = result.agents OR result.agent_configs OR [result]
    configs = []
    FOR i, ad IN enumerate(agents_data):
        entity = batch[i] IF i < len(batch) ELSE {}
        etype = resolve_type_alias(ad.entity_type OR entity.type)
        configs.append(AgentActivityConfig(
            entity_type = etype,
            name = ad.name OR entity.name,
            post_frequency = clamp(ad.post_frequency, 0, 1),
            activity_hours = ad.activity_hours OR [8..22],
            ...
        ))
    RETURN configs
```

### generate_agent_config_by_rule
```
FUNCTION generate_agent_config_by_rule(entity):
    raw_type = entity.type OR entity.entity_type OR "Person"
    etype = resolve_type_alias(raw_type)
    rules = TYPE_RULES[etype]

    stance = weighted_random(rules.stance_weights)
    RETURN {
        entity_type: etype,
        post_frequency: uniform(rules.post_frequency.min, rules.post_frequency.max),
        activity_hours: rules.activity_hours,
        topics: rules.topics_focus,
        writing_style: rules.writing_style,
        credibility_score: uniform(rules.credibility_score.min, rules.credibility_score.max),
        influence_score: uniform(rules.influence_score.min, rules.influence_score.max),
        stance: stance
    }
```

### assign_initial_post_agents
```
FUNCTION assign_initial_post_agents(event_config, agent_configs):
    FOR EACH post IN event_config.initial_posts:
        author_type = post.author_type
        IF author_type:
            matched = [a FOR a IN agent_configs
                       IF a.entity_type == resolve_type_alias(author_type)]
            IF matched:
                post.assigned_agent = random_choice(matched).name
    RETURN event_config
```

### generate_platform_config
```
FUNCTION generate_platform_config(context, requirement, time_config, event_config, num_agents):
    IF NOT llm_available: RAISE
    prompt = "Gere configuracao de plataforma.
              Requisito: {requirement}
              Intensidade: {event_config.event_intensity}
              Agentes: {num_agents}
              Retorne JSON com: algorithm_weights, content_moderation_threshold,
              virality_threshold, echo_chamber_factor,
              cross_platform_boost, trending_noise, recommendation_sensitivity"
    result = call_llm_with_retry(prompt, SYSTEM_PROMPT)
    RETURN result
```

## Estrutura TYPE_RULES

```
TYPE_RULES = {
    "Official":    { freq: (0.3,0.5), hours: [8-18],  style: formal,     cred: (0.7,0.95), inf: (0.6,0.9)   },
    "MediaOutlet": { freq: (0.6,1.0), hours: [6-22],  style: formal,     cred: (0.5,0.85), inf: (0.7,0.95)  },
    "Student":     { freq: (0.4,0.8), hours: [14-22], style: casual,     cred: (0.2,0.5),  inf: (0.2,0.5)   },
    "Professor":   { freq: (0.2,0.4), hours: [8-17],  style: tecnico,    cred: (0.7,0.95), inf: (0.5,0.8)   },
    "Alumni":      { freq: (0.1,0.3), hours: [18-22]+[7-9], style: variado, cred: (0.3,0.6), inf: (0.3,0.6) },
    "Person":      { freq: (0.3,0.6), hours: [7-22],  style: casual,     cred: (0.1,0.4),  inf: (0.1,0.4)   },
}
```

## Algoritmo de Confianca

```
FUNCTION compute_confidence(steps_completed, steps_fallback):
    total = len(steps_completed) + len(steps_fallback)
    IF NOT llm_available:
        RETURN clamp(0.29 - fallback_ratio * 0.1, 0.0, 1.0)
    RETURN clamp(1.0 - fallback_ratio * 0.35, 0.0, 1.0)
```

## Type Alias Resolution

```
TYPE_ALIASES = {
    "official" -> "Official", "gov" -> "Official", "government" -> "Official",
    "media" -> "MediaOutlet", "news" -> "MediaOutlet", "press" -> "MediaOutlet",
    "student" -> "Student", "undergrad" -> "Student", "graduate" -> "Student",
    "professor" -> "Professor", "prof" -> "Professor", "teacher" -> "Professor",
    "alumni" -> "Alumni", "alum" -> "Alumni", "former" -> "Alumni",
    "person" -> "Person", "individual" -> "Person", "user" -> "Person",
}
```

## Fluxo de Erro Completo

```
generate()
  +-- Step 1 (Time) ------ LLM OK ------> parse_time_config()
  |                        LLM FALHA ----> get_default_time_config()
  |
  +-- Step 2 (Event) ----- LLM OK ------> parse_event_config()
  |                        LLM FALHA ----> EventConfig(topic=requirement[:80])
  |
  +-- Step 3 (Agents) ---- LLM OK ------> parse_agent_batch()
  |    FOR each batch      LLM FALHA ----> generate_agent_config_by_rule() p/ cada
  |
  +-- Step 4 (Platform) -- LLM OK ------> parse_platform_config()
                           LLM FALHA ----> get_default_platform_config(intensity)
```
