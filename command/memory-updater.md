<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Inspirado pelo GraphMemoryUpdater do MiroFish-Offline (graph_memory_updater.py).
-->

---
description: >
  Atualiza grafos em tempo real com atividades de agentes em simulação.
  Buffer por plataforma (twitter/reddit) com envio em lotes de 5.
  Modos: start, simulate, stop, stats.
  Uso: /memory-updater [start|simulate|stop|stats] [--graph <id>] [--rounds N]
  Exemplos:
    /memory-updater start --graph demo
    /memory-updater simulate --graph demo --rounds 10
    /memory-updater stop --simulation sim_20260517_123456
pinned: false
---

# Graph Memory Updater

Ativa o **Graph Memory Updater** para registrar atividades em tempo real.

```
/memory-updater <modo> [opções]
```

| Modo | Descrição | Opções |
|------|-----------|--------|
| `start` | Iniciar monitoramento | `--graph` |
| `simulate` | Simular atividades | `--graph`, `--rounds` |
| `stop` | Parar simulação | `--simulation` |
| `stats` | Métricas | — |

### Exemplo

```
/memory-updater simulate --graph demo --rounds 10
→ 🎲 Simulando 10 rodadas...
→ Rodada 10/10 — Total: 35, Enviados: 7, Falhas: 0
→ ✅ Conclusão: 35 atividades, 7 lotes, 0 falhas
```
