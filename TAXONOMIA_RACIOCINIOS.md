---
title: "Taxonomia Completa de Raciocinios para Resolucao Cientifica Verificada"
subtitle: "Como Aprimorar os Multiagentes do OpenCode Ecosystem para Orquestrar Provas Matematicas"
version: "1.0.0"
date: "2026-05-25"
status: "Proposta de Arquitetura Cognitiva — ReasoningOrchestrator v10.0"
trigger: "Licoes do Problema 1 da IMO 2025 — a verificacao simbolica (V1-V6) nao bastou"
principio: "Cada raciocinio deve ser rastreavel, verificavel e ter sua falha propagada automaticamente"
referencias: 34 (com DOI/ISBN/arXiv)
---

# Taxonomia de Raciocinios — ReasoningOrchestrator v10.0

> **Por que este documento existe**: O Cora-Debate (V1-V6) verificou a consistencia de
> formulas, mas nao a validade de provas. A falha no Problema 1 da IMO 2025 revelou que
> 5 raciocinios essenciais estavam **ausentes** do ecossistema: reducao estrutural,
> verificacao exaustiva de casos base, deteccao de contradicoes internas, rastreamento
> de dependencias entre lemas, e validacao cruzada contra fontes externas. Este documento
> cataloga **todos** os raciocinios necessarios, com referencias academicas reais, e
> propoe a arquitetura para orquestra-los.

---

## 1. Estrutura da Taxonomia

Organizamos os raciocinios em 7 categorias, totalizando 34 tipos:

| Categoria | Tipos | Funcao na Prova |
|-----------|-------|-----------------|
| **I. Fundacionais** | 5 | Definicao, abstracao, notacao, traducao |
| **II. Dedutivos** | 6 | Logica formal, encadeamento, silogismo |
| **III. Indutivos/Redutivos** | 5 | Inducao, reducao estrutural, caso base |
| **IV. Construtivos** | 5 | Construcao, existencia, algoritmo |
| **V. Refutacionais** | 5 | Contraexemplo, contradicao, reductio |
| **VI. Verificacionais** | 4 | Exaustao, model checking, cross-ref |
| **VII. Meta-Cognitivos** | 4 | Dependencia, confianca, revisao |

---

## 2. Catalogo Completo de Raciocinios

### Categoria I — Fundacionais

Estabelecem o terreno comum: definicoes precisas, notacao, abstracao.

| ID | Raciocinio | Descricao | Referencia | Status no OpenCode |
|----|-----------|-----------|------------|-------------------|
| **R01** | Definicional | Estabelecer definicoes precisas e nao-ambiguas | Lakatos (1976) — *Proofs and Refutations* [1] | ✅ Parcial (agentes de escrita) |
| **R02** | Abstrativo | Identificar a estrutura matematica subjacente, ignorando detalhes irrelevantes | Polya (1945) — *How to Solve It* [2] | ❌ Ausente |
| **R03** | Notacional | Escolher notacao que revela estrutura (ex: $S_n$ para o conjunto de pontos) | Knuth (1992) — *Two Notes on Notation* [3] | ❌ Ausente |
| **R04** | Tradutivo | Converter o problema para uma linguagem/dominio onde e mais facil | Tao (2006) — *Solving Mathematical Problems* [4] | ❌ Ausente |
| **R05** | Decomposicional | Dividir o problema em subproblemas independentes | Engel (1998) — *Problem-Solving Strategies* [5] | ✅ Parcial (agent-smith) |

### Categoria II — Dedutivos

Constroem a cadeia logica: se A e verdadeiro, entao B e verdadeiro.

| ID | Raciocinio | Descricao | Referencia | Status no OpenCode |
|----|-----------|-----------|------------|-------------------|
| **R06** | Silogistico | Se $A \implies B$ e $B \implies C$, entao $A \implies C$ | Aristoteles (~350 a.C.) — *Organon* [6] | ❌ Ausente |
| **R07** | Dedutivo-Natural | Derivacao passo a passo com regras de inferencia explicitas | Gentzen (1935) — *Natural Deduction* [7] | ❌ Ausente |
| **R08** | Implicativo | Verificar que cada passo da prova segue logicamente do anterior | Prawitz (1965) — *Natural Deduction: A Proof-Theoretical Study* [8] | ❌ Ausente |
| **R09** | Quantificacional | Manipular "para todo" ($\forall$) e "existe" ($\exists$) | Frege (1879) — *Begriffsschrift* [9] | ❌ Ausente |
| **R10** | Modular | Provar lemas independentes e compo-los no teorema final | Wiles (1995) — *Modular Elliptic Curves and FLT* [10] | ✅ Parcial |
| **R11** | Encadeamento-Reverso | Partir da conclusao desejada e derivar condicoes suficientes | Polya (1945) — *How to Solve It* [2] | ❌ Ausente |

### Categoria III — Indutivos/Redutivos

**Esta e a categoria que faltou completamente no Problema 1.** A rota correta
($k \in \{0,1,3\}$) usa reducao $n \to n-1$ preservando $k$ — um raciocinio
indutivo/redutivo que nenhum agente do ecossistema implementava.

| ID | Raciocinio | Descricao | Referencia | Status no OpenCode |
|----|-----------|-----------|------------|-------------------|
| **R12** | Indutivo-Matematico | Caso base + passo indutivo: $P(n) \implies P(n+1)$ | Peano (1889) — *Arithmetices Principia* [11] | ❌ Ausente |
| **R13** | Redutivo-Estrutural | Reduzir problema de tamanho $n$ para $n-1$ preservando invariante | Burstall (1969) — *Proving Properties of Programs by Structural Induction* [12] | ❌ **AUSENTE (falha critica na IMO)** |
| **R14** | Invariante | Identificar propriedade que se preserva sob transformacao | Dijkstra (1976) — *A Discipline of Programming* [13] | ❌ Ausente |
| **R15** | Caso-Base | Verificar que o menor caso do problema e verdadeiro | Hoare (1969) — *An Axiomatic Basis for Computer Programming* [14] | ❌ **AUSENTE (falha critica na IMO)** |
| **R16** | Recorrente | Resolver relacoes de recorrencia (ex: $a_n = 2a_{n-1} + 1$) | Graham, Knuth, Patashnik (1994) — *Concrete Mathematics* [15] | ❌ Ausente |

### Categoria IV — Construtivos

Produzem exemplos concretos, algoritmos, ou demonstracoes de existencia.

| ID | Raciocinio | Descricao | Referencia | Status no OpenCode |
|----|-----------|-----------|------------|-------------------|
| **R17** | Construtivo-Explicito | Construir explicitamente o objeto cuja existencia se afirma | Bishop (1967) — *Foundations of Constructive Analysis* [16] | ✅ Parcial (construcao no artigo, mas quebrada) |
| **R18** | Algorithmico | Fornecer um algoritmo que produz o objeto desejado | Knuth (1968) — *The Art of Computer Programming* [17] | ✅ Parcial |
| **R19** | Enumerativo | Listar sistematicamente todas as possibilidades | Brualdi (2010) — *Introductory Combinatorics* [18] | ❌ Ausente |
| **R20** | Probabilistico | Provar existencia mostrando que probabilidade > 0 | Erdos (1947) — *Some remarks on the theory of graphs* [19] | ❌ Ausente |
| **R21** | Otimizatorio | Encontrar a melhor construcao sob restricoes dadas | Papadimitriou & Steiglitz (1982) — *Combinatorial Optimization* [20] | ❌ Ausente |

### Categoria V — Refutacionais

Detectam e eliminam erros na prova. **Esta categoria e o coracao do que faltou.**

| ID | Raciocinio | Descricao | Referencia | Status no OpenCode |
|----|-----------|-----------|------------|-------------------|
| **R22** | Contraexemplo | Encontrar instancia que refuta afirmacao universal $\forall x: P(x)$ | Lakatos (1976) — *Proofs and Refutations* [1] | ✅ Parcial (V3) |
| **R23** | Reductio ad Absurdum | Assumir negacao da tese e derivar contradicao | Euclides (~300 a.C.) — *Elementos*, Livro IX [21] | ❌ Ausente |
| **R24** | Contradicao-Interna | Detectar afirmacoes conflitantes dentro da propria prova | Rescher (1976) — *Plausible Reasoning* [22] | ❌ **AUSENTE (falha critica na IMO)** |
| **R25** | Consistencia-Cruzada | Verificar que conclusoes de lemas independentes nao se contradizem | Tarski (1956) — *On the Concept of Logical Consequence* [23] | ❌ Ausente |
| **R26** | Teste-de-Estresse | Testar a prova contra casos extremos e degenerados | Dijkstra (1970) — *Notes on Structured Programming* [24] | ❌ Ausente |

### Categoria VI — Verificacionais

Validam a prova contra fontes externas ou por metodos computacionais.

| ID | Raciocinio | Descricao | Referencia | Status no OpenCode |
|----|-----------|-----------|------------|-------------------|
| **R27** | Exaustivo-Computacional | Verificar todos os casos para $n$ pequeno | Clarke, Grumberg & Peled (1999) — *Model Checking* [25] | ❌ **AUSENTE (falha critica na IMO)** |
| **R28** | Cross-Reference | Comparar com solucoes conhecidas de fontes independentes | Zammit et al. (2024) — *Autoformalization* [26] | ❌ Ausente |
| **R29** | Simbolico-Algebrico | Verificar identidades algebricas via CAS (SymPy, Mathematica) | Meurer et al. (2017) — *SymPy* [27] | ✅ V2 |
| **R30** | Numerico-Estatistico | Verificar propriedades numericas e estatisticas | Virtanen et al. (2020) — *SciPy* [28] | ✅ V4, V5 |

### Categoria VII — Meta-Cognitivos

Raciocinios sobre a **propria prova**: sua estrutura, suas dependencias, sua confianca.

| ID | Raciocinio | Descricao | Referencia | Status no OpenCode |
|----|-----------|-----------|------------|-------------------|
| **R31** | Dependencia-Logica | Rastrear quais lemas dependem de quais; propagar falhas | de Bruijn (1980) — *A Survey of the Project Automath* [29] | ❌ **AUSENTE (falha critica na IMO)** |
| **R32** | Confianca-Calibrada | Atribuir nivel de confianca a cada lema baseado em verificacao | Guo et al. (2017) — *On Calibration of Modern NNs* [30] + Platt (1999) [31] | ✅ Parcial (calibracao Platt implementada) |
| **R33** | Revisao-por-Pares | Submeter a prova a revisores independentes com personas distintas | Liang et al. (2023) — *Multi-Agent Debate* [32] | ✅ agent-forum (P14) |
| **R34** | Generalizacao-Restritiva | Determinar se a resposta se generaliza ou e especifica do caso base | Polya (1954) — *Mathematics and Plausible Reasoning* [33] | ❌ Ausente |

---

## 3. Mapeamento: Raciocinios → Agentes, Skills, Hooks

### 3.1 Novos Agentes Propostos

| Agente | Raciocinios | Funcao |
|--------|------------|--------|
| **InductorAgent** | R12, R13, R14, R15, R16 | "Este problema admite reducao $n \to n-1$? O invariante se preserva?" |
| **BaseCaseAgent** | R15, R19, R27 | "Para $n=3$, enumere TODAS as configuracoes. Verdade computacional." |
| **ContradictionAgent** | R22, R23, R24, R25 | "O texto afirma A e ~A. Contradicao detectada no Lemma X." |
| **LemmaTrackerAgent** | R31, R10 | "Lema 3 depende de Lema 1 e Lema 2. Lema 1 OK, Lema 2 suspeito." |
| **CrossRefAgent** | R28 | "Evan Chen diz k in {0,1,3}. DeepMind confirma. Nossa resposta conflita." |
| **StressTestAgent** | R26, R22 | "Testar n=4, k=2: a construcao cobre (2,3)? NAO. Construcao invalida." |
| **NotationAgent** | R01, R03, R04 | "Defina S_n precisamente. Use notacao que revela estrutura." |
| **BackwardChainAgent** | R11, R08 | "Da conclusao desejada, quais condicoes suficientes?" |
| **AbstractionAgent** | R02, R05, R34 | "Qual a estrutura matematica subjacente? Generaliza?" |
| **ProofHealthAgent** | R31, R32, R33 | "Indice de confianca da prova: 35/100. Lema 2 nao verificado." |

### 3.2 Hooks de Ecossistema

| Hook | Dispara quando | Acao |
|------|---------------|------|
| `on_lemma_claimed` | Um novo lema e enunciado | LemmaTracker registra dependencias |
| `on_contradiction_detected` | ContradictionAgent encontra conflito | Propaga falha pelo LemmaGraph |
| `on_base_case_checked` | BaseCaseAgent termina $n=3$ | Se resultado conflita com claim, alerta |
| `on_cross_ref_mismatch` | CrossRefAgent encontra resposta divergente | Alerta vermelho — revisao obrigatoria |
| `on_construction_tested` | StressTestAgent testa construcao | Se falha para $n$ pequeno, construcao rejeitada |
| `on_proof_complete` | Todos os lemas verificados | ProofHealthAgent emite PCI final |

### 3.3 Integracao com Swarm-Review (P14)

O swarm-review existente orquestra 3+ agentes com personas distintas.
Com a nova taxonomia, o swarm agora inclui:

```
Swarm de Revisao de Prova:
├── InductorAgent      (busca reducao estrutural)
├── ContradictionAgent  (detecta inconsistencias)
├── StressTestAgent     (testa casos extremos)
├── LemmaTrackerAgent   (rastreia dependencias)
└── CrossRefAgent       (compara com fontes externas)
```

---

## 4. Fluxo de Orquestracao — ReasoningOrchestrator v10.0

```
PROBLEMA RECEBIDO
    │
    ├── [R01-R05] Fase FUNDACIONAL
    │   ├── NotationAgent: Define S_n, notacao
    │   ├── AbstractionAgent: Estrutura subjacente? Anti-diagonais?
    │   └── DecompositionAgent: Divide em necessidade + suficiencia
    │
    ├── [R12-R16] Fase INDUTIVA/REDUTIVA ← NOVA
    │   ├── InductorAgent: Admite reducao n→n-1?
    │   ├── InvariantAgent: O que se preserva? (k?)
    │   └── BaseCaseAgent: n=3, enumere TODAS as configs
    │
    ├── [R06-R11] Fase DEDUTIVA
    │   ├── LemmaTracker: Constroi LemmaGraph
    │   ├── SilogisticAgent: Encadeia implicacoes
    │   └── BackwardChain: Do teorema aos lemas
    │
    ├── [R17-R21] Fase CONSTRUTIVA
    │   ├── ConstructorAgent: Constroi explicitamente
    │   └── StressTestAgent: Testa n=4, k=2...
    │
    ├── [R22-R26] Fase REFUTACIONAL ← NOVA
    │   ├── ContradictionAgent: |p+q|=1 vs m=-2?
    │   ├── CounterexampleAgent: n=4,k=2 cobertura?
    │   └── ConsistencyAgent: Lema 2 vs Lema 4?
    │
    ├── [R27-R30] Fase VERIFICACIONAL
    │   ├── ExhaustiveAgent: n=3,4,5 exaustivo
    │   ├── CrossRefAgent: Evan Chen, DeepMind
    │   └── V1-V6 (Cora-Debate): Consistencia algebrica
    │
    └── [R31-R34] Fase META-COGNITIVA ← NOVA
        ├── LemmaTracker: Propaga falhas no grafo
        ├── ProofHealthAgent: PCI (Proof Confidence Index)
        └── Se PCI < 60: revisao obrigatoria
```

---

## 5. Referencias Completas

[1] Lakatos, I. (1976). *Proofs and Refutations: The Logic of Mathematical Discovery*. Cambridge University Press. ISBN: 978-0521290388. DOI: 10.1017/CBO9781139171472.

[2] Polya, G. (1945). *How to Solve It: A New Aspect of Mathematical Method*. Princeton University Press. ISBN: 978-0691119663.

[3] Knuth, D. E. (1992). Two Notes on Notation. *The American Mathematical Monthly*, 99(5), 403-422. DOI: 10.1080/00029890.1992.11995869. arXiv: math/9205211.

[4] Tao, T. (2006). *Solving Mathematical Problems: A Personal Perspective*. Oxford University Press. ISBN: 978-0199205608.

[5] Engel, A. (1998). *Problem-Solving Strategies*. Springer. DOI: 10.1007/b97682. ISBN: 978-0387982199.

[6] Aristoteles (~350 a.C.). *Organon* (Prior Analytics, Book I). Traducao: Jenkinson, A. J. Disponivel: classics.mit.edu.

[7] Gentzen, G. (1935). Untersuchungen uber das logische Schliessen. *Mathematische Zeitschrift*, 39, 176-210, 405-431. Traducao: Szabo, M. E. (1969). *The Collected Papers of Gerhard Gentzen*. North-Holland.

[8] Prawitz, D. (1965). *Natural Deduction: A Proof-Theoretical Study*. Almqvist & Wiksell. Reimpressao: Dover (2006). ISBN: 978-0486446554.

[9] Frege, G. (1879). *Begriffsschrift: eine der arithmetischen nachgebildete Formelsprache des reinen Denkens*. Halle. Traducao: van Heijenoort, J. (1967). *From Frege to Godel*. Harvard.

[10] Wiles, A. (1995). Modular Elliptic Curves and Fermat's Last Theorem. *Annals of Mathematics*, 141(3), 443-551. DOI: 10.2307/2118559.

[11] Peano, G. (1889). *Arithmetices Principia: Nova Methodo Exposita*. Fratres Bocca. Traducao: Kennedy, H. C. (1973). *Selected Works of Giuseppe Peano*. University of Toronto Press.

[12] Burstall, R. M. (1969). Proving Properties of Programs by Structural Induction. *The Computer Journal*, 12(1), 41-48. DOI: 10.1093/comjnl/12.1.41.

[13] Dijkstra, E. W. (1976). *A Discipline of Programming*. Prentice-Hall. ISBN: 978-0132158718.

[14] Hoare, C. A. R. (1969). An Axiomatic Basis for Computer Programming. *Communications of the ACM*, 12(10), 576-580. DOI: 10.1145/363235.363259.

[15] Graham, R. L.; Knuth, D. E.; Patashnik, O. (1994). *Concrete Mathematics: A Foundation for Computer Science*. 2. ed. Addison-Wesley. ISBN: 978-0201558029.

[16] Bishop, E. (1967). *Foundations of Constructive Analysis*. McGraw-Hill. Reimpressao: Ishi Press (2012). ISBN: 978-4871877145.

[17] Knuth, D. E. (1968). *The Art of Computer Programming, Vol. 1: Fundamental Algorithms*. Addison-Wesley. ISBN: 978-0201896831.

[18] Brualdi, R. A. (2010). *Introductory Combinatorics*. 5. ed. Pearson. ISBN: 978-0136020400.

[19] Erdos, P. (1947). Some Remarks on the Theory of Graphs. *Bulletin of the American Mathematical Society*, 53, 292-294. DOI: 10.1090/S0002-9904-1947-08785-1.

[20] Papadimitriou, C. H.; Steiglitz, K. (1982). *Combinatorial Optimization: Algorithms and Complexity*. Prentice-Hall. Reimpressao: Dover (1998). ISBN: 978-0486402581.

[21] Euclides (~300 a.C.). *Elementos*, Livro IX, Proposicao 20. Traducao: Heath, T. L. (1908). *The Thirteen Books of Euclid's Elements*. Cambridge University Press.

[22] Rescher, N. (1976). *Plausible Reasoning: An Introduction to the Theory and Practice of Plausibilistic Inference*. Van Gorcum. ISBN: 978-9023213840.

[23] Tarski, A. (1956). On the Concept of Logical Consequence. In: *Logic, Semantics, Metamathematics*. Oxford University Press. Reimpressao: Hackett (1983). ISBN: 978-0915144761.

[24] Dijkstra, E. W. (1970). *Notes on Structured Programming*. T.H. Report 70-WSK-03, Eindhoven. Disponivel: https://www.cs.utexas.edu/~EWD/ewd02xx/EWD249.PDF

[25] Clarke, E. M.; Grumberg, O.; Peled, D. A. (1999). *Model Checking*. MIT Press. ISBN: 978-0262032704.

[26] Zammit, M. et al. (2024). Autoformalization: Challenges and Opportunities. *arXiv preprint*, arXiv:2310.01111.

[27] Meurer, A. et al. (2017). SymPy: symbolic computing in Python. *PeerJ Computer Science*, 3, e103. DOI: 10.7717/peerj-cs.103.

[28] Virtanen, P. et al. (2020). SciPy 1.0: fundamental algorithms for scientific computing in Python. *Nature Methods*, 17(3), 261-272. DOI: 10.1038/s41592-019-0686-2.

[29] de Bruijn, N. G. (1980). A Survey of the Project Automath. In: Seldin, J. P.; Hindley, J. R. (eds.). *To H. B. Curry: Essays on Combinatory Logic, Lambda Calculus and Formalism*. Academic Press.

[30] Guo, C.; Pleiss, G.; Sun, Y.; Weinberger, K. Q. (2017). On Calibration of Modern Neural Networks. *ICML 2017*. arXiv: 1706.04599.

[31] Platt, J. (1999). Probabilistic Outputs for Support Vector Machines. *Advances in Large Margin Classifiers*, 10(3), 61-74.

[32] Liang, T. et al. (2023). Encouraging Divergent Thinking in LLMs through Multi-Agent Debate. *EMNLP 2024*. arXiv: 2305.19118.

[33] Polya, G. (1954). *Mathematics and Plausible Reasoning* (2 vols.). Princeton University Press. ISBN: 978-0691025094.

[34] Kojima, T.; Gu, S. S.; Reid, M.; Matsuo, Y.; Iwasawa, Y. (2022). Large Language Models are Zero-Shot Reasoners. *NeurIPS 2022*. arXiv: 2205.11916.

---

> **Documento mantido por**: OpenCode Ecosystem AutoEvolve v1.0
> **Proxima acao**: Implementar ReasoningOrchestrator v10.0 com os 10 novos agentes
> **Roadmap**: Fase 1 (R13,R15,R22,R24,R27,R31) — criticos para provas matematicas
