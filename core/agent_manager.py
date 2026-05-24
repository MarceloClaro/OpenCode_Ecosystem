"""
core/agent_manager.py — Gerenciamento do Ciclo de Vida de Agentes com DI.

Registro, criação, execução e monitoramento de agentes.
Agentes são unidades autônomas de processamento com ciclo de vida
definido: INIT → RUN → HEALTH_CHECK → DESTROY.

Uso com DI (novo):
    container = Container.instance()
    manager = AgentManager(container=container)
    manager.register_agent_type("reversa-scout", ScoutAgent)
    agent_id = await manager.create_agent("reversa-scout", {"target": "./src"})
    result = await manager.run_agent(agent_id)

Uso legado (compatível):
    manager = AgentManager()
    # Funciona exatamente como antes
"""

from __future__ import annotations

import enum
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional, Protocol

from core.errors import AgentError, NotFoundError

logger = logging.getLogger(__name__)


class AgentStatus(enum.Enum):
    """Estados possíveis de um agente."""
    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DESTROYED = "destroyed"


# ── Protocolo Base para Agentes ────────────────────────────────────


class Agent(Protocol):
    """Protocolo que todos os agentes devem implementar."""

    async def initialize(self, config: dict[str, Any]) -> None:
        """Inicializa o agente com configuração."""
        ...

    async def execute(self, context: dict[str, Any]) -> Any:
        """Executa a tarefa principal do agente."""
        ...

    async def health_check(self) -> dict[str, Any]:
        """Retorna status de saúde do agente."""
        ...

    async def destroy(self) -> None:
        """Limpa recursos do agente."""
        ...


# ── Definição de Tipo ──────────────────────────────────────────────


@dataclass
class AgentTypeDef:
    """Definição de um tipo de agente registrado."""
    name: str
    description: str
    version: str = "1.0.0"


@dataclass
class AgentInstance:
    """Instância em execução de um agente."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    type_name: str = ""
    status: AgentStatus = AgentStatus.CREATED
    config: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    health: dict[str, Any] = field(default_factory=dict)


# ── AgentManager ───────────────────────────────────────────────────


class AgentManager:
    """Gerenciador central de agentes com suporte a DI.

    Responsável por:
    - Registrar tipos de agente
    - Criar instâncias com configuração
    - Executar agentes com ciclo de vida completo
    - Monitorar health checks
    - Destruir agentes e limpar recursos

    DI: Se um Container for fornecido, os agentes criados podem
    resolver dependências através dele. O próprio AgentManager
    se registra como 'agent_manager' no container.
    """

    def __init__(self, container: Any = None) -> None:
        self._types: dict[str, type] = {}
        self._type_defs: dict[str, AgentTypeDef] = {}
        self._instances: dict[str, AgentInstance] = {}
        self._agents: dict[str, Agent] = {}
        self._container = container

        # Auto-registro no Container DI
        if container is not None and not container.is_registered('agent_manager'):
            container.register('agent_manager', self)

    # ── Registro de Tipos ──────────────────────────────────────────

    def register_agent_type(
        self,
        name: str,
        agent_class: type,
        description: str = "",
        version: str = "1.0.0",
    ) -> None:
        """Registra um novo tipo de agente.

        Args:
            name: Nome único do tipo (ex: "reversa-scout").
            agent_class: Classe do agente (deve implementar Protocol Agent).
            description: Descrição do agente.
            version: Versão do agente.

        Raises:
            AgentError: Se o tipo já estiver registrado.
        """
        if name in self._types:
            raise AgentError(f"Agent type '{name}' already registered")
        self._types[name] = agent_class
        self._type_defs[name] = AgentTypeDef(
            name=name, description=description, version=version
        )
        logger.info("Registered agent type '%s' (v%s)", name, version)

    def unregister_agent_type(self, name: str) -> bool:
        """Remove um tipo de agente registrado."""
        if name in self._types:
            del self._types[name]
            del self._type_defs[name]
            logger.info("Unregistered agent type '%s'", name)
            return True
        return False

    def get_type_def(self, name: str) -> Optional[AgentTypeDef]:
        """Retorna a definição de um tipo."""
        return self._type_defs.get(name)

    def list_types(self) -> list[AgentTypeDef]:
        """Lista todos os tipos de agente registrados."""
        return list(self._type_defs.values())

    # ── Criação de Instâncias ─────────────────────────────────────

    async def create_agent(
        self,
        type_name: str,
        config: Optional[dict[str, Any]] = None,
        agent_id: Optional[str] = None,
    ) -> str:
        """Cria uma nova instância de agente.

        Args:
            type_name: Nome do tipo registrado.
            config: Configuração específica da instância.
            agent_id: ID opcional (caso contrário, gerado automaticamente).

        Returns:
            ID da instância criada.

        Raises:
            NotFoundError: Se o tipo não estiver registrado.
            AgentError: Se a inicialização falhar.
        """
        agent_class = self._types.get(type_name)
        if agent_class is None:
            raise NotFoundError(f"Agent type '{type_name}' not registered")

        instance = AgentInstance(
            id=agent_id or uuid.uuid4().hex[:12],
            type_name=type_name,
            config=config or {},
        )
        instance.status = AgentStatus.INITIALIZING

        try:
            agent = agent_class(container=self._container) if self._container else agent_class()
            await agent.initialize(instance.config)
            instance.status = AgentStatus.READY
            self._instances[instance.id] = instance
            self._agents[instance.id] = agent
            logger.info(
                "Created agent %s (%s)", instance.id[:8], type_name
            )
            return instance.id
        except Exception as e:
            instance.status = AgentStatus.FAILED
            instance.error = f"{type(e).__name__}: {e}"
            self._instances[instance.id] = instance
            raise AgentError(
                f"Failed to initialize agent '{type_name}': {e}",
                original=e,
            )

    # ── Execução ───────────────────────────────────────────────────

    async def run_agent(
        self,
        agent_id: str,
        context: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Executa um agente com ciclo de vida completo.

        Fluxo: READY → RUNNING → COMPLETED/FAILED

        Args:
            agent_id: ID da instância.
            context: Contexto de execução.

        Returns:
            Resultado da execução.

        Raises:
            NotFoundError: Se o agente não existir.
            AgentError: Se o agente não estiver pronto.
        """
        instance = self._instances.get(agent_id)
        if instance is None:
            raise NotFoundError(f"Agent '{agent_id[:8]}' not found")

        if instance.status != AgentStatus.READY:
            raise AgentError(
                f"Agent '{agent_id[:8]}' is {instance.status.value}, expected READY"
            )

        agent = self._agents.get(agent_id)
        if agent is None:
            raise NotFoundError(f"Agent instance '{agent_id[:8]}' not found")

        instance.status = AgentStatus.RUNNING
        instance.started_at = time.time()

        try:
            result = await agent.execute(context or {})
            instance.status = AgentStatus.COMPLETED
            instance.result = result
            logger.info(
                "Agent %s (%s) completed", agent_id[:8], instance.type_name
            )
            return result
        except Exception as e:
            instance.status = AgentStatus.FAILED
            instance.error = f"{type(e).__name__}: {e}"
            logger.error(
                "Agent %s (%s) failed: %s",
                agent_id[:8], instance.type_name, e,
            )
            raise AgentError(
                f"Agent '{instance.type_name}' execution failed: {e}",
                original=e,
            )
        finally:
            instance.completed_at = time.time()

    # ── Health Check ───────────────────────────────────────────────

    async def health_check(self, agent_id: str) -> dict[str, Any]:
        """Executa health check em um agente."""
        instance = self._instances.get(agent_id)
        if instance is None:
            raise NotFoundError(f"Agent '{agent_id[:8]}' not found")

        agent = self._agents.get(agent_id)
        if agent is None:
            return {"status": "error", "message": "Agent instance not loaded"}

        try:
            health = await agent.health_check()
            instance.health = health
            return health
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    # ── Destruição ─────────────────────────────────────────────────

    async def destroy_agent(self, agent_id: str) -> bool:
        """Remove um agente, liberando recursos."""
        instance = self._instances.get(agent_id)
        if instance is None:
            return False

        agent = self._agents.get(agent_id)
        if agent is not None:
            try:
                await agent.destroy()
            except Exception as e:
                logger.warning("Error destroying agent %s: %s", agent_id[:8], e)

        instance.status = AgentStatus.DESTROYED
        del self._agents[agent_id]
        logger.info("Destroyed agent %s", agent_id[:8])
        return True

    # ── Consultas ──────────────────────────────────────────────────

    def get_instance(self, agent_id: str) -> Optional[AgentInstance]:
        """Retorna uma instância pelo ID."""
        return self._instances.get(agent_id)

    def list_instances(
        self,
        type_name: Optional[str] = None,
        status: Optional[AgentStatus] = None,
    ) -> list[AgentInstance]:
        """Lista instâncias com filtros opcionais."""
        result = list(self._instances.values())
        if type_name:
            result = [i for i in result if i.type_name == type_name]
        if status:
            result = [i for i in result if i.status == status]
        return result

    def count_by_status(self) -> dict[str, int]:
        """Contagem de instâncias por status."""
        counts: dict[str, int] = {}
        for inst in self._instances.values():
            counts[inst.status.value] = counts.get(inst.status.value, 0) + 1
        return counts

    def __repr__(self) -> str:
        return (
            f"AgentManager(types={len(self._types)}, "
            f"instances={len(self._instances)})"
        )
