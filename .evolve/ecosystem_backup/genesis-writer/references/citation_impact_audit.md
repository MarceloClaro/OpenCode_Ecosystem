<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%).
  Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)
  Genesis-Writer: integrado ao ecossistema v4.0
-->

# Protocolo de Auditoria de Impacto de Citação (Genesis-Writer v4.0)

O Protocolo de Auditoria de Impacto de Citação do Genesis-Writer v4.0 é um componente crítico da Camada L5 (Scientific Audit & Micro-Validation), garantindo que as citações incluídas no documento não apenas sejam autênticas, mas também de alta relevância e impacto acadêmico.

## 1. Princípios Fundamentais da Auditoria de Impacto

-   **Relevância Qualis A1:** Prioriza a inclusão de artigos publicados em periódicos classificados como Qualis A1 (no contexto brasileiro) ou equivalentes internacionais de alto impacto.
-   **Fator de Impacto:** Avalia o fator de impacto do periódico onde o artigo foi publicado, utilizando bases de dados como Journal Citation Reports (JCR) ou Scopus.
-   **Índice H do Autor:** Considera o índice H do autor principal para artigos sem fator de impacto claro ou para avaliar a influência individual de pesquisadores.
-   **Citações Recebidas:** Verifica o número de vezes que o artigo foi citado por outros trabalhos, indicando sua influência na comunidade científica.
-   **Atualidade:** Prioriza citações de pesquisas recentes (últimos 5-10 anos), a menos que sejam trabalhos seminais ou clássicos da área.

## 2. Componentes do Protocolo de Auditoria de Impacto

### 2.1. Agente de Busca Bibliográfica Avançada (L4)

-   Este agente, na Camada L4, é responsável por realizar buscas estratégicas em bases de dados acadêmicas (Web of Science, Scopus, Google Scholar, SciELO, etc.) utilizando palavras-chave, operadores booleanos e filtros avançados.
-   Ele não apenas busca, mas pré-seleciona artigos com base em critérios iniciais de impacto e relevância.

### 2.2. Citation Impact Auditor (L5)

-   Este subagente da Camada L5 recebe as citações propostas (seja pelo Agente de Busca ou por outros agentes de escrita) e as submete a um processo de validação de impacto.
-   **Fluxo de Validação:**
    1.  **Verificação de DOI/URL:** Confirma a existência e acessibilidade da fonte.
    2.  **Consulta a Bases de Dados:** Interage com APIs de bases de dados bibliométricas para extrair:
        -   Fator de Impacto do Periódico.
        -   Classificação Qualis (se aplicável).
        -   Número de citações recebidas pelo artigo.
        -   Índice H do autor principal (se disponível).
    3.  **Análise de Relevância Contextual:** Avalia a aderência do conteúdo do artigo ao tópico específico do texto em produção, utilizando técnicas de Processamento de Linguagem Natural (PLN).
    4.  **Geração de Score de Impacto:** Atribui uma pontuação ponderada de impacto com base nos critérios acima.
    5.  **Decisão:** Se a pontuação de impacto for abaixo de um limiar pré-definido, a citação é sinalizada para revisão ou rejeitada, e o `Micro Feedback Loop` (L6) é acionado para buscar alternativas.

### 2.3. Harness de Veracidade (L0 & L5)

-   O `Harness de Veracidade` trabalha em conjunto com o `Citation Impact Auditor` para garantir que a fonte seja não apenas autêntica, mas também de alta qualidade e impacto.
-   Ele verifica a integridade do trecho original citado e sua tradução, garantindo que a interpretação esteja correta e não distorça o sentido original.

## 3. Integração com o Processo de Escrita

-   **Priorização de Fontes:** Durante a fase de pesquisa (L1) e geração de conteúdo (L4), os agentes são instruídos a priorizar fontes com alto score de impacto.
-   **Feedback Contínuo:** O feedback do `Citation Impact Auditor` é incorporado ao `Meta-Learning Engine` (L6) para refinar continuamente as estratégias de busca e seleção de citações dos agentes.
-   **Relatório de Qualidade:** O `Report Generator` (L7) inclui uma seção detalhada sobre a qualidade e o impacto das citações utilizadas, demonstrando o rigor bibliográfico do documento.

Este protocolo assegura que o Genesis-Writer v4.0 produza documentos com uma base bibliográfica robusta, atualizada e de impacto comprovado, essencial para publicações de nível Qualis A1 e PhD.
