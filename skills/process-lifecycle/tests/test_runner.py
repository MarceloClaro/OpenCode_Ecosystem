"""
TDD tests for ProcessRunner — Gerenciamento cross-platform de processos.
CT-1: test_init — inicializacao de ProcessState e ProcessRunner
CT-2: test_start_stop — ciclo start -> stop com script dummy
CT-3: test_state_persistence — save/load de ProcessState em JSON
CT-4: test_available — pause, resume, list_processes e cleanup
"""

import os
import sys
import json
import time
import tempfile
import pytest

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, SCRIPT_DIR)

from runner import (
    ProcessRunner, ProcessState, RunnerStatus,
)


class TestProcessRunner:

    def test_init(self):
        state = ProcessState("test-process")
        assert state.process_id == "test-process"
        assert state.status == RunnerStatus.IDLE
        assert state.progress_percent == 0.0
        assert state.pid is None

        d = state.to_dict()
        assert d["process_id"] == "test-process"
        assert d["status"] == "idle"

        state2 = ProcessState.from_dict(d)
        assert state2.process_id == state.process_id
        assert state2.status == state.status

    def test_start_stop(self):
        dummy_script = None
        try:
            fd, dummy_script = tempfile.mkstemp(suffix=".py")
            os.close(fd)
            with open(dummy_script, "w", encoding="utf-8") as f:
                f.write("""import sys, time, json
for i in range(3):
    print(json.dumps({"event_type":"round_end","round":i+1,"total":3}))
    print(f"[PROGRESS:{i+1}/3]")
    sys.stdout.flush()
    time.sleep(0.1)
print(json.dumps({"event_type":"simulation_end","platform":"test"}))
""")

            state = ProcessRunner.start(
                "test-runner-1",
                [sys.executable, dummy_script],
                total_steps=3,
            )
            assert state is not None
            assert state.status in (RunnerStatus.STARTING, RunnerStatus.RUNNING)

            time.sleep(1.0)

            s = ProcessRunner.get_state("test-runner-1")
            if s:
                assert s.total_steps > 0

            ProcessRunner.cleanup_logs("test-runner-1")

        finally:
            if dummy_script and os.path.exists(dummy_script):
                os.unlink(dummy_script)

    def test_state_persistence(self):
        with tempfile.TemporaryDirectory() as d:
            ProcessRunner.configure(state_dir=d)

            state = ProcessState("persist-test")
            state.status = RunnerStatus.RUNNING
            state.pid = 12345
            state.current_step = 5
            state.total_steps = 10
            state.progress_percent = 50.0

            ProcessRunner._states["persist-test"] = state
            ProcessRunner._save_state("persist-test")

            loaded = ProcessRunner._load_state("persist-test")
            assert loaded is not None
            assert loaded.process_id == "persist-test"
            assert loaded.status == RunnerStatus.RUNNING
            assert loaded.pid == 12345
            assert loaded.progress_percent == 50.0

            ProcessRunner._states.clear()

    def test_available(self):
        procs = ProcessRunner.list_processes()
        assert isinstance(procs, list)

        stats = ProcessRunner.get_agent_stats("nonexistent")
        assert stats["total_actions"] == 0

        actions = ProcessRunner.get_actions("nonexistent")
        assert actions == []

        timeline = ProcessRunner.get_timeline("nonexistent")
        assert timeline == []
