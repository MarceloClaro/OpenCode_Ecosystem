<p align="center"><b>INTELIGÊNCIA ARTIFICIAL MULTIAGENTE NO ENSINO SUPERIOR:<br>UM GUIA PRÁTICO PARA PESQUISA CIENTÍFICA ASSISTIDA E ÉTICA</b></p>

<br>

**Linha de Pesquisa:** Linha 1: Inovações e Práticas em Tecnologia Educacional

**Primeira Opção de Tema:** Tema 03: Aplicação de Inteligência Artificial no Desenvolvimento de Ferramentas para Suporte ao Contexto Educacional

**Segunda Opção de Tema:** Tema 04: Avaliação de Aspectos da LGPD e Privacidade de Dados no Contexto Educacional

**Tipo de Produto Educacional:** Conteúdo educacional digital

---

## RESUMO

A disseminação de ferramentas de Inteligência Artificial (IA) generativa no ensino superior introduziu riscos de alucinações, plágio involuntário, vazamento de dados e perda de rastreabilidade de fontes. Este anteprojeto propõe o desenvolvimento de um guia prático de uso ético de uma plataforma de IA multiagente de código aberto, que coordena 125 agentes especializados com auditoria caixa branca e rastreabilidade por Digital Object Identifier (DOI), como ferramenta de suporte à pesquisa acadêmica assistida. A pesquisa adota metodologia mista em três fases: (1) análise documental da arquitetura do ecossistema frente às normativas de ética em IA (Lei Geral de Proteção de Dados Pessoais, LGPD, Lei nº 13.709/2018; Resolução PRPPG/UFC nº 39/2025); (2) desenvolvimento do guia prático validado por especialistas; (3) estudo de caso com grupo focal de pesquisadores de pós-graduação. O produto educacional será um manual digital interativo que sistematiza boas práticas de uso ético de IA multiagente na pesquisa.

**Palavras-chave:** IA Multiagente. Ética na Pesquisa. Código Aberto. LGPD. Tecnologia Educacional.

---

## JUSTIFICATIVA E DELIMITAÇÃO DO PROBLEMA

O avanço acelerado das IAs generativas transformou a pesquisa acadêmica, mas expôs vulnerabilidades críticas: (a) modelos geram conteúdo plausível, porém factualmente incorreto, incluindo referências bibliográficas inexistentes; (b) o usuário não consegue auditar como o modelo chegou a uma conclusão, violando o princípio da reprodutibilidade científica; (c) pesquisadores inserem dados inéditos em plataformas que os utilizam para treinamento, infringindo a LGPD (Lei nº 13.709/2018); (d) a paráfrase automatizada pode reproduzir trechos protegidos sem atribuição (FLORIDI, 2023; RUSSELL; NORVIG, 2022).

O Edital nº 01/2026 do PPGTE/UFC exige que todo candidato declare o uso ou não uso de IA (Anexo IV). Essa exigência evidencia uma lacuna: faltam diretrizes práticas e ferramentas validadas que permitam ao pesquisador utilizar IA de forma ética, rastreável e em conformidade com a lei.

A plataforma de IA multiagente que fundamenta este anteprojeto, disponível publicamente em repositório de código aberto, preenche essa lacuna ao implementar: (1) auditoria de cada afirmação vinculada a DOIs verificáveis; (2) logs imutáveis com hash SHA-256; (3) debate entre agentes com 38 tipos de raciocínio e 10 estratégias de Teoria dos Jogos (NASH, 1950); (4) corretor automático de vazamentos de dados.

O problema de pesquisa delimita-se à questão: como sistematizar, por meio de um guia prático validado, o uso ético de uma plataforma de IA multiagente como ferramenta de suporte à pesquisa científica no ensino superior, em conformidade com a LGPD e as normativas de integridade acadêmica da UFC? A relevância justifica-se nas dimensões acadêmica (conhecimento original sobre IA multiagente e ética na pesquisa), tecnológica (democratização de ferramenta gratuita e de código aberto) e social (diretrizes replicáveis para uso responsável de IA, alinhadas aos Objetivos de Desenvolvimento Sustentável (ODS) 4: Educação de Qualidade).

---

## OBJETIVOS

### Objetivo Geral

Desenvolver e validar um guia prático de uso ético de uma plataforma de IA multiagente como ferramenta de suporte à pesquisa científica assistida no ensino superior, em conformidade com a LGPD e as normativas de integridade acadêmica da UFC.

### Objetivos Específicos

1. Analisar a arquitetura multiagente da plataforma (125 agentes, pipeline de escrita científica, sistema de auditoria caixa branca) quanto à adequação aos princípios de ética, rastreabilidade e privacidade de dados no contexto educacional.

2. Mapear as normativas vigentes sobre uso de IA na pesquisa (Resolução PRPPG/UFC nº 39/2025, LGPD, Marco Civil da Internet) e identificar lacunas entre as exigências legais e as práticas atuais dos pesquisadores.

3. Sistematizar boas práticas em formato de guia digital, organizado nos módulos: (a) configuração ética do ambiente; (b) pesquisa bibliográfica com rastreabilidade DOI; (c) redação assistida com auditoria de citações; (d) proteção de dados sensíveis conforme a LGPD.

4. Validar o guia por meio de estudo de caso com grupo focal de 8 a 12 pesquisadores de pós-graduação, avaliando usabilidade, efetividade na prevenção de más condutas e percepção de utilidade.

5. Avaliar os aspectos de privacidade e proteção de dados do ecossistema, verificando conformidade com a LGPD e propondo recomendações de aprimoramento (Tema 04).

---

## FUNDAMENTAÇÃO TEÓRICA

A fundamentação estrutura-se em três eixos interdisciplinares:

### Eixo 1: IA e Sistemas Multiagentes

Russell e Norvig (2022) definem agente inteligente como entidade que percebe o ambiente por sensores e age por atuadores. Sistemas multiagentes (SMA) estendem esse conceito: múltiplos agentes autônomos cooperam e competem para resolver problemas complexos. Diferentemente dos Large Language Models (LLMs) monolíticos, que processam *prompts* em única inferência estatística, SMAs distribuem o raciocínio entre agentes especializados, cada um com conhecimento de domínio e protocolos de validação específicos. Wooldridge (2009) aponta três vantagens dos SMAs: robustez (falha de um agente não compromete o sistema), escalabilidade e explicabilidade (rastreabilidade de cada decisão a um agente específico); propriedades que os tornam ideais para aplicações educacionais que exigem auditabilidade.

A plataforma que fundamenta este anteprojeto concretiza esses princípios em um pipeline de escrita científica no qual 49 agentes colaboram em 8 estágios para produzir artigos. Seu diferencial é o fórum de debate entre agentes, que utiliza 38 tipos de raciocínio e 10 estratégias de Teoria dos Jogos para confrontar hipóteses e validar conclusões antes de apresentá-las ao usuário (NASH, 1950).

### Eixo 2: Tecnologia Educacional e Letramento Digital

Valente (2014) argumenta que a integração de tecnologias digitais no ensino superior requer *transposição didática* que transforme práticas pedagógicas, não apenas substitua ferramentas. Moran (2018) complementa que metodologias ativas apoiadas por tecnologia deslocam o professor para mediador e o aluno para protagonista. Siemens (2004), com o Conectivismo, concebe a aprendizagem como construção de redes entre nodos de informação: artigos, bases de dados, pesquisadores e agentes de IA, valorizando a capacidade de navegar, filtrar e sintetizar informações. O letramento digital crítico (FREIRE, 1996) oferece a lente pedagógica para distinguir o uso instrumental do uso crítico-reflexivo das ferramentas de IA.

### Eixo 3: Ética da IA, Privacidade e Conformidade Legal

Floridi (2023) estabelece cinco princípios para IA ética: beneficência, não maleficência, autonomia, justiça e explicabilidade. A plataforma alinha-se a todos: beneficência na aceleração da produção científica com qualidade; não maleficência pelos filtros de plágio e corretor automático; autonomia porque o sistema é assistente (não substituto) do pesquisador; justiça pelo código aberto e gratuito; explicabilidade pela arquitetura de auditoria caixa branca. A LGPD (BRASIL, 2018) e a Resolução PRPPG/UFC nº 39/2025 operacionalizam esses princípios na pesquisa acadêmica. O orientador dos Temas 03 e 04 do PPGTE atua precisamente na interseção entre desenvolvimento de ferramentas de IA para suporte educacional e avaliação de privacidade de dados, conferindo aderência temática ao projeto.

---

## METODOLOGIA

Pesquisa de abordagem mista (qualitativa-quantitativa), natureza aplicada, objetivo exploratório-descritivo, estruturada em três fases:

**Fase 1: Análise Documental e Arquitetural (Meses 1-4):** mapeamento da arquitetura da plataforma (125 agentes, pipeline de escrita científica, sistema de auditoria); revisão documental da LGPD e Resolução PRPPG/UFC nº 39/2025; análise de conformidade entre recursos de auditoria e exigências legais. Produto: Relatório técnico de conformidade LGPD.

**Fase 2: Desenvolvimento do Guia Prático (Meses 5-12):** estruturação em 4 módulos: (A) configuração ética do ambiente; (B) pesquisa bibliográfica com rastreabilidade DOI; (C) redação acadêmica com auditoria integrada; (D) proteção de dados sensíveis e protocolos de anonimização. Validação por painel de 3 especialistas (IA, Direito Digital/LGPD, Educação). Produto: manual digital interativo (web responsivo, com exemplos e checklists).

**Fase 3: Estudo de Caso com Grupo Focal (Meses 13-20):** participantes: 8 a 12 pesquisadores de pós-graduação da UFC. Quatro encontros quinzenais de 2h utilizando a plataforma com o guia prático. Coleta: gravações (com consentimento), questionários Likert pré/pós-intervenção e análise de logs. Análise: estatística descritiva e análise de conteúdo temática (BARDIN, 2016).

**Fase 4: Sistematização e Defesa (Meses 21-24):** consolidação dos resultados, redação da dissertação, publicação do produto educacional e defesa pública.

**Aspectos Éticos:** projeto submetido ao Comitê de Ética em Pesquisa (CEP) da UFC; todos os participantes assinarão Termo de Consentimento Livre e Esclarecido (TCLE); nenhum dado sensível será inserido em plataformas externas; processamento local na plataforma multiagente.

---

## CRONOGRAMA

| Atividade | Sem. 1 | Sem. 2 | Sem. 3 | Sem. 4 |
|-----------|:------:|:------:|:------:|:------:|
| Revisão de literatura | ████████ | ████ | | |
| Fase 1: Análise documental e arquitetural | ████████ | | | |
| Fase 2: Desenvolvimento do guia prático | | ████████ | ██████ | |
| Validação por especialistas | | | ████ | |
| Fase 3: Estudo de caso (grupo focal) | | | ████████ | ██████ |
| Análise dos dados | | | | ██████ |
| Redação da dissertação | | ██ | ████ | ████████ |
| Publicação do produto educacional | | | | ██████ |
| Defesa pública | | | | ████ |

---

## REFERÊNCIAS

BARDIN, L. **Análise de conteúdo**. São Paulo: Edições 70, 2016. ISBN 978-85-62938-04-7.

BRASIL. **Lei nº 13.709, de 14 de agosto de 2018**. Lei Geral de Proteção de Dados Pessoais (LGPD). Diário Oficial da União, Brasília, DF, 15 ago. 2018. Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm. Acesso em: 24 maio 2026.

FLORIDI, L. **The Ethics of Artificial Intelligence**: principles, challenges, and opportunities. Oxford: Oxford University Press, 2023. DOI: https://doi.org/10.1093/oso/9780198883098.001.0001.

FREIRE, P. **Pedagogia da autonomia**: saberes necessários à prática educativa. São Paulo: Paz e Terra, 1996. ISBN 978-85-7753-015-1.

MORAN, J. M. **Metodologias ativas para uma educação inovadora**: uma abordagem teórico-prática. Porto Alegre: Penso, 2018. ISBN 978-85-8429-116-8.

NASH, J. F. Equilibrium points in n-person games. **Proceedings of the National Academy of Sciences**, v. 36, n. 1, p. 48-49, 1950. DOI: https://doi.org/10.1073/pnas.36.1.48.

RUSSELL, S.; NORVIG, P. **Inteligência artificial**: uma abordagem moderna. 4. ed. Rio de Janeiro: GEN LTC, 2022. ISBN 978-85-216-3749-3.

SIEMENS, G. Conectivismo: uma teoria de aprendizagem para a era digital. **International Journal of Instructional Technology and Distance Learning**, v. 2, n. 1, p. 3-10, 2004. Disponível em: http://www.itdl.org/Journal/Jan_05/article01.htm. Acesso em: 24 maio 2026.

UNIVERSIDADE FEDERAL DO CEARÁ. Pró-Reitoria de Pesquisa e Pós-Graduação. **Resolução PRPPG/UFC nº 39, de 1º de outubro de 2025**. Dispõe sobre o uso de Inteligência Artificial na pesquisa acadêmica. Fortaleza: UFC, 2025. Disponível em: https://ppgte.ufc.br/pt/editais/. Acesso em: 24 maio 2026.

UNIVERSIDADE FEDERAL DO CEARÁ. Programa de Pós-Graduação em Tecnologia Educacional. **Edital nº 01/2026**: processo seletivo ao Mestrado Profissional em Tecnologia Educacional. Fortaleza: PPGTE/UFC, 2026. Disponível em: https://ppgte.ufc.br/pt/editais/. Acesso em: 24 maio 2026.

VALENTE, J. A. A comunicação e a educação baseada no uso das tecnologias digitais de informação e comunicação. **UNOPAR Científica Ciências Humanas e Educação**, Londrina, v. 1, n. 1, p. 141-166, 2014.

WOOLDRIDGE, M. **An Introduction to MultiAgent Systems**. 2. ed. Chichester: John Wiley & Sons, 2009. ISBN 978-0-470-51946-2.
