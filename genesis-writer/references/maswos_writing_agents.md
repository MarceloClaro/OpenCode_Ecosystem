<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
  Genesis-Writer: integrado ao ecossistema v4.0
-->

# Agentes de Escrita MASWOS (Genesis-Writer v2.0)

O Genesis-Writer v2.0 integra os **MASWOS Writing Agents** na Camada L4 (Specialization & Content Generation) para a produção de conteúdo textual de alta qualidade, com especialização e adaptação de estilo.

## 1. Estrutura e Especialização dos Agentes

Os MASWOS Writing Agents são um ecossistema de agentes especializados, cada um com uma função específica no processo de escrita:

| Agente | Função Principal | Camada de Atuação | Integração Chave |
| :--- | :--- | :--- | :--- |
| **Agente Pesquisador** | Coleta e sintetiza informações de fontes primárias e secundárias. | L1 (Knowledge & Domain Discovery) | Skill Registry, Memory Store |
| **Agente Analista** | Aplica os 38 sub-tipos de raciocínio para extrair insights e correlações. | L2 (Autonomous Reasoning) | Micro Reasoning Types |
| **Agente Redator** | Compõe o texto principal de seções e capítulos, seguindo diretrizes de estilo. | L4 (Specialization & Content Generation) | Adaptive Capabilities |
| **Agente Revisor Gramatical** | Corrige erros gramaticais, ortográficos e de pontuação. | L5 (Scientific Audit & Validation) | Micro Validation (Constraints) |
| **Agente Revisor de Estilo** | Garante a fluidez, clareza e aderência ao tom acadêmico/literário. | L4 (Specialization & Content Generation) | Adaptive Capabilities |
| **Agente Citador** | Insere citações e referências no formato correto (ABNT/APA/Vancouver). | L5 (Scientific Audit & Validation) | Citation Validator |
| **Agente de Coesão Lógica** | Verifica a consistência argumentativa e a progressão lógica do texto. | L5 (Scientific Audit & Validation) | Consistency Checker |
| **Agente de Densidade Acadêmica** | Monitora a densidade de informações e sugere aprofundamentos. | L5 (Scientific Audit & Validation) | Qualis A1 Auditor |
| **Agente de Simulação de Banca** | Atua como revisor crítico, identificando lacunas e pontos fracos. | L6 (Observability & Evolutionary Feedback) | Simulação de Banca Examinadora |
| **Agente de Otimização** | Propõe melhorias com base no feedback e nos resultados da auditoria. | L6 (Observability & Evolutionary Feedback) | Meta-Learning Engine |

## 2. Fluxo de Trabalho e Orquestração

A orquestração dos MASWOS Writing Agents é realizada pela Camada L3 (Fractional Execution & Multi-Agent) e supervisionada pelo Master Agent Loop. O `Subagent Spawner` cria instâncias desses agentes conforme a necessidade, e o `Teammate Mailboxes` facilita a comunicação entre eles.

1.  **Delegação Fracionada:** O Master Agent Loop delega a escrita de uma seção ou subseção a um conjunto de agentes (Pesquisador, Analista, Redator).
2.  **Execução Isolada:** O `Worktree Isolator` garante que cada agente trabalhe em um ambiente isolado, minimizando conflitos e permitindo paralelização.
3.  **Validação Contínua:** As `Micro Sync Barriers` e `Micro Validation` (L5) garantem que a saída de cada agente atenda a todas as constraints antes de ser passada para o próximo.
4.  **Feedback Iterativo:** O `Micro Feedback Loop` (L6) coleta feedback de cada operação, que é utilizado pelo `Meta-Learning Engine` para refinar o comportamento dos agentes e otimizar o processo de escrita.

## 3. Adaptação e Especialização Emergente

Os agentes possuem a capacidade de **Especialização Emergente** (L4), onde aprendem e adaptam suas capacidades com base nos padrões de sucesso e no feedback recebido. Isso permite que o sistema ajuste dinamicamente o estilo, o tom e a profundidade da escrita para atender aos requisitos específicos de cada tipo de publicação (artigo, tese, livro) e área do conhecimento.
