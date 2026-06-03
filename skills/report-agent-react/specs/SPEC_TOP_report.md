# SPEC_TOP_report — ReportAgent TDD Specification

**Skill:** report-agent-react  
**Source:** scripts/report_agent.py → ReportAgent, ReflectionEngine  
**Framework:** pytest  
**Status:** Spec-Driven

---

## CT-1: test_init — Inicializacao de ReportAgent e ferramentas mock

**Objetivo:** Verificar que `ReportAgent` inicializa com `graph_id`,
`requirement`, `MockGraphTools` e `ReflectionEngine`.

**Passos:**
1. `ReportAgent("graph-001", "Analisar impacto da IA", mock=True)`
2. Verificar `agent.graph_id`, `agent.requirement`
3. Verificar `agent.tools is not None`
4. Verificar `isinstance(agent.reflector, ReflectionEngine)`

**Esperado:** Agente pronto para geracao de relatorio.

---

## CT-2: test_plan_outline — Geracao de ReportOutline com secoes

**Objetivo:** Confirmar que `plan_outline()` gera `ReportOutline` com
numero de secoes entre `MIN_SECTIONS` e `MAX_SECTIONS`, titulo e
summary nao vazios.

**Passos:**
1. `agent.plan_outline()` → `ReportOutline`
2. `len(outline.sections) >= MIN_SECTIONS`
3. `outline.title != ""` e `outline.summary != ""`

**Esperado:** Outline valido para qualquer requirement.

---

## CT-3: test_generate_section — ReACT loop mock por secao

**Objetivo:** Validar que `generate_section()` executa ciclo ReACT,
chama ferramentas mock, e marca secao como `completed`.

**Passos:**
1. Obter outline, selecionar primeira secao
2. `agent.generate_section(section, outline)`
3. Verificar `section.status == "completed"`
4. Verificar `section.tool_calls >= MIN_TOOL_CALLS_PER_SECTION`

**Esperado:** Conteudo gerado e tool calls registradas.

---

## CT-4: test_available — Reflexao em 3 dimensoes (consistencia, correcao, lacunas)

**Objetivo:** Garantir que `ReflectionEngine.reflect()` retorna
`ReflectionResult` com `consistency_score` entre 0 e 1, e listas
de issues, gaps, suggestions e corrections.

**Passos:**
1. Criar `ReflectionEngine()`
2. `engine.reflect(report_md, context="mercado de IA")`
3. Verificar `0 <= score <= 1.0`
4. Verificar que issues, gaps, suggestions, corrections sao listas

**Esperado:** Resultado de reflexao completo.
