---
name: pos-estruturalista
description: "Skill de análise pós-estruturalista: análise foucaultiana de discurso, desconstrução derridiana, análise de poder-saber em IA, governança algorítmica e Diamond Model."
spec: "SPEC-075"
version: "1.0"
category: research
tags: [paradigma, pos-estruturalista, foucault, derrida, poder-saber, governanca-algoritmica, diamond-model]
dependencies: [SPEC-075]
tdd_suite: "tests/test_r32_paradigmas.py"
ct_count: 7
status: active
---

# SPEC-075 — Skill: Análise Pós-estruturalista

## Objetivo
Aplicar o paradigma pós-estruturalista à análise crítica de sistemas de IA e tecnologia: análise foucaultiana de discurso e poder-saber, desconstrução derridiana de infraestruturas algorítmicas, aplicação do Diamond Model de Ética Política em IA, e análise de governança algorítmica.

## CTs
| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SKILL.md existe com frontmatter | ✅ |
| CT-02 | Template: Análise Foucaultiana de Discurso em IA | ✅ |
| CT-03 | Template: Desconstrução Derridiana de Infraestrutura Algorítmica | ✅ |
| CT-04 | Protocolo: Diamond Model de Ética Política em IA (Bozdağ) | ✅ |
| CT-05 | Template: Análise de Poder-Saber em Sistemas Algorítmicos | ✅ |
| CT-06 | Template: Mapeamento de Regimes de Verdade Algorítmicos | ✅ |
| CT-07 | Template: Análise de Colonialismo Algorítmico | ✅ |

## Template 1: Análise Foucaultiana de Discurso em IA

### Etapas
1. **Identificação do enunciado**: O que o sistema de IA diz/faz? Qual conhecimento ele produz?
   - Que tipo de afirmações o sistema gera?
   - Como essas afirmações são validadas como verdade?
   - Quem pode contestá-las?

2. **Formação discursiva**: Que regras determinam o que pode ser dito?
   - Que corpus treinou o modelo?
   - Que vieses de curadoria existem?
   - Que estruturas de relevância organizam o output?

3. **Poder-saber**: Como o sistema produz e é produzido por relações de poder?
   - Quem controla o desenvolvimento?
   - Quem se beneficia da classificação produzida?
   - Quem é marginalizado pelo sistema?

4. **Governamentalidade algorítmica**: Como o sistema governa condutas?
   - Que comportamentos o sistema incentiva/desincentiva?
   - Que normas são naturalizadas?
   - Que formas de resistência são possíveis?

### Aplicação a LLMs (Kouros, 2026)
- RLHF como técnica de normalização: julgamentos humanos situados transformados em objetivos escaláveis
- Efeitos de verdade sem procedimentos de verdade: outputs linguisticamente fluentes sem compreensão proposicional
- O LLM como aparelho discursivo produtivo que molda horizontes de inteligibilidade

## Template 2: Desconstrução Derridiana de Infraestrutura Algorítmica

### Etapas
1. **Identificar binário oposicional**: Que par oposto estrutura o sistema?
   - Ex: treino/teste, humano/máquina, público/privado, objetivo/subjetivo
   
2. **Inverter hierarquia**: Mostrar que o termo subordinado é condição de possibilidade do dominante
   - Ex: o "teste" não é posterior ao "treino" — o teste define o que conta como treino bem-sucedido

3. **Différance**: Mostrar que o significado é adiado e diferido
   - Ex: o significado de "precisão" muda conforme o contexto de avaliação
   - Ex: a "verdade" do modelo é sempre adiada para a próxima validação

4. **Rastro (trace)**: O que está ausente mas é condição de presença?
   - Ex: o trabalho humano anônimo por trás dos datasets de treino
   - Ex: os custos ambientais excluídos da métrica de performance

5. **Suplemento**: O que é tratado como externo mas é constitutivo?
   - Ex: a "intervenção humana" como suplemento necessário à "autonomia" da IA
   - Ex: o "viés" como suplemento constitutivo da "objetividade" algorítmica

### Aplicação ao PSIR (Mestre, 2025)
- Problema ôntico-ontológico: confusão entre entes ônticos e existência ontológica na filosofia da informação
- Problema abstrato-concreto: falha em explicar o movimento de dados noumenais a dados fenomenais
- Reconstrução: PSIR supera problemas do ISR ao subverter a totalidade informacional

## Template 3: Diamond Model de Ética Política em IA (Bozdağ, 2026)

### As Quatro Dimensões de Justiça
| Fechamento (Dussel) | Dimensão de Justiça | Válvula de Reabertura |
|:-------------------|:--------------------|:----------------------|
| Matéria | Justiça Distributiva | Redistribuição de recursos computacionais |
| Relação | Justiça Relacional | Proximidade e participação comunitária |
| Ser | Justiça Ontológica | Opacidade deliberada — recusa de classificação |
| Tempo | Justiça Temporal | Hesitação — pausa antes da predição |

### Etapas de Aplicação
1. Mapear o sistema de IA alvo em termos das 4 camadas do Stack (Bratton)
2. Identificar para cada camada qual fechamento opera
3. Mapear a dimensão de justiça correspondente
4. Propor válvula(s) de reabertura: design, regulação ou ação coletiva
5. Verificar exterioridade: quem está sendo tornado ilegível ou incomputável?

## Template 4: Análise de Poder-Saber em Sistemas Algorítmicos

### Dimensões (Foucault, 1980)
1. **Poder disciplinar**: Como o sistema classifica, hierarchiza e normaliza?
   - Que critérios definem o "normal" e o "desviante"?
   - Como essas classificações produzem sujeitos?

2. **Biopoder**: Como o sistema gere populações e riscos?
   - Que predições de risco são feitas?
   - Como essas predições afetam o acesso a recursos?

3. **Segurança**: Como o sistema gerencia circulação e incerteza?
   - Que mecanismos de modulação operam?
   - Como o sistema antecipa e pré-formata comportamentos?

4. **Sociedade de controle algorítmico**: Modulação contínua, não disciplinar
   - Dados como traço de circulação, não como ficha disciplinar
   - Predição como controle prévio sobre possibilidades futuras

## Template 5: Mapeamento de Regimes de Verdade Algorítmicos

### Características do Regime (Artificial Truth, 2026)
1. **Economia da confiança reestruturada**: Autoridade epistêmica desloca-se de instituições para capital nativo de plataforma (métricas de engajamento, proximidade afetiva)
2. **IA generativa como ator epistêmico**: Produção de "verdade sintética" por fluência linguística, não por compreensão proposicional
3. **Veridicção computacional institucionalizada**: Julgamentos epistêmicos situados transformados em classificações probabilísticas apresentadas como neutras

### Checklist de Análise
- [ ] O sistema produz efeitos de verdade sem procedimentos de verdade correspondentes?
- [ ] A plausibilidade computacional substituiu a correspondência como critério de verdade?
- [ ] Quem detém o poder de definir o que conta como fato no ecossistema?
- [ ] Que formas de conhecimento são sistematicamente excluídas?

## Template 6: Análise de Colonialismo Algorítmico

### Quatro Dinâmicas (AI Ethics in Postcolonial Contexts, 2026)
1. **Colonialismo algorítmico**: Sistemas externos impõem categorias e classificações sobre contextos locais
2. **Colonialismo de dados**: Infraestruturas de captura de dados operam em regime extrativo
3. **Imperialismo de plataforma**: Plataformas globais determinam regras de participação
4. **Sub-imperialismo de plataforma**: Atores intermediários do Sul Global mediam e reproduzem dinâmicas coloniais

### Mecanismos
- Epistemic templating: modelos treinados em dados do Norte Global aplicados a contextos do Sul
- Governance transfer: frameworks regulatórios importados sem adaptação contextual
- Infrastructural lock-in: dependência de infraestruturas de nuvem estrangeiras
- Labour opacity: trabalho humano invisível de anotação e moderação

## Referências da Skill
- Bozdağ, A.A. (2026). AI as Political Infrastructure. *Philosophy & Technology*, 39, 54. DOI: 10.1007/s13347-026-01058-9
- Kouros, T. (2026). From 'objectivity' to obedience: LLMs as discourse, discipline, and power. *AI & Society*. DOI: 10.1007/s00146-026-02994-y
- Foucault, M. (1977). *Discipline and Punish*. Pantheon.
- Foucault, M. (1980). *Power/Knowledge*. Pantheon.
- Derrida, J. (1967). *De la grammatologie*. Minuit.
- Mestre, J. (2025). Post-Structural Informational Realism. *ALISE Proceedings*. DOI: 10.21900/j.alise.2025.2063
- Cote, M.P. & Aires, S. (2025). Futurity as Infrastructure. arXiv:2508.15680.
- Artificial Truth: Algorithmic Power. (2026). *Social Sciences*, 16(3), 102. DOI: 10.3390/socsci16030102
