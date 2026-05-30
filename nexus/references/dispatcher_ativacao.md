<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# Dispatcher de Ativação Multiagente Evolutivo: Auto-Otimização e Aprendizado

Este documento define a lógica de orquestração evolutiva e os protocolos de auto-otimização do sistema multiagente.

## 1. Pipeline de Execução Evolutivo com Barreiras Dinâmicas

| Fase | Agentes Ativados | Gatilho de Entrada | Barreira Dinâmica (Dynamic Barrier) | Artefato de Saída |
| :--- | :--- | :--- | :--- | :--- |
| **F1: Embedding** | A1 (Contexto) | Requisito Bruto | **DB1:** Validação de Requisitos (Rigor Evolutivo) | `token_inicial.json` |
| **F2: Attention** | A2 (Impacto), A3 (Heads) | `token_inicial.json` | **DB2:** Protocolo de Consenso (Otimizado por RL) | `consenso_design.json` |
| **F3: Feed-Forward** | A4 (Execução) | `consenso_design.json` | **DB3:** Validação de Testes (Mutação de Testes) | Código + Testes |
| **F4: Add & Norm** | A5 (QA/Refino) | Código + Testes | **DB4:** Checksum de Arquitetura (Auto-Audit) | Código Final Revisado |
| **F5: Decoding** | A6 (Entrega) | Código Final | **DB5:** Auditoria de Documentação (Evolutiva) | Pacote de Entrega |
| **F6: Evolution** | A7 (Optimizer) | `evolution_log.json` | **DB6:** Validação de Mutação (Fitness Check) | `evolution_report.json` |

## 2. Protocolo de Auto-Otimização (Fase 6)

Na Fase 6, o Agente de Evolução (A7) atua sobre o pipeline para otimizar o próximo ciclo:

1. **Análise de Fitness:** O A7 calcula o score de eficácia do ciclo atual com base em:
   - Cobertura de Testes (Target: >90%).
   - Débito Técnico (Target: <5%).
   - Velocidade de Sincronização (Target: <300s por fase).
2. **Mutação de Prompts:** Se o score estiver abaixo do baseline, o A7 gera novas versões das instruções dos agentes (prompts) para corrigir falhas recorrentes.
3. **Ajuste de Barreiras:** O sistema aprende a aumentar ou diminuir o rigor das barreiras (DB1-DB5) dinamicamente.
4. **Publicação de Lições Aprendidas:** O Agente de Memória de Longo Prazo (A8) atualiza a base de conhecimento no `system_state.json`.

## 3. Mecanismo de "Genetic Feedback" e Rollback Evolutivo

O Dispatcher monitora a eficácia das mutações aplicadas:

- **Validação de Mutação:** Se uma mutação (ex: novo prompt para A4) resultar em uma queda no Fitness Score, o sistema realiza um **Rollback Evolutivo** para a versão anterior estável.
- **Relatório de Evolução:** Um `evolution_report.json` é gerado detalhando quais mutações foram bem-sucedidas e quais foram descartadas.

## 4. KV Store Evolutiva (Estado do Sistema)

O arquivo `system_state.json` agora é o repositório central de inteligência evolutiva:

```json
{
  "project_id": "UUID",
  "evolution_version": "2.1.0",
  "fitness_score": 0.92,
  "learned_patterns": [
    "Increase DB1 rigor for legacy integration tasks",
    "Prefer Strategy over Factory for payment modules"
  ],
  "active_mutations": {
    "A4_prompt_v3": "Added explicit check for O(n) complexity",
    "DB2_timeout": "Increased to 300s for high-conflict domains"
  },
  "last_stable_commit": "HASH",
  "checksum_input": "HASH_F1",
  "consensus_status": "READY"
}
```

## 5. Regras de Transição Evolutiva

- **F5 -> F6:** Requer `evolution_log.json` completo do ciclo atual.
- **F6 -> F1 (Próximo Ciclo):** Requer `evolution_report.json` validado e mutações aplicadas.
