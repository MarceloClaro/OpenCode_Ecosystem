# Catálogo de Features — Pipeline ML ARM+IAG

## Features do Dataset (11 + 3)

| # | Feature | Descrição | Fonte | Tipo |
|---|---------|-----------|-------|------|
| 1 | gdp_per_capita | PIB per capita (USD correntes) | WDI | Contínua |
| 2 | rd_spending | Gastos em P&D (% do PIB) | WDI/UNESCO | Contínua |
| 3 | internet_users | Usuários de internet (% da população) | WDI/ITU | Contínua |
| 4 | fdi_inflows | Investimento estrangeiro direto (% do PIB) | WDI/UNCTAD | Contínua |
| 5 | services_emp | Emprego em serviços (% do total) | WDI/OIT | Contínua |
| 6 | gini | Índice Gini (desigualdade) | WDI/PIP | Contínua |
| 7 | high_tech_exp | Exportações de alta tecnologia (% manufatura) | WDI | Contínua |
| 8 | unemployment | Taxa de desemprego (% força de trabalho) | WDI/OIT | Contínua |
| 9 | tertiary_enrollment | Matrícula no ensino superior (% bruto) | WDI/UNESCO | Contínua |
| 10 | patent_apps | Pedidos de patente (residentes) | WIPO/WDI | Contínua |
| 11 | ai_readiness | Índice de Prontidão para IA (0-100) | Oxford Insights AIPI | Contínua |

## Features de Complexidade Econômica (3 novas — v3)

| # | Feature | Descrição | Fonte / Metodologia | Tipo |
|---|---------|-----------|---------------------|------|
| 12 | knowledge_complexity | Índice de Complexidade do Conhecimento (KCI proxy): primeiro componente principal (PC1) de 6 features de inovação e capital humano (P&D, patentes, alta tecnologia, internet, ensino superior, prontidão IA) | PCA sobre features existentes, adaptado de Hausmann-Hidalgo (2014) — método dos reflections aplicado ao espaço de conhecimento produtivo | Contínua (z-score) |
| 13 | export_sophistication | Sofisticação das Exportações (EXPY proxy): média ponderada do PIB per capita pela intensidade tecnológica das exportações — captura o nível de renda associado à cesta exportadora | Adaptado de Hausmann, Hwang & Rodrik (2007) — PRODY/EXPY, usando high_tech_exp + patent_apps + P&D como proxies de sofisticação setorial | Contínua (z-score) |
| 14 | product_density | Densidade Produtiva (Product Density proxy): similaridade cosseno do perfil de desenvolvimento do país com a fronteira tecnológica (top 10% PIB per capita) — mede a distância para diversificação em produtos mais sofisticados | Adaptado de Hidalgo et al. (2007) — Product Space, usando perfil multivariado de 11 features vs. fronteira de referência | Contínua (0-1) |

### Justificativa Teórica

1. **knowledge_complexity (KCI)**: A ARM decorre da incapacidade de acumular know-how produtivo (Hausmann et al., 2014). Países com alta complexidade diversificam para setores de maior valor agregado e escapam da armadilha. O PC1 das features de inovação captura a dimensão latente de capacidade absortiva tecnológica.

2. **export_sophistication (EXPY)**: O que um país exporta importa para o crescimento (Hausmann, Hwang & Rodrik, 2007). A ARM está associada a cestas de exportação com baixo teor tecnológico. Países que exportam produtos sofisticados (alta renda implícita) crescem mais rápido e têm menor risco de armadilha.

3. **product_density**: A densidade no product space prediz a probabilidade de um país diversificar para novos produtos mais sofisticados (Hidalgo et al., 2007). Quanto maior a densidade, menor o custo de transição para atividades de maior complexidade, reduzindo o risco de ARM.

## Targets

| Target | Descrição | Tipo |
|--------|-----------|------|
| arm_trapped | ARM strict (3 países) | Binária (0/1) |
| arm_relative | ARM relativa (29 países) | Binária (0/1) |
| gdp_growth | Crescimento do PIB (%) | Contínua (regressão) |

## Feature Importance (Sessão Real)

| Feature | RF Importance | Permutation Importance |
|---------|:------------:|:---------------------:|
| PIB per capita | 19.24% | 5.06% |
| Gastos em P&D | 12.17% | 1.74% |
| Usuários Internet | 11.38% | 3.93% |
| FDI inflows | 10.67% | 0.74% |
| Emprego Serviços | 9.03% | 2.39% |
| Gini | 8.98% | 3.57% |
| Export. Alta Tecnologia | 8.18% | 4.03% |
| Desemprego | 7.32% | 2.10% |
| Ensino Superior | 6.69% | 2.21% |
| Pedidos Patente | 4.06% | 2.18% |
| Prontidão para IA | 2.27% | 0.21% |
