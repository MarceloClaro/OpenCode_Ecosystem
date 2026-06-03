# Qualis Target Navigator (QTNav)

Navegador inteligente de periodicos cientificos com classificacao Qualis CAPES.
Seleciona o veiculo ideal para publicacao com base no manuscrito, area de avaliacao,
estrato Qualis (A1-C), escopo tematico, metricas de aceitacao e estrategias de submissao.

## Triggers
- "qual periodico publicar", "qualis capes", "onde submeter artigo"
- "target journal", "journal finder", "periodico qualis A1"
- "classificacao qualis", "estrato qualis", "selecionar revista"
- "match de escopo", "journal scope", "venue selection"
- Quando o artigo esta pronto e precisa escolher destino de publicacao
- Quando precisa avaliar se um periodico especifico e adequado

## Pipeline Base

1. **EXTRACT**: Extrair titulo, abstract, palavras-chave e area do manuscrito
2. **CLASSIFY**: Determinar area-mae CAPES (47 areas) via correspondencia semantica
3. **SEARCH**: Buscar periodicos no Qualis CAPES do quadrienio vigente (2021-2024)
4. **SCOPE-MATCH**: Calcular alinhamento tematico periodico-manuscrito (Jaccard + embeddings)
5. **RANK**: Ordenar por estrato Qualis × alinhamento tematico × tempo medio de resposta
6. **RECOMMEND**: Top-5 periodicos com justificativa detalhada e estrategia de submissao

## Fluxo de Decisao

```
Manuscrito → Extracao (meta+corpo) → Area CAPES → Qualis DB
    ↓
Scope match (titulo/abstract vs escopo periodico)
    ↓
Ranking estratificado: A1 > A2 > A3 > A4 > B1 > B2 > B3 > B4 > C
    ↓
Filtros: acesso aberto, APC, tempo revisao, taxa aceitacao
    ↓
Recomendacao top-5 + justificativas + plano de adequacao
```

## Fatores de Ranqueamento

| Fator | Peso | Justificativa |
|-------|------|---------------|
| Estrato Qualis | 30% | Requisito minimo de programas PG |
| Alinhamento tematico | 25% | Fit com escopo do periodico |
| Qualidade percebida | 15% | CiteScore, SJR, H-index |
| Tempo medio de resposta | 12% | Prazo ate decisao editorial |
| Taxa de aceitacao | 10% | Probabilidade de sucesso |
| Acesso aberto | 5% | Visibilidade e alcance |
| APC (custo) | 3% | Viabilidade financeira |

## Formatos de Saida

- **Tabela de Periodicos**: Top-N com colunas rank, periodico, ISSN, estrato, score, prazo, taxa aceitacao, APC
- **Radar de Compatibilidade**: Grafico spider com 5 eixos (escopo, metodologia, impacto, prazo, custo) por periodico
- **Plano de Adaptacao**: Checklist do que ajustar no manuscrito para cada periodico-alvo
- **Comparativo Pares**: Side-by-side de ate 3 periodicos com forcas e fraquezas

## Integracao com Ecossistema

- `editais-br`: Cruzamento com periodicos indicados em editais de fomento
- `academic-export-abnt`: Formatacao automatica para normas do periodico-alvo
- `cora-debate`: Debate multiagente sobre trade-offs da escolha (A1 lento vs A2 rapido)
- `scihub`: Verificacao de artigos publicados no periodico para analise de afinidade
- `code-graphrag`: Registro de decisoes de escolha no grafo de conhecimento

## Referencias Externas

- Plataforma Sucupira (Qualis CAPES): https://sucupira.capes.gov.br/
- Directory of Open Access Journals (DOAJ): https://doaj.org/
- Scimago Journal Rank (SJR): https://www.scimagojr.com/
- Journal Citation Reports (JCR): via Clarivate
- SHERPA/RoMEO (copyright policies): https://v2.sherpa.ac.uk/romeo/

## Limitacoes e Cuidados

- Qualis CAPES e atualizado a cada quadrienio; sempre verificar vigencia
- Classificacao Qualis varia por area de avaliacao; um mesmo periodico pode ser A1 em uma area e B1 em outra
- Recomendacoes sao probabilisticas; consultar edital do programa de PG sempre
- Para periodicos predadores, usar checklist Think.Check.Submit como verificacao adicional
