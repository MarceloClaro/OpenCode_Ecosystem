"""
TDD tests for GraphBuilderService — Pipeline assincrono de construcao de grafos.
CT-1: test_init — inicializacao de TaskManager e MockGraphStorage
CT-2: test_text_processor — chunking com overlap
CT-3: test_build_graph — build_graph_async com acompanhamento
CT-4: test_available — status, data e delete de grafos
"""

import os
import sys
import json
import tempfile
import time
from pathlib import Path
import pytest

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, SCRIPT_DIR)

from graph_builder import (
    GraphBuilderService, TaskManager, TextProcessor,
    MockGraphStorage, TaskStatus,
)


class TestGraphBuilderPipeline:

    def test_init(self):
        tm = TaskManager()
        assert len(tm._tasks) == 0

        task_id = tm.create_task("test_task")
        assert task_id.startswith("task_")

        task = tm.get_task(task_id)
        assert task is not None
        assert task.status == TaskStatus.PENDING

    def test_text_processor(self):
        text = "Primeiro paragrafo de exemplo com varias palavras. " * 3
        chunks = TextProcessor.split_text(text, chunk_size=200, chunk_overlap=0)
        assert len(chunks) > 0
        assert all(len(c) > 0 for c in chunks)

        assert TextProcessor.split_text("", chunk_size=500) == []
        assert TextProcessor.split_text("curto", chunk_size=500) == ["curto"]

    def test_build_graph(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = Path(f.name)
        try:
            storage = MockGraphStorage(db_path=db_path)
            builder = GraphBuilderService(storage)

            text = "Entidade A interage com Entidade B. " * 5
            ontology = {
                "entity_types": {
                    "Person": {"description": "Pessoa fisica"},
                    "Organization": {"description": "Organizacao"},
                },
                "relations": ["interacts_with", "belongs_to"],
            }

            task_id = builder.build_graph_async(text, ontology, graph_name="TestGraph")
            assert task_id.startswith("task_")

            timeout = 10
            start = time.time()
            while time.time() - start < timeout:
                task = builder.task_manager.get_task(task_id)
                if task and task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                    break
                time.sleep(0.2)

            task = builder.task_manager.get_task(task_id)
            assert task is not None
            assert task.status == TaskStatus.COMPLETED
            assert task.result is not None
            assert "graph_id" in task.result

        finally:
            try:
                os.unlink(str(db_path))
            except OSError:
                pass

    def test_available(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = Path(f.name)
        try:
            storage = MockGraphStorage(db_path=db_path)
            graph_id = storage.create_graph("TestGraph", "descricao de teste")
            assert graph_id.startswith("graph_")

            storage.add_text(graph_id, "Entidade X colabora com Entidade Y.")
            info = storage.get_graph_info(graph_id)
            assert info["graph_id"] == graph_id
            assert info["node_count"] > 0

            data = storage.get_graph_data(graph_id)
            assert "episodes" in data

            storage.delete_graph(graph_id)
            info2 = storage.get_graph_info(graph_id)
            assert info2.get("node_count", 0) == 0
        finally:
            try:
                os.unlink(str(db_path))
            except OSError:
                pass
