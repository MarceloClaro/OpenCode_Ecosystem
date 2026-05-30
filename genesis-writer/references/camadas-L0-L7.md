<!-- Conteudo extraido de genesis-writer/SKILL.md via progressive-disclosure -->

## 4. Arquitetura Unificada de 8 Camadas (SEES - Claude Code Enhanced - PhD Level)

O Genesis-Writer v5.0 adota uma arquitetura de 8 camadas, inspirada e aprimorada a partir do Claude Code Architecture, integrando os princípios de sincronização meta-granular do Nexus-v6 e o rigor acadêmico do MASWOS. Cada camada é interconectada e orquestrada pelo **Master Agent Loop**, com granularização extrema dos agentes e subagentes.

| Camada | Nome | Componentes Chave Integrados | Função Principal e Sincronização |
| :--- | :--- | :--- | :--- |
| **L0** | **Input & Meta-Coordination** | User Interface, Session Manager, Permission Gate, Meta-Orchestrator, **Harness de Veracidade (Nexus L0 - Auditoria Forense)** | Ponto de entrada, gerenciamento de sessão, controle de permissões e validação inicial de autenticidade e relevância de fontes, com auditoria forense de veracidade. |
| **L1** | **Knowledge & Domain Discovery** | Skill Registry, Context Compressor, Task Graph, Memory Store, Domain Discovery Engine, **Motor de Insights de Variáveis Cruzadas** | Gerenciamento dinâmico de conhecimento, injeção de habilidades, compressão de contexto para coerência, mapeamento de conceitos/relações do domínio e descoberta de novos insights através do cruzamento de variáveis. |
| **L2** | **Autonomous Reasoning & Methodological Alignment** | Micro Reasoning Types (38 sub-tipos), Self-Reflection, **Metodologia-Agente Mapper**, **Agente de Análise Crítica de Gaps** | Seleção dinâmica e aplicação de 38 sub-tipos de raciocínio granular, alinhados a metodologias científicas específicas, com capacidade de auto-crítica e identificação/cobertura de gaps teóricos. |
| **L3** | **Fractional Execution & Multi-Agent Orchestration** | Subagent Spawner (45+ Agentes, 60+ Subagentes), Teammate Mailboxes, FSM Protocol, Autonomous Board, Worktree Isolator, Micro Sync Barriers (120+) | Orquestração multiagente, delegação de tarefas, comunicação inter-agente, isolamento de worktree e execução fracionada de conteúdo para evitar timeouts. |
| **L4** | **Specialization & Content Generation** | Emergent Specialization, Adaptive Capabilities, **MASWOS Writing Agents (Granular)**, **Agentes de Análise Estatística e ML**, **Agentes de Busca Bibliográfica Avançada (Revisor Teórico Minucioso)** | Agentes PhD-level especializados por capítulo/tema/metodologia, adaptação de estilo e tom, geração de conteúdo textual, e integração de análises estatísticas/ML e busca bibliográfica rigorosa e crítica. |
| **L5** | **Scientific Audit & Micro-Validation** | Micro Validation (500+ Constraints), Qualis A1 Auditor, Citation Validator, Consistency Checker, **Micro-Audit Protocol**, **Statistical Validation Harness (Confiança Zero)**, **ML Model Audit (Confiança Zero)**, **Citation Impact Auditor (Auditoria Forense)** | Auditoria rigorosa de todas as 500+ constraints, verificação de citações (DOI, trecho original), consistência lógica e densidade acadêmica, com validação estatística/ML de confiança zero e auditoria forense de impacto de citações. |
| **L6** | **Observability & Evolutionary Feedback** | Event Bus, Background Executor, Micro Feedback Loop (120+ points), Meta-Learning Engine, **Simulação de Banca Examinadora (Nexus L6)** | Monitoramento de eventos, execução em segundo plano, feedback granular, otimização contínua e simulação de revisão por pares para garantir 10/10. |
| **L7** | **Output & Deliverables** | Task Result, Final Integrator, Report Generator, **Audit Trail Generator** | Consolidação final do documento, geração de relatórios de qualidade e trilhas de auditoria detalhadas, e entrega dos resultados verificados ao usuário. |


---

## 6. Metodologias e Raciocínios Sincronizados (L2 & L4)

A Camada L2 (`Autonomous Reasoning & Methodological Alignment`) agora inclui um **Metodologia-Agente Mapper** que associa dinamicamente as metodologias científicas aos agentes especializados e aos 38 sub-tipos de raciocínio. Isso garante que a aplicação do raciocínio seja sempre contextualizada e metodologicamente sólida.


---

## 7. Protocolo de Auditoria Micro-Granular (L5) com Sincronização V4

A Camada L5 (`Scientific Audit & Micro-Validation`) foi aprimorada com um **Micro-Audit Protocol** que registra e valida cada operação atômica realizada pelos agentes. Isso inclui:
- **Validação de Input/Output:** Cada entrada e saída de um agente é verificada contra constraints específicas.
- **Rastreabilidade de Decisão:** Cada decisão de raciocínio (L2) e ação de escrita (L4) é registrada e auditável.
- **Sincronização de Estado:** As `Micro Sync Barriers` garantem que o estado do sistema esteja consistente antes de qualquer agente prosseguir.


---

## 8. Rigor Estatístico e Validação de Machine Learning (L4 & L5)

O Genesis-Writer v5.0 integra agentes especializados para garantir o mais alto rigor em análises quantitativas:
- **Agentes de Análise Estatística:** Realizam análises descritivas, inferenciais e multivariadas, com validação de pressupostos e interpretação de resultados.
- **Agentes de Machine Learning:** Desenvolvem, treinam e avaliam modelos de ML, com foco em validação cruzada, interpretabilidade e mitigação de vieses.
- **Statistical Validation Harness (L5 - Confiança Zero):** Um subcomponente da Camada L5 que verifica a correção metodológica das análises estatísticas, a adequação dos testes e a robustez dos resultados. Inclui verificação de p-valores, intervalos de confiança e tamanhos de efeito, operando sob o princípio de "Confiança Zero".
- **ML Model Audit (L5 - Confiança Zero):** Auditoria de modelos de ML para garantir a validade interna e externa, a generalização e a ética dos algoritmos utilizados. Inclui análise de métricas de desempenho, curvas ROC, e matrizes de confusão, também sob o princípio de "Confiança Zero".


---

## 9. Auditoria de Citações de Alto Impacto em 7 Níveis (L5)

O protocolo de auditoria de citações foi expandido para além da autenticidade, focando na relevância e impacto acadêmico:
- **Citation Impact Auditor (L5 - Auditoria Forense):** Este agente verifica o fator de impacto do periódico, o índice H do autor, o número de citações do artigo e a relevância Qualis A1 da fonte. Ele prioriza a inclusão de literatura seminal e de ponta, garantindo que o texto seja fundamentado nas pesquisas mais influentes e atuais. Opera em modo de "Auditoria Forense", exigindo DOI, verificação em bases como Scopus/Web of Science e extração direta de trechos para validação.
- **Harness de Veracidade (L0 & L5 - Auditoria Forense):** Continua a garantir a autenticidade (DOI real, URL, trecho original) e agora também a relevância Qualis A1 da fonte, com o mesmo rigor de auditoria forense.


---

## 10. Pesquisador Metodológico Perfeito e Arquiteto de Conhecimento Crítico (L1 & L2)

O Genesis-Writer v5.0 integra novas capacidades para atuar como um pesquisador e revisor de elite:
- **Motor de Insights de Variáveis Cruzadas (L1):** Este novo componente na Camada L1 realiza cruzamentos complexos de dados e teorias para identificar correlações não óbvias, revelando novos insights, soluções ou fatos que seriam imperceptíveis em análises convencionais. Ele busca ativamente por "gaps" de conhecimento e oportunidades de contribuição original.
- **Agente de Análise Crítica de Gaps (L2):** Localizado na Camada L2, este agente é especializado em identificar lacunas teóricas e metodológicas na literatura existente. Ele utiliza raciocínios complexos para propor abordagens inovadoras para cobrir esses gaps, garantindo que a pesquisa seja sempre relevante e contribua significativamente para o campo.
- **Revisor Teórico Minucioso (L4 - Subagente de Busca Bibliográfica Avançada):** O Agente de Busca Bibliográfica Avançada (A4.13) agora incorpora um subagente especializado em revisão teórica minuciosa. Ele não apenas busca referências, mas as analisa criticamente, buscando correlações lógicas e inconsistências, e sugerindo como preencher os gaps identificados pelo Agente de Análise Crítica de Gaps.
