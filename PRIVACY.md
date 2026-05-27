# Política de Privacidade e Uso de Dados — OpenCode Ecosystem

> **Última atualização**: 2026-05-25
> **Versão**: 1.0.0

---

## Modelo deepseek-v4-pro (OpenCode Zen)

O ecossistema OpenCode utiliza por padrão o modelo `opencode/deepseek-v4-pro` (OpenCode Zen),
que opera através de um **gateway gratuito** fornecido pela OpenCode.

### O que você precisa saber

| Aspecto | Detalhe |
|---------|---------|
| **Provedor** | OpenCode (gateway gratuito) |
| **Modelo base suspeito** | GLM-4.6 (Zhipu AI, China) — proveniência não confirmada oficialmente |
| **Contexto** | 200K tokens de entrada, 128K tokens de saída |
| **Custo** | Gratuito durante o período de acesso antecipado |
| **Dados de treinamento** | ⚠️ **Durante o período gratuito, dados das interações podem ser utilizados para melhoria do modelo** |

### Implicações de Privacidade

O uso do gateway gratuito implica que:

1. **O conteúdo das suas interações** (prompts, código, documentos) **pode ser utilizado para treinamento** do modelo pelo provedor
2. **Não há isolamento de sessão**: os dados trafegam pela infraestrutura do provedor
3. **Não há garantia de retenção zero**: mesmo que os dados não sejam usados para treinamento, podem ser armazenados em logs do provedor

### Recomendações por Nível de Sensibilidade

| Nível | Tipo de Conteúdo | Recomendação |
|-------|-----------------|--------------|
| 🟢 **Baixo** | Código open-source, pesquisa pública, documentação | ✅ Uso adequado com deepseek-v4-pro |
| 🟡 **Médio** | Código proprietário não-crítico, dados de pesquisa não-sensíveis | ⚠️ Considere modo local ou aguarde suporte offline |
| 🔴 **Alto** | Código proprietário crítico, dados de saúde, dados financeiros, PII | ❌ **Não use** deepseek-v4-pro. Aguarde suporte a modelos self-hosted |
| 🔴 **Crítico** | Segredos industriais, dados sob NDA, pesquisa sob embargo | ❌ **Nunca use** gateway gratuito. Use apenas modelos locais |

### Alternativas

| Alternativa | Status | Privacidade |
|------------|--------|-------------|
| `opencode/small-pickle` | Disponível | Similar ao deepseek-v4-pro |
| Modelo local (via Ollama) | **Roadmap Q3 2026** | ✅ Dados permanecem locais |
| Modelo offline (via vLLM) | **Roadmap Q4 2026** | ✅ Dados permanecem locais |

### Dados que NUNCA devem ser enviados

- Chaves de API (OpenAI, GitHub, AWS, etc.)
- Tokens de acesso pessoal
- Senhas ou credenciais
- Dados de pacientes ou informações médicas protegidas (HIPAA/LGPD)
- Informações financeiras pessoais (PII)
- Código proprietário sob NDA

> O ecossistema OpenCode possui um mecanismo de limpeza de segredos (`limpa_segredos.py`)
> que remove credenciais de arquivos de configuração antes do commit, mas **não pode**
> impedir que segredos sejam enviados em prompts para o modelo.

---

## Auditoria e Logs

O ecossistema mantém logs de auditoria locais:

| Arquivo | Conteúdo | Persistência |
|---------|----------|-------------|
| `.evolve/ecosystem-observability.jsonl` | Log de operações do AutoEvolve | Local |
| `.evolve/cora-qscore-audit.jsonl` | Log de recompensas do Q-Score | Local |

Estes logs **não são enviados** para o provedor do modelo. Permanecem no seu sistema de arquivos local.

---

## Compromissos

1. **Transparência**: Esta política será atualizada sempre que houver mudança no modelo ou provedor
2. **Alternativas**: Estamos desenvolvendo suporte a modelos locais (Ollama, vLLM) para eliminar a dependência de gateways externos
3. **Auditoria**: Os logs de interação com o modelo (quando disponíveis) serão documentados

---

> **Dúvidas ou preocupações?** Abra uma issue no repositório ou consulte o [CORRIGENDUM.md](CORRIGENDUM.md)
> para outras correções e transparências sobre o ecossistema.
