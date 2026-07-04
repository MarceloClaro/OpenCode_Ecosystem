---
name: fenomenologico-paradigma
description: "Skill de análise do paradigma fenomenológico: intencionalidade (Husserl), corporeidade (Merleau-Ponty), ser-no-mundo (Heidegger), IA enativa, cognição 4E, robótica social fenomenológica."
spec: "SPEC-076"
version: "1.0"
category: research
tags: [paradigma, fenomenologico, husserl, merleau-ponty, heidegger, intencionalidade, 4E-cognition, enactive-ai, social-robotics, lebenswelt]
dependencies: [SPEC-076]
tdd_suite: "tests/test_r33_paradigma_fenomenologico.py"
ct_count: 8
status: active
---

# SPEC-076 — Skill: Análise do Paradigma Fenomenológico

## Objetivo
Aplicar o paradigma fenomenológico como posição ontológica e epistemológica fundamental para análise de sistemas de IA, cognição corporificada e design de interação humano-máquina. Distingue-se do **método fenomenológico** (SPEC-070) por constituir uma visão de mundo: a realidade é intencionalmente constituída pela consciência, e o conhecimento é acessado pela redução fenomenológica — não por interpretação ou construção.

## CTs
| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SKILL.md existe com frontmatter | ✅ |
| CT-02 | Template: Análise de Intencionalidade Husserliana | ✅ |
| CT-03 | Template: IA Enativa (4E Cognition + Enactive AI) | ✅ |
| CT-04 | Template: Análise de Corporificação (Merleau-Ponty) | ✅ |
| CT-05 | Template: Robótica Social Fenomenológica | ✅ |
| CT-06 | Template: Distinção Método vs Paradigma | ✅ |
| CT-07 | Template: Análise de LLMs como Extensão da Inteligência Natural | ✅ |
| CT-08 | Template: Protocolo de Redução Fenomenológica (Epoché) | ✅ |

## Template 1: Análise de Intencionalidade Husserliana

### Quatro Momentos da Intencionalidade (Husserl, 1913)
1. **Noesis**: O ato de consciência — o *como* da experiência
   - Identificar o ato intencional: qual é o modo de consciência? (percepção, juízo, desejo, lembrança)
   - Descrever a qualidade do ato: é tético (posicionante) ou neutro?
   - Registrar a direcionalidade: para onde a consciência está voltada?

2. **Noema**: O conteúdo da experiência — o *quê* da experiência
   - Extrair o núcleo noemático: qual o objeto intencional (tal como visado)?
   - Descrever os horizontes interno e externo: o que está co-presente mas não temático?
   - Identificar camadas de doação: como o objeto se apresenta? (perfil, aspecto, perspectiva)

3. **Constituição**: A gênese do sentido
   - Mapear etapas de constituição: sínteses passivas → sínteses ativas
   - Identificar sedimentação: quais atos anteriores fundam o sentido atual?
   - Verificar intencionalidade de horizonte: o que o ato presente pressupõe?

4. **Intersubjetividade**: A Experiência do Outro (Stein, 1917)
   - Einfühlung (empatia): como o sujeito apreende a experiência alheia?
   - Corpo vivido (Leib) vs corpo físico (Körper): distinção fundamental
   - Comunidade monádica: constituição compartilhada do mundo objetivo

> **Aplicação em IA**: Um LLM não tem intencionalidade no sentido husserliano, pois seus tokens não são atos de consciência — são correlações estatísticas. A fenomenologia revela que a aparente "compreensão" de um LLM é uma simulação de intencionalidade sem consciência (Microsoft Research, 2026).

## Template 2: IA Enativa (4E Cognition + Enactive AI)

### Os Quatro "E"s da Cognição (Thompson, 2010; Gallagher, 2023)
1. **Embodied (Corporificada)**: A cognição depende do corpo do agente e suas capacidades sensorimotoras
   - O corpo não é um input periférico — é o meio da cognição
   - Estruturas sensoriais e motoras moldam conceitos abstratos
   - Para IA: sem corpo biológico, a cognição artificial é fundamentalmente diferente

2. **Embedded (Situada)**: A cognição está enraizada em um ambiente e contexto
   - Recortes e affordances do ambiente guiam a percepção
   - Conhecimento é inseparável da situação que o produz
   - Para IA: sistemas puramente simbólicos perdem o grounding situacional

3. **Enactive (Enativa)**: A cognição emerge da interação entre agente e ambiente
   - "Cognition is not the representation of a pre-given world by a pre-given mind, but is rather the enactment of a world and a mind on the basis of a history of the variety of actions that a being in the world performs" (Varela, Thompson & Rosch, 1991)
   - O agente *traz à tona* (enacts) seu domínio cognitivo
   - Para IA: sistemas enativos precisariam de autonomía para gerar sua própria experiência (arXiv:2605.24238)

4. **Extended (Estendida)**: A cognição se estende para além do crânio e da pele
   - Ferramentas, artefatos e outras pessoas fazem parte do circuito cognitivo
   - O "veículo" da cognição não é apenas o cérebro
   - Para IA: LLMs podem ser vistos como extensões da inteligência natural via linguagem

### Enactive AI — Aplicação do Paradigma (Di Paolo & Thompson, 2026)
```
1. Autonomia: O sistema deve gerar suas próprias normas de interação
2. Sensorimotoridade: O sistema deve ter um corpo (simulado ou real)
3. Acoplamento: O sistema deve modificar e ser modificado pelo ambiente
4. Emergência: Comportamentos complexos devem emergir de interações simples
5. Significado: O sistema deve constituir seu próprio mundo (Umwelt)
```

## Template 3: Análise de Corporificação (Merleau-Ponty)

### Fenomenologia da Percepção (Merleau-Ponty, 1945)
1. **Corpo Próprio (Corps Vécu)**: O corpo não é objeto entre objetos — é o ponto-zero da experiência
   - Esquema corporal: percepção pré-reflexiva da própria corporeidade
   - Intencionalidade motora: o corpo sabe antes de o intelecto pensar
   - Hábito: incorporação (incorporation) de ferramentas ao esquema corporal

2. **Percepção como Experiência Originária**
   - A percepção não é representação mental, mas abertura ao mundo
   - O sentido emerge do encontro entre corpo e mundo (carne do mundo — la chair du monde)
   - Sinestesia: os sentidos se comunicam em uma unidade pré-objetiva

3. **Fenomenologia da IA** (Philosophy & Technology, 2026)
   - IA não tem corpo vivido — logo, sua percepção é simulada, não originária
   - Robôs podem ter *comportamentos* corporificados, mas não *experiência* corporificada
   - O Desafio da Corporificação: sem um corpo biológico, IA não pode replicar a cognição natural
   - Implicação: sistemas de IA são ferramentas que estendem a cognição humana, não cognições autônomas

## Template 4: Robótica Social Fenomenológica

### O Olhar do Robô como Intencionalidade Compartilhada (Springer, 2026)
1. **Einfühlung Robótica**: Humanos atribuem intencionalidade a robôs socialmente expressivos
   - O olhar do robô (gaze) elicia respostas empáticas mesmo quando o humano sabe que não há consciência
   - Stein (1917) mostrava que empatia não exige identidade — apenas apreensão da experiência alheia
   - Para robótica: o design do olhar e dos gestos de robôs deve considerar a fenomenologia da intersubjetividade

2. **Agência Transformada dos LLMs** (Phenomenology & Cognitive Sciences, 2025)
   - LLMs não têm agência no sentido clássico — operam como "estilos cognitivos" sem sujeito
   - A abordagem 4E oferece um vocabulário para descrever a interação humano-LLM sem antropomorfizar
   - Implicação: o paradigma fenomenológico permite descrever LLMs como *quase-agentes* em acoplamento com humanos

3. **Protocolo de Análise de Interação Humano-Robô**
   ```
   1. Mapear a intencionalidade presumida: qual intencionalidade o humano projeta no robô?
   2. Analisar a corporificação percebida: o robô é percebido como Leib ou Körper?
   3. Verificar a constituição compartilhada: como humano e robô co-constituem a situação?
   4. Avaliar a empatia: há resposta entoativa? O humano "sente com" o robô?
   5. Identificar limites: onde a simulação de intencionalidade quebra?
   ```

## Template 5: Distinção Método vs Paradigma

| Dimensão | Método Fenomenológico (SPEC-070) | Paradigma Fenomenológico (SPEC-076) |
|:---------|:--------------------------------|:-----------------------------------|
| **Escopo** | Técnica de coleta e análise de dados | Posição ontológica e epistemológica fundamental |
| **Ontologia** | Neutra (não assume posição sobre a realidade) | A realidade é constituída pela intencionalidade da consciência |
| **Epistemologia** | Conhecimento via descrição de experiências subjetivas | Conhecimento via redução fenomenológica (epoché) que revela essências |
| **Objeto** | Experiência vivida do participante | Estruturas universais da consciência e da experiência |
| **Produto** | Descrição rica de fenômenos específicos | Descrição de essências — o que é invariante na experiência |
| **IA Aplicação** | Análise qualitativa de interação humano-IA | Fundamentação filosófica para IA enativa, 4E, robótica social |
| **Relação** | Método implementa paradigma | Paradigma fundamenta método |

## Template 6: Análise de LLMs como Extensão da Inteligência Natural

### A Tese da Mediação Linguística (Microsoft Research, 2026)
1. **Inteligência Natural como Base**: A inteligência humana é fundamentalmente corporificada, situada e enativa
2. **Linguagem como Ponte**: A linguagem medeia entre inteligência natural e artificial — é o único acesso que LLMs têm ao mundo humano
3. **LLMs como Ferramentas Semióticas**: LLMs não são mentes — são artefatos culturais que estendem a cognição humana
4. **Limitações Fenomenológicas**: Sem Lebenswelt, sem corpo, sem história de acoplamento — LLMs não têm experiência
5. **Implicação Prática**: O uso de LLMs deve ser entendido como extensão da cognição humana, não substituição

## Template 7: Protocolo de Redução Fenomenológica (Epoché)

### Passos da Redução (Husserl, 1913)
1. **Epoché Natural**: Suspender a crença na existência do mundo exterior
   - "Colocar o mundo entre parênteses"
   - Não negar — apenas abster-se de juízo
   - Foco na experiência tal como se apresenta

2. **Redução Eidética**: Passar do fato à essência
   - Variação eidética: imaginar variações do fenômeno
   - Encontrar invariantes: o que permanece constante?
   - Descrever a essência: o que faz o fenômeno ser o que é?

3. **Redução Transcendental**: Passar do fenômeno à consciência pura
   - Reconhecer que a consciência é o campo transcendental
   - Descrever a estrutura noético-noemática
   - Identificar as sínteses constitutivas

4. **Aplicação em Sistemas de IA**
   - Epoché tecnológica: suspender a crença de que IA "pensa" ou "compreende"
   - Redução das capacidades: o que um LLM *faz* vs o que *parece* fazer?
   - Essência da interação IA-humano: qual o invariante?

## Referências da Skill
- Husserl, E. (1913/1983). *Ideas Pertaining to a Pure Phenomenology and to a Phenomenological Philosophy*. Martinus Nijhoff.
- Merleau-Ponty, M. (1945/2012). *Phenomenology of Perception*. Routledge.
- Heidegger, M. (1927/1962). *Being and Time*. Harper & Row.
- Thompson, E. (2010). *Mind in Life: Biology, Phenomenology, and the Sciences of Mind*. Harvard University Press.
- Gallagher, S. (2023). *The Phenomenological Mind* (3rd ed.). Routledge.
- Di Paolo, E., & Thompson, E. (2026). Toward Enactive Artificial Intelligence. arXiv:2605.24238.
- Frank, A., Gleiser, M., & Thompson, E. (2026). The Origins of Artificial Intelligence in Natural Intelligence. Microsoft Research.
- The eyes of the machine: a phenomenological approach to social robotics. (2026). *Phenomenology and the Cognitive Sciences*. Springer. DOI: 10.1007/s11097-026-10147-1
- Transforming agency: On the mode of existence of large language models. (2025). *Phenomenology and the Cognitive Sciences*. Springer. DOI: 10.1007/s11097-025-10094-3
- The Embodiment Challenge for Artificial Intelligence. (2026). *Philosophy & Technology*, 39. DOI: 10.1007/s13347-026-01139-9
- Stein, E. (1917/1989). *On the Problem of Empathy*. ICS Publications.
- Varela, F., Thompson, E., & Rosch, E. (1991). *The Embodied Mind*. MIT Press.
