"""
PipelineState — Estado tipado e serializável do pipeline ANP.

Hierarquia de dados:
  PipelineState
    ├── phases: List[Phase]          # Fases executadas
    ├── node_results: Dict[str, Any] # Resultados por nó
    ├── dag: Dict[str, List[str]]    # DAG de dependências (nó -> [dependências])
    └── metadata: Dict               # Metadados (query, timestamps, etc.)

Inspirado por State/Paragraph/Research em BettaFish QueryEngine/state/state.py.
Generalizado para ser reutilizável em qualquer pipeline de nós.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
import json
import os


@dataclass
class NodeResult:
    """Resultado da execução de um único nó."""

    node_name: str = ""
    status: str = "pending"  # pending | running | completed | failed
    input_summary: str = ""
    output_summary: str = ""
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_name": self.node_name,
            "status": self.status,
            "input_summary": self.input_summary[:200],
            "output_summary": self.output_summary[:200],
            "error": self.error,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NodeResult":
        return cls(
            node_name=data.get("node_name", ""),
            status=data.get("status", "pending"),
            input_summary=data.get("input_summary", ""),
            output_summary=data.get("output_summary", ""),
            error=data.get("error"),
            duration_ms=data.get("duration_ms", 0.0),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
        )


@dataclass
class Phase:
    """Uma fase do pipeline, composta por um ou mais nós."""

    name: str = ""
    node_names: List[str] = field(default_factory=list)
    status: str = "pending"  # pending | running | completed | failed
    order: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "node_names": self.node_names,
            "status": self.status,
            "order": self.order,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Phase":
        return cls(
            name=data.get("name", ""),
            node_names=data.get("node_names", []),
            status=data.get("status", "pending"),
            order=data.get("order", 0),
        )


@dataclass
class PipelineState:
    """Estado completo do pipeline.

    Attributes:
        query: Consulta/entrada original do pipeline.
        phases: Lista ordenada de fases executadas.
        node_results: Mapa node_name → NodeResult.
        artifacts: Dados produzidos por cada nó (conteúdo real).
        dag: DAG de dependências (node_name -> lista de nós dos quais depende).
        metadata: Metadados gerais (título, timestamps, config).
        is_completed: Se o pipeline terminou.
        checkpoint_path: Caminho do último checkpoint salvo (vazio se nunca salvo).
    """

    query: str = ""
    phases: List[Phase] = field(default_factory=list)
    node_results: Dict[str, NodeResult] = field(default_factory=dict)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    dag: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_completed: bool = False
    checkpoint_path: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # ── Gerenciamento de fases ─────────────────────────────────────────

    def add_phase(self, name: str, node_names: List[str]) -> int:
        """Adiciona uma fase ao pipeline.

        Returns:
            Índice da fase adicionada.
        """
        order = len(self.phases)
        self.phases.append(Phase(name=name, node_names=node_names, order=order))
        self._touch()
        return order

    def get_phase(self, index: int) -> Optional[Phase]:
        if 0 <= index < len(self.phases):
            return self.phases[index]
        return None

    def set_phase_status(self, index: int, status: str):
        phase = self.get_phase(index)
        if phase:
            phase.status = status
            self._touch()

    # ── Gerenciamento de resultados ────────────────────────────────────

    def register_result(self, node_name: str, result: NodeResult):
        self.node_results[node_name] = result
        self._touch()

    def get_result(self, node_name: str) -> Optional[NodeResult]:
        return self.node_results.get(node_name)

    # ── Gerenciamento de artefatos ─────────────────────────────────────

    def store_artifact(self, key: str, value: Any):
        """Armazena um artefato produzido por um nó.

        Comportamento padrão: substituição (replace semantics).
        Para merge inteligente, use merge_artifact_list().
        """
        self.artifacts[key] = value
        self._touch()

    def get_artifact(self, key: str, default: Any = None) -> Any:
        return self.artifacts.get(key, default)

    # ── DeerFlow Reducers (cap. 2.1) ──────────────────────────────────

    def merge_artifact_list(
        self,
        key: str,
        items: List[Any],
    ) -> None:
        """Merge de lista com dedup ordenado (DeerFlow merge_artifacts).

        Usa dict.fromkeys() para preservar ordem e remover duplicatas,
        exatamente como o reducer merge_artifacts do DeerFlow.

        Exemplo:
            state.artifacts["paths"] = ["a.txt", "b.txt"]
            state.merge_artifact_list("paths", ["b.txt", "c.txt"])
            # Resultado: ["a.txt", "b.txt", "c.txt"]
        """
        existing = self.artifacts.get(key, [])
        if not isinstance(existing, list):
            existing = [existing]
        merged = list(dict.fromkeys(existing + items))
        self.artifacts[key] = merged
        self._touch()

    def merge_artifact_dict(
        self,
        key: str,
        values: Dict[str, Any],
    ) -> None:
        """Merge de dict com update simples.

        Útil para acumular resultados parciais de múltiplos nós.
        """
        existing = self.artifacts.get(key, {})
        if not isinstance(existing, dict):
            existing = {}
        existing.update(values)
        self.artifacts[key] = existing
        self._touch()

    def merge_viewed_images(
        self,
        images: Dict[str, str],
    ) -> None:
        """Merge com clear-on-empty (DeerFlow merge_viewed_images).

        Se images for um dict vazio, limpa Td0 o viewed_images do estado.
        Caso contrario, faz merge no existing.

        DeerFlow usa este padrao para evitar memory bloat de base64 strings
        em threads longas. Se um middleware retorna {}, todo o cache e limpo.
        """
        key = "_viewed_images"
        if not images:
            # Clear-on-empty: reset completo
            self.artifacts.pop(key, None)
        else:
            existing = self.artifacts.get(key, {})
            if isinstance(existing, dict):
                existing.update(images)
                self.artifacts[key] = existing
            else:
                self.artifacts[key] = images
        self._touch()

    # ── Metadados ──────────────────────────────────────────────────────

    def set_metadata(self, key: str, value: Any):
        self.metadata[key] = value
        self._touch()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)

    # ── Gerenciamento DAG ──────────────────────────────────────────────

    def set_dag(self, dag: Dict[str, List[str]]):
        """Define o DAG de dependências entre nós.

        Args:
            dag: Mapa node_name -> [node_names dos quais depende].
                  Nós sem dependências (raízes) devem ter lista vazia.
        """
        self.dag = dag
        self._touch()

    def get_dependency_order(self) -> List[Set[str]]:
        """Retorna a ordenação topológica do DAG em camadas paralelas.

        Returns:
            Lista de sets, cada set contém nós que podem executar em paralelo.
            Exemplo: [{'busca'}, {'sumario', 'reflexao'}, {'formata'}]
        """
        if not self.dag:
            return []

        # Calcular grau de entrada (quantas dependências cada nó tem)
        in_degree: Dict[str, int] = {}
        all_nodes: Set[str] = set()
        for node, deps in self.dag.items():
            all_nodes.add(node)
            in_degree[node] = len(deps)
            for dep in deps:
                all_nodes.add(dep)
                if dep not in in_degree:
                    in_degree[dep] = 0

        # Adicionar nós que estão nas dependências mas não como chaves
        for node in all_nodes:
            if node not in in_degree:
                in_degree[node] = 0

        # Kahn's algorithm para ordenação topológica por camada
        layers: List[Set[str]] = []
        current_layer = {n for n, d in in_degree.items() if d == 0}

        remaining = set(in_degree.keys())

        while current_layer:
            layers.append(current_layer)
            remaining -= current_layer
            next_layer: Set[str] = set()
            for node in current_layer:
                # Encontrar todos os nós que dependem deste
                for candidate, deps in self.dag.items():
                    if candidate in remaining and node in deps:
                        in_degree[candidate] -= 1
                        if in_degree[candidate] == 0:
                            next_layer.add(candidate)
            current_layer = next_layer

        # Se ainda há nós restantes, há ciclo
        if remaining:
            raise ValueError(
                f"Detectado ciclo no DAG. Nós não processados: {remaining}"
            )

        return layers

    # ── Conveniência ───────────────────────────────────────────────────

    def mark_completed(self):
        self.is_completed = True
        self._touch()

    def get_progress(self) -> Dict[str, Any]:
        """Resumo do progresso do pipeline."""
        total = len(self.phases)
        completed = sum(1 for p in self.phases if p.status == "completed")
        failed = sum(1 for p in self.phases if p.status == "failed")
        return {
            "query": self.query,
            "total_phases": total,
            "completed_phases": completed,
            "failed_phases": failed,
            "progress_pct": (completed / total * 100) if total > 0 else 0,
            "is_completed": self.is_completed,
            "phase_details": [p.to_dict() for p in self.phases],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def _touch(self):
        self.updated_at = datetime.now().isoformat()

    # ── Serialização ───────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "phases": [p.to_dict() for p in self.phases],
            "node_results": {
                k: v.to_dict() for k, v in self.node_results.items()
            },
            "artifacts": self._serialize_artifacts(),
            "dag": self.dag,
            "metadata": self.metadata,
            "is_completed": self.is_completed,
            "checkpoint_path": self.checkpoint_path,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def _serialize_artifacts(self) -> Dict[str, Any]:
        """Tenta serializar artefatos; fallback para string em caso de erro."""
        result = {}
        for k, v in self.artifacts.items():
            try:
                json.dumps(v)
                result[k] = v
            except (TypeError, ValueError):
                result[k] = str(v)[:500]
        return result

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PipelineState":
        phases = [Phase.from_dict(p) for p in data.get("phases", [])]
        node_results = {
            k: NodeResult.from_dict(v)
            for k, v in data.get("node_results", {}).items()
        }
        return cls(
            query=data.get("query", ""),
            phases=phases,
            node_results=node_results,
            artifacts=data.get("artifacts", {}),
            dag=data.get("dag", {}),
            metadata=data.get("metadata", {}),
            is_completed=data.get("is_completed", False),
            checkpoint_path=data.get("checkpoint_path", ""),
            created_at=data.get(
                "created_at", datetime.now().isoformat()
            ),
            updated_at=data.get(
                "updated_at", datetime.now().isoformat()
            ),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "PipelineState":
        return cls.from_dict(json.loads(json_str))

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def load(cls, filepath: str) -> "PipelineState":
        with open(filepath, "r", encoding="utf-8") as f:
            return cls.from_json(f.read())

    # ── Checkpoint ─────────────────────────────────────────────────────

    def save_checkpoint(self, dir_path: str) -> str:
        """Salva checkpoint com timestamp no nome do arquivo.

        O nome inclui timestamp ISO no início para garantir ordenação
        cronológica correta por sorted()/listdir() — o checkpoint mais
        recente sempre aparece por último em ordenação crescente.

        Args:
            dir_path: Diretório onde salvar o checkpoint.

        Returns:
            Caminho completo do arquivo de checkpoint salvo.
        """
        os.makedirs(dir_path, exist_ok=True)
        # Timestamp ISO simplificado para ordenação lexicográfica
        ts = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        phase_status = "-".join(
            f"{p.name[:8]}-{p.status[:4]}" for p in self.phases[-3:]
        )
        query_prefix = str(self.query)[:12] if self.query is not None else ""
        fname = f"ckpt_{ts}_{query_prefix}_{phase_status}.json"
        # Sanitizar nome
        fname = "".join(c if c.isalnum() or c in "-_." else "_" for c in fname)
        fpath = os.path.join(dir_path, fname)
        self.save(fpath)
        self.checkpoint_path = fpath
        return fpath

    @classmethod
    def load_checkpoint(cls, filepath: str) -> "PipelineState":
        """Carrega estado de um arquivo de checkpoint."""
        return cls.load(filepath)

    @classmethod
    def find_latest_checkpoint(cls, dir_path: str) -> Optional[str]:
        """Encontra o checkpoint mais recente em um diretório."""
        if not os.path.isdir(dir_path):
            return None
        ckpt_files = [
            f for f in os.listdir(dir_path)
            if f.startswith("ckpt_") and f.endswith(".json")
        ]
        if not ckpt_files:
            return None
        ckpt_files.sort(reverse=True)
        return os.path.join(dir_path, ckpt_files[0])
