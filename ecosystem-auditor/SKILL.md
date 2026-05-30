---
name: ecosystem-auditor
description: "Automatiza a auditoria, diagnóstico e correção de ecossistemas multiagentes complexos. Use para: realizar varreduras técnicas, identificar falhas de integração, verificar dependências, executar testes de sanidade e aplicar correções automáticas em arquiteturas como a do NEXUS-ULTRA-ECOSYSTEM."
---

# Ecosystem Auditor

## Visão Geral

A skill **Ecosystem Auditor** foi projetada para garantir a integridade e o funcionamento otimizado de ecossistemas multiagentes, especialmente aqueles baseados na arquitetura Transformer como o NEXUS-ULTRA-ECOSYSTEM. Ela automatiza o processo de auditoria, desde a análise estática de código até a execução de testes de integração, identificando e reportando quaisquer inconsistências, erros ou bugs.

## Funcionalidades Principais

*   **Análise Estática de Código:** Verifica a sintaxe e a estrutura dos scripts Python em busca de erros básicos.
*   **Verificação de Dependências:** Garante que todos os módulos e skills necessários podem ser importados e estão acessíveis.
*   **Testes de Integração:** Executa um conjunto de testes de sanidade para validar o roteamento de tarefas e a funcionalidade básica das skills integradas (Jurídico, BSDT, Acadêmico, Sci-Hub).
*   **Geração de Relatórios:** Produz um relatório detalhado com todas as descobertas, incluindo erros, avisos e um resumo do status da auditoria.

## Como Usar

Para auditar um ecossistema, execute o script `audit_ecosystem.py` localizado no diretório `scripts/` desta skill. O script irá realizar uma auditoria completa e imprimir um relatório JSON com os resultados.

```bash
python3 /home/ubuntu/skills/ecosystem-auditor/scripts/audit_ecosystem.py
```

O relatório de saída incluirá:

*   `status`: `PASSED` se nenhum erro crítico for encontrado, `FAILED` caso contrário.
*   `findings`: Uma lista de todos os problemas identificados (erros, avisos, informações).
*   `summary`: Um resumo conciso dos resultados da auditoria.

## Recursos

### scripts/

*   `audit_ecosystem.py`: O script principal que orquestra todas as etapas da auditoria do ecossistema.

### references/

*   `audit_guidelines.md`: (TODO) Documentação detalhada sobre as diretrizes e critérios de auditoria utilizados.
