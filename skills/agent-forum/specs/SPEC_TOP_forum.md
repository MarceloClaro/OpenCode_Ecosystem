# SPEC_TOP_forum — Agent Forum TDD Specification

**Skill:** agent-forum  
**Source:** scripts/moderator.py → Forum, AgentSpeech, ModeratorSpeech  
**Framework:** pytest  
**Status:** Spec-Driven

---

## CT-1: test_init — Inicializacao de Forum e componentes

**Objetivo:** Verificar que `Forum` inicializa com agentes, perfil de
debate, canal de memoria e estado `IDLE`.

**Passos:**
1. Instanciar `Forum(agents=["A","B"], debate_profile="LOGICO_RIGOROSO")`
2. Verificar `len(forum.agents) == 2`
3. Verificar `forum.debate_profile` e `forum.stage == IDLE`
4. Verificar canal e `MemoryChannel`

**Esperado:** Forum pronto para abrir sessao.

---

## CT-2: test_session_lifecycle — Ciclo open → publish → conclude

**Objetivo:** Validar o ciclo completo de uma sessao de debate: abertura,
publicacao de discursos por agentes, e conclusao.

**Passos:**
1. `open_session("Topico X")` → stage muda para OPEN
2. `publish("AgenteA", "conteudo", confidence=0.85)` → AgentSpeech criado
3. `conclude()` → stage muda para CLOSED
4. `get_json_report()` → contem topic, stage, total_speeches

**Esperado:** Fluxo completo sem erros.

---

## CT-3: test_game_theory — Analise de Teoria dos Jogos

**Objetivo:** Confirmar que `run_game_theory_analysis()` retorna
analise do Dilema do Prisioneiro e `describe_strategies()` retorna
catalogo com 38 estrategias.

**Passos:**
1. `run_game_theory_analysis()` → contem "prisoners_dilemma"
2. `describe_strategies()` → `total == 38`, contem "categorias"

**Esperado:** Engine de game theory funcional.

---

## CT-4: test_available — Modo offline/demo sem LLM

**Objetivo:** Garantir que Forum funciona sem API key (modo offline)
gerando fallback synthesis e completando o ciclo de debate.

**Passos:**
1. Criar Forum sem api_key
2. Abrir sessao, publicar discurso, concluir
3. Verificar que transcript contem entradas e stage == CLOSED

**Esperado:** Operacao normal mesmo sem LLM disponivel.
