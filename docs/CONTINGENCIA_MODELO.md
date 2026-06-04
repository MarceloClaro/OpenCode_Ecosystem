# Plano de Contingência — Descontinuação do Modelo Base

**Versao:** 1.0 | **Data:** 2026-06-04 | **Status:** Ativo

---

## 1. Situação Atual

O OpenCode Ecosystem depende do modelo **deepseek-v4-pro** (OpenCode Zen) como
back-end principal. Caracteristicas atuais:

| Propriedade | Valor |
|-------------|-------|
| Provedor | DeepSeek / OpenCode |
| Contexto maximo | 200K tokens |
| Saida maxima | 128K tokens |
| Custo | Gratuito (sem SLA) |
| Disponibilidade | 24/7 (nao garantida) |

**Risco:** Modelo gratuito sem acordo de nivel de servico (SLA). Descontinuacao
ou mudanca de politica pode interromper 100% do ecossistema.

---

## 2. Alternativas Identificadas

### 2.1 Claude 3.5 Sonnet (Anthropic) — Opcao Primaria

| Propriedade | Valor |
|-------------|-------|
| Contexto maximo | 200K tokens |
| Saida maxima | 8.192 tokens |
| Custo estimado | ~US$ 3,00/1M tokens input, ~US$ 15,00/1M tokens output |
| Compatibilidade | Alta — suporta tool calling, structured output, system prompts |
| API | Anthropic Messages API |

**Vantagens:** Melhor raciocinio multi-step do mercado; excelente para tarefas
academicas; tool calling robusto.

**Desvantagens:** Custo significativo para uso intensivo (14 rounds de evolucao
consomem ~500K tokens/sessao); saida limitada a 8K tokens (vs 128K atual).

### 2.2 GPT-4o (OpenAI) — Opcao Secundaria

| Propriedade | Valor |
|-------------|-------|
| Contexto maximo | 128K tokens |
| Saida maxima | 16.384 tokens |
| Custo estimado | ~US$ 2,50/1M tokens input, ~US$ 10,00/1M tokens output |
| Compatibilidade | Alta — tool calling nativo, JSON mode, response format |

**Vantagens:** Ecossistema OpenAI consolidado; preco competitivo; JSON mode
confiavel para saidas estruturadas.

**Desvantagens:** Contexto menor (128K vs 200K); latencia maior em horarios
de pico.

### 2.3 Gemini 2.0 Flash (Google) — Opcao de Contingencia

| Propriedade | Valor |
|-------------|-------|
| Contexto maximo | 1M tokens |
| Saida maxima | 8.192 tokens |
| Custo estimado | ~US$ 0,075/1M tokens input, ~US$ 0,30/1M tokens output |
| Compatibilidade | Media — API Google, adaptacao necessaria |

**Vantagens:** Menor custo do mercado; contexto massivo (1M tokens); gratuito
para uso moderado.

**Desvantagens:** Raciocinio inferior em tarefas cientificas complexas;
tool calling menos maduro; necessidade de adaptacao do pipeline.

---

## 3. Protocolo de Migracao

### 3.1 Fase 1: Deteccao (Tempo: 0-24h)

1. Monitorar status do modelo atual via health check automatico
2. Confirmar descontinuacao por canais oficiais (DeepSeek/OpenCode)
3. Notificar stakeholders (via GitHub Issues + Discord)

### 3.2 Fase 2: Ativacao (Tempo: 24-72h)

1. Selecionar alternativa conforme matriz de decisao (secao 4)
2. Configurar chave de API no ambiente (`OPENCODE_MODEL` env var)
3. Ajustar adaptador de modelo em `config/models.py`
4. Executar suite completa TDD (206 testes) para validar compatibilidade
5. Recalibrar verificadores V1-V7 se necessario

### 3.3 Fase 3: Validacao (Tempo: 72h-7d)

1. Executar CORA-Eval completo (10 dimensoes) com novo modelo
2. Comparar scores com baseline (CORA-Score 3.04)
3. Ajustar thresholds de verificacao se necessario
4. Publicar relatorio de compatibilidade

### 3.4 Fase 4: Estabilizacao (Tempo: 7-30d)

1. Monitorar performance em producao por 30 dias
2. Coletar metricas de custo, latencia, qualidade
3. Otimizar prompts para o novo modelo
4. Documentar diferencas e adaptacoes

---

## 4. Matriz de Decisao

| Criterio | Peso | Claude 3.5 | GPT-4o | Gemini Flash |
|----------|:----:|:----------:|:------:|:------------:|
| Qualidade de raciocinio | 40% | 9 | 8 | 6 |
| Custo operacional | 25% | 5 | 6 | 9 |
| Compatibilidade API | 20% | 8 | 9 | 5 |
| Tamanho de contexto | 10% | 9 | 7 | 10 |
| Velocidade | 5% | 7 | 7 | 9 |
| **Ponderado** | **100%** | **7.6** | **7.4** | **7.0** |

**Recomendacao:** Claude 3.5 Sonnet como substituto primario.

---

## 5. Custos Mensais Estimados

| Uso | Tokens/mes | Claude 3.5 | GPT-4o | Gemini Flash |
|-----|:----------:|:----------:|:------:|:------------:|
| Leve (10 sessoes) | 5M | ~US$ 90 | ~US$ 62 | ~US$ 1,90 |
| Moderado (50 sessoes) | 25M | ~US$ 450 | ~US$ 312 | ~US$ 9,40 |
| Intenso (200 sessoes) | 100M | ~US$ 1.800 | ~US$ 1.250 | ~US$ 37,50 |

---

## 6. Cronograma de Mitigacao

| Marco | Prazo | Acao |
|-------|:-----:|------|
| M1 | Imediato | Documentar variavel `OPENCODE_MODEL` no codigo |
| M2 | 30 dias | Implementar adaptador multi-modelo (Factory Pattern) |
| M3 | 60 dias | Testar Claude 3.5 Sonnet com suite TDD completa |
| M4 | 90 dias | Implementar fallback automatico (health check → switch) |

---

## 7. Health Check Automatizado

```python
# Exemplo de health check para deteccao precoce de descontinuacao
import os, requests

def check_model_health():
    model = os.getenv("OPENCODE_MODEL", "deepseek-v4-pro")
    try:
        response = requests.get(
            "https://status.deepseek.com/api/v2/status.json",
            timeout=10
        )
        return response.json().get("status") == "operational"
    except Exception:
        return False
```

---

## 8. Referencias

- [Anthropic API Docs](https://docs.anthropic.com/)
- [OpenAI API Docs](https://platform.openai.com/docs/)
- [Google AI Studio](https://ai.google.dev/)
- [DeepSeek Status Page](https://status.deepseek.com/)

---

**Plano de Contingencia** · 2026-06-04 · OpenCode Ecosystem v4.7.1
