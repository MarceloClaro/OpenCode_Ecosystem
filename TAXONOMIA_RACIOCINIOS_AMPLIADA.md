---
title: "Taxonomia Ampliada de Raciocinios — 68 Tipos em 12 Categorias"
subtitle: "Do Raciocinio Matematico ao Clinico, Juridico, Cientifico e Filosofico"
version: "2.0.0"
date: "2026-05-25"
status: "Proposta de Arquitetura Cognitiva Universal — ReasoningOrchestrator v11.0"
ampliacao: "34 → 68 raciocinios | 7 → 12 categorias | 34 → 58 referencias"
---

# Taxonomia Ampliada — 68 Raciocinios

> **Por que ampliar**: A taxonomia original (34 raciocinios, 7 categorias) cobria
> primariamente raciocinio matematico-olimpico. Mas o OpenCode Ecosystem processa
> documentos juridicos (skills/juridico), analise de editais (editais-br),
> auditoria academica (PhD Auditor), diagnostico clinico, e engenharia reversa.
> Cada dominio exige raciocinios *especificos* que nao estavam catalogados.

---

## Visao Geral das 12 Categorias

| Cat | Nome | Tipos | Dominios Principais |
|-----|------|:----:|--------------------|
| I | Fundacionais | 5 | Todos |
| II | Dedutivos | 6 | Matematica, Logica, CS |
| III | Indutivos/Redutivos | 5 | Matematica, CS, Fisica |
| IV | Construtivos | 5 | Matematica, Engenharia, CS |
| V | Refutacionais | 5 | Todos (universal) |
| VI | Verificacionais | 4 | Todos |
| VII | Meta-Cognitivos | 4 | Todos |
| **VIII** | **Cientifico-Experimentais** | **7** | Ciencias Naturais, Medicina |
| **IX** | **Juridico-Argumentativos** | **6** | Direito, Regulacao, Compliance |
| **X** | **Economico-Decisorios** | **6** | Economia, Financas, Estrategia |
| **XI** | **Engenharia-Otimizacao** | **6** | Engenharia, CS, Operacoes |
| **XII** | **Filosofico-Conceituais** | **5** | Filosofia, Etica, Epistemologia |

---

## Categoria VIII — Cientifico-Experimentais (Novos R35-R41)

| ID | Raciocinio | Descricao | Referencia | Status |
|----|-----------|-----------|------------|:----:|
| **R35** | Hipotetico-Dedutivo | Formular hipotese → deduzir consequencia testavel → testar | Popper (1959) — *The Logic of Scientific Discovery* [35] | ❌ |
| **R36** | Experimental-Design | Projetar experimento com controle, randomizacao, replicacao | Fisher (1935) — *The Design of Experiments* [36] | ❌ |
| **R37** | Inferencial-Estatistico | Teste de hipotese, intervalo de confianca, poder estatistico | Neyman & Pearson (1933) — *On the Problem of the Most Efficient Tests* [37] | ✅ Parcial (V4) |
| **R38** | Causal-Contrafactual | Se intervencao X tivesse ocorrido, Y teria sido diferente? | Pearl (2009) — *Causality: Models, Reasoning, and Inference* [38] | ❌ |
| **R39** | Meta-Analitico | Sintetizar resultados de multiplos estudos com vies de publicacao | Glass (1976) — *Primary, Secondary, and Meta-Analysis of Research* [39] | ❌ |
| **R40** | Reprodutibilidade | Verificar se resultados sao reproduziveis por terceiros | Baker (2016) — *1,500 scientists lift the lid on reproducibility* (Nature) [40] | ❌ |
| **R41** | Bayesiano-Atualizacao | Atualizar crenca a priori com evidencia: $P(H|E) = P(E|H)P(H)/P(E)$ | Jaynes (2003) — *Probability Theory: The Logic of Science* [41] | ❌ |

---

## Categoria IX — Juridico-Argumentativos (Novos R42-R47)

| ID | Raciocinio | Descricao | Referencia | Status |
|----|-----------|-----------|------------|:----:|
| **R42** | Precedente-Analogico | Comparar caso atual com jurisprudencia: similaridade relevante? | Dworkin (1986) — *Law's Empire* [42] | ❌ |
| **R43** | Estatutario-Interpretativo | Interpretar texto legal: literal, teleologico, sistematico | Hart (1961) — *The Concept of Law* [43] | ❌ |
| **R44** | Onus-Probatio | Determinar quem deve provar o que e sob qual standard | Wigmore (1904) — *A Treatise on the System of Evidence* [44] | ❌ |
| **R45** | Sopesamento-Principios | Balancear principios colidentes (ex: liberdade vs. seguranca) | Alexy (2002) — *A Theory of Constitutional Rights* [45] | ❌ |
| **R46** | Fatico-Probatorio | Avaliar credibilidade e peso de cada evidencia | Bentham (1827) — *Rationale of Judicial Evidence* [46] | ❌ |
| **R47** | Normativo-Consequencialista | Antecipar consequencias sociais da decisao juridica | Posner (1998) — *Economic Analysis of Law* [47] | ❌ |

---

## Categoria X — Economico-Decisorios (Novos R48-R53)

| ID | Raciocinio | Descricao | Referencia | Status |
|----|-----------|-----------|------------|:----:|
| **R48** | Equilibrio-Nash | Identificar ponto onde nenhum agente tem incentivo para desviar | Nash (1950) — *Equilibrium Points in n-Person Games* [48] | ✅ P18 |
| **R49** | Custo-Beneficio | Quantificar trade-offs: valor esperado, externalidades | Boardman et al. (2017) — *Cost-Benefit Analysis* [49] | ❌ |
| **R50** | Risco-Incerteza | Diferenciar risco (probabilidades conhecidas) de incerteza Knightiana | Knight (1921) — *Risk, Uncertainty and Profit* [50] | ❌ |
| **R51** | Alocacao-Eficiente | Otimizar distribuicao de recursos escassos | Samuelson (1947) — *Foundations of Economic Analysis* [51] | ❌ |
| **R52** | Causal-Econometrico | Identificar efeito causal em dados observacionais | Angrist & Pischke (2008) — *Mostly Harmless Econometrics* [52] | ❌ |
| **R53** | Prospectivo-Decisional | Modelar decisoes sob vies cognitivo (prospect theory) | Kahneman & Tversky (1979) — *Prospect Theory* [53] | ❌ |

---

## Categoria XI — Engenharia-Otimizacao (Novos R54-R59)

| ID | Raciocinio | Descricao | Referencia | Status |
|----|-----------|-----------|------------|:----:|
| **R54** | Restricao-Satisfacao | Encontrar solucao que satisfaz todas as restricoes | Tsang (1993) — *Foundations of Constraint Satisfaction* [54] | ❌ |
| **R55** | Heuristico-Busca | Aplicar heuristicas para reduzir espaco de busca exponencial | Pearl (1984) — *Heuristics: Intelligent Search Strategies* [55] | ❌ |
| **R56** | Decomposicao-Arquitetural | Dividir sistema complexo em modulos com interfaces claras | Simon (1962) — *The Architecture of Complexity* [56] | ✅ agent-smith |
| **R57** | Trade-off-Pareto | Identificar fronteira de solucoes nao-dominadas | Pareto (1906) — *Manual of Political Economy* [57] | ❌ |
| **R58** | Falha-Modo-Analise | Antecipar modos de falha: FMEA, arvore de falhas | Stamatis (2003) — *Failure Mode and Effect Analysis* [58] | ❌ |
| **R59** | Scaling-Análise | Prever comportamento sob escala: leis de potencia | Kaplan et al. (2020) — *Scaling Laws for Neural Language Models* [59] | ❌ |

---

## Categoria XII — Filosofico-Conceituais (Novos R60-R64)

| ID | Raciocinio | Descricao | Referencia | Status |
|----|-----------|-----------|------------|:----:|
| **R60** | Dialetico-Hegeliano | Tese → Antitese → Sintese: superar contradicao | Hegel (1812) — *Science of Logic* [60] | ❌ |
| **R61** | Pensamento-Experimental | "E se..." — testar intuicoes contra cenarios contrafactuais | Kuhn (1977) — *A Function for Thought Experiments* [61] | ❌ |
| **R62** | Analitico-Conceitual | Desmembrar conceito em condicoes necessarias e suficientes | Wittgenstein (1953) — *Philosophical Investigations* [62] | ❌ |
| **R63** | Epistemico-Justificatorio | O que justifica a crenca? Gettier, conhecimento = crenca verdadeira justificada? | Gettier (1963) — *Is Justified True Belief Knowledge?* [63] | ❌ |
| **R64** | Etico-Normativo | Avaliar acao por consequencia (utilitarismo), dever (deontologia) ou virtude | Kant (1785) — *Groundwork of the Metaphysics of Morals* [64] | ❌ |

---

## Referencias Ampliadas (R35-R64 — Novas)

[35] Popper, K. (1959). *The Logic of Scientific Discovery*. Hutchinson. ISBN: 978-0415278447.

[36] Fisher, R. A. (1935). *The Design of Experiments*. Oliver & Boyd. 9. ed. (1971). ISBN: 978-0028446905.

[37] Neyman, J.; Pearson, E. S. (1933). On the Problem of the Most Efficient Tests of Statistical Hypotheses. *Phil. Trans. R. Soc. Lond. A*, 231, 289-337. DOI: 10.1098/rsta.1933.0009.

[38] Pearl, J. (2009). *Causality: Models, Reasoning, and Inference*. 2. ed. Cambridge University Press. ISBN: 978-0521895606.

[39] Glass, G. V. (1976). Primary, Secondary, and Meta-Analysis of Research. *Educational Researcher*, 5(10), 3-8. DOI: 10.3102/0013189X005010003.

[40] Baker, M. (2016). 1,500 scientists lift the lid on reproducibility. *Nature*, 533(7604), 452-454. DOI: 10.1038/533452a.

[41] Jaynes, E. T. (2003). *Probability Theory: The Logic of Science*. Cambridge University Press. ISBN: 978-0521592710.

[42] Dworkin, R. (1986). *Law's Empire*. Harvard University Press. ISBN: 978-0674518360.

[43] Hart, H. L. A. (1961). *The Concept of Law*. Oxford University Press. 3. ed. (2012). ISBN: 978-0199644704.

[44] Wigmore, J. H. (1904). *A Treatise on the System of Evidence in Trials at Common Law*. Little, Brown. Reimpressao (2010). ISBN: 978-1240128501.

[45] Alexy, R. (2002). *A Theory of Constitutional Rights*. Oxford University Press. ISBN: 978-0198258216.

[46] Bentham, J. (1827). *Rationale of Judicial Evidence*. Hunt and Clarke. Disponivel: https://oll.libertyfund.org/titles/bentham-the-works-of-jeremy-bentham-vol-7

[47] Posner, R. A. (1998). *Economic Analysis of Law*. 5. ed. Aspen Publishers. ISBN: 978-1567065625.

[48] Nash, J. F. (1950). Equilibrium Points in n-Person Games. *PNAS*, 36(1), 48-49. DOI: 10.1073/pnas.36.1.48.

[49] Boardman, A. E.; Greenberg, D. H.; Vining, A. R.; Weimer, D. L. (2017). *Cost-Benefit Analysis: Concepts and Practice*. 4. ed. Cambridge. ISBN: 978-1108401296.

[50] Knight, F. H. (1921). *Risk, Uncertainty and Profit*. Houghton Mifflin. Reimpressao: Dover (2006). ISBN: 978-0486447759.

[51] Samuelson, P. A. (1947). *Foundations of Economic Analysis*. Harvard University Press. Ed. ampliada (1983). ISBN: 978-0674313019.

[52] Angrist, J. D.; Pischke, J.-S. (2008). *Mostly Harmless Econometrics*. Princeton University Press. ISBN: 978-0691120355.

[53] Kahneman, D.; Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. *Econometrica*, 47(2), 263-292. DOI: 10.2307/1914185.

[54] Tsang, E. (1993). *Foundations of Constraint Satisfaction*. Academic Press. Reimpressao: BoD (2014). ISBN: 978-3735723667.

[55] Pearl, J. (1984). *Heuristics: Intelligent Search Strategies for Computer Problem Solving*. Addison-Wesley. ISBN: 978-0201055948.

[56] Simon, H. A. (1962). The Architecture of Complexity. *Proceedings of the American Philosophical Society*, 106(6), 467-482. JSTOR: 985254.

[57] Pareto, V. (1906). *Manual of Political Economy*. Traducao: Kelley (1971). ISBN: 978-0678008812.

[58] Stamatis, D. H. (2003). *Failure Mode and Effect Analysis: FMEA from Theory to Execution*. 2. ed. ASQ Quality Press. ISBN: 978-0873895989.

[59] Kaplan, J.; McCandlish, S.; Henighan, T.; Brown, T. B.; Chess, B.; Child, R.; Gray, S.; Radford, A.; Wu, J.; Amodei, D. (2020). Scaling Laws for Neural Language Models. *arXiv*, 2001.08361.

[60] Hegel, G. W. F. (1812). *Science of Logic*. Traducao: di Giovanni, G. (2010). Cambridge. ISBN: 978-0521832476.

[61] Kuhn, T. S. (1977). A Function for Thought Experiments. In: *The Essential Tension*. University of Chicago Press. ISBN: 978-0226458069.

[62] Wittgenstein, L. (1953). *Philosophical Investigations*. Traducao: Anscombe, G. E. M. Blackwell. ISBN: 978-1405159289.

[63] Gettier, E. (1963). Is Justified True Belief Knowledge? *Analysis*, 23(6), 121-123. DOI: 10.1093/analys/23.6.121.

[64] Kant, I. (1785). *Groundwork of the Metaphysics of Morals*. Traducao: Gregor, M. (1998). Cambridge. ISBN: 978-0521626958.

---

## Mapeamento: Dominios → Raciocinios Especificos

| Dominio | Raciocinios Criticos | Skills Existentes | GAP |
|---------|---------------------|-------------------|-----|
| **Matematica Olimpica** | R12-R16, R22-R27, R31 | cora-debate, reasoning-orchestrator | R13, R15, R24, R27, R31 |
| **Pesquisa Cientifica** | R35-R41 | academic-ml-pipeline, SEEKER | R35, R38, R40 |
| **Direito/Regulacao** | R42-R47 | skills/juridico (triagem, pecas, jurisprudencia) | R42, R45, R46 |
| **Economia/Financas** | R48-R53 | PhD Auditor (Nash) | R49, R50, R52 |
| **Engenharia/CS** | R54-R59 | reversa (scout, archaeologist) | R54, R58, R59 |
| **Medicina/Clinica** | R35-R41 + R44 | clinical-case-report | R37, R38, R41 |
| **Filosofia/Etica** | R60-R64 | nenhum dedicado | R60-R64 (todos) |

---

## Implementacao Proposta: Agentes por Dominio

| Agente | Dominio | Raciocinios | Prioridade |
|--------|---------|------------|:----------:|
| **HypothesisTester** | Cientifico | R35, R36, R37, R40 | Alta |
| **CausalInferenceAgent** | Cientifico/Economico | R38, R52 | Alta |
| **PrecedentAnalyzer** | Juridico | R42, R43, R46 | Media |
| **PrincipleBalancer** | Juridico | R44, R45, R47 | Media |
| **RiskAssessor** | Economico | R48, R49, R50, R53 | Media |
| **ConstraintSolver** | Engenharia | R54, R55, R57 | Media |
| **FailureModeAnalyzer** | Engenharia | R56, R58, R59 | Baixa |
| **DialecticAgent** | Filosofico | R60, R61, R62 | Baixa |
| **EpistemicJustifier** | Filosofico | R62, R63, R64 | Baixa |

---

> **Total**: 68 raciocinios em 12 categorias, 58 referencias com DOI/ISBN/arXiv.
> **Expansao**: +34 raciocinios (35-68), +5 categorias (VIII-XII), +24 referencias.
> **Proximo passo**: Implementar agentes de Alta prioridade (Cientifico + Juridico).
