# SPEC_TOP_process — ProcessRunner TDD Specification

**Skill:** process-lifecycle  
**Source:** scripts/runner.py → ProcessRunner, ProcessState, RunnerStatus  
**Framework:** pytest  
**Status:** Spec-Driven

---

## CT-1: test_init — Inicializacao de ProcessState e serializacao

**Objetivo:** Verificar que `ProcessState` inicializa com valores padrao
e o round-trip `to_dict()` → `from_dict()` preserva todos os campos.

**Passos:**
1. `ProcessState("test")` → status=IDLE, progress=0%, pid=None
2. `state.to_dict()` → dict com chaves esperadas
3. `ProcessState.from_dict(d)` → objeto identico

**Esperado:** Serializacao/desserializacao preserva estado.

---

## CT-2: test_start_stop — Ciclo start com script dummy

**Objetivo:** Confirmar que `ProcessRunner.start()` inicia um subprocesso,
a thread de monitoramento atualiza `current_step` via tokens `[PROGRESS:]`,
e o processo finaliza com status COMPLETED ou FAILED.

**Passos:**
1. Criar script Python dummy que emite `[PROGRESS:1/3]` tokens
2. `ProcessRunner.start("test-runner-1", cmd, total_steps=3)`
3. Aguardar 1s e verificar `get_state()` nao-nulo

**Esperado:** Processo inicia e monitoramento detecta progresso.

---

## CT-3: test_state_persistence — Save/Load de ProcessState em JSON

**Objetivo:** Validar que `_save_state()` persiste em arquivo JSON e
`_load_state()` recupera com todos os campos intactos.

**Passos:**
1. `ProcessRunner.configure(state_dir=tmpdir)`
2. Criar `ProcessState` com pid, current_step, progress_percent
3. `_save_state("persist-test")`
4. `_load_state("persist-test")` → pid=12345, progress=50.0%

**Esperado:** Estado recuperado identico ao salvo.

---

## CT-4: test_available — Operacoes de consulta sem processo ativo

**Objetivo:** Garantir que metodos de consulta (`list_processes`,
`get_agent_stats`, `get_actions`, `get_timeline`) retornam
estruturas vazias/seguras quando nao ha processos ativos.

**Passos:**
1. `list_processes()` → retorna lista
2. `get_agent_stats("nonexistent")` → `total_actions == 0`
3. `get_actions("nonexistent")` → `[]`
4. `get_timeline("nonexistent")` → `[]`

**Esperado:** Sem excecoes, retornos seguros.
