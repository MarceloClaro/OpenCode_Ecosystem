### Etapa 5: Detecção de Anomalias e Clusterização
- **Anomalias**: Isolation Forest (contamination=auto, random_state=42)
  - Top 20 anomalias com scores
  - Visualização: scatter plot PIBpc × AI Readiness
- **Clusters**: K-Means (k=4, KMeans++ initialization)
  - Perfis: GDP per capita médio, AI readiness médio, contagem ARM
  - Visualização: scatter plot com centroides
