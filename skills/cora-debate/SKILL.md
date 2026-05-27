---
name: cora-debate
description: "Arquitetura de debate multiagente com verificacao simbolica (Cora: Cognitive ORchestrated Argumentation). Q-Score UCB1, 6 verificadores V1-V6, self-consistency K=7, temperatura adaptativa, calibracao Platt. Integra agent-forum + reasoning-orchestrator + swarm-review. Use quando precisar de raciocinio cientifico verificavel, validacao formal de afirmacoes, ou debate estruturado com garantias de correcao."
version: 1.0.0
author: ecosystem
inspired_by: Cora Architecture (Antiprojeto UFC 2026) + MiroFish ForumEngine + BettaFish Debate Strategies
compatibility: deepseek-v4-pro, deepseek-v4-pro
tags: [debate, verificacao, simbolico, raciocinio, Q-Score, multiagente, self-consistency, calibracao]
---

# P19 — Cora-Debate (Cognitive ORchestrated Argumentation)

## Visão Geral

Pipeline de debate multiagente com **verificação simbólica formal** e **seleção adaptativa de arguedores via Q-Score UCB1**. Projetado para tarefas que exigem raciocínio científico verificável — demonstrações matemáticas, análise estatística, validação dimensional e busca de contraexemplos.

Diferencia-se do `agent-forum` (P14) por adicionar:
- **6 verificadores simbólicos** (V1-V6) que auditam cada afirmação
- **Q-Score UCB1** (exploration-exploitation) para selecionar arguedores
- **Self-consistency (K=7)** com votação ponderada
- **Temperatura adaptativa** via annealing por debatedor
- **Calibração Platt** da confiança reportada

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    CORA-DEBATE PIPELINE                          │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Agente 1 │  │ Agente 2 │  │ Agente 3 │  │ Agente 4 │        │
│  │ T=T₁(t)  │  │ T=T₂(t)  │  │ T=T₃(t)  │  │ T=T₄(t)  │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │             │             │             │                │
│       └──────┬──────┴──────┬──────┴──────┬──────┘                │
│              │             │             │                        │
│              ▼             ▼             ▼                        │
│  ┌──────────────────────────────────────────┐                    │
│  │         Q-Score Engine (UCB1)             │                    │
│  │  Q_i = v̄_i + sqrt(2 ln N / n_i)          │                    │
│  │  Seleciona arguedores por exploração     │                    │
│  └────────────────┬─────────────────────────┘                    │
│                   │                                              │
│                   ▼                                              │
│  ┌──────────────────────────────────────────┐                    │
│  │       Verificadores Simbólicos            │                    │
│  │  V1: Análise Dimensional                 │                    │
│  │  V2: Verificador Algébrico (SymPy)       │                    │
│  │  V3: Contraexemplos (randomizado)        │                    │
│  │  V4: Estatístico (Shapiro-Wilk, Cohen)   │                    │
│  │  V5: Numérico (IEEE 754, tolerância)     │                    │
│  │  V6: PDE / Equações Diferenciais         │                    │
│  └────────────────┬─────────────────────────┘                    │
│                   │                                              │
│                   ▼                                              │
│  ┌──────────────────────────────────────────┐                    │
│  │      Moderador (LLM + Parada Adaptativa)  │                    │
│  │  · Consenso: K amostras concordam?        │                    │
│  │  · Verificação: todos V passam?           │                    │
│  │  · Confiança: Platt calibrada > θ?        │                    │
│  └────────────────┬─────────────────────────┘                    │
│                   │                                              │
│                   ▼                                              │
│  ┌──────────────────────────────────────────┐                    │
│  │  Output: Afirmação Verificada + Evidência │                    │
│  └──────────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

## Quando Usar

### Gatilhos Primários
- Validar afirmação matemática com verificação simbólica
- Debater hipótese científica entre múltiplos especialistas
- Detectar erros em demonstrações via contraexemplos
- Calibrar confiança de resposta de LLM
- Análise dimensional de equações físicas
- Verificação de consistência estatística

### Gatilhos Secundários
- `"verifique esta demonstração"`
- `"debata esta hipótese"`
- `"encontre contraexemplos para"`
- `"calibre a confiança desta afirmação"`
- `"valide dimensionalmente esta equação"`
- `"execute self-consistency K=7"`
- `/debate <topico>` (comando slash)

## Fluxo de Trabalho

### Estágio 1: CONFIG (Configuração do Debate)

```yaml
debate_config:
  topic: "afirmação a ser verificada"
  n_agentes: 4
  k_self_consistency: 7
  temperatura_inicial: 1.0
  alpha_annealing: 0.85
  limiar_confianca: 0.75
  verificadores_ativos: [V1, V2, V3, V4, V5]
  timeout_rodada: 60s
```

### Estágio 2: DEBATE (Rodadas Multiagente)

Cada rodada:
1. **Seleção**: Q-Score UCB1 escolhe arguedor com maior $Q_i = \bar{v}_i + \sqrt{2\ln N/n_i}$
2. **Geração**: Agente produz afirmação com temperatura $T(t) = T_0 \cdot \alpha^t$
3. **Verificação**: Afirmação passa pelos verificadores ativos (V1-V6)
4. **Atualização**: Q-Score atualizado com reward da verificação
5. **Repetição**: Até convergência (consenso + verificação) ou timeout

### Estágio 3: CONSENSUS (Self-Consistency)

- Coleta K=7 amostras do debatedor de maior Q-Score
- Votação ponderada pelo Q-Score acumulado
- Afirmação final = argmax da soma de Q-Scores por resposta

### Estágio 4: CALIBRATE (Calibração Platt)

- Aplica calibração sigmoide: $\hat{p} = \sigma(a \cdot \logit(p_{raw}) + b)$
- Reporta confiança calibrada com ECE ≤ 0.10

### Estágio 5: OUTPUT (Relatório Final)

```markdown
# Relatório Cora-Debate

**Afirmação verificada:** [conclusão]
**Confiança calibrada:** [0-1]
**ECE:** [erro de calibração]
**Verificações aprovadas:** V1(✓), V2(✓), V3(✓), V4(✓)
**Contraexemplos encontrados:** 0
**Q-Score final dos agentes:** [A: 0.87, B: 0.72, C: 0.91, D: 0.65]
**Rodadas até convergência:** 12
```

## Verificadores (V1-V6)

| ID | Verificador | Entrada | Saída | Dependência |
|----|------------|---------|-------|-------------|
| **V1** | Análise Dimensional | Equação com unidades | dimensionalmente consistente? | Ontologia de unidades |
| **V2** | Verificador Algébrico | Expressão matemática | expandida/verificada | SymPy |
| **V3** | Contraexemplos | Afirmação $\forall x: P(x)$ | $x$ tal que $\neg P(x)$ | Busca randomizada |
| **V4** | Estatístico | Dados + conclusão | Shapiro-Wilk, Cohen's d | SciPy |
| **V5** | Numérico | Cálculo numérico | erro < $10^{-6}$? | Tolerância IEEE 754 |
| **V6** | PDE / Eq. Dif. | EDO/EDP + solução | solução verifica eq.? | SymPy dsolve |

## Integração com o Ecossistema

| Componente | Tipo | Conexão |
|-----------|------|---------|
| `agent-forum` | Skill (P14) | Herda protocolo de fórum, adiciona verificadores |
| `reasoning-orchestrator` | Skill | 204 tipos de raciocínio (25 categorias) alimentam debatedores |
| `swarm-review` | Skill | Revisão por enxame integrada ao estágio DEBATE |
| `cora-qscore` | Plugin | Motor UCB1 para seleção de arguedores |
| `cora-verifier` | MCP | Servidor com 6 verificadores simbólicos |
| `sequential-thinking` | MCP | Raciocínio em cadeia para cada debatedor |
| `code-runner` | MCP | Executa verificações Python/SymPy |
| `mirofish-sync` | Skill | Sincroniza com ForumEngine do BettaFish |

## Boas Práticas

1. **Sempre ative pelo menos V2 e V4** para qualquer debate — mínimo de cobertura
2. **Ajuste $\alpha$ conforme o domínio**: 0.85 para matemática, 0.70 para ciências sociais
3. **K=7 é o sweet spot** empírico: custo 7× vs ganho +34pp de acurácia
4. **Verificadores são lazy**: só executam quando necessário, evitando latência
5. **Q-Score persiste entre sessões**: debatedores de alto Q-Score são reutilizados
6. **Scratchpad rastreável**: cada passo tem `[TIPO: algebra|physics|stats|demo]`

## Comandos Rápidos

| Comando | Ação |
|---------|------|
| `/debate` | Inicia debate Cora completo |
| `/debate --quick` | Debate rápido (K=3, 2 agentes) |
| `/debate --verify-only` | Apenas verificação simbólica (sem debate) |
| `/debate --calibrate` | Apenas calibração de confiança |
| `/cora-score` | Exibe Q-Score de todos os debatedores |
| `/cora-reset` | Reseta Q-Scores acumulados |

## Constraintes

- **Não use** para tarefas triviais (aritmética simples) — custo desproporcional
- **Verificadores V3 e V6** exigem SymPy instalado (>=1.12)
- **K=7** multiplica custo de API por 7 — reserve para tarefas de alto valor
- **Temperatura adaptativa** requer histórico de rodadas — não funciona em single-shot
- **Calibração Platt** precisa de ≥20 amostras para ajuste confiável

## Referências

| Arquivo | Propósito |
|---------|-----------|
| `servers/cora_verifier.py` | Servidor MCP com V1-V6 |
| `references/qscore_algorithm.md` | Especificação formal do Q-Score UCB1 |
| `references/verifier_specs.md` | Especificação detalhada de cada verificador |
| `references/integration_matrix.md` | Matriz de integração com o ecossistema |

## Scripts

```bash
# Iniciar servidor MCP de verificadores
python skills/cora-debate/servers/cora_verifier.py

# Testar verificadores isoladamente
python skills/cora-debate/servers/cora_verifier.py --test

# Executar simulação completa (benchmark 100 problemas)
python simulacao_cora_debate.py
```
