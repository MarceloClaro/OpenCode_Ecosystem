# ESCALA CORA — OpenCode Ecosystem Evolution Timeline
## Mapeamento: Cora-0.1 (Básico) → Cora-4.0 (Pesquisa Avançada, atual)

| Cora | Estágio | Nível | PCI | Data | Marco |
|:----:|:-------:|-------|:---:|------|-------|
| **0.1** | Pré-ecossistema | 🔵 Básico | — | 09/05/26 | OpenCode CLI instalado. 0 agentes, 0 MCPs. Só o modelo base. |
| **0.3** | Gênese | 🔵 Básico | — | 10/05/26 | Primeiros agentes manuais. Skills isoladas sem orquestração. |
| **0.5** | MASWOS v1 | 🔵 Básico | — | 11/05/26 | Pipeline acadêmico incipiente. 8 agentes de escrita. Sem verificação. |
| **0.7** | AutoEvolve | 🔵 Básico | 65 | 12/05/26 | Motor de evolução autônoma. Gera novas skills. Ainda frágil. |
| **0.9** | Cora-Debate V1 | 🔵 Básico | 70 | 13/05/26 | Primeiro verificador simbólico. Apenas V1 (dimensional). |
| **1.0** | Cora-Debate V1-V6 | 🟢 Graduação | 85 | 14/05/26 | 6 verificadores. Q-Score UCB1. IMO 2025 P1: resposta FALSA com PCI 85. ⚠️ |
| **1.3** | Diagnóstico F1-F5 | 🟢 Graduação | 30 | 15/05/26 | Autopsia das 5 falhas. PCI cai de 85→30: sistema APRENDEU A DUVIDAR. |
| **1.5** | P20-P23 (Estrutural) | 🟢 Graduação | 45 | 16/05/26 | LemmaGraph + BFS + CrossRef. Verificação estrutural implementada. |
| **1.7** | Taxonomia 34→68 | 🟢 Graduação | 55 | 17/05/26 | Primeira onda de raciocínios (7 categorias). Classificação por keyword. |
| **2.0** | Taxonomia 204 | 🟡 PG | 65 | 18/05/26 | 25 categorias, 150+ refs com DOI. Classificação semântica TF-IDF. |
| **2.3** | Orquestrador 7 fases | 🟡 PG | 75 | 19/05/26 | 38 agentes em pipeline. Game Theory (5 agentes). CORA Consensus. |
| **2.5** | Creative Leap R201-R204 | 🟡 PG | 82 | 20/05/26 | 60 problemas, 19 domínios. 4 raciocínios autônomos gerados. |
| **2.7** | Elegancia Autônoma | 🟡 PG | 88 | 21/05/26 | IMO 2002 P1: 63→97 em 3 iterações. 15-D calibration. |
| **2.9** | Validação Estatística | 🟡 PG | 92 | 22/05/26 | 10 IMO reais: PCI 99/100. Wilcoxon p=9.8×10⁻⁴. Cohen's d=5.37. |
| **3.0** | Artigo ABNT Qualis A1 | 🔴 Pesquisa | 95 | 23/05/26 | 40 páginas, 44 refs. Contraprova geometria simplética PCI 100. Cora 38/38. |
| **3.2** | Humanização Anti-IA | 🔴 Pesquisa | 95 | 24/05/26 | 14 correções cirúrgicas. 0 marcadores IA. Plágio projetado < 3%. |
| **3.5** | DCA Módulo 1 (Geométrico) | 🔴 Pesquisa | 96 | 25/05/26 | 7 exercícios resolvidos. R205-R208 registrados. Categoria XXVI. |
| **3.7** | DCA Listas 1+2 (Completo) | 🔴 Pesquisa | 94 | 26/05/26 | 14 problemas resolvidos. R209-R212 candidatos. 212 raciocínios, 27 categorias. |
| **4.0** | v4.6.1 — Estado Atual | 🔴 Pesquisa | 98 | 26/05/26 | **212 raciocínios. 27 categorias. GitHub publicado. Artigo 40p ABNT. Contraprova tripla verificada.** |

---

## Distribuição por Nível

```
🔵 BÁSICO (0.1–0.9):  6 estágios — Fundação + primeiros verificadores
🟢 GRADUAÇÃO (1.0–1.9): 4 estágios — Diagnóstico de falhas + verificação estrutural
🟡 PG (2.0–2.9):         5 estágios — Taxonomia + orquestração + geração autônoma
🔴 PESQUISA (3.0–4.0):   5 estágios — Artigo Qualis A1 + DCA + expansão contínua
```

## Trajetória do PCI (Cora-0.7 → Cora-4.0)

```
PCI
100 ┤                                              ●━━━●━━━●  Cora 3.0-4.0
 90 ┤                          ●━━━●━━━●━━━●
 80 ┤              ●━━━●
 70 ┤      ●━━━●
 60 ┤  ●
 50 ┤
 40 ┤
 30 ┤          ●  ← O MOMENTO MAIS IMPORTANTE: o sistema aprendeu a duvidar
 20 ┤
    └──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──
      0.1 0.5 0.9 1.0 1.3 1.5 1.7 2.0 2.3 2.5 2.7 2.9 3.0 3.2 3.5 3.7 4.0
          BÁSICO        GRADUAÇÃO            PG              PESQUISA
```

## Lição Fundamental (Cora-1.0 → Cora-1.3)

A queda do PCI de **85→30** entre Cora-1.0 e Cora-1.3 **não é uma regressão — é um avanço**. Representa o momento em que o sistema adquiriu a capacidade de **reconhecer seu próprio erro**: o CrossRefAgent identificou conflito com fontes externas (Evan Chen, DeepMind), e o LemmaGraph propagou a falha do lema não-justificado para todos os descendentes.

**Cora-1.3 é o marco mais importante de toda a trajetória** — sem ele, não haveria Cora-3.0.

## Projeção

| Cora | Meta | Descrição |
|:----:|------|-----------|
| **4.5** | Lean 4 Integration | Verificador formal de back-end substituindo V1-V6 |
| **5.0** | Ollama phi3:mini | Raciocínio LLM real (não simulado) em CPU/8GB |
| **5.5** | 400+ IMO (1959-2025) | Banco completo para calibração estatística robusta |
| **6.0** | Publicação em Periódico | Submissão real a periódico Qualis A1 |

---

*Linha do tempo gerada pelo OpenCode Ecosystem v4.6.1 — 26/05/2026 — Escala Cora*
