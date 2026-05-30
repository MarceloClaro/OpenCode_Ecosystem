<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# TMA Handoff Template

**Padrão de Entrega Entre Agentes**

Use este template para padronizar a entrega de artefatos entre agentes no pipeline TMA.

---

## 1. Informações de Handoff

| Campo | Valor |
|-------|-------|
| **De (Agente)** | A[N] (Papel) |
| **Para (Agente)** | A[N+1] (Papel) |
| **Fase** | [Embedding/Attention/Feed-Forward/Add & Norm/Decoding/Evolution] |
| **Timestamp** | YYYY-MM-DD HH:MM:SS UTC |
| **Sync Barrier ID** | SB-[Phase]-[Sequence] |
| **Status** | [PENDING/IN_PROGRESS/CHECKPOINT/COMMITTED] |

---

## 2. Artefatos Entregues

### 2.1 Artefatos Principais
- [ ] `[artifact_name].json` - Descrição e propósito
- [ ] `[artifact_name].py` - Código-fonte ou script
- [ ] `[artifact_name].md` - Documentação

### 2.2 Checksum e Integridade
```
SHA256: [hash_do_artefato]
Tamanho: [bytes]
Formato: [json/python/markdown/binary]
```

---

## 3. Contexto da Entrega

### 3.1 Operações Completadas
- [x] Operação 1: [Descrição]
- [x] Operação 2: [Descrição]
- [ ] Operação 3: [Descrição] (pendente)

### 3.2 Métricas da Fase
| Métrica | Valor | Status |
|---------|-------|--------|
| Success Rate | 95% | ✓ OK |
| Execution Time | 2.3s | ✓ OK |
| Quality Score | 0.88 | ⚠️ REVIEW |
| Resource Usage | 45% | ✓ OK |

### 3.3 Dependências Satisfeitas
- [x] Dependência 1: [Descrição]
- [x] Dependência 2: [Descrição]
- [ ] Dependência 3: [Descrição] (bloqueante)

---

## 4. Instruções para Próximo Agente

### 4.1 Pré-requisitos
1. Validar checksum dos artefatos
2. Verificar formato e estrutura
3. Confirmar todas as dependências satisfeitas

### 4.2 Próximas Ações
1. [Ação 1]
2. [Ação 2]
3. [Ação 3]

### 4.3 Pontos de Atenção
- ⚠️ [Ponto crítico 1]
- ⚠️ [Ponto crítico 2]
- ℹ️ [Informação importante]

---

## 5. Consenso e Aprovação

### 5.1 Validação de Especialistas
| Especialista | Status | Comentário |
|--------------|--------|-----------|
| A[N] (Remetente) | ✓ Aprovado | Artefatos prontos |
| A[N+1] (Destinatário) | ⏳ Pendente | Aguardando revisão |
| A3 (Mediador) | ⏳ Pendente | Aguardando consenso |

### 5.2 Assinatura Digital
```
Assinado por: [Agent ID]
Timestamp: [ISO 8601]
Signature: [SHA256 hash]
```

---

## 6. Rastreamento e Auditoria

### 6.1 Histórico de Versões
| Versão | Data | Alteração |
|--------|------|-----------|
| 1.0 | YYYY-MM-DD | Versão inicial |
| 1.1 | YYYY-MM-DD | Correção de bug |

### 6.2 Referências de Commit Git
- Commit de origem: `[hash] [TMA-Phase] [message]`
- Commit de destino: (será criado após aceitar handoff)

### 6.3 Rastreamento de Linhagem
```json
{
  "handoff_id": "hoff-[phase]-[sequence]",
  "source_agent": "A[N]",
  "target_agent": "A[N+1]",
  "phase": "[Phase Name]",
  "artifacts": ["artifact1", "artifact2"],
  "fitness_delta": +0.05,
  "timestamp": "2026-04-14T15:30:00Z"
}
```

---

## 7. Exemplo de Preenchimento

### Exemplo: Embedding → Attention

**De:** A1 (Embedding Specialist)  
**Para:** A2 (Attention Analyst)  
**Fase:** Attention  
**Timestamp:** 2026-04-14 15:30:00 UTC

#### Artefatos Entregues
- `token_inicial.json` - Contexto mapeado e requisitos extraídos
- `domain_model.py` - Modelo de domínio estruturado
- `embedding_report.md` - Relatório de análise

#### Métricas
| Métrica | Valor |
|---------|-------|
| Success Rate | 100% |
| Execution Time | 1.8s |
| Quality Score | 0.92 |

#### Próximas Ações para A2
1. Validar estrutura do domain_model.py
2. Executar análise de impacto
3. Identificar riscos e dependências
4. Propor estratégia de consenso

---

**Nota:** Preencha todos os campos obrigatórios (marcados com *). Campos opcionais podem ser deixados em branco se não aplicáveis.
