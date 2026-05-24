---
name: followup-advocacia
description: "Skill do ecossistema OpenCode - followup-advocacia"
---


name: followup-advocacia
description: >
  Rotina de follow-up para escritorio de advocacia: lembretes de prazos,
  cadencia de contatos, pipeline de demandas e produtividade.
  Use quando usuario mencionar "follow-up", "lembrete", "prazo", "pipeline",
  "produtividade escritorio", "cadencia", "relatorio semanal", "rotina OAB".
---

---
name: followup-advocacia
description: >
  Rotina de follow-up para escritorio de advocacia: lembretes de prazos,
  cadencia de contatos, pipeline de demandas e produtividade.
  Use quando usuario mencionar "follow-up", "lembrete", "prazo", "pipeline",
  "produtividade escritorio", "cadencia", "relatorio semanal", "rotina OAB".
---

# Follow-up Advocacia — Produtividade e Gestao de Demandas



## Principio Central

Todo advogado precisa de sistema simples para nunca perder prazo,
manter contato com cliente e acompanhar pipeline de demandas.
Este follow-up opera em 3 camadas: diaria, semanal e mensal.


> *Detalhes de "Camada Diaria (Ritual Matinal)" em `references/`*



## Camada Semanal (Revisao de Sexta)

### Checklist Semanal

1. **Novos andamentos:** Verificar sistemas dos tribunais
2. **Clientes sem retorno:** Contatar quem nao respondeu na semana
3. **Prazo da semana que vem:** Antecipar tarefas
4. **Novos leads:** Avaliar status do funil deCaptação
5. **Honorarios:** Verificar inadimplencia

### Relatorio Semanal

```
SEMANA [DD a DD/MM/AAAA]
==========

AUDiencias: [N]
Prazos cumpridos: [N]
Novos processos: [N]
Clientes contatados: [N]
Honorarios recebidos: R$ [valor]
Clientes inadimplentes: [N]

OBSERVACOES:
- [items relevantes]

PROXIMA SEMANA:
- [N] prazos a vencer
- [N] audiencias agendadas
```


> *Detalhes de "Camada Mensal (Gestao Estrategica)" em `references/`*



## Integracao com MCPs

- **time (mcp-time):** Agendar lembretes de prazos
- **sqlite (mcp-server-sqlite):** Armazenar log de contatos
- **websearch:** Verificar prazos em tribunais
- **fetch:** Acessar sistemas de tribunais



## Sistema de Alertas

| Tipo | Trigger | Acao |
|------|---------|------|
| URGENTE | Prazo < 48h | Contato imediato |
| ALTO | Prazo < 5 dias | Alerta hoje |
| MEDIO | Prazo < 15 dias | Agendar revisao |
| BAIXO | Prazo > 15 dias | Revisao semanal |

