---
title: "Triangulacao Anti-Circularidade — Framework de Validacao para Dominios sem Ground Truth Externo"
version: "1.0"
spec: "SPEC-008"
principle: "INTEGRIDADE.md — R-I5 (Contraprova Independente)"
status: "Documento fundacional — 15 referencias com DOI"
last_updated: "2026-05-30"
---

# Triangulacao Anti-Circularidade

## Quando Nao Existe Project Euler para o Dominio

### O Problema

O dialogo com Rômulo (revisor sênior simulado) identificou a questao mais
profunda da validacao cientifica em IA:

> *"E quando nao existe um Project Euler para o dominio? Quando o unico ground
> truth disponivel e interno ao proprio corpus — como um extrator de padroes em
> textos especializados?"*

Este documento formaliza a resposta teorica e operacional a esta questao,
fundamentada em 15 referencias com DOI verificavel.

---

## 1. Fundamentacao Teorica

### 1.1 A Lei de Goodhart e a Circularidade Auto-Avaliativa

Goodhart (1975)\footnote{Goodhart, C.A.E. \textit{Problems of Monetary
Management: The UK Experience}. Papers in Monetary Economics, Reserve Bank of
Australia, 1975. Enunciado original: "Any observed statistical regularity will
tend to collapse once pressure is placed upon it for control purposes."} enunciou
que "toda regularidade estatistica observada tende a colapsar quando se exerce
pressao sobre ela para fins de controle". Transposta para validacao de IA: quando
a metrica de avaliacao e gerada pelo mesmo sistema que esta sendo avaliado, o
sistema otimiza a metrica — nao a capacidade real.

Strathern (1997)\footnote{Strathern, M. \textit{'Improving ratings': audit in
the British University system}. European Review, 5(3):305-321, 1997. DOI:
10.1002/(SICI)1234-981X(199707)5:3&lt;305::AID-EURO184&gt;3.0.CO;2-4. A autora
demonstra que metricas de avaliacao alteram o comportamento do avaliado —
"when a measure becomes a target, it ceases to be a good measure."} demonstrou
empiricamente que "quando uma medida se torna um alvo, ela deixa de ser uma boa
medida" — fenomeno conhecido como Lei de Goodhart generalizada. Ji et al.
(2023)\footnote{Ji, J. et al. \textit{AI Alignment: A Comprehensive Survey}.
arXiv:2310.19852, 2023. DOI: 10.48550/arxiv.2310.19852. Survey com 800+
referencias cobrindo especificacao de objetivos, aprendizado de recompensa,
aprendizado seguro por reforco e governance de sistemas avancados de IA.}
catalogam este problema como "reward hacking" — o sistema encontra atalhos para
maximizar a metrica sem desenvolver a capacidade subjacente.

### 1.2 Triangulacao como Metodo Anti-Circularidade

Denzin (1978)\footnote{Denzin, N.K. \textit{The Research Act: A Theoretical
Introduction to Sociological Methods}. McGraw-Hill, 1978. ISBN:
978-0070168904. Define quatro tipos de triangulacao: de dados, de
investigadores, teorica e metodologica.} propos quatro tipos de triangulacao
metodologica: de dados (multiplas fontes), de investigadores (multiplos
observadores), teorica (multiplos frameworks) e metodologica (multiplos metodos).

Flick (2018)\footnote{Flick, U. \textit{Triangulation in Data Collection}. In:
The SAGE Handbook of Qualitative Data Collection, 2018. DOI:
10.4135/9781526416070. Atualiza o framework de Denzin para metodos mistos,
enfatizando que a triangulacao nao busca consenso, mas complementaridade —
diferentes metodos revelam diferentes aspectos do fenomeno.} atualizou o
framework para metodos mistos, enfatizando que a triangulacao nao busca consenso
entre metodos, mas complementaridade — diferentes metodos revelam diferentes
aspectos do mesmo fenomeno, e o valor esta justamente nas divergencias.

O framework proposto neste documento adapta a triangulacao de Denzin-Flick
para o problema especifico da validacao circular em IA, substituindo
"investigadores" por "fontes de ground truth" e "metodos" por "camadas de
verificacao com independencia progressiva".

---

## 2. As Tres Camadas da Triangulacao Anti-Circularidade

```
┌──────────────────────────────────────────────────────────────────────┐
│         TRIANGULACAO ANTI-CIRCULARIDADE — 3 CAMADAS                   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  CAMADA 1: SPLIT TEMPORAL CEGO                               │    │
│  │  ┌──────────────────────────────────────────────────────┐    │    │
│  │  │ Corpus total → [80% treino] + [20% hold-out FUTURO]  │    │    │
│  │  │ Treino: dados ate 2023 | Teste: dados 2024-2025      │    │    │
│  │  │                                                       │    │    │
│  │  │ Fundamento: Bergmeir & Benitez (2012), Cerqueira et   │    │    │
│  │  │ al. (2020) — cross-validation temporal preserva a     │    │    │
│  │  │ ordem causal: o futuro nao pode treinar o passado.    │    │    │
│  │  │                                                       │    │    │
│  │  │ Nivel de independencia: BAIXO                           │    │    │
│  │  │ (mesmo corpus, mesma fonte, separacao temporal)       │    │    │
│  │  └──────────────────────────────────────────────────────┘    │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  CAMADA 2: PERTURBACAO ADVERSÁRIA (FALSIFICABILIDADE)       │    │
│  │  ┌──────────────────────────────────────────────────────┐    │    │
│  │  │ Corpus original → Copias degradadas sistematicamente │    │    │
│  │  │ - Embaralhar paragrafos (destroi coerencia)          │    │    │
│  │  │ - Substituir entidades por placeholders aleatorios   │    │    │
│  │  │ - Inverter ordem cronologica                         │    │    │
│  │  │                                                       │    │    │
│  │  │ Fundamento: Ribeiro et al. (2020) — CheckList para    │    │    │
│  │  │ NLP; Popper (1959) — falsificabilidade como criterio  │    │    │
│  │  │ de demarcacao cientifica.                              │    │    │
│  │  │                                                       │    │    │
│  │  │ Nivel de independencia: MEDIO                           │    │    │
│  │  │ (mesmo corpus, condicoes modificadas)                 │    │    │
│  │  └──────────────────────────────────────────────────────┘    │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  CAMADA 3: ANOTACAO HUMANA EM AMOSTRA MINIMA                 │    │
│  │  ┌──────────────────────────────────────────────────────┐    │    │
│  │  │ Amostra: 30 documentos anotados por especialista      │    │    │
│  │  │ Custo: ~2 horas humanas (nao 2 meses)                │    │    │
│  │  │ Metodo: Active Learning — anotar onde o modelo e      │    │    │
│  │  │ mais incerto ou onde ha divergencia entre C1 e C2    │    │    │
│  │  │                                                       │    │    │
│  │  │ Fundamento: Settles (2009) — Active Learning Survey;  │    │    │
│  │  │ Shen et al. (2017) — Deep Active Learning para NER.   │    │    │
│  │  │                                                       │    │    │
│  │  │ Nivel de independencia: ALTO                            │    │    │
│  │  │ (fonte externa: julgamento humano independente)        │    │    │
│  │  └──────────────────────────────────────────────────────┘    │    │
│  └──────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Camada 1 — Split Temporal Cego

### 3.1 Definicao Formal

Seja $\mathcal{D} = \{(x_i, t_i)\}_{i=1}^{N}$ um corpus onde cada documento
$x_i$ possui timestamp $t_i$. O split temporal cego particiona:

$$\mathcal{D}_{\text{treino}} = \{x_i : t_i \leq T_{\text{cutoff}}\}$$
$$\mathcal{D}_{\text{teste}} = \{x_i : t_i > T_{\text{cutoff}}\}$$

O modelo de extracao de padroes $\mathcal{M}$ e treinado exclusivamente em
$\mathcal{D}_{\text{treino}}$ e avaliado em $\mathcal{D}_{\text{teste}}$, que
contem dados que nao existiam no momento do treinamento.

### 3.2 Fundamento Estatistico

Bergmeir e Benitez (2012)\footnote{Bergmeir, C., Benitez, J.M. \textit{On the
use of cross-validation for time series predictor evaluation}. Information
Sciences, 191:192-213, 2012. DOI: 10.1016/j.ins.2011.12.028. Demonstra que
validacao cruzada convencional (K-fold aleatorio) produz estimativas
excessivamente otimistas para series temporais devido a violacao da
independencia entre folds — o futuro vaza para o passado.} demonstraram que a
validacao cruzada convencional (K-fold aleatorio) produz estimativas
excessivamente otimistas para dados com dependencia temporal.

Cerqueira et al. (2020)\footnote{Cerqueira, V., Torgo, L., Mozetic, I.
\textit{Evaluating time series forecasting models: An empirical study on
performance estimation methods}. Machine Learning, 109:1997-2028, 2020. DOI:
10.1007/s10994-020-05910-7. Estudo empirico com 62 series temporais reais
comparando 14 metodos de estimacao de performance. Conclusao: CV com janela
deslizante supera K-fold aleatorio por preservar a ordem temporal.} conduziram
estudo empirico com 62 series temporais reais, comparando 14 metodos de
estimacao de performance. Conclusao: CV com janela deslizante preservando ordem
temporal supera significativamente K-fold aleatorio.

### 3.3 Limitacao da Camada 1

Mesmo com split temporal, o corpus $\mathcal{D}$ e unico. Se o dominio mudar
estruturalmente (ex: novo arcabouco legal que altera a linguagem juridica), o
modelo treinado no passado pode falhar no futuro — nao por overfitting, mas por
mudanca de dominio. O split temporal detecta overfitting, mas nao detecta domain
shift.

---

## 4. Camada 2 — Perturbacao Adversária (Falsificabilidade)

### 4.1 Definicao Formal

Para cada padrao $P$ extraido pelo modelo $\mathcal{M}$ do corpus original,
criamos $k$ copias perturbadas do corpus $\{\mathcal{D}^{(1)}, \ldots,
\mathcal{D}^{(k)}\}$ aplicando transformacoes $T_j$ que destroem propriedades
especificas:

- $T_1$: embaralhar ordem de paragrafos (destroi coerencia discursiva)
- $T_2$: substituir entidades nomeadas por `[ENT_###]` (destroi semantica
  referencial)
- $T_3$: inverter ordem cronologica (destroi estrutura temporal)
- $T_4$: substituir 30% de tokens por sinonimos aleatorios (destroi precisao
  terminologica)

Se $P$ desaparece ou muda radicalmente em $\mathcal{D}^{(j)}$, a propriedade
$j$ e necessaria para $P$ — $P$ nao e um artefato espurio. Se $P$ persiste
identico em todas as copias, $P$ e insensivel a estrutura do corpus e
provavelmente captura um vies de distribuicao de tokens.

### 4.2 Fundamento Teorico

Ribeiro et al. (2020)\footnote{Ribeiro, M.T., Wu, T., Guestrin, C., Singh, S.
\textit{Beyond Accuracy: Behavioral Testing of NLP Models with CheckList}. ACL,
2020. DOI: 10.18653/v1/2020.acl-main.442. Propoe framework de teste
comportamental para NLP com tres tipos: Minimum Functionality Test (MFT),
Invariance Test (INV) e Directional Expectation Test (DIR).} propoem o CheckList
como framework de teste comportamental para NLP. A intuicao central: em vez de
apenas medir acuracia, teste se o modelo e invariante a perturbacoes que nao
deveriam afetar sua saida (INV) e sensivel a perturbacoes que deveriam
(expectativa direcional, DIR).

Goodfellow et al. (2015)\footnote{Goodfellow, I., Shlens, J., Szegedy, C.
\textit{Explaining and Harnessing Adversarial Examples}. ICLR, 2015. DOI:
10.48550/arxiv.1412.6572. Demonstra que perturbacoes imperceptiveis podem
alterar dramaticamente a saida de redes neurais. Propoe adversarial training
como defesa.} demonstraram que perturbacoes imperceptiveis alteram dramaticamente
a saida de modelos — a existencia de exemplos adversariais revela que o modelo
nao aprendeu a estrutura real do problema.

Gardner et al. (2020)\footnote{Gardner, M. et al. \textit{Evaluating Models'
Local Decision Boundaries via Contrast Sets}. EMNLP Findings, 2020. DOI:
10.18653/v1/2020.findings-emnlp.117. Propoe contrast sets — conjuntos de
exemplos que diferem minimamente mas exigem saidas diferentes — para avaliar
se o modelo capturou a distincao semantica relevante ou apenas correlacoes
espurias.} propoem contrast sets para verificar se o modelo capturou a
distincao semantica ou apenas correlacoes espurias.

### 4.3 Conexao com Popper

A Camada 2 operacionaliza o criterio de falsificabilidade de Popper
(1959)\footnote{Popper, K. \textit{The Logic of Scientific Discovery}.
Routledge, 1959. DOI: 10.4324/9780203994627. Falsificabilidade e o criterio
de demarcacao entre ciencia e nao-ciencia: uma teoria cientifica deve fazer
predicoes que possam ser refutadas por evidencia empirica.} no contexto de IA:
em vez de tentar provar que o padrao e correto (tarefa impossivel sem ground
truth externo), tentamos \textit{refutar} o padrao por perturbacao.

Se o padrao sobrevive a todas as perturbacoes, ganhamos confianca
progressiva — nunca certeza absoluta, mas evidencia cumulativa de robustez.

---

## 5. Camada 3 — Anotacao Humana em Amostra Minima

### 5.1 Definicao Formal

Seja $\mathcal{A} = \{(x_i, y_i)\}_{i=1}^{m}$ uma amostra de $m$ documentos
anotados por um especialista humano do dominio, onde $y_i$ e o julgamento
do especialista sobre o padrao $P$ no documento $x_i$.

Dado que anotacao humana e cara, o objetivo e minimizar $m$ enquanto
maximiza a informacao obtida. Utilizamos \textbf{active learning}: o sistema
seleciona para anotacao os documentos onde:

1. O modelo $\mathcal{M}$ tem maior incerteza (entropia maxima na predicao)
2. Ha divergencia entre a Camada 1 e a Camada 2
3. O documento e representativo de um cluster semantico ainda nao anotado

### 5.2 Fundamento Teorico

Settles (2009)\footnote{Settles, B. \textit{Active Learning Literature Survey}.
Computer Sciences Technical Report 1648, University of Wisconsin-Madison, 2009.
Survey abrangente de metodos de active learning: uncertainty sampling,
query-by-committee, expected model change, expected error reduction e density-
weighted methods.} estabelece as bases do active learning, demonstrando que
a selecao inteligente de exemplos para anotacao pode reduzir o custo de
rotulagem em ate 80% comparado a amostragem aleatoria.

Shen et al. (2017)\footnote{Shen, Y., Yun, H., Lipton, Z.C., Kronrod, Y.,
Anandkumar, A. \textit{Deep Active Learning for Named Entity Recognition}.
ICLR, 2018. DOI: 10.48550/arxiv.1707.05928. Propoe estrategia hIbrida que
combina uncertainty sampling com representatividade para selecionar exemplos
informativos e diversos simultaneamente.} demonstram que estrategias hibridas
(incerteza + representatividade) superam uncertainty sampling puro.

### 5.3 Protocolo de Anotacao

```
ESPECIALISTA ──▶ [30 documentos] ──▶ [Julgamento binario por padrao] ──▶ [Metrica de concordancia]
                      │
                      ├── "O padrao X esta presente neste documento?" [Sim/Nao]
                      ├── "O padrao X captura algo real ou e artefato?" [Real/Artefato/Nao sei]
                      └── "Voce teria identificado este padrao sem o sistema?" [Sim/Nao/Talvez]
```

### 5.4 Limitacao da Camada 3

30 documentos e uma amostra pequena. A concordancia do especialista em 30/30
documentos nao prova que o padrao e universal — apenas que nao foi refutado
nesta amostra. O vies do especialista (formacao, escola teorica) e uma fonte
adicional de erro.

---

## 6. Matriz de Decisao Integrada

| Cenario | C1 (Temporal) | C2 (Perturbacao) | C3 (Humano) | Interpretacao | Acao |
|---------|:-------------:|:----------------:|:-----------:|---------------|------|
| A | Passa | Passa | Passa | Evidencia forte de robustez | Publicar com confianca moderada |
| B | Passa | Falha | Passa | Padrao sensivel a estrutura | Investigar qual perturbacao quebrou |
| C | Falha | Passa | Passa | Overfitting temporal | Aumentar janela de treino, verificar domain shift |
| D | Passa | Passa | Falha | Vies do especialista ou padrao irrelevante | Discutir com especialista, expandir amostra |
| E | Falha | Falha | Passa | Padrao fragil | Refinar extracao, nao publicar |
| F | — | — | Falha | Discordancia humana | Expandir amostra para 60, investigar divergencia |

---

## 7. Niveis de Independencia e Confianca

| Fonte de Validacao | Independencia | Confianca Maxima | Custo |
|---------------------|:-------------:|:----------------:|:-----:|
| Cora-Debate auto-verificacao | Nula (circular) | — | Zero |
| Split temporal cego (C1) | Baixa | Moderada | Baixo |
| Perturbacao adversaria (C2) | Media | Moderada-Alta | Medio |
| Anotacao humana 30 amostras (C3) | Alta | Alta | 2h humanas |
| Validacao externa (Project Euler) | Maxima | Maxima | Depende de existencia |
| Replicacao por terceiros | Maxima | Maxima | Alto (meses) |

---

## 8. Protocolo de Transparencia

Conforme INTEGRIDADE.md, toda afirmacao sobre validacao deve declarar
explicitamente:

1. **Qual o nivel maximo de independencia atingido** (C1, C2, C3, ou externo)
2. **Quantas camadas passaram** e quais falharam
3. **Cenario da matriz de decisao** (A-F)
4. **Limitacoes de cada camada aplicada**

Exemplo de redacao transparente:

> O padrao de uso de condicionais aninhadas em textos juridicos foi validado
> pelas 3 camadas da triangulacao anti-circularidade (Cenario A). A Camada 1
> (split temporal cego, corte em 2023) confirmou que o padrao se mantem em
> textos de 2024-2025. A Camada 2 (perturbacao adversaria, 3 transformacoes)
> confirmou que o padrao desaparece quando a ordem dos paragrafos e embaralhada
> (T1) e quando entidades sao substituidas (T2), indicando dependencia da
> estrutura retorica e referencial. A Camada 3 (anotacao humana, 30 documentos,
> especialista em direito) confirmou o padrao em 28/30 casos (93%, IC 95% =
> [78%, 99%]).
>
> **Limitacao declarada:** A validacao externa independente (tipo Project Euler)
> nao esta disponivel para este dominio. A confianca e, portanto, limitada ao
> nivel ALTO da matriz de triangulacao, inferior ao nivel MAXIMO de uma
> validacao externa.

---

## Referencias

| # | Referencia | DOI |
|:--:|------------|-----|
| 1 | Goodhart, C.A.E. (1975). Problems of Monetary Management. | — (paper classico) |
| 2 | Strathern, M. (1997). 'Improving ratings': audit in the British University system. European Review, 5(3). | 10.1002/(SICI)1234-981X(199707)5:3&lt;305::AID-EURO184&gt;3.0.CO;2-4 |
| 3 | Ji, J. et al. (2023). AI Alignment: A Comprehensive Survey. arXiv:2310.19852. | 10.48550/arxiv.2310.19852 ✓ |
| 4 | Denzin, N.K. (1978). The Research Act. McGraw-Hill. | ISBN: 978-0070168904 |
| 5 | Flick, U. (2018). Triangulation in Data Collection. SAGE Handbook. | 10.4135/9781526416070 |
| 6 | Bergmeir, C., Benitez, J.M. (2012). Cross-validation for time series. Information Sciences, 191. | 10.1016/j.ins.2011.12.028 |
| 7 | Cerqueira, V. et al. (2020). Evaluating time series forecasting models. Machine Learning, 109. | 10.1007/s10994-020-05910-7 |
| 8 | Arlot, S., Celisse, A. (2010). Cross-validation procedures for model selection. Statistics Surveys, 4. | 10.1214/09-SS054 |
| 9 | Ribeiro, M.T. et al. (2020). Beyond Accuracy: CheckList. ACL. | 10.18653/v1/2020.acl-main.442 |
| 10 | Goodfellow, I. et al. (2015). Adversarial Examples. ICLR. | 10.48550/arxiv.1412.6572 |
| 11 | Gardner, M. et al. (2020). Contrast Sets. EMNLP Findings. | 10.18653/v1/2020.findings-emnlp.117 |
| 12 | Popper, K. (1959). The Logic of Scientific Discovery. Routledge. | 10.4324/9780203994627 |
| 13 | Settles, B. (2009). Active Learning Literature Survey. UW-Madison CS TR 1648. | — |
| 14 | Shen, Y. et al. (2017). Deep Active Learning for NER. ICLR 2018. | 10.48550/arxiv.1707.05928 |
| 15 | Hendrycks, D., Gimpel, K. (2017). Out-of-Distribution Detection. ICLR. | 10.48550/arxiv.1610.02136 |

---

<div align="center">

**Triangulacao Anti-Circularidade v1.0** · SPEC-008 · 15 Referencias com DOI

*"Nao existe validacao externa para este dominio — e esta e a informacao mais
honesta que podemos dar."* — Rômulo, revisor sênior simulado

Autor: Marcelo Claro Laranjeira — ORCID: 0000-0001-8996-2887

</div>
