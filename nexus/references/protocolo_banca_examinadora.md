<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# Protocolo de Simulação de Banca Examinadora (Peer-Review) - Nexus L6

Este protocolo detalha o funcionamento da **Simulação de Banca Examinadora** integrada à Camada L6 (Feedback & Evolução) do `Nexus-Multiagents-v6`. Seu objetivo é submeter teses, dissertações e artigos gerados pelo `criador-de-artigo-v2` a uma avaliação rigorosa, em tempo real, contra os critérios Qualis A1 e padrões internacionais de excelência acadêmica, garantindo uma pontuação de 10/10 antes da entrega final.

## 1. Princípios Fundamentais da Simulação

*   **Avaliação Cega (Blind Review):** O sistema simula múltiplos avaliadores independentes, sem conhecimento prévio do "autor" (o agente `criador-de-artigo-v2`).
*   **Critérios Multidimensionais:** A avaliação abrange todas as dimensões de um artigo científico de alta qualidade: originalidade, rigor metodológico, profundidade teórica, clareza da escrita, relevância e impacto.
*   **Feedback Iterativo:** O resultado da simulação não é apenas uma nota, mas um conjunto detalhado de feedbacks acionáveis que retroalimentam o `Master Agent Loop` do `criador-de-artigo-v2` para ciclos de correção e aprimoramento.
*   **Conformidade Qualis A1:** Todos os critérios de avaliação são calibrados para os mais altos padrões da CAPES (Qualis A1) e periódicos internacionais de impacto (Scopus/WoS).

## 2. Agentes Envolvidos na Simulação (Nexus L6)

O Nexus L6 orquestra um conjunto de subagentes especializados para a simulação da banca:

| Agente | Função Principal | Critérios de Avaliação |
| :--- | :--- | :--- |
| **Avaliador Teórico (AT)** | Foco na solidez do referencial teórico, originalidade e profundidade da discussão. | Coerência teórica, atualização da literatura, diálogo crítico, contribuição para o campo. |
| **Avaliador Metodológico (AM)** | Foco no rigor do design de pesquisa, coleta e análise de dados. | Adequação metodológica, replicabilidade, validade interna/externa, ética. |
| **Avaliador de Escrita (AE)** | Foco na clareza, coesão, fluidez, conformidade ABNT/APA/Vancouver e qualidade da linguagem. | Gramática, estilo, estrutura do texto, uso de terminologia, conformidade com normas. |
| **Avaliador de Impacto (AI)** | Foco na relevância do problema, potencial de impacto e contribuições práticas/teóricas. | Originalidade do problema, aplicabilidade dos resultados, implicações para a pesquisa futura. |
| **Avaliador de Citações (AC)** | Foco na qualidade e auditabilidade das citações (conforme `citacoes_auditaveis.md`). | Veracidade do DOI, correção do trecho original/tradução, profundidade do fichamento crítico. |

## 3. Fluxo de Trabalho da Simulação de Banca

1.  **Submissão (criador-de-artigo-v2 → Nexus L6):** Após a conclusão da escrita do artigo (Fase 4 do `criador-de-artigo-v2`), o manuscrito é submetido ao Nexus L6.
2.  **Distribuição:** O Nexus L6 distribui o manuscrito para os `Avaliadores (AT, AM, AE, AI, AC)`.
3.  **Avaliação Paralela:** Cada avaliador executa sua análise de forma independente, gerando um relatório de avaliação detalhado com notas e comentários específicos para cada seção do artigo.
4.  **Consolidação:** O Nexus L6 consolida os relatórios individuais, identificando pontos de consenso e divergência entre os avaliadores.
5.  **Geração de Feedback:** Um relatório de feedback unificado é gerado, destacando as áreas que necessitam de aprimoramento para atingir a nota 10/10 Qualis A1.
6.  **Retroalimentação (Nexus L6 → criador-de-artigo-v2):** O feedback é enviado de volta ao `Master Agent Loop` do `criador-de-artigo-v2`, que ativa os módulos de correção (A44/A45) e, se necessário, os módulos de pesquisa (A2/A3) para refinar o artigo.
7.  **Ciclos Iterativos:** O processo se repete até que o artigo atinja uma pontuação consensual de 10/10 em todos os critérios de avaliação da banca simulada.

## 4. Critérios de Avaliação (Exemplos)

*   **Originalidade:** O artigo apresenta uma contribuição nova e significativa para o conhecimento? (1-5 pontos)
*   **Rigor Metodológico:** O design de pesquisa é apropriado e os métodos são aplicados corretamente? (1-5 pontos)
*   **Profundidade Teórica:** A discussão teórica é robusta e bem fundamentada? (1-5 pontos)
*   **Qualidade da Escrita:** O texto é claro, conciso, coeso e livre de erros? (1-5 pontos)
*   **Relevância das Citações:** As citações são apropriadas, auditáveis e contribuem significativamente para o argumento? (1-5 pontos)

**Nota Final:** A média ponderada das pontuações dos avaliadores, com um limiar de 10/10 para aprovação. Se a nota for inferior, o ciclo de correção é reativado.

## 5. Integração com APIs Externas (Veracidade)

Para o `Avaliador de Citações (AC)`, o Nexus L6 pode integrar-se com APIs externas como Crossref, PubMed, Scopus e Web of Science para verificar a existência e a validade de DOIs, bem como a reputação e o fator de impacto dos periódicos citados, garantindo que as referências sejam 100% reais e relevantes. Isso atua como um "Harness de Veracidade" em tempo real, impedindo a inclusão de informações fictícias ou de baixa credibilidade. 
