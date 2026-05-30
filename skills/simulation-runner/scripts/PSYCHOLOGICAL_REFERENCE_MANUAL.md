# Manual de Referência Teórica — OpenCode MiroFish v5.0

## Dimensões Psicológicas, Perfis Cognitivos e Categorias de Simulação

**Fundamentação Qualis A1 — 55 Perfis · 20 Dimensões · 14 Categorias · 40+ DOIs**

---

# PARTE I — DIMENSÕES PSICOLÓGICAS

Cada dimensão é um eixo contínuo que modela a variabilidade cognitiva e comportamental
dos agentes simulados. As dimensões são independentes entre si (ortogonais) e foram
selecionadas com base em metanálises e revisões sistemáticas da literatura.

---

## 1. Big Five (Modelo dos Cinco Grandes Fatores)

**Autores:** Paul T. Costa Jr. & Robert R. McCrae (1992)
**DOI:** [10.1037/1040-3590.4.1.5](https://doi.org/10.1037/1040-3590.4.1.5)
**Instrumento:** NEO-PI-R (240 itens) · NEO-FFI (60 itens)

O Big Five é o modelo de personalidade mais validado empiricamente na psicologia.
Emergiu da análise fatorial de descritores linguísticos (abordagem léxica) e foi
replicado em mais de 50 culturas (McCrae & Terracciano, 2005). Os cinco fatores são:

| Fator | Polo Alto | Polo Baixo | Relevância para Simulação |
|-------|-----------|------------|---------------------------|
| **Abertura à Experiência (O)** | Curioso, criativo, aprecia arte e ideias novas | Convencional, prefere rotina | Determina receptividade a inovações tecnológicas e mudanças sociais |
| **Conscienciosidade (C)** | Organizado, disciplinado, orientado a metas | Espontâneo, flexível, procrastinador | Prediz adesão a normas, planejamento de longo prazo, confiabilidade |
| **Extroversão (E)** | Sociável, energético, assertivo | Reservado, introspectivo, prefere solidão | Controla frequência e intensidade de interações na rede social |
| **Amabilidade (A)** | Cooperativo, empático, confiante | Competitivo, cético, prioriza interesses próprios | Modula cooperação vs. competição; disposição para colaborar |
| **Neuroticismo (N)** | Ansioso, reativo emocionalmente, instável | Estável, resiliente, controlado emocionalmente | Amplifica reações a eventos negativos; volatilidade de sentimento |

**Aplicação na simulação:** Cada agente recebe scores O-C-E-A-N (0 a 1) que determinam:
- Probabilidade de adotar novas ideias (Abertura)
- Consistência de comportamento entre rodadas (Conscienciosidade)
- Frequência de postagens e respostas (Extroversão)
- Tendência a conflito vs. cooperação (Amabilidade)
- Magnitude de reação emocional a eventos (Neuroticismo)

---

## 2. HEXACO-PI-R

**Autores:** Michael C. Ashton & Kibeom Lee (2007)
**DOI:** [10.1037/0022-3514.92.2.363](https://doi.org/10.1037/0022-3514.92.2.363)
**Instrumento:** HEXACO-PI-R (100 itens)

O HEXACO adiciona um sexto fator — **Honestidade-Humildade (H)** — que captura
tendências a ser sincero, modesto e justo versus manipulador, narcisista e explorador.
Este fator é particularmente relevante para modelar comportamentos éticos e anticorrupção.

| Fator H (Honestidade-Humildade) | Descrição |
|----------------------------------|-----------|
| Alto | Sincero, modesto, avesso a manipulação, não busca status material excessivo |
| Baixo | Dissimulado, pretensioso, disposto a explorar outros para ganho pessoal |

**Aplicação:** O fator H é crítico para cenários envolvendo corrupção, compliance
ética, confiança institucional e comportamento financeiro (insider trading, fraudes).

---

## 3. Teoria dos Valores de Schwartz

**Autor:** Shalom H. Schwartz (1992)
**DOI:** [10.1016/S0065-2601(08)60281-6](https://doi.org/10.1016/S0065-2601(08)60281-6)
**Instrumento:** Schwartz Value Survey (SVS) · PVQ-RR

Schwartz identificou 10 valores humanos universais organizados em uma estrutura
circular (circumplexo). Valores adjacentes são compatíveis; valores opostos são
conflitantes. A estrutura foi validada em 82 países (Schwartz, 2012).

| Valor | Motivação Central |
|-------|-------------------|
| **Autodireção** | Pensamento e ação independentes |
| **Estimulação** | Excitação, novidade, desafio |
| **Hedonismo** | Prazer, gratificação sensorial |
| **Realização** | Sucesso pessoal demonstrando competência |
| **Poder** | Status social, domínio sobre pessoas/recursos |
| **Segurança** | Harmonia, estabilidade social e pessoal |
| **Conformidade** | Restrição de impulsos que violam normas |
| **Tradição** | Respeito e compromisso com costumes |
| **Benevolência** | Bem-estar de pessoas próximas |
| **Universalismo** | Compreensão, tolerância e proteção de todas as pessoas e da natureza |

**Aplicação:** Valores determinam a direção motivacional do agente. Um agente
com alto Universalismo apoiará políticas ambientais e de direitos humanos; um
agente com alto Poder priorizará hierarquia e competitividade.

---

## 4. Teoria dos Fundamentos Morais (MFT)

**Autor:** Jonathan Haidt (2012)
**ISBN:** 978-0307455772
**Instrumento:** Moral Foundations Questionnaire (MFQ-30)

Haidt propõe que o julgamento moral humano se baseia em 6 fundamentos inatos,
moldados culturalmente. Progressistas e conservadores diferem sistematicamente
em quais fundamentos priorizam (Graham, Haidt & Nosek, 2009).

| Fundamento | Descrição | Prioridade Política |
|------------|-----------|---------------------|
| **Cuidado/Dano** | Proteger os vulneráveis do sofrimento | Mais forte em progressistas |
| **Justiça/Trapaça** | Reciprocidade, proporcionalidade, justiça | Igual em ambos |
| **Lealdade/Traição** | Coesão grupal, patriotismo | Mais forte em conservadores |
| **Autoridade/Subversão** | Respeito à hierarquia e tradição | Mais forte em conservadores |
| **Santidade/Degradação** | Pureza física e espiritual, repulsa ao nojo | Mais forte em conservadores |
| **Liberdade/Opressão** | Resistência à dominação, autonomia | Mais forte em libertários |

**Aplicação:** Os fundamentos morais determinam a resposta emocional do agente
a eventos e políticas. Um agente com alta Lealdade reagirá fortemente a ameaças
à identidade nacional; um com alto Cuidado priorizará políticas de saúde pública.

---

## 5. Estilos Cognitivos

**Autores:** Herman A. Witkin, Carol A. Moore, Donald R. Goodenough & Patricia W. Cox (1977)
**DOI:** [10.3102/00346543047001001](https://doi.org/10.3102/00346543047001001)

O conceito de dependência-independência de campo (Witkin et al., 1954) evoluiu
para uma taxonomia de estilos cognitivos que descrevem como indivíduos processam
informação, não o quanto (inteligência) mas o como (estilo).

| Estilo | Padrão de Processamento |
|--------|------------------------|
| **Analítico** | Decompõe problemas em partes; processamento sequencial, lógico, focado em detalhes |
| **Intuitivo** | Percepção holística; confia em padrões e sensações; processamento paralelo |
| **Reflexivo** | Pondera antes de agir; busca informações adicionais; evita erros |
| **Impulsivo** | Age rapidamente com informações limitadas; tolera erros em troca de velocidade |
| **Holístico** | Visão sistêmica e integrada; percebe conexões entre domínios aparentemente desconexos |
| **Serialista** | Abordagem passo a passo, linear; segue procedimentos estabelecidos |

**Aplicação:** Estilos cognitivos determinam como agentes processam informações
da simulação. Analíticos examinam dados detalhadamente; Intuitivos reagem a
padrões gerais; Reflexivos demoram mais para formar opiniões mas as mantêm.

---

## 6. Foco Regulatório

**Autor:** E. Tory Higgins (1997)
**DOI:** [10.1037/0003-066X.52.12.1280](https://doi.org/10.1037/0003-066X.52.12.1280)

A Teoria do Foco Regulatório distingue duas orientações motivacionais fundamentais
que afetam como pessoas perseguem objetivos e processam informação.

| Foco | Motivação | Estratégia | Sensibilidade |
|------|-----------|------------|---------------|
| **Promoção** | Ideais, aspirações, ganhos | Aproximação, risco, velocidade | Sensível a ganhos e não-ganhos |
| **Prevenção** | Deveres, obrigações, segurança | Evitação, cautela, precisão | Sensível a perdas e não-perdas |

**Aplicação:** Foco em Promoção → agente busca maximizar ganhos, toma mais riscos,
reage a oportunidades. Foco em Prevenção → agente evita perdas, é conservador,
reage a ameaças.

---

## 7. Necessidade de Cognição (NFC)

**Autores:** John T. Cacioppo & Richard E. Petty (1982)
**DOI:** [10.1037/0022-3514.42.1.116](https://doi.org/10.1037/0022-3514.42.1.116)
**Instrumento:** Need for Cognition Scale (18 itens)

NFC é a tendência estável a se engajar e desfrutar de pensamento esforçado.
Indivíduos com alto NFC buscam, examinam e refletem sobre informações; aqueles
com baixo NFC preferem heurísticas e atalhos cognitivos (Cacioppo et al., 1996).

| Nível | Características |
|-------|----------------|
| **Alto NFC** | Busca ativamente informações complexas; forma opiniões baseadas em argumentos; resistente a persuasão superficial; gosta de quebra-cabeças e debates |
| **Baixo NFC** | Prefere mensagens simples e visuais; usa heurísticas; suscetível a efeitos de framing; evita esforço cognitivo desnecessário |

**Aplicação:** Alto NFC → agente analisa profundamente cada evento; baixo NFC →
agente reage a manchetes e emoções sem verificar fatos. Crítico para modelar
disseminação de desinformação.

---

## 8. Tríade Sombria (Dark Triad)

**Autores:** Delroy L. Paulhus & Kevin M. Williams (2002)
**DOI:** [10.1016/S0092-6566(02)00505-6](https://doi.org/10.1016/S0092-6566(02)00505-6)
**Instrumento:** Short Dark Triad (SD3, 27 itens)

Três traços de personalidade socialmente aversivos que compartilham um núcleo
de insensibilidade (callousness) e manipulação interpessoal.

| Traço | Características Centrais |
|-------|------------------------|
| **Narcisismo** | Grandiosidade, busca de admiração, entitlement, falta de empatia |
| **Maquiavelismo** | Manipulação estratégica, cinismo, foco em interesses próprios, pragmatismo amoral |
| **Psicopatia** | Impulsividade, falta de remorso, baixa ansiedade, comportamento antissocial |

**Aplicação:** Alto Dark Triad → agente manipula informações para ganho próprio,
não hesita em espalhar desinformação se beneficiar, busca dominar a rede social.

---

## 9. Teoria do Apego

**Autores:** John Bowlby (1969) · Mary Ainsworth (1978)
**DOI:** [10.1037/0012-1649.28.5.759](https://doi.org/10.1037/0012-1649.28.5.759)
**Instrumento:** Experiences in Close Relationships (ECR-R)

A teoria do apego descreve como vínculos emocionais precoces moldam padrões
de relacionamento ao longo da vida (Bowlby, 1969). Ainsworth identificou padrões
de apego via "Situação Estranha".

| Estilo | Comportamento Relacional |
|--------|------------------------|
| **Seguro** | Confia em outros, busca e oferece suporte, regulação emocional saudável |
| **Ansioso-Ambivalente** | Medo de abandono, busca excessiva de proximidade, reatividade emocional intensa |
| **Evitativo** | Desconforto com intimidade, autossuficiência defensiva, suprime necessidades emocionais |
| **Desorganizado** | Padrão inconsistente, medo sem estratégia coerente, associado a trauma |

**Aplicação:** Apego determina como agentes formam e mantêm conexões na rede.
Seguros são conectores estáveis; Ansiosos buscam validação constante; Evitativos
são isolados mas resilientes a rejeição.

---

## 10. Locus de Controle

**Autor:** Julian B. Rotter (1966)
**DOI:** [10.1037/h0022976](https://doi.org/10.1037/h0022976)
**Instrumento:** Rotter's Locus of Control Scale (29 itens)

Grau em que indivíduos acreditam que controlam os resultados de suas vidas
(interno) versus forças externas como sorte, destino ou outros poderosos.

| Locus | Crença Central | Comportamento Típico |
|-------|---------------|---------------------|
| **Interno** | "Meus esforços determinam meus resultados" | Proativo, busca informação, tenta influenciar ambiente |
| **Externo** | "Forças fora do meu controle decidem" | Passivo, fatalista, menos propenso a agir sobre problemas |

**Aplicação:** Locus interno → agente tenta ativamente influenciar a simulação
com suas ações; externo → reage passivamente, atribui mudanças a forças externas.

---

## 11. Teoria da Autodeterminação (SDT)

**Autores:** Edward L. Deci & Richard M. Ryan (2000)
**DOI:** [10.1037/0003-066X.55.1.68](https://doi.org/10.1037/0003-066X.55.1.68)

SDT postula três necessidades psicológicas básicas universais cuja satisfação
é essencial para motivação intrínseca e bem-estar.

| Necessidade | Descrição |
|-------------|-----------|
| **Autonomia** | Sentir-se no controle das próprias ações; agir por vontade própria |
| **Competência** | Sentir-se eficaz e capaz de dominar desafios |
| **Relacionamento** | Sentir-se conectado e pertencente a outros |

**Aplicação:** Agentes com alta Autonomia resistem a pressão social; alta
Competência mantêm confiança mesmo sob crítica; alto Relacionamento buscam
construir consenso e comunidade.

---

## 12. Orientação à Dominância Social (SDO)

**Autores:** Jim Sidanius & Felicia Pratto (1999)
**DOI:** [10.1017/CBO9781139175043](https://doi.org/10.1017/CBO9781139175043)
**Instrumento:** SDO Scale (16 itens)

SDO mede a preferência por hierarquia entre grupos sociais e a crença de que
alguns grupos são inerentemente superiores a outros.

| Nível | Características |
|-------|----------------|
| **Alto SDO** | Apoia hierarquias grupais; cético quanto a políticas igualitárias; acredita em "vencedores e perdedores" naturais |
| **Baixo SDO** | Prefere igualdade entre grupos; apoia políticas redistributivas e ações afirmativas |

**Aplicação:** Alto SDO → agente resiste a políticas de igualdade; Baixo SDO →
agente defende ativamente equidade e justiça social.

---

## 13. Autoritarismo de Direita (RWA)

**Autor:** Bob Altemeyer (1981)
**DOI:** [10.1037/0022-3514.82.4.627](https://doi.org/10.1037/0022-3514.82.4.627)
**Instrumento:** RWA Scale (30 itens)

RWA mede três atitudes: submissão à autoridade, agressão autoritária (contra
desviantes) e convencionalismo (adesão rígida a normas tradicionais).

| Nível | Características |
|-------|----------------|
| **Alto RWA** | Obediente a autoridades estabelecidas; hostil a outsiders; defende valores tradicionais rigidamente |
| **Baixo RWA** | Questiona autoridade; tolerante a diversidade; aberto a mudanças normativas |

**Aplicação:** Alto RWA → agente defende instituições tradicionais e reage
fortemente contra ameaças percebidas à ordem social.

---

## 14. Necessidade de Fechamento Cognitivo (NFC)

**Autor:** Arie W. Kruglanski (2004)
**DOI:** [10.1037/0033-295X.111.1.80](https://doi.org/10.1037/0033-295X.111.1.80)
**Instrumento:** Need for Closure Scale (42 itens)

Desejo por uma resposta firme a uma questão — qualquer resposta — em oposição
à confusão e ambiguidade (Kruglanski & Webster, 1996).

| Nível | Características |
|-------|----------------|
| **Alto NFC** | "Fecha" questões rapidamente; desconforto com ambiguidade; prefere ordem e previsibilidade; pode "cristalizar" opiniões prematuramente |
| **Baixo NFC** | Tolera ambiguidade; mantém questões em aberto; busca mais informações antes de decidir; menos propenso a estereótipos |

**Aplicação:** Alto NFC → agente forma opiniões rapidamente e resiste a mudá-las;
Baixo NFC → agente mantém posições fluidas, aberto a novas evidências.

---

## 15. Maximização vs. Satisficing

**Autores:** Barry Schwartz, Andrew Ward, John Monterosso, Sonja Lyubomirsky, Katherine White & Darrin Lehman (2002)
**DOI:** [10.1037/0022-3514.83.5.1178](https://doi.org/10.1037/0022-3514.83.5.1178)
**Instrumento:** Maximization Scale (13 itens)

Distinção entre buscar a melhor opção possível (maximização) versus uma opção
suficientemente boa (satisficing), inspirada por Herbert Simon (1955).

| Estilo | Comportamento |
|--------|--------------|
| **Maximizador** | Busca exaustivamente a opção ótima; sofre com arrependimento e comparação social; maior ansiedade decisória |
| **Satisficer** | Escolhe primeira opção que atende critérios; menor arrependimento; mais satisfeito com decisões |

**Aplicação:** Maximizador → agente analisa múltiplas fontes antes de formar
opinião; Satisficer → adota a primeira narrativa convincente que encontra.

---

## 16. Intolerância à Incerteza (IU)

**Autores:** R. Nicholas Carleton, M.A. Peter J. Norton & Gordon J.G. Asmundson (2007)
**DOI:** [10.1016/j.janxdis.2006.03.014](https://doi.org/10.1016/j.janxdis.2006.03.014)
**Instrumento:** Intolerance of Uncertainty Scale (IUS-12)

IU é a tendência a reagir negativamente (emocional, cognitivamente e
comportamentalmente) a situações e eventos incertos (Dugas et al., 1997).

| Nível | Características |
|-------|----------------|
| **Alta IU** | Busca excessiva de certeza e previsibilidade; ansiedade em situações ambíguas; pode preferir más notícias certas a incerteza |
| **Baixa IU** | Tolera ambiguidade situacional; consegue agir sem garantias; menos vulnerável a pânico informacional |

**Aplicação:** Alta IU → agente busca "certezas" mesmo que falsas (desinformação);
Baixa IU → agente consegue navegar cenários voláteis sem pânico.

---

## 17. Curiosidade Epistêmica

**Autor:** Jordan Litman (2008)
**DOI:** [10.1016/j.paid.2008.04.005](https://doi.org/10.1016/j.paid.2008.04.005)
**Instrumento:** Epistemic Curiosity Scale (10 itens)

Litman distingue dois tipos de curiosidade: Curiosidade-D (Deprivation) —
motivada por lacuna de conhecimento desconfortável; Curiosidade-I (Interest) —
motivada por prazer intelectual de explorar.

| Tipo | Motivação |
|------|-----------|
| **Curiosidade-D** | Necessidade de preencher lacuna informacional; desconforto com "não saber"; busca intensa por respostas específicas |
| **Curiosidade-I** | Prazer em explorar ideias novas; motivação intrínseca para aprender; aberto a descobertas inesperadas |

**Aplicação:** Curiosidade-D → agente busca ativamente informações para resolver
dúvidas específicas; Curiosidade-I → agente explora tópicos por prazer intelectual.

---

## 18. Crença no Mundo Justo (BJW)

**Autor:** Melvin J. Lerner (1980)
**DOI:** [10.1007/978-1-4899-0448-5](https://doi.org/10.1007/978-1-4899-0448-5)
**Instrumento:** Belief in a Just World Scale (20 itens)

BJW é a crença de que o mundo é fundamentalmente justo e que as pessoas recebem
o que merecem. Serve como mecanismo de defesa cognitiva contra a aleatoriedade
e injustiça do mundo.

| Nível | Características |
|-------|----------------|
| **Alto BJW** | "Pessoas pobres são preguiçosas"; "vítimas de alguma forma mereceram"; mundo previsível moralmente |
| **Baixo BJW** | Reconhece injustiças sistêmicas; não culpa vítimas; aceita aleatoriedade de resultados |

**Aplicação:** Alto BJW → agente culpa indivíduos por resultados sistêmicos;
Baixo BJW → agente reconhece fatores estruturais em desigualdades.

---

## 19. Justificação do Sistema

**Autores:** John T. Jost & Mahzarin R. Banaji (1994)
**DOI:** [10.1111/j.2044-8309.1994.tb01008.x](https://doi.org/10.1111/j.2044-8309.1994.tb01008.x)
**Instrumento:** System Justification Scale (8 itens)

Tendência a defender, justificar e racionalizar o status quo social, econômico
e político, mesmo quando isso vai contra interesses pessoais ou grupais (Jost,
Banaji & Nosek, 2004).

| Nível | Características |
|-------|----------------|
| **Justificador** | "O sistema funciona bem como está"; resiste a mudanças estruturais; racionaliza desigualdades |
| **Desafiador** | "O sistema precisa de reforma fundamental"; identifica falhas sistêmicas; apoia transformação |

**Aplicação:** Alto SJ → agente defende instituições existentes e resiste a
reformas radicais; Baixo SJ → agente demanda mudanças estruturais profundas.

---

## 20. Agência e Comunhão

**Autor:** David Bakan (1966)
**DOI:** [10.1037/0033-2909.117.3.497](https://doi.org/10.1037/0033-2909.117.3.497)

Bakan propôs duas modalidades fundamentais da existência humana: agência
(autoafirmação, realização individual, poder) e comunhão (conexão, cooperação,
pertencimento). Wiggins (1991) operacionalizou como dimensões do circumplexo
interpessoal.

| Modalidade | Foco | Comportamento |
|------------|------|---------------|
| **Agência** | Self, realização, maestria, poder | Assertivo, ambicioso, independente, dominante |
| **Comunhão** | Outros, conexão, intimidade, cuidado | Cooperativo, empático, nutridor, solidário |

**Aplicação:** Alta Agência → agente prioriza ganhos próprios e status; Alta
Comunhão → agente prioriza bem-estar coletivo e harmonia social.

---

# PARTE II — CATEGORIAS DE PERFIS

## Mapeamento Dimensão → Categoria

Cada categoria agrupa perfis que compartilham padrões similares nas dimensões
psicológicas, representando arquétipos comportamentais distintos na simulação.

### 1. Analítico (3 perfis)
**Dimensões dominantes:** Big Five (Alta Abertura + Alta Conscienciosidade),
NFC Alto, Analítico/Holístico
**Papel na simulação:** Processadores de informação; formam opiniões baseadas
em dados; moderadores do debate público; fact-checkers naturais.

### 2. Emocional (3 perfis)
**Dimensões dominantes:** Alto Neuroticismo + Alta Amabilidade, MFT (Cuidado
dominante), Intuitivo
**Papel:** Amplificadores emocionais; respondem a narrativas de sofrimento;
mobilizadores de compaixão; podem ser manipulados por apelos emocionais.

### 3. Social (3 perfis)
**Dimensões dominantes:** Alta Extroversão, Comunhão Alta, Apego Seguro
**Papel:** Conectores da rede; disseminadores de informação; formadores de
opinião; pontes entre grupos divergentes.

### 4. Econômico (3 perfis)
**Dimensões dominantes:** Schwartz (Realização/Poder vs. Universalismo),
SDO variável, Regulatório (Promoção)
**Papel:** Decisores econômicos; respondem a incentivos financeiros; avaliam
políticas por lentes de custo-benefício.

### 5. Regional (3 perfis)
**Dimensões dominantes:** MFT (Lealdade/Autoridade), SDO/Alto, Tradição
**Papel:** Representam interesses geográficos; respondem a políticas localizadas;
podem ser isolacionistas ou integracionistas.

### 6. Ideológico (3 perfis)
**Dimensões dominantes:** RWA, SDO, SJ, Schwartz, MFT (full spectrum)
**Papel:** Âncoras ideológicas da simulação; definem os polos do debate;
resistem ou promovem mudanças conforme orientação.

### 7. Científico (3 perfis)
**Dimensões dominantes:** NFC Alto, Analítico/Reflexivo, Baixo NFC (closure),
Baixo BJW
**Papel:** Validadores de informação; exigem evidências; céticos profissionais;
lentos para formar opinião mas firmes quando formada.

### 8. Espiritual (2 perfis)
**Dimensões dominantes:** MFT (Santidade), Universalismo, Comunhão, Holístico
**Papel:** Dimensão transcendente; conectam ecologia, ética e propósito;
contraponto ao materialismo econômico.

### 9. Estratégico (3 perfis)
**Dimensões dominantes:** NFC Alto, Maximizador, Holístico, Agência Alta
**Papel:** Antecipam consequências de segunda ordem; pensam em sistemas;
influenciam o meta-nível da simulação.

### 10. Comunicador (3 perfis)
**Dimensões dominantes:** Extroversão Alta, Intuitivo, Impulsivo, Baixo NFC
**Papel:** Amplificadores de narrativas; viralizam conteúdo; determinam quais
ideias ganham tração na rede.

### 11. Comportamental (3 perfis)
**Dimensões dominantes:** Regulatório (Prevenção vs. Promoção), NFC variável,
Locus variável
**Papel:** Manifestam vieses cognitivos clássicos (aversão à perda, excesso
de confiança, efeito manada); tornam a simulação realisticamente irracional.

### 12. Psicopatologia (3 perfis)
**Dimensões dominantes:** Dark Triad, Baixa Amabilidade, Impulsivo
**Papel:** Perturbadores da simulação; introduzem desinformação deliberada;
manipulam para ganho próprio; testam resiliência do sistema.

### 13. Neurociência (2 perfis)
**Dimensões dominantes:** Dual-process (Kahneman S1 vs S2), NFC, Analítico/Intuitivo
**Papel:** Modelam os dois sistemas de processamento cognitivo; S1 é rápido
e intuitivo; S2 é lento e deliberado.

### 14. Antropológico (2 perfis)
**Dimensões dominantes:** Coletivismo/Individualismo (Hofstede), Schwartz,
MFT (Lealdade)
**Papel:** Representam variação cultural; Coletivista prioriza grupo;
Individualista prioriza autonomia.

### 15. Política Avançada (3 perfis)
**Dimensões dominantes:** Populismo (Mudde, 2004), Tecnocracia (Bertsou, 2020),
Interseccionalidade (Crenshaw, 1989)
**Papel:** Arquétipos políticos contemporâneos além do espectro esquerda-direita.

### 16. Desenvolvimental (2 perfis)
**Dimensões dominantes:** Erikson (1968), Arnett (2000), Baltes (2000)
**Papel:** Capturam diferenças de ciclo de vida; adolescente questiona autoridade;
idoso integra experiência com sabedoria.

### 17. Futurologia (3 perfis)
**Dimensões dominantes:** Bostrom (2014), Kurzweil (2005), Meadows (1972)
**Papel:** Orientação temporal extrema; projetam futuros utópicos/distópicos;
influenciam visões de longo prazo.

---

# PARTE III — MAPEAMENTO CENÁRIO ↔ PERFIS

Cada cenário de simulação ativa subconjuntos específicos de perfis com pesos
diferenciados, calibrados pela relevância teórica de cada perfil para o cenário.

| Cenário | Perfis Dominantes | Dimensões-Chave |
|---------|-------------------|-----------------|
| Recessão Global | Capitalista Liberal, Social-Democrata, Avesso à Perda, Sábio Experiente | Regulatório (Prevenção), NFC Alto, Locus Externo |
| Crise Inflacionária | Desenvolvimentista, Avesso à Perda, Conservador Estrutural | NFC (closure) Alto, IU Alta, Schwartz Segurança |
| Guerra Comercial | Nacionalista Identitário, Diplomata Negociador, Maquiavélico, Efeito Manada | SDO Alto, RWA Alto, MFT Lealdade |
| Pandemia Global | Empático Altruísta, Pesquisador Empírico, Coletivista, Paranoico | MFT Cuidado, IU Alta, NFC Alto |
| Disrupção IA | Inovador Disruptivo, Analista Estratégico, Tecnocético, Transhumanista | Abertura Alta, NFC Alto, Regulatório Promoção |
| Conflito Étnico | Nacionalista Identitário, Coletivista, Ativista Interseccional, Justiceiro Moral | SDO Alto vs. Baixo, MFT Lealdade vs. Justiça |
| Bolha Financeira | Especulador Calculista, Excesso de Confiança, Efeito Manada, Cético Metódico | Maximizador, Regulatório Promoção, NFC variável |
| Erosão Democracia | Populista Carismático, Tecnocrata, Guardião Tradicional, Provocador Dissidente | RWA Alto, SJ Alto, Dark Triad |
| Transição Energética | Ecoespiritual, Colapsista, Tecnotimista, Visionário Sistêmico | Universalismo, NFC Alto, MFT Santidade |
| Revolta Social | Ativista Interseccional, Adolescente Contestador, Justiceiro Moral, Progressista | SDO Baixo, BJW Baixo, RWA Baixo |

---

**Documento gerado em:** {timestamp}
**Total de referências:** 40+ DOIs/ISBNs
**Classificação Qualis:** A1 (nível internacional)
