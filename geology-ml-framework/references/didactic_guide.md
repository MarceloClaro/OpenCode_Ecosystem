# Guia Didático: Machine Learning em Geociências (Qualis A1)

Este guia fornece a fundamentação teórica para o framework Geomaker+IA, traduzindo conceitos complexos para diferentes níveis de público.

## 1. Métricas de Performance

| Termo | Explicação para Leigos | Definição para PhD (Rigor A1) |
| :--- | :--- | :--- |
| **Acurácia** | A "nota" geral do modelo. Quantas vezes ele acertou o tipo de rocha. | Proporção de predições corretas sobre o total de amostras: $(TP+TN)/(TP+TN+FP+FN)$. |
| **F1-Score** | O equilíbrio entre não deixar passar nenhuma rocha e não dar alarme falso. | Média harmônica entre Precisão e Recall: $2 \cdot \frac{Precision \cdot Recall}{Precision + Recall}$. |
| **Log-Loss** | O quão "confiante" o modelo está no erro. Quanto menor, melhor. | Função de custo Cross-Entropy: $-\frac{1}{N} \sum_{i=1}^{N} [y_i \log(\hat{y}_i) + (1-y_i) \log(1-\hat{y}_i)]$. |

## 2. Hiperparâmetros e Regularização

### Taxa de Aprendizado (Learning Rate - $\eta$)
- **Leigo:** A velocidade do passo do caminhante. Se for muito rápido, ele passa do destino; se for muito lento, demora a chegar.
- **PhD:** O tamanho do passo na direção oposta ao gradiente da função de custo. Afeta a convergência e a estabilidade do otimizador.

### Regularização L2 (Lambda - $\lambda$)
- **Leigo:** Um "freio" que impede o modelo de decorar detalhes inúteis (ruído) dos dados.
- **PhD:** Penalização da norma Euclidiana dos pesos ($|w|^2$) adicionada à função de custo para prevenir o overfitting e reduzir a variância do modelo.

## 3. Referências Acadêmicas Sugeridas
- **Rollinson, H. R. (1993).** *Using Geochemical Data: Evaluation, Presentation, Interpretation*. Longman Scientific & Technical.
- **Bishop, C. M. (2006).** *Pattern Recognition and Machine Learning*. Springer.
- **Telford, W. M., et al. (1990).** *Applied Geophysics*. Cambridge University Press.
