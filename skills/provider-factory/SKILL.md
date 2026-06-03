---
name: provider-factory
version: "1.0.0"
kind: python
category: system
affinity: {llm_client: 0.95, maswos-v5-nexus: 0.85, agent-node-pipeline: 0.80}
---

# ProviderFactory — Multi-LLM com Fallback Automatico

## Origem
Extraido de **SandeClaw** (specs/architecture.md secao 2.7, PRD.md RF-03).
SandeClaw e um agente pessoal Telegram-first que opera 100% local.

## Como Funciona
Fabrica que instancia provedores LLM (Gemini, DeepSeek, Groq) por configuracao.
Cada provedor tem prioridade; se o primario falhar, o proximo assume
automaticamente com retry + backoff exponencial.

```
LLM_PROVIDERS=gemini,deepseek  (variavel de ambiente)
      |
ProviderFactory.from_env()
      |
   .chat(messages)
      |
   [gemini tenta 3x com backoff]
      |-- falhou --> [deepseek tenta 3x]
                        |-- falhou --> RuntimeError
                        |-- OK --> resposta
```

## Valor para OpenCode
- **Unificacao**: Substitui chamadas dispersas a APIs de LLM por interface unica
- **Resiliencia**: Fallback transparente evita interrupcao quando API primaria falha
- **Extensibilidade**: Adicionar novo provedor = registrar classe + variavel de env
- **Compatibilidade**: Protocolo `SupportsChat` — qualquer skill que precise de LLM
  pode receber uma ProviderFactory sem alteracoes

## Uso
```python
from skills.provider_factory.scripts.provider_factory import ProviderFactory

factory = ProviderFactory.from_env("LLM_")
response = factory.chat([{"role": "user", "content": "Explique ReAct"}])
```

## Configuracao (.env)
```env
LLM_PROVIDERS=gemini,deepseek
LLM_GEMINI_API_KEY=AIza...
LLM_GEMINI_MODEL=gemini-2.0-flash
LLM_GEMINI_PRIORITY=0
LLM_DEEPSEEK_API_KEY=sk-...
LLM_DEEPSEEK_MODEL=deepseek-chat
LLM_DEEPSEEK_PRIORITY=1
```

## Ficheiros
- `scripts/provider_factory.py` — implementacao completa (197 linhas)
