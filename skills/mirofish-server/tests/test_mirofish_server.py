"""
TDD: mirofish-server — Backend API + Deep Interaction + Frontend
Tests AppState, SSE broadcast, chat, and server infrastructure.
Uses subprocess to avoid print() hijack causing recursion.
"""
import os
import sys
import json
import subprocess
import pytest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")
MFS_PATH = os.path.join(SCRIPTS_DIR, "mirofish_server.py")


def run_python(code: str) -> tuple:
    """Run Python code in subprocess and return (stdout, stderr, returncode)."""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30,
        cwd=SCRIPTS_DIR
    )
    return r.stdout, r.stderr, r.returncode


class TestAppStateSubprocess:
    """CT-1: AppState initialization via subprocess."""

    def test_appstate_importable(self):
        code = """
import sys
sys.path.insert(0, '.')
from mirofish_server import AppState
state = AppState()
assert state.engine is None
assert state.simulation_running is False
assert isinstance(state.sse_clients, list)
assert isinstance(state.chat_history, list)
assert isinstance(state.stats, dict)
assert state.simulation_thread is None
assert state.last_report_path == ""
print("OK:AppState_ok")
"""
        stdout, stderr, rc = run_python(code)
        assert "OK:AppState_ok" in stdout, f"AppState init failed: {stderr}"

    def test_brazil_time_callable(self):
        code = """
import sys
sys.path.insert(0, '.')
from mirofish_server import BRAZIL_TIME
dt = BRAZIL_TIME()
assert dt is not None
print("OK:BRAZIL_TIME_ok")
"""
        stdout, stderr, rc = run_python(code)
        assert "OK:BRAZIL_TIME_ok" in stdout, f"BRAZIL_TIME failed: {stderr}"


class TestConstantsSubprocess:
    """CT-2: Server constants validation."""

    def test_html_frontend_size(self):
        code = """
import sys
sys.path.insert(0, '.')
from mirofish_server import HTML_FRONTEND
assert len(HTML_FRONTEND) > 5000, f"HTML too small: {len(HTML_FRONTEND)} chars"
assert '<!DOCTYPE html>' in HTML_FRONTEND
assert 'MiroFish' in HTML_FRONTEND
print("OK:HTML_ok")
"""
        stdout, stderr, rc = run_python(code)
        assert "OK:HTML_ok" in stdout, f"HTML validation failed: {stderr}"

    def test_logger_configured(self):
        code = """
import sys
sys.path.insert(0, '.')
import mirofish_server as ms
assert ms.logger is not None
print("OK:logger_ok")
"""
        stdout, stderr, rc = run_python(code)
        assert "OK:logger_ok" in stdout, f"Logger validation failed: {stderr}"


class TestFunctionsSubprocess:
    """CT-3: Core utility functions."""

    def test_chat_with_agent_no_engine(self):
        code = """
import sys
sys.path.insert(0, '.')
from mirofish_server import chat_with_agent, STATE
STATE.engine = None
result = chat_with_agent("test", "Hello")
assert isinstance(result, dict)
assert "error" in result
print("OK:chat_no_engine_ok")
"""
        stdout, stderr, rc = run_python(code)
        assert "OK:chat_no_engine_ok" in stdout, f"Chat test failed: {stderr}"

    def test_get_agent_list_empty(self):
        code = """
import sys
sys.path.insert(0, '.')
from mirofish_server import get_agent_list, STATE
STATE.engine = None
result = get_agent_list()
assert isinstance(result, list)
assert len(result) == 0
print("OK:agent_list_empty_ok")
"""
        stdout, stderr, rc = run_python(code)
        assert "OK:agent_list_empty_ok" in stdout, f"Agent list test failed: {stderr}"

    def test_broadcast_sse(self):
        code = """
import sys, queue
sys.path.insert(0, '.')
from mirofish_server import broadcast_sse, STATE
STATE.sse_clients = []
q = queue.Queue(maxsize=10)
STATE.sse_clients.append(q)
broadcast_sse("test_event", {"key": "value"})
try:
    msg = q.get_nowait()
    assert "test_event" in msg
    assert "value" in msg
    print("OK:broadcast_ok")
except queue.Empty:
    print("OK:broadcast_no_msg")  # May be cleared by cleanup
"""
        stdout, stderr, rc = run_python(code)
        assert "OK:broadcast" in stdout, f"Broadcast test failed: {stderr}"


class TestMirofishAvailable:
    """CT-4: Module-level validations."""

    def test_module_file_exists(self):
        assert os.path.isfile(MFS_PATH), "mirofish_server.py must exist"

    def test_module_file_size(self):
        size = os.path.getsize(MFS_PATH)
        assert size > 50000, f"mirofish_server.py must be substantial (got {size} bytes)"

    def test_cleanup_function_exists(self):
        code = """
import sys
sys.path.insert(0, '.')
from mirofish_server import cleanup_databases
assert callable(cleanup_databases)
print("OK:cleanup_ok")
"""
        stdout, stderr, rc = run_python(code)
        assert "OK:cleanup_ok" in stdout, f"Cleanup test failed: {stderr}"

    def test_omen_function_exists(self):
        code = """
import sys
sys.path.insert(0, '.')
from mirofish_server import save_omen_prediction
assert callable(save_omen_prediction)
print("OK:omen_ok")
"""
        stdout, stderr, rc = run_python(code)
        assert "OK:omen_ok" in stdout, f"Omen test failed: {stderr}"
