# SPEC_TOP_provider — ProviderFactory TDD Specification

**Skill:** provider-factory  
**Source:** scripts/provider_factory.py → ProviderFactory  
**Framework:** pytest  
**Status:** Spec-Driven

---

## CT-1: test_register — Registro de provedor no registry global

**Objetivo:** Verificar que um novo tipo de provedor pode ser registrado e
recuperado do dicionario global `_PROVIDER_REGISTRY`.

**Pre-condicoes:** `_PROVIDER_REGISTRY` contem os provedores padrao
(gemini, deepseek, groq).

**Passos:**
1. Registrar `DummyProvider` com chave `"dummy_test"`
2. Verificar que `"dummy_test" in _PROVIDER_REGISTRY`
3. Verificar que a classe armazenada e `DummyProvider`

**Esperado:** `assert _PROVIDER_REGISTRY["dummy_test"] is DummyProvider`

---

## CT-2: test_get — Instanciacao com validacao de disponibilidade

**Objetivo:** Confirmar que `ProviderFactory` instancia apenas provedores
com API key configurada e os ordena por prioridade.

**Pre-condicoes:** Variavel de ambiente `DUMMY_API_KEY="test-key"` definida.

**Passos:**
1. Criar `ProviderConfig` com `api_key_env="DUMMY_API_KEY"`
2. Instanciar `ProviderFactory([cfg])`
3. Verificar `len(factory._providers) == 1`
4. Verificar `provider.available is True`

**Esperado:** Factory contem 1 provider disponivel.

---

## CT-3: test_fallback — Fallback automatico entre providers

**Objetivo:** Validar que `ProviderFactory.chat()` percorre a lista de
providers em ordem de prioridade e retorna resposta do primeiro disponivel.

**Pre-condicoes:** 2 providers registrados com prioridades 0 e 1, ambos
com API key valida.

**Passos:**
1. Criar factory com 2 configs (primary priority=0, fallback priority=1)
2. Chamar `factory.chat(messages)`
3. Verificar que o resultado contem `"dummy:"`

**Esperado:** Resposta obtida do provider primario sem acionar fallback.

---

## CT-4: test_available — Erro quando nenhum provider disponivel

**Objetivo:** Garantir que `RuntimeError("Nenhum provider disponivel")`
e lancado se nenhum provider tiver API key configurada.

**Pre-condicoes:** `NONEXISTENT_KEY` nao definida no ambiente.

**Passos:**
1. Garantir que `NONEXISTENT_KEY` nao existe em `os.environ`
2. Tentar instanciar `ProviderFactory([cfg])`
3. Capturar `pytest.raises(RuntimeError)`

**Esperado:** Excecao com mensagem "Nenhum provider disponivel".
