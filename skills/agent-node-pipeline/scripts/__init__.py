"""
Agent Node Pipeline (ANP) — Framework de Agentes como Pipelines de Nós Tipados.

Inspirado pelos motores QueryEngine, MediaEngine e InsightEngine do
BettaFish (666ghj/BettaFish). Generalizado como padrão P16 do Reversa.

P17 — MiddlewareChain: Pipeline de middlewares inspirado pelo DeerFlow
11-layer Middleware Pipeline (ByteDance).
"""

from .base_node import BaseNode, StateMutationNode
from .pipeline_state import PipelineState, Phase, NodeResult
from .llm_client import LLMClient
from .pipeline import AgentNodePipeline
from .node_types import (
    TransformNode,
    LLMQueryNode,
    SearchNode,
    ReflectNode,
    StructureNode,
    SummaryNode,
    FormatNode,
)
from .middleware_chain import (
    BaseMiddleware,
    MiddlewareChain,
    LoggingMiddleware,
    TimingMiddleware,
    ValidationMiddleware,
    RetryMiddleware,
    CheckpointMiddleware,
    SummarizationMiddleware,
    DanglingCallMiddleware,
    StatsMiddleware,
    create_default_chain,
)

__all__ = [
    # P16 — Base
    "BaseNode",
    "StateMutationNode",
    "PipelineState",
    "Phase",
    "NodeResult",
    "LLMClient",
    "AgentNodePipeline",
    # P16 — Node Types
    "TransformNode",
    "LLMQueryNode",
    "SearchNode",
    "ReflectNode",
    "StructureNode",
    "SummaryNode",
    "FormatNode",
    # P17 — MiddlewareChain
    "BaseMiddleware",
    "MiddlewareChain",
    "LoggingMiddleware",
    "TimingMiddleware",
    "ValidationMiddleware",
    "RetryMiddleware",
    "CheckpointMiddleware",
    "SummarizationMiddleware",
    "DanglingCallMiddleware",
    "StatsMiddleware",
    "create_default_chain",
]
