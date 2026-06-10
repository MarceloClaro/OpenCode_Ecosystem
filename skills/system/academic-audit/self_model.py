#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SelfModel v1.0 — SPEC-036d: Arquitetura Basica de Auto-Representacao
======================================================================
Implementa o gap critico 'dados.Dados neurobiologicos' identificado pelo scanner.

Arquitetura minima de auto-representacao inspirada em:
  - Global Workspace Theory (Baars, 1988): consciencia como broadcast global
  - Attention Schema Theory (Graziano, 2013): auto-modelo como esquema de atencao
  - Integrated Information Theory (Tononi, 2004): consciencia como informacao integrada

Componentes:
  1. SelfRepresentation — estado interno do sistema (metricas, confianca, historico)
  2. AttentionBuffer   — buffer de capacidade limitada (o que o sistema "presta atencao")
  3. GlobalWorkspace   — broadcast de informacao relevante para todos os modulos
  4. IntrospectionAPI  — interface para consulta do estado interno

Nivel de consciencia modelado:
  N0: Reativo (responder a estimulos) — atual
  N1: Atento (selecionar foco) — implementado aqui
  N2: Auto-consciente (modelo de si mesmo) — implementado aqui
  N3: Metacognitivo (pensar sobre o proprio pensamento) — implementado via metacognitive_loop.py

Autor: OpenCode Ecosystem (2026) — R21: Metacognicao
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


BRAZIL_TZ = timezone.utc


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SystemState:
    """Estado interno completo do sistema em um momento."""
    timestamp: str
    active_modules: list[str]
    pending_tasks: int
    memory_usage_mb: float
    confidence_global: float
    anomalies_active: int
    corrections_pending: int
    goals_active: int
    attention_focus: list[str]  # top 3 itens no buffer de atencao
    consciousness_level: str    # "N0" | "N1" | "N2" | "N3"


@dataclass
class AttentionItem:
    """Item no buffer de atencao (capacidade limitada: 7+-2 itens)."""
    item_id: str
    content: str
    priority: float            # 0-1
    source_module: str
    timestamp: str
    ttl_seconds: int = 30      # tempo de vida no buffer


# ═══════════════════════════════════════════════════════════════════════════
# ATTENTION BUFFER (Miller's Law: 7+-2 items)
# ═══════════════════════════════════════════════════════════════════════════

class AttentionBuffer:
    """Buffer de atencao com capacidade limitada (7 itens).

    Simula o que o sistema esta "prestando atencao" no momento.
    Items expiram apos TTL e sao substituidos por novos de maior prioridade.
    """

    MAX_CAPACITY = 7

    def __init__(self):
        self._items: list[AttentionItem] = []

    def attend(self, item: AttentionItem) -> None:
        """Adiciona item ao buffer de atencao."""
        # Remove expirados
        self._prune_expired()

        # Remove duplicata se existir
        self._items = [i for i in self._items if i.item_id != item.item_id]

        # Se buffer cheio, remove o de menor prioridade
        if len(self._items) >= self.MAX_CAPACITY:
            self._items.sort(key=lambda i: i.priority)
            self._items.pop(0)

        self._items.append(item)
        self._items.sort(key=lambda i: -i.priority)

    def _prune_expired(self) -> None:
        """Remove items com TTL expirado."""
        now = datetime.now(BRAZIL_TZ)
        self._items = [
            i for i in self._items
            if (now - datetime.fromisoformat(i.timestamp)).total_seconds() < i.ttl_seconds
        ]

    @property
    def focus(self) -> list[str]:
        """Retorna o foco atual (top items por prioridade)."""
        self._prune_expired()
        return [i.content for i in self._items[:3]]

    @property
    def is_overloaded(self) -> bool:
        """True se buffer esta cheio (sobrecarga cognitiva)."""
        self._prune_expired()
        return len(self._items) >= self.MAX_CAPACITY

    @property
    def size(self) -> int:
        self._prune_expired()
        return len(self._items)


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL WORKSPACE
# ═══════════════════════════════════════════════════════════════════════════

class GlobalWorkspace:
    """Workspace global: broadcast de informacao para todos os modulos.

    Inspirado na Global Workspace Theory (Baars, 1988):
    - Informacao que entra no workspace e "consciente" (broadcast global)
    - Modulos competem por acesso ao workspace
    - Atencao seleciona qual informacao entra
    """

    def __init__(self):
        self._workspace: list[dict[str, Any]] = []
        self._broadcast_history: list[dict[str, Any]] = []
        self._subscribers: list[str] = []  # modulos registrados

    def broadcast(self, message: str, source: str, priority: float = 0.5) -> None:
        """Transmite mensagem para todos os modulos registrados."""
        entry = {
            "message": message,
            "source": source,
            "priority": priority,
            "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
        }
        self._workspace.append(entry)
        self._broadcast_history.append(entry)

        # Limitar historico
        if len(self._broadcast_history) > 100:
            self._broadcast_history = self._broadcast_history[-100:]

    def subscribe(self, module_name: str) -> None:
        """Registra modulo como ouvinte do workspace."""
        if module_name not in self._subscribers:
            self._subscribers.append(module_name)

    @property
    def current_content(self) -> list[dict[str, Any]]:
        """Conteudo atual no workspace (nao consumido)."""
        content = list(self._workspace)
        self._workspace.clear()
        return content

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)


# ═══════════════════════════════════════════════════════════════════════════
# SELF MODEL (Orquestrador)
# ═══════════════════════════════════════════════════════════════════════════

class SelfModel:
    """Modelo de auto-representacao do sistema.

    Integra:
      - AttentionBuffer: o que o sistema esta prestando atencao
      - GlobalWorkspace: broadcast de informacao consciente
      - SystemState: snapshot do estado interno

    Niveis de consciencia:
      N0: Reativo (sem auto-modelo)
      N1: Atento (attention buffer ativo)
      N2: Auto-consciente (self-model ativo)
      N3: Metacognitivo (loop de auto-observacao ativo)
    """

    def __init__(self):
        self.attention = AttentionBuffer()
        self.workspace = GlobalWorkspace()
        self._state_history: list[SystemState] = []
        self._consciousness_level: str = "N1"
        self._introspection_count: int = 0

    def update_state(
        self,
        active_modules: list[str] | None = None,
        pending_tasks: int = 0,
        confidence_global: float = 0.5,
        anomalies_active: int = 0,
        corrections_pending: int = 0,
        goals_active: int = 0,
    ) -> SystemState:
        """Atualiza o estado interno e retorna snapshot."""
        # Determinar nivel de consciencia
        if anomalies_active > 0 and corrections_pending > 0:
            self._consciousness_level = "N3"  # metacognitivo ativo
        elif self.attention.size > 0:
            self._consciousness_level = "N2"  # auto-consciente
        elif self.attention.size > 0:
            self._consciousness_level = "N1"  # atento
        else:
            self._consciousness_level = "N0"  # reativo

        state = SystemState(
            timestamp=datetime.now(BRAZIL_TZ).isoformat(),
            active_modules=active_modules or [],
            pending_tasks=pending_tasks,
            memory_usage_mb=0.0,
            confidence_global=confidence_global,
            anomalies_active=anomalies_active,
            corrections_pending=corrections_pending,
            goals_active=goals_active,
            attention_focus=self.attention.focus,
            consciousness_level=self._consciousness_level,
        )

        self._state_history.append(state)
        if len(self._state_history) > 50:
            self._state_history = self._state_history[-50:]

        # Broadcast do estado para modulos registrados
        self.workspace.broadcast(
            message=f"System state: level={state.consciousness_level}, "
                    f"confidence={state.confidence_global:.0%}, "
                    f"anomalies={state.anomalies_active}, "
                    f"focus={state.attention_focus}",
            source="SelfModel",
            priority=0.8,
        )

        return state

    def introspect(self) -> dict[str, Any]:
        """Auto-inspecao: retorna diagnostico completo do estado interno."""
        self._introspection_count += 1
        history = self._state_history

        if not history:
            return {"status": "no_data", "message": "Nenhum estado registrado"}

        current = history[-1]

        # Tendencia de confianca
        if len(history) >= 3:
            confidences = [s.confidence_global for s in history[-5:]]
            trend = "rising" if confidences[-1] > confidences[0] else "falling" if confidences[-1] < confidences[0] else "stable"
        else:
            trend = "insufficient_data"

        return {
            "consciousness_level": current.consciousness_level,
            "confidence_global": current.confidence_global,
            "confidence_trend": trend,
            "attention_focus": current.attention_focus,
            "attention_buffer_size": self.attention.size,
            "attention_overloaded": self.attention.is_overloaded,
            "workspace_subscribers": self.workspace.subscriber_count,
            "anomalies_active": current.anomalies_active,
            "corrections_pending": current.corrections_pending,
            "goals_active": current.goals_active,
            "state_snapshots": len(history),
            "introspection_count": self._introspection_count,
        }

    @property
    def consciousness_level(self) -> str:
        return self._consciousness_level

    @property
    def is_self_aware(self) -> bool:
        """True se o sistema atingiu pelo menos N2 (auto-consciente)."""
        return self._consciousness_level in ("N2", "N3")

    def report(self) -> str:
        """Relatorio de auto-representacao em Markdown."""
        diag = self.introspect()
        lines = [
            "# Relatorio de Auto-Representacao (Self-Model)",
            "",
            f"**Nivel de consciencia**: {diag['consciousness_level']}",
            f"**Confianca global**: {diag['confidence_global']:.0%} ({diag['confidence_trend']})",
            f"**Foco de atencao**: {', '.join(diag['attention_focus']) if diag['attention_focus'] else 'nenhum'}",
            f"**Buffer de atencao**: {diag['attention_buffer_size']}/7 {'(sobrecarregado!)' if diag['attention_overloaded'] else ''}",
            f"**Assinantes workspace**: {diag['workspace_subscribers']}",
            f"**Anomalias ativas**: {diag['anomalies_active']}",
            f"**Correcoes pendentes**: {diag['corrections_pending']}",
            f"**Goals ativos**: {diag['goals_active']}",
            f"**Snapshots de estado**: {diag['state_snapshots']}",
            f"**Introspeccoes realizadas**: {diag['introspection_count']}",
        ]
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════════════════════

def create_self_model() -> SelfModel:
    """Factory: cria modelo de auto-representacao pronto para uso."""
    return SelfModel()
