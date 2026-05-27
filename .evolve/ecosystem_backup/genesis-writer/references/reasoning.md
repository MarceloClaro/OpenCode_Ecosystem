<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
  Genesis-Writer: integrado ao ecossistema v4.0
-->

# 38 Sub-tipos de Raciocínio Granular (Genesis-Writer)

O Genesis-Writer utiliza uma seleção dinâmica de raciocínios para extrair insights micro e macro.

## 1. Categoria: Dedutivo (8 tipos)
- **Modus Ponens:** Se P, então Q. P ocorre, logo Q.
- **Modus Tollens:** Se P, então Q. Q não ocorre, logo P não ocorreu.
- **Silogismo Hipotético:** Cadeia de implicações lógicas.
- **Silogismo Disjuntivo:** Escolha entre alternativas mutuamente exclusivas.
- **Dilema Construtivo:** P ou Q; se P então R; se Q então S; logo R ou S.
- **Prova por Contradição:** Assume o oposto para provar a falsidade.
- **Instanciação Universal:** Aplica regra geral a caso específico.
- **Generalização Universal:** Conclui regra geral de casos representativos.

## 2. Categoria: Indutivo (6 tipos)
- **Generalização Estatística:** Projeção de amostra para população.
- **Analogia Forte:** Semelhança estrutural entre domínios distintos.
- **Indução Preditiva:** Baseada em padrões históricos.
- **Indução Causal:** Identificação de causa por repetição.
- **Enumeração Completa:** Verificação de todos os casos possíveis.
- **Eliminação:** Descarte de hipóteses improváveis.

## 3. Categoria: Causal (5 tipos)
- **Causalidade Direta:** A causa B sem intermediários.
- **Causalidade Indireta:** Cadeia de eventos (A -> B -> C).
- **Fator Confundidor:** Identificação de variável oculta (C causa A e B).
- **Feedback Loop:** Causalidade circular (A causa B, que reforça A).
- **Causalidade Estrutural:** O sistema força o comportamento.

## 4. Categoria: Contrafactual (4 tipos)
- **Simples:** "E se X não tivesse ocorrido?"
- **Condicional:** "Se X fosse Y, então Z seria W?"
- **Múltiplo:** Teste de múltiplos cenários alternativos.
- **Iterativo:** Evolução de cenários contrafactuais em cascata.

## 5. Categoria: Bayesiano (5 tipos)
- **Prior Analysis:** Conhecimento prévio antes da evidência.
- **Likelihood Estimation:** Probabilidade da evidência dada a hipótese.
- **Posterior Update:** Atualização da crença após novos dados.
- **Fator de Bayes:** Comparação entre duas hipóteses rivais.
- **Rede de Crenças:** Interdependência de probabilidades.

## 6. Categoria: Analógico (4 tipos)
- **Estrutural:** Mapeamento de relações entre sistemas.
- **Funcional:** Semelhança no propósito ou operação.
- **Processual:** Semelhança na sequência de passos.
- **Metafórico:** Uso de conceitos de um domínio para iluminar outro.

## 7. Categoria: Formal (3 tipos)
- **Prova Direta:** Sequência lógica ininterrupta.
- **Indução Matemática:** Base, passo indutivo e conclusão.
- **Redução:** Transformar problema complexo em um já resolvido.

## 8. Categoria: Abdutivo (3 tipos)
- **Melhor Explicação:** Seleção da hipótese mais simples e abrangente.
- **Diagnóstico:** Identificação de causa por sintomas/sinais.
- **Heurística de Descoberta:** Salto criativo baseado em evidências incompletas.
