---
name: cora-debate
description: "Arquitetura de debate multiagente com verificacao simbolica (Cora: Cognitive ORchestrated Argumentation). Q-Score UCB1, 7 verificadores V1-V7, self-consistency K=7, temperatura adaptativa, calibracao Platt. Integra agent-forum + reasoning-orchestrator + swarm-review + code-review. Use quando precisar de raciocinio cientifico verificavel, validacao formal de afirmacoes, debate estruturado com garantias de correcao, ou verificacao formal de codigo-fonte."
version: 1.1.0
author: ecosystem
inspired_by: Cora Architecture (Antiprojeto UFC 2026) + MiroFish ForumEngine + BettaFish Debate Strategies
compatibility: deepseek-v4-pro, deepseek-v4-pro
tags: [debate, verificacao, simbolico, raciocinio, Q-Score, multiagente, self-consistency, calibracao, codigo-fonte, verificacao-formal, V7]
---

# P19 — Cora-Debate (Cognitive ORchestrated Argumentation)

## Visão Geral

Pipeline de debate multiagente com **verificação simbólica formal** e **seleção adaptativa de arguedores via Q-Score UCB1**. Projetado para tarefas que exigem raciocínio científico verificável — demonstrações matemáticas, análise estatística, validação dimensional e busca de contraexemplos.

Diferencia-se do `agent-forum` (P14) por adicionar:
- **7 verificadores simbólicos** (V1-V7) que auditam cada afirmação
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
│  │  V7: Código-Fonte (V7a-V7g)              │                    │
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
- Verificação formal de código-fonte (V7)
- Auditoria de segurança de código contra OWASP Top 10 (V7e)
- Prova de corretude com triplas Hoare (V7b)
- Análise de complexidade algorítmica (V7d)

### Gatilhos Secundários
- `"verifique esta demonstração"`
- `"debata esta hipótese"`
- `"encontre contraexemplos para"`
- `"calibre a confiança desta afirmação"`
- `"valide dimensionalmente esta equação"`
- `"execute self-consistency K=7"`
- `"verifique este código-fonte"`
- `"analise a segurança deste código"`
- `"prove a corretude desta função"`
- `"calcule a complexidade deste algoritmo"`
- `"cubra este código com testes"`
- `/debate <topico>` (comando slash)
- `/code-verify <arquivo>` (comando slash para V7)

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
3. **Verificação**: Afirmação passa pelos verificadores ativos (V1-V7)
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

## Verificadores (V1-V7)

| ID | Verificador | Entrada | Saída | Dependência |
|----|------------|---------|-------|-------------|
| **V1** | Análise Dimensional | Equação com unidades | dimensionalmente consistente? | Ontologia de unidades |
| **V2** | Verificador Algébrico | Expressão matemática | expandida/verificada | SymPy |
| **V3** | Contraexemplos | Afirmação $\forall x: P(x)$ | $x$ tal que $\neg P(x)$ | Busca randomizada |
| **V4** | Estatístico | Dados + conclusão | Shapiro-Wilk, Cohen's d | SciPy |
| **V5** | Numérico | Cálculo numérico | erro < $10^{-6}$? | Tolerância IEEE 754 |
| **V6** | PDE / Eq. Dif. | EDO/EDP + solução | solução verifica eq.? | SymPy dsolve |
| **V7** | Verif. Código-Fonte | Código-fonte (Python/JS/TS) | Verdict + score 0-100 + CWE IDs | V7a-V7g (7 sub-verificadores) |

## V7 — Verificador Formal de Código-Fonte

V7 estende a verificação simbólica do Cora-Debate para código-fonte, aplicando 7 sub-verificadores especializados que auditam propriedades formais de programas.

### Sub-Verificadores V7a-V7g

| ID | Verificador | Entrada | Saída | Descrição |
|:--:|-------------|---------|-------|-----------|
| **V7a** | Syntax Validator | Código-fonte (Python/JS/TS) | Validade AST, contagem de erros de sintaxe | Parseia o código e valida a estrutura da AST |
| **V7b** | Logic Prover | Código com pré/pós-condições | Verificação de tripla Hoare | Checa `{P} código {Q}` via execução simbólica |
| **V7c** | Type Safety | Código tipado (TS/Python types) | Contagem de erros de tipo | Valida consistência de tipos entre fronteiras de funções |
| **V7d** | Resource Bounds | Algoritmo + tamanho da entrada | Complexidade Big-O + limite de memória | Analisa loops e recursão para limites de complexidade |
| **V7e** | Security Patterns | Código-fonte | Contagem de vulnerabilidades por categoria CWE | Casamento de padrões contra OWASP Top 10 / base CWE |
| **V7f** | Test Coverage | Código + suite de testes | % de cobertura de branches | Analisa cobertura de testes em caminhos críticos |
| **V7g** | Invariant Checker | Código com loops pesados | Violações de invariantes de loop | Valida invariantes de loop via bounded model checking |

### Formato de Saída (Todos os Sub-Verificadores)

Cada sub-verificador retorna um dicionário padronizado:

```json
{
  "verifier_id": "V7a",
  "verdict": "PASS|FAIL|WARNING",
  "score": 0-100,
  "evidence": ["string de evidência 1", "string de evidência 2"],
  "cwe_ids": ["CWE-79", "CWE-89"],
  "execution_time_ms": 1234
}
```

### Ponderação da Pontuação V7

A pontuação geral do V7 é calculada pela média ponderada:

| Sub-Verificador | Peso |
|:---------------:|:----:|
| V7a (Syntax) | 10% |
| V7b (Logic Prover) | 25% |
| V7c (Type Safety) | 15% |
| V7d (Resource Bounds) | 15% |
| V7e (Security Patterns) | 20% |
| V7f (Test Coverage) | 10% |
| V7g (Invariant Checker) | 5% |

**Fórmula**: `score_V7 = 0.10·V7a + 0.25·V7b + 0.15·V7c + 0.15·V7d + 0.20·V7e + 0.10·V7f + 0.05·V7g`

### Dependências Técnicas

- **V7a**: Parser AST nativo (Python `ast`, TypeScript `@typescript-eslint/parser`)
- **V7b**: Execução simbólica via `sympy` ou `z3-solver`
- **V7c**: Type checker nativo (Python `mypy`, TypeScript `tsc --noEmit`)
- **V7d**: Analisador estático de complexidade (custom)
- **V7e**: Base de padrões CWE + OWASP Top 10 (2021)
- **V7f**: Coverage analyzer (Python `pytest-cov`, Jest `--coverage`)
- **V7g**: Bounded model checker via `z3-solver`

## Integração com o Ecossistema

| Componente | Tipo | Conexão |
|-----------|------|---------|
| `agent-forum` | Skill (P14) | Herda protocolo de fórum, adiciona verificadores |
| `reasoning-orchestrator` | Skill | 204 tipos de raciocínio (25 categorias) alimentam debatedores |
| `swarm-review` | Skill | Revisão por enxame integrada ao estágio DEBATE |
| `cora-qscore` | Plugin | Motor UCB1 para seleção de arguedores |
| `cora-verifier` | MCP | Servidor com 7 verificadores simbólicos (V1-V7) |
| `sequential-thinking` | MCP | Raciocínio em cadeia para cada debatedor |
| `code-runner` | MCP | Executa verificações Python/SymPy/Z3 |
| `mirofish-sync` | Skill | Sincroniza com ForumEngine do BettaFish |
| `code-review` (system) | Skill | Metodologia de revisão em 4 camadas alimenta V7 |
| `code-reviewer` | Skill | Revisão multi-eixo integrada ao V7e (Security) |
| `swarm-review` | Skill | Revisão por enxame consome outputs do V7 |
| `cora-v7-plugin` | Plugin | Motor de verificação formal de código (V7a-V7g) |
| `z3-solver` | Dep | Resolvedor SMT para V7b (Logic Prover) e V7g (Invariant Checker) |

## Boas Práticas

1. **Sempre ative pelo menos V2, V4 e V7** para verificação completa — cobertura mínima
2. **Ajuste $\alpha$ conforme o domínio**: 0.85 para matemática, 0.70 para ciências sociais
3. **K=7 é o sweet spot** empírico: custo 7× vs ganho +34pp de acurácia
4. **Verificadores são lazy**: só executam quando necessário, evitando latência
5. **Q-Score persiste entre sessões**: debatedores de alto Q-Score são reutilizados
6. **Scratchpad rastreável**: cada passo tem `[TIPO: algebra|physics|stats|demo|code]`
7. **V7 exige z3-solver e parsers AST** instalados para verificação de código completa
8. **Ative V7e (Security) ao revisar código com dados sensíveis** — cobre OWASP Top 10

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
- **V7** exige `z3-solver` (>=4.12) e parsers AST específicos por linguagem
- **V7a (Syntax)** suporta Python, JavaScript e TypeScript — outras linguagens retornam WARNING
- **V7b (Logic Prover)** requer anotações de pré/pós-condição no código (docstrings)
- **V7e (Security)** cobre OWASP Top 10 2021 — ameaças emergentes podem não ser detectadas
- **V7f (Test Coverage)** exige suite de testes executável com relatório de cobertura
- **K=7** multiplica custo de API por 7 — reserve para tarefas de alto valor
- **Temperatura adaptativa** requer histórico de rodadas — não funciona em single-shot
- **Calibração Platt** precisa de ≥20 amostras para ajuste confiável

## Referências

| Arquivo | Propósito |
|---------|-----------|
| `servers/cora_verifier.py` | Servidor MCP com V1-V7 |
| `servers/cora_v7_verifier.py` | Servidor MCP especializado em V7a-V7g |
| `references/qscore_algorithm.md` | Especificação formal do Q-Score UCB1 |
| `references/verifier_specs.md` | Especificação detalhada de cada verificador (V1-V7) |
| `references/v7_code_verification.md` | Especificação detalhada dos 7 sub-verificadores V7 |
| `references/integration_matrix.md` | Matriz de integração com o ecossistema |

## Scripts

```bash
# Iniciar servidor MCP de verificadores (V1-V6)
python skills/cora-debate/servers/cora_verifier.py

# Iniciar servidor MCP de verificação formal de código (V7)
python skills/cora-debate/servers/cora_v7_verifier.py

# Testar verificadores isoladamente
python skills/cora-debate/servers/cora_verifier.py --test

# Executar verificação V7 em um arquivo específico
python skills/cora-debate/servers/cora_v7_verifier.py --file path/to/code.py --all

# Executar verificação V7 apenas com security patterns (V7e)
python skills/cora-debate/servers/cora_v7_verifier.py --file path/to/code.py --v7e

# Executar simulação completa (benchmark 100 problemas)
python simulacao_cora_debate.py

# Executar benchmark V7 com 50 amostras de código
python skills/cora-debate/servers/cora_v7_verifier.py --benchmark 50
```
