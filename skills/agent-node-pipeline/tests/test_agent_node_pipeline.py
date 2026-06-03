"""Tests for agent-node-pipeline skill."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import pytest


class TestPipelineState:
    """CT-1: PipelineState serialization and lifecycle."""

    def test_state_creation_and_phases(self):
        from pipeline_state import PipelineState
        state = PipelineState(query="test query")
        idx = state.add_phase("Fase 1", ["no1", "no2"])
        assert idx == 0
        assert len(state.phases) == 1
        assert state.phases[0].name == "Fase 1"

    def test_state_serialization_roundtrip(self):
        from pipeline_state import PipelineState, NodeResult
        state = PipelineState(query="roundtrip")
        state.store_artifact("key", {"val": 42})
        state.register_result("no1", NodeResult(node_name="no1", status="completed"))
        json_str = state.to_json()
        restored = PipelineState.from_json(json_str)
        assert restored.query == "roundtrip"
        assert restored.get_artifact("key") == {"val": 42}
        assert restored.node_results["no1"].status == "completed"

    def test_deerflow_merge_artifact_list(self):
        from pipeline_state import PipelineState
        state = PipelineState(query="merge")
        state.merge_artifact_list("paths", ["a.txt", "b.txt"])
        state.merge_artifact_list("paths", ["b.txt", "c.txt"])
        assert state.get_artifact("paths") == ["a.txt", "b.txt", "c.txt"]

    def test_dag_dependency_order(self):
        from pipeline_state import PipelineState
        state = PipelineState(query="dag")
        state.set_dag({"b": ["a"], "c": ["a"], "a": []})
        layers = state.get_dependency_order()
        assert len(layers) >= 2
        assert "a" in layers[0]


class TestBaseNode:
    """CT-2: BaseNode contracts work."""

    def test_transform_node(self):
        from node_types import TransformNode
        node = TransformNode(fn=lambda x: x.upper(), node_name="upper")
        assert node.run("hello") == "HELLO"
        assert node.describe()["node_name"] == "upper"

    def test_format_node_markdown(self):
        from node_types import FormatNode
        from pipeline_state import PipelineState
        state = PipelineState(query="test format")
        node = FormatNode(format_type="markdown", node_name="fmt")
        result = node.run(state)
        assert "# Relatório" in result
        assert "test format" in result


class TestPipelineOrchestrator:
    """CT-3: AgentNodePipeline orchestration."""

    def test_pipeline_creation(self):
        from pipeline import AgentNodePipeline
        pipe = AgentNodePipeline("TestPipe")
        assert pipe.name == "TestPipe"
        assert len(pipe._nodes) == 0

    def test_pipeline_add_node_and_phase(self):
        from pipeline import AgentNodePipeline
        from node_types import TransformNode
        pipe = AgentNodePipeline("TestPipe")
        node = TransformNode(fn=lambda x: x, node_name="pass")
        pipe.add_node("pass", node)
        pipe.add_phase("Entrega", ["pass"])
        desc = pipe.describe()
        assert desc["num_nodes"] == 1
        assert desc["num_phases"] == 1

    def test_pipeline_run_sequential(self):
        from pipeline import AgentNodePipeline
        from node_types import TransformNode
        pipe = AgentNodePipeline("SeqPipe")
        node = TransformNode(fn=lambda x: f"processed: {x}", node_name="proc")
        pipe.add_node("proc", node)
        pipe.add_phase("Proc", ["proc"])
        state = pipe.run("hello")
        assert state.get_artifact("proc") == "processed: hello"
        assert state.is_completed
