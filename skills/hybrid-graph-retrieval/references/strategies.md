# Estratégias de Busca Híbrida — Referência Rápida

## 1. InsightForge — Análise Profunda

**Quando usar:** Perguntas complexas que exigem compreensão multidimensional.

**Pipeline:**
1. LLM (ou regras) decompõe em sub-perguntas
2. Cada sub-pergunta busca no grafo
3. Entidades extraídas com detalhes
4. Cadeias de relacionamento montadas
5. Resultado integrado

**Dimensões de análise:**
- Stakeholders: quem são os participantes?
- Causas: o que motivou o evento?
- Impactos: quais as consequências?
- Temporal: como evoluiu no tempo?
- Contrafactual: o que poderia ter sido diferente?

## 2. PanoramaSearch — Visão Panorâmica

**Quando usar:** Contexto completo, incluindo informações históricas.

**Pipeline:**
1. Obtém TODOS os nós e arestas
2. Categoriza: ativo vs. histórico/expirado
3. Pontua por relevância à consulta
4. Retorna visão completa

**Campos temporais (quando disponíveis):**
- `valid_at`: quando o fato começou a valer
- `invalid_at`: quando perdeu validade
- `expired_at`: quando expirou automaticamente
- `created_at`: quando foi criado

## 3. QuickSearch — Busca Rápida

**Quando usar:** Respostas rápidas, perguntas simples.

**Pipeline:**
1. Busca combinada (keywords + semântica)
2. Top-K resultados
3. Cache de consultas frequentes (quando ativado)

## Comparação

| Estratégia | Profundidade | Velocidade | Cobertura | # Tools Calls |
|---|---|---|---|---|
| InsightForge | Máxima | Lenta | Focada | N sub-queries |
| PanoramaSearch | Média | Média | Máxima | 2 (nodes+edges) |
| QuickSearch | Mínima | Rápida | Limitada | 1 |

## Exemplos de Uso

```bash
# Análise profunda de um tópico
python hybrid_search.py insight --graph meu_grafo --query "Impacto das políticas de privacidade"

# Visão panorâmica
python hybrid_search.py panorama --graph meu_grafo --query "privacidade" --include-historical

# Busca rápida
python hybrid_search.py quick --graph meu_grafo --query "GDPR" --limit 5

# Estatísticas do grafo
python hybrid_search.py stats --graph meu_grafo
```
