# 🎮 Teoria dos Jogos — 10 Estratégias (Reasoning Orchestrator v9.0)

Integração da Teoria dos Jogos como categoria de primeira classe no reasoning-orchestrator.
Conecta-se ao Agent Forum (P14) e PhD Auditor (P18) do ecossistema OpenCode.

## Catálogo Completo

### 1. Equilíbrio de Nash (Nash Equilibrium)
- **Conceito**: Cada jogador escolhe estratégia ótima dado que todos os outros também jogam de forma ótima
- **Aplicação IA**: Otimização de estratégias em sistemas multiagente competitivos
- **Profundidade**: L3 (Crítico/Acadêmico)

### 2. Dilema do Prisioneiro (Prisoner's Dilemma)
- **Conceito**: Dois agentes racionais podem não cooperar mesmo quando cooperação é benéfica
- **Aplicação IA**: Decisões de cooperação entre agentes autônomos, compartilhamento de recursos
- **Profundidade**: L3

### 3. Soma Zero (Zero-Sum)
- **Conceito**: Ganho de um participante é exatamente igual à perda do outro
- **Aplicação IA**: Competição direta, alocação de recursos fixos, adversarial ML
- **Profundidade**: L2 (Estrutural/Técnico)

### 4. Tit-for-Tat (Olho por Olho)
- **Conceito**: Cooperar no primeiro movimento, depois replicar o último movimento do oponente
- **Aplicação IA**: Estratégia de reputação em sistemas multiagente iterados (Axelrod, 1984)
- **Profundidade**: L2

### 5. Stackelberg (Líder-Seguidor)
- **Conceito**: Jogador líder age primeiro, seguidor responde otimamente
- **Aplicação IA**: First-mover advantage, pricing strategies, segurança de IA
- **Profundidade**: L3

### 6. Barganha de Nash (Nash Bargaining)
- **Conceito**: Solução cooperativa que maximiza o produto dos ganhos excedentes
- **Aplicação IA**: Negociação entre agentes, divisão de recursos computacionais
- **Profundidade**: L3

### 7. Sinalização (Signaling)
- **Conceito**: Jogadores com informação privada enviam sinais custosos para revelar tipo
- **Aplicação IA**: Credibilidade de agentes, verificação de qualidade em mercados de IA
- **Profundidade**: L3

### 8. Teoria dos Jogos Evolutiva (Evolutionary Game Theory)
- **Conceito**: Estratégias evoluem por seleção natural em populações ao longo do tempo
- **Aplicação IA**: Simulação MiroFish/BettaFish, evolução de populações de agentes
- **Profundidade**: L4 (Axiomático/Meta)

### 9. Jogos Bayesianos (Harsanyi)
- **Conceito**: Jogadores têm crenças sobre tipos incertos dos outros jogadores
- **Aplicação IA**: Decisões sob incerteza, inferência de intenções de agentes
- **Profundidade**: L4

### 10. Teoria dos Jogos Cooperativos (Shapley Value)
- **Conceito**: Contribuição marginal de cada jogador para cada coalizão possível
- **Aplicação IA**: Atribuição de crédito em ensembles, feature importance, divisão justa
- **Profundidade**: L4

## Matriz de Aplicação por Domínio

| Domínio | Estratégia Primária | Secundária | Contexto |
|---------|-------------------|------------|----------|
| **Debate Multiagente** | Nash Equilibrium | Tit-for-Tat | Agent Forum P14 |
| **Validação Acadêmica** | Nash Bargaining | Bayesiano (Harsanyi) | PhD Auditor P18 |
| **Simulação Social** | Evolutivo | Sinalização | MiroFish/BettaFish |
| **Otimização de Recursos** | Cooperativo (Shapley) | Stackelberg | DataOrchestrator |
| **Segurança de IA** | Soma Zero | Stackelberg | Adversarial ML |

## Integração com o Ecossistema

```python
from reasoning_audit_bridge import GameTheoryValidator

# Validar diversidade de raciocínio em sessão de pesquisa
validator = GameTheoryValidator()
score = validator.evaluate_session(audit_trail, required_strategies=2)
# → Score reduzido se menos de 2 estratégias de Teoria dos Jogos foram usadas
```
