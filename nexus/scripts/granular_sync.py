# -*- coding: utf-8 -*-
# SAÃDA OBRIGATÃ“RIA: PORTUGUÃŠS BRASILEIRO FORMAL
# Toda resposta ao usuÃ¡rio DEVE ser em portuguÃªs do Brasil formal.
# Contexto em chinÃªs para eficiÃªncia de tokens (densidade +40%%).
# Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)

#!/usr/bin/env python3
"""
Granular Synchronization: Operation-level barriers and checkpoints.

Enables:
- Sub-phase synchronization (not just phase-level)
- Per-operation checkpoints and rollback
- Dependency tracking at operation granularity
- Atomic transaction semantics
- Distributed consensus at operation level
"""

import json
from typing import Any, Dict, List, Optional, Set, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timezone
import hashlib


class OperationStatus(Enum):
    """Status of an operation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    CHECKPOINT = "checkpoint"
    COMMITTED = "committed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class SyncBarrierType(Enum):
    """Types of synchronization barriers."""
    OPERATION = "operation"  # Single operation
    TRANSACTION = "transaction"  # Multiple related operations
    PHASE = "phase"  # TMA phase boundary
    CONSENSUS = "consensus"  # Requires specialist agreement
    CRITICAL = "critical"  # Cannot be rolled back


@dataclass
class OperationCheckpoint:
    """Checkpoint of an operation state."""
    checkpoint_id: str
    operation_id: str
    phase: str
    agent_id: str
    state_hash: str
    artifacts: Dict[str, str] = field(default_factory=dict)  # artifact_name -> path
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class OperationDependency:
    """Dependency relationship between operations."""
    dependent_op_id: str
    prerequisite_op_id: str
    dependency_type: str = "sequential"  # sequential, parallel, conditional
    condition: Optional[str] = None  # Condition for conditional dependencies


@dataclass
class SyncBarrier:
    """Synchronization barrier for operations."""
    barrier_id: str
    barrier_type: SyncBarrierType
    phase: str
    operation_ids: List[str]
    required_consensus: List[str] = field(default_factory=list)  # Agent IDs
    status: OperationStatus = OperationStatus.PENDING
    checkpoints: Dict[str, OperationCheckpoint] = field(default_factory=dict)
    created_at: str = ""
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
    
    def is_ready(self) -> bool:
        """Check if barrier is ready to proceed."""
        return self.status in [OperationStatus.CHECKPOINT, OperationStatus.COMMITTED]


@dataclass
class GranularOperation:
    """Atomic operation with fine-grained tracking."""
    operation_id: str
    phase: str
    agent_id: str
    operation_type: str  # e.g., "code_generation", "test_execution"
    status: OperationStatus = OperationStatus.PENDING
    dependencies: List[OperationDependency] = field(default_factory=list)
    checkpoints: List[OperationCheckpoint] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: int = 0
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
    
    def get_latest_checkpoint(self) -> Optional[OperationCheckpoint]:
        """Get most recent checkpoint."""
        return self.checkpoints[-1] if self.checkpoints else None
    
    def can_proceed(self, operations_map: Dict[str, 'GranularOperation']) -> bool:
        """Check if all dependencies are satisfied."""
        for dep in self.dependencies:
            if dep.dependency_type == "sequential":
                prereq = operations_map.get(dep.prerequisite_op_id)
                if not prereq or prereq.status != OperationStatus.COMMITTED:
                    return False
            elif dep.dependency_type == "conditional":
                # Evaluate condition
                if dep.condition and not self._evaluate_condition(dep.condition, operations_map):
                    return False
        return True
    
    def _evaluate_condition(self, condition: str, operations_map: Dict[str, 'GranularOperation']) -> bool:
        """Evaluate a condition string safely using AST."""
        import ast
        ALLOWED = (ast.Expression, ast.BoolOp, ast.Compare, ast.Attribute,
                   ast.Subscript, ast.Constant, ast.Name, ast.Load,
                   ast.And, ast.Or, ast.Eq, ast.NotEq, ast.Lt, ast.LtE,
                   ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn,
                   ast.UnaryOp, ast.Not, ast.USub)
        try:
            tree = ast.parse(condition, mode="eval")
            for node in ast.walk(tree):
                if not isinstance(node, ALLOWED):
                    return False
            code = compile(tree, "<safe>", "eval")
            result = eval(code, {"__builtins__": {}}, {"ops": operations_map})
            return bool(result)
        except Exception:
            return False


class GranularSyncManager:
    """Manager for granular synchronization barriers."""
    
    def __init__(self):
        self.operations: Dict[str, GranularOperation] = {}
        self.barriers: Dict[str, SyncBarrier] = {}
        self.operation_history: List[Dict[str, Any]] = []
    
    def create_operation(
        self,
        operation_id: str,
        phase: str,
        agent_id: str,
        operation_type: str,
        dependencies: Optional[List[OperationDependency]] = None
    ) -> GranularOperation:
        """Create a new granular operation."""
        operation = GranularOperation(
            operation_id=operation_id,
            phase=phase,
            agent_id=agent_id,
            operation_type=operation_type,
            dependencies=dependencies or []
        )
        self.operations[operation_id] = operation
        return operation
    
    def create_barrier(
        self,
        barrier_id: str,
        barrier_type: SyncBarrierType,
        phase: str,
        operation_ids: List[str],
        required_consensus: Optional[List[str]] = None
    ) -> SyncBarrier:
        """Create a synchronization barrier for operations."""
        barrier = SyncBarrier(
            barrier_id=barrier_id,
            barrier_type=barrier_type,
            phase=phase,
            operation_ids=operation_ids,
            required_consensus=required_consensus or []
        )
        self.barriers[barrier_id] = barrier
        return barrier
    
    def start_operation(self, operation_id: str) -> None:
        """Mark operation as started."""
        if operation_id in self.operations:
            op = self.operations[operation_id]
            op.status = OperationStatus.IN_PROGRESS
            op.started_at = datetime.now(timezone.utc).isoformat()
    
    def checkpoint_operation(
        self,
        operation_id: str,
        state_hash: str,
        artifacts: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> OperationCheckpoint:
        """Create a checkpoint for an operation."""
        if operation_id not in self.operations:
            raise ValueError(f"Operation {operation_id} not found")
        
        op = self.operations[operation_id]
        checkpoint = OperationCheckpoint(
            checkpoint_id=f"cp-{operation_id}-{len(op.checkpoints)}",
            operation_id=operation_id,
            phase=op.phase,
            agent_id=op.agent_id,
            state_hash=state_hash,
            artifacts=artifacts or {},
            metadata=metadata or {}
        )
        
        op.checkpoints.append(checkpoint)
        op.status = OperationStatus.CHECKPOINT
        return checkpoint
    
    def commit_operation(self, operation_id: str, result: Optional[Dict[str, Any]] = None) -> None:
        """Commit an operation (make it permanent)."""
        if operation_id not in self.operations:
            raise ValueError(f"Operation {operation_id} not found")
        
        op = self.operations[operation_id]
        op.status = OperationStatus.COMMITTED
        op.completed_at = datetime.now(timezone.utc).isoformat()
        if result:
            op.result = result
        
        if op.started_at:
            start = datetime.fromisoformat(op.started_at)
            end = datetime.fromisoformat(op.completed_at)
            op.execution_time_ms = int((end - start).total_seconds() * 1000)
        
        self._record_history(operation_id, "committed")
    
    def fail_operation(self, operation_id: str, error: str) -> None:
        """Mark operation as failed."""
        if operation_id not in self.operations:
            raise ValueError(f"Operation {operation_id} not found")
        
        op = self.operations[operation_id]
        op.status = OperationStatus.FAILED
        op.error = error
        op.completed_at = datetime.now(timezone.utc).isoformat()
        
        self._record_history(operation_id, "failed", {"error": error})
    
    def rollback_operation(self, operation_id: str, checkpoint_id: Optional[str] = None) -> None:
        """Rollback an operation to a previous checkpoint."""
        if operation_id not in self.operations:
            raise ValueError(f"Operation {operation_id} not found")
        
        op = self.operations[operation_id]
        
        if checkpoint_id:
            # Find and restore specific checkpoint
            checkpoint = next(
                (cp for cp in op.checkpoints if cp.checkpoint_id == checkpoint_id),
                None
            )
            if not checkpoint:
                raise ValueError(f"Checkpoint {checkpoint_id} not found")
        else:
            # Rollback to last checkpoint
            checkpoint = op.get_latest_checkpoint()
            if not checkpoint:
                raise ValueError(f"No checkpoints available for {operation_id}")
        
        op.status = OperationStatus.ROLLED_BACK
        op.completed_at = datetime.now(timezone.utc).isoformat()
        
        self._record_history(operation_id, "rolled_back", {"checkpoint_id": checkpoint.checkpoint_id})
    
    def check_barrier_readiness(self, barrier_id: str) -> Dict[str, Any]:
        """Check if a barrier is ready to proceed."""
        if barrier_id not in self.barriers:
            raise ValueError(f"Barrier {barrier_id} not found")
        
        barrier = self.barriers[barrier_id]
        
        # Check all operations in barrier
        all_committed = all(
            self.operations[op_id].status == OperationStatus.COMMITTED
            for op_id in barrier.operation_ids
            if op_id in self.operations
        )
        
        # Check consensus requirements
        consensus_ready = len(barrier.required_consensus) == 0  # Simplified
        
        readiness = {
            "barrier_id": barrier_id,
            "all_operations_committed": all_committed,
            "consensus_ready": consensus_ready,
            "is_ready": all_committed and consensus_ready,
            "operations_status": {
                op_id: self.operations[op_id].status.value
                for op_id in barrier.operation_ids
                if op_id in self.operations
            }
        }
        
        if readiness["is_ready"]:
            barrier.status = OperationStatus.COMMITTED
            barrier.completed_at = datetime.now(timezone.utc).isoformat()
        
        return readiness
    
    def get_operation_graph(self, phase: str) -> Dict[str, Any]:
        """Get dependency graph for operations in a phase."""
        phase_ops = {
            op_id: op for op_id, op in self.operations.items()
            if op.phase == phase
        }
        
        graph = {
            "phase": phase,
            "operations": list(phase_ops.keys()),
            "dependencies": [],
            "critical_path": self._compute_critical_path(phase_ops)
        }
        
        for op_id, op in phase_ops.items():
            for dep in op.dependencies:
                graph["dependencies"].append({
                    "from": dep.prerequisite_op_id,
                    "to": op_id,
                    "type": dep.dependency_type
                })
        
        return graph
    
    def _compute_critical_path(self, operations: Dict[str, GranularOperation]) -> List[str]:
        """Compute critical path (longest dependency chain)."""
        # Simplified: return operations sorted by execution time
        sorted_ops = sorted(
            operations.items(),
            key=lambda x: x[1].execution_time_ms,
            reverse=True
        )
        return [op_id for op_id, _ in sorted_ops[:3]]
    
    def _record_history(
        self,
        operation_id: str,
        event_type: str,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record operation event in history."""
        history_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation_id": operation_id,
            "event_type": event_type,
            **(extra_data or {})
        }
        self.operation_history.append(history_entry)
    
    def export_sync_report(self, filepath: str) -> None:
        """Export synchronization report to JSON."""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_operations": len(self.operations),
            "total_barriers": len(self.barriers),
            "operations": {
                op_id: {
                    "phase": op.phase,
                    "agent_id": op.agent_id,
                    "status": op.status.value,
                    "execution_time_ms": op.execution_time_ms,
                    "checkpoints": len(op.checkpoints),
                    "dependencies": len(op.dependencies)
                }
                for op_id, op in self.operations.items()
            },
            "barriers": {
                barrier_id: {
                    "type": barrier.barrier_type.value,
                    "status": barrier.status.value,
                    "operations": barrier.operation_ids
                }
                for barrier_id, barrier in self.barriers.items()
            },
            "history": self.operation_history[-100:]  # Last 100 events
        }
        
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)


# Example usage
if __name__ == "__main__":
    sync_mgr = GranularSyncManager()
    
    # Create operations for Embedding phase
    op1 = sync_mgr.create_operation(
        "op-embed-001",
        "Embedding",
        "A1",
        "requirement_analysis"
    )
    
    op2 = sync_mgr.create_operation(
        "op-embed-002",
        "Embedding",
        "A1",
        "domain_modeling",
        dependencies=[
            OperationDependency("op-embed-002", "op-embed-001", "sequential")
        ]
    )
    
    # Create barrier
    barrier = sync_mgr.create_barrier(
        "barrier-embed-001",
        SyncBarrierType.PHASE,
        "Embedding",
        ["op-embed-001", "op-embed-002"]
    )
    
    print(f"Created barrier: {barrier.barrier_id}")
    print(f"Operations: {barrier.operation_ids}")
    
    # Simulate execution
    sync_mgr.start_operation("op-embed-001")
    sync_mgr.checkpoint_operation("op-embed-001", "hash123", {"output": "/tmp/requirements.json"})
    sync_mgr.commit_operation("op-embed-001", {"status": "success"})
    
    sync_mgr.start_operation("op-embed-002")
    sync_mgr.checkpoint_operation("op-embed-002", "hash456", {"output": "/tmp/domain_model.json"})
    sync_mgr.commit_operation("op-embed-002", {"status": "success"})
    
    # Check barrier readiness
    readiness = sync_mgr.check_barrier_readiness("barrier-embed-001")
    print(f"\nBarrier readiness: {readiness['is_ready']}")
    print(f"Operations status: {readiness['operations_status']}")
