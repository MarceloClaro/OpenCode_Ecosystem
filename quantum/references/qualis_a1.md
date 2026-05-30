# Guia de Pesquisa para Publicações Qualis A1 em QML

Para elevar um experimento de Machine Learning Quântico ao nível de excelência científica (Qualis A1), siga estas diretrizes:

## 1. Rigor Estatístico
- **Cross-Validation**: Use `StratifiedKFold` para garantir que as classes estejam equilibradas em cada fold.
- **Múltiplas Sementes**: Execute o experimento com pelo menos 5 sementes aleatórias diferentes para reportar média e desvio padrão.
- **Testes de Significância**: Aplique testes como o teste t de Student ou ANOVA para comparar modelos.

## 2. Benchmarking Abrangente
- Compare contra modelos clássicos SOTA (SVM, Random Forest, XGBoost).
- Compare contra modelos quânticos base (VQC padrão vs. seu modelo proposto).
- Utilize métricas variadas: Acurácia, F1-Score, Precisão, Recall e AUC-ROC.

## 3. Análise Teórica de Circuitos
- **Expressividade**: Quantifique a capacidade do seu ansatz de cobrir o espaço de Hilbert.
- **Emaranhamento**: Meça a capacidade de gerar correlações quânticas.
- **Barren Plateaus**: Analise a variância do gradiente em relação à profundidade do circuito.

## 4. Mitigação de Erros
- Empregue técnicas como **Zero Noise Extrapolation (ZNE)** ou **Probabilistic Error Cancellation (PEC)** para demonstrar viabilidade em hardware NISQ real.

## 5. Visualização Científica
- Use boxplots para mostrar a distribuição de performance.
- Gere curvas ROC para análise de sensibilidade/especificidade.
- Use heatmaps para visualizar a paisagem de custo ou correlações de parâmetros.
