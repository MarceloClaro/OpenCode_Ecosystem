"""Tests for fs-ipc skill (refined IPC)."""
import os
import json
import tempfile
import time
import threading
import importlib.util
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"

spec = importlib.util.spec_from_file_location(
    "ipc_client_fs", str(SCRIPTS_DIR / "ipc_client.py")
)
ipc_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ipc_module)
IPCClient = ipc_module.IPCClient
IPCServer = ipc_module.IPCServer
IPCCommand = ipc_module.IPCCommand
IPCResponse = ipc_module.IPCResponse
CommandType = ipc_module.CommandType
CommandStatus = ipc_module.CommandStatus

import pytest


class TestFSIPCClient:
    """CT-1: IPCClient send/receive."""

    def test_client_initialization(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = IPCClient(tmp)
            assert os.path.exists(client.commands_dir)

    def test_command_types_enum(self):
        assert CommandType.INTERVIEW.value == "interview"
        assert CommandType.CUSTOM.value == "custom"

    def test_ipc_command_serialization(self):
        cmd = IPCCommand(CommandType.CUSTOM, {"action": "ping"})
        d = cmd.to_dict()
        assert d["command_type"] == "custom"
        restored = IPCCommand.from_dict(d)
        assert restored.command_type == CommandType.CUSTOM

    def test_full_cycle_with_demo(self):
        with tempfile.TemporaryDirectory() as tmp:
            server = IPCServer(tmp)
            server.demo()
