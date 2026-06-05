### Etapa 4: Classificação Supervisionada
- Target: ARM relativa (0/1)
- Modelos: Regressão Logística (baseline) + Random Forest
- Validação: Stratified K-Fold (k=5), 3 repeats
- Métricas: acurácia, F1, ROC-AUC, precisão, recall (com desvio padrão)
- Feature importance: importance_inherent (RF) + permutation importance (3 repeats)
- Threshold de 0.5 para classificação binária
