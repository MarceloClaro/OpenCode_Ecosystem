# Fluxo de Pesquisa Acadêmica para Computação Quântica

Este guia integra o `academic-pipeline` para garantir rigor e integridade em publicações de QML.

## Estágios do Pipeline Quântico

| Estágio | Atividade Quântica | Ferramenta/Skill |
| :--- | :--- | :--- |
| **1. Pesquisa** | Revisão bibliográfica de ansätze e algoritmos SOTA. | `deep-research` |
| **2. Escrita** | Descrição formal do circuito e formulação matemática. | `academic-paper` |
| **2.5 Integridade** | Verificação de fidelidade de simulação e consistência de dados. | `integrity_verification_agent` |
| **3. Revisão** | Avaliação crítica da vantagem quântica proposta. | `academic-paper-reviewer` |

## Verificação de Integridade (Stage 2.5)
Para artigos quânticos, a verificação de integridade deve focar em:
- **Reprodutibilidade**: Disponibilidade de sementes aleatórias (random seeds) e configurações de hardware.
- **Citações**: Garantir que as bibliotecas (Qiskit, PennyLane) sejam citadas corretamente com suas versões específicas.
- **Dados**: Verificação de que os gráficos de convergência correspondem aos logs de execução.

## Formatação de Referências
Utilize o padrão BibTeX para citações quânticas, garantindo a inclusão de DOIs para artigos do arXiv e periódicos da APS/IEEE.
