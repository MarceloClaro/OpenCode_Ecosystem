# Especificacao Formal do Q-Score UCB1

## Algoritmo Base

### Formula Principal

$$Q_i(N) = \bar{v}_i + \sqrt{\frac{2 \ln N}{n_i}}$$

Onde:
- $Q_i(N)$: Q-Score do agente $i$ apos $N$ selecoes totais
- $\bar{v}_i = \frac{1}{n_i}\sum_{j=1}^{n_i} r_j$: recompensa media do agente $i$
- $n_i$: numero de vezes que o agente $i$ foi selecionado
- $N = \sum_i n_i$: numero total de selecoes

### Interpretacao dos Termos

| Termo | Nome | Significado | Comportamento |
|-------|------|-------------|---------------|
| $\bar{v}_i$ | **Exploitation** | Confianca no desempenho historico | Cresce com boas rodadas |
| $\sqrt{2\ln N / n_i}$ | **Exploration** | Bonus por incerteza | Decai com $\sqrt{1/n_i}$ |

### Propriedades Matematicas

1. **Balanceamento automatico**: Agentes pouco testados ($n_i$ pequeno) recebem bonus de exploracao alto
2. **Convergencia**: Quando $n_i \to \infty$, exploration $\to 0$, Q-Score $\to \bar{v}_i$
3. **Otimismo diante da incerteza**: Nunca testado $\to$ Q-Score $= \infty$ (prioridade maxima)
4. **Garantia de arrependimento**: Regret bound $O(\log N)$ (provado por Auer et al. 2002)

## Extensao por Dominio

$$Q_i(N, d) = Q_i(N) + 0.15 \cdot \bar{v}_{i,d}$$

Onde $\bar{v}_{i,d}$ e a recompensa media do agente $i$ no dominio $d$.

## Parametros Recomendados

| Parametro | Valor | Justificativa |
|-----------|-------|---------------|
| Recompensa inicial | 0.5 | Neutra (nem otimista, nem pessimista) |
| Peso do dominio | 0.15 | +15% bonus para expertise comprovada |
| Persistencia | Arquivo JSON | Sobrevive a reinicios do ecossistema |

## Referencias

- Auer, P., Cesa-Bianchi, N., & Fischer, P. (2002). Finite-time Analysis of the Multi-armed Bandit Problem. *Machine Learning*, 47(2), 235-256.
- Condorcet, M. (1785). *Essai sur l'application de l'analyse a la probabilite des decisions rendues a la pluralite des voix*.
