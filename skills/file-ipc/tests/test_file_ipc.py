"""Tests for file-ipc skill."""
import os
import sys
import json
import tempfile
import importlib.util
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"

# Load the file-ipc module explicitly to avoid collision with fs-ipc
spec = importlib.util.spec_from_file_location(
    "ipc_client_file", str(SCRIPTS_DIR / "ipc_client.py")
)
ipc_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ipc_module)
FileIPCClient = ipc_module.FileIPCClient

import pytest


class TestFileIPCClient:
    """CT-1: FileIPCClient command/response cycle."""

    def test_client_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = FileIPCClient(tmp)
            assert client.commands_dir.exists()
            assert client.responses_dir.exists()

    def test_send_command_returns_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = FileIPCClient(tmp)
            cmd_id = client.send_command("ping", {"msg": "hello"})
            assert cmd_id.startswith("cmd-")
            assert (client.commands_dir / f"{cmd_id}.json").exists()

    def test_send_and_wait_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = FileIPCClient(tmp)
            response = client.send_and_wait("ping", {}, timeout=1)
            assert response["status"] == "timeout"

    def test_cleanup_orphans(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = FileIPCClient(tmp)
            client.send_command("old_cmd", {})
            client.cleanup(max_age_hours=-1)
            remaining = list(client.commands_dir.glob("*.json"))
            assert len(remaining) == 0
