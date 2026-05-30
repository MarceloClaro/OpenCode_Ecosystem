"""
Filesystem IPC — P12 (Refinado)
Comunicação entre processos via diretórios commands/ + responses/.
Inspirado pelo SimulationIPC do MiroFish-Offline (simulation_ipc.py).
Refina o padrão P2 file-ipc com arquitetura Client/Server completa.

Uso:
    from skills.fs_ipc.scripts.ipc_client import IPCClient, IPCServer, CommandType

    # Server
    server = IPCServer(".ipc")
    server.start()
    cmd = server.poll_commands()
    if cmd:
        server.send_success(cmd.command_id, {"ok": True})
    server.stop()

    # Client
    client = IPCClient(".ipc")
    resp = client.send_command(CommandType.CUSTOM, {"action": "ping"})
"""

import os
import json
import time
import uuid
import shutil
import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class CommandType(str, Enum):
    INTERVIEW = "interview"
    BATCH_INTERVIEW = "batch_interview"
    CLOSE_ENV = "close_env"
    CUSTOM = "custom"


class CommandStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class IPCCommand:
    def __init__(
        self,
        command_type: CommandType,
        args: Dict[str, Any],
        command_id: Optional[str] = None,
    ):
        self.command_id = command_id or str(uuid.uuid4())
        self.command_type = command_type
        self.args = args
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command_id": self.command_id,
            "command_type": self.command_type.value,
            "args": self.args,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IPCCommand":
        return cls(
            command_type=CommandType(data.get("command_type", "custom")),
            args=data.get("args", {}),
            command_id=data.get("command_id"),
        )

    def write_to(self, path: str) -> str:
        filepath = os.path.join(path, f"{self.command_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.debug("Written command %s -> %s", self.command_id, filepath)
        return filepath


class IPCResponse:
    def __init__(
        self,
        command_id: str,
        status: CommandStatus,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
    ):
        self.command_id = command_id
        self.status = status
        self.result = result or {}
        self.error = error
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command_id": self.command_id,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IPCResponse":
        return cls(
            command_id=data.get("command_id", ""),
            status=CommandStatus(data.get("status", "failed")),
            result=data.get("result"),
            error=data.get("error"),
        )

    def write_to(self, path: str) -> str:
        filepath = os.path.join(path, f"{self.command_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.debug("Written response %s -> %s", self.command_id, filepath)
        return filepath


class IPCClient:
    """Lado emissor: envia comandos, aguarda respostas com timeout."""

    def __init__(self, ipc_dir: str):
        self.commands_dir = os.path.join(ipc_dir, "commands")
        self.responses_dir = os.path.join(ipc_dir, "responses")
        os.makedirs(self.commands_dir, exist_ok=True)
        os.makedirs(self.responses_dir, exist_ok=True)

    def send_command(
        self,
        command_type: CommandType,
        args: Dict[str, Any],
        timeout: float = 60.0,
        poll_interval: float = 0.5,
    ) -> IPCResponse:
        cmd = IPCCommand(command_type=command_type, args=args)
        cmd_path = cmd.write_to(self.commands_dir)

        deadline = time.time() + timeout
        resp_path = os.path.join(self.responses_dir, f"{cmd.command_id}.json")

        while time.time() < deadline:
            if os.path.exists(resp_path):
                try:
                    with open(resp_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, IOError) as exc:
                    logger.warning("Error reading response %s: %s", resp_path, exc)
                    time.sleep(poll_interval)
                    continue

                response = IPCResponse.from_dict(data)
                self._cleanup(cmd.command_id)
                return response

            time.sleep(poll_interval)

        self._cleanup(cmd.command_id)
        raise TimeoutError(
            f"Command {cmd.command_id} ({command_type.value}) timed out "
            f"after {timeout}s"
        )

    def send_interview(
        self,
        agent_id: str,
        prompt: str,
        platform: Optional[str] = None,
        timeout: float = 60.0,
    ) -> IPCResponse:
        args: Dict[str, Any] = {"agent_id": agent_id, "prompt": prompt}
        if platform:
            args["platform"] = platform
        return self.send_command(CommandType.INTERVIEW, args, timeout=timeout)

    def send_batch_interview(
        self,
        interviews: List[Dict[str, str]],
        timeout: float = 120.0,
    ) -> IPCResponse:
        return self.send_command(
            CommandType.BATCH_INTERVIEW,
            {"interviews": interviews},
            timeout=timeout,
        )

    def send_close_env(self, timeout: float = 10.0) -> IPCResponse:
        return self.send_command(CommandType.CLOSE_ENV, {}, timeout=timeout)

    def check_env_alive(self, ipc_dir: Optional[str] = None) -> bool:
        env_path = os.path.join(ipc_dir or os.path.dirname(self.commands_dir), "env_status.json")
        if not os.path.exists(env_path):
            return False
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("status") == "alive"
        except (json.JSONDecodeError, IOError):
            return False

    def _cleanup(self, command_id: str) -> None:
        for d in (self.commands_dir, self.responses_dir):
            p = os.path.join(d, f"{command_id}.json")
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError as exc:
                    logger.warning("Cleanup warning for %s: %s", p, exc)


class IPCServer:
    """Lado receptor: polling de comandos, execução, resposta."""

    def __init__(self, ipc_dir: str):
        self.commands_dir = os.path.join(ipc_dir, "commands")
        self.responses_dir = os.path.join(ipc_dir, "responses")
        self.ipc_dir = ipc_dir
        os.makedirs(self.commands_dir, exist_ok=True)
        os.makedirs(self.responses_dir, exist_ok=True)
        self._running = False

    def start(self) -> None:
        self._running = True
        self._update_env_status("alive")
        logger.info("IPCServer started at %s", self.ipc_dir)

    def stop(self) -> None:
        self._running = False
        self._update_env_status("stopped")
        logger.info("IPCServer stopped at %s", self.ipc_dir)

    def poll_commands(self) -> Optional[IPCCommand]:
        if not self._running:
            return None
        try:
            entries = [
                os.path.join(self.commands_dir, f)
                for f in os.listdir(self.commands_dir)
                if f.endswith(".json")
            ]
        except FileNotFoundError:
            return None

        if not entries:
            return None

        entries.sort(key=os.path.getmtime)
        target = entries[0]

        try:
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)
            return IPCCommand.from_dict(data)
        except (json.JSONDecodeError, IOError) as exc:
            logger.warning("Removing corrupt command file %s: %s", target, exc)
            try:
                os.remove(target)
            except OSError:
                pass
            return None

    def send_response(self, response: IPCResponse) -> None:
        response.write_to(self.responses_dir)
        cmd_path = os.path.join(self.commands_dir, f"{response.command_id}.json")
        if os.path.exists(cmd_path):
            try:
                os.remove(cmd_path)
            except OSError as exc:
                logger.warning("Could not remove command %s: %s", cmd_path, exc)

    def send_success(self, command_id: str, result: Dict[str, Any]) -> None:
        self.send_response(
            IPCResponse(command_id, CommandStatus.COMPLETED, result=result)
        )

    def send_error(self, command_id: str, error: str) -> None:
        self.send_response(
            IPCResponse(command_id, CommandStatus.FAILED, error=error)
        )

    def is_running(self) -> bool:
        return self._running

    def _update_env_status(self, status: str) -> None:
        env_path = os.path.join(self.ipc_dir, "env_status.json")
        data = {
            "status": status,
            "pid": os.getpid(),
            "started_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
        }
        with open(env_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def demo(self) -> None:
        """Demonstra comunicação Client -> Server em um único processo."""
        import tempfile

        tmpdir = tempfile.mkdtemp(prefix="fs_ipc_demo_")
        print(f"[demo] IPC dir: {tmpdir}")

        client = IPCClient(tmpdir)
        server = IPCServer(tmpdir)
        server.start()

        # 1. Client envia comando manualmente
        cmd = IPCCommand(CommandType.CUSTOM, {"action": "ping", "payload": {"ts": 1}})
        cmd_path = cmd.write_to(server.commands_dir)
        print(f"[demo] Client wrote: {cmd_path}")

        # 2. Server faz polling e processa
        pulled = server.poll_commands()
        assert pulled is not None, "Server should have pulled the command"
        print(f"[demo] Server pulled: {pulled.command_id} ({pulled.command_type.value})")
        assert pulled.args.get("action") == "ping"
        server.send_success(pulled.command_id, {"pong": True, "echo": pulled.args})
        print(f"[demo] Server responded")

        # 3. Client lê a resposta manualmente
        resp_path = os.path.join(client.responses_dir, f"{pulled.command_id}.json")
        assert os.path.exists(resp_path), "Response file should exist"
        with open(resp_path) as f:
            resp_data = json.load(f)
        assert resp_data["status"] == "completed"
        assert resp_data["result"]["pong"] is True
        client._cleanup(pulled.command_id)
        print(f"[demo] Client read response: {resp_data['status']}")

        # 4. Teste de ciclo completo via send_command com servidor ativo
        def _poll_loop(server, duration):
            deadline = time.time() + duration
            while time.time() < deadline and server.is_running():
                c = server.poll_commands()
                if c:
                    server.send_success(c.command_id, {"pong": True, "echo": c.args})
                time.sleep(0.1)
            server.stop()

        import threading
        t = threading.Thread(target=_poll_loop, args=(server, 5.0), daemon=True)
        t.start()

        resp = client.send_command(CommandType.CUSTOM, {"action": "ping2"}, timeout=10.0)
        print(f"[demo] Client send_command: status={resp.status.value}, result={resp.result}")
        assert resp.status == CommandStatus.COMPLETED
        assert resp.result.get("pong") is True

        # 5. Verificar limpeza
        remaining_cmds = [f for f in os.listdir(server.commands_dir) if f.endswith(".json")]
        remaining_resps = [f for f in os.listdir(server.responses_dir) if f.endswith(".json")]
        assert len(remaining_cmds) == 0, f"Commands dir should be clean, got: {remaining_cmds}"
        assert len(remaining_resps) == 0, f"Responses dir should be clean, got: {remaining_resps}"
        print("[demo] Cleanup verified: zero leftover files")

        # 6. Verificar heartbeat
        alive = client.check_env_alive(tmpdir)
        print(f"[demo] Env alive after full cycle: {alive}")

        shutil.rmtree(tmpdir)
        print("[demo] All assertions passed. Cleanup OK.")


def _cli_main() -> None:
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if len(sys.argv) < 2:
        print("Usage: python ipc_client.py <demo|server|client> [args]")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "demo":
        server = IPCServer(".ipc")
        server.start()
        client = IPCClient(".ipc")

        print("FS-IPC Demo running. Send commands via:")
        print("  python ipc_client.py client ping")
        print("  python ipc_client.py client interview '{\"agent_id\":\"x\",\"prompt\":\"hello\"}'")
        print("Press Ctrl+C to stop.\n")

        try:
            while server.is_running():
                cmd = server.poll_commands()
                if cmd:
                    print(f"[server] Received: {cmd.command_id} ({cmd.command_type.value})")
                    if cmd.command_type == CommandType.CUSTOM and cmd.args.get("action") == "ping":
                        server.send_success(cmd.command_id, {"pong": True})
                    elif cmd.command_type == CommandType.INTERVIEW:
                        server.send_success(cmd.command_id, {
                            "agent_id": cmd.args.get("agent_id"),
                            "response": f"Entrevista com {cmd.args.get('agent_id')} concluida",
                        })
                    elif cmd.command_type == CommandType.BATCH_INTERVIEW:
                        results = []
                        for iv in cmd.args.get("interviews", []):
                            results.append({
                                "agent_id": iv.get("agent_id"),
                                "response": f"Entrevista em lote com {iv.get('agent_id')}",
                            })
                        server.send_success(cmd.command_id, {"results": results})
                    elif cmd.command_type == CommandType.CLOSE_ENV:
                        server.send_success(cmd.command_id, {"closed": True})
                        server.stop()
                        print("[server] Env closed. Exiting.")
                    else:
                        server.send_error(cmd.command_id, f"Unknown type: {cmd.command_type}")
                time.sleep(0.5)
        except KeyboardInterrupt:
            server.stop()
            print("\n[demo] Stopped.")

    elif mode == "server":
        ipc_dir = sys.argv[2] if len(sys.argv) > 2 else ".ipc"
        action = sys.argv[3] if len(sys.argv) > 3 else "start"
        server = IPCServer(ipc_dir)

        if action == "start":
            server.start()
            print(f"Server started at {ipc_dir}")
            try:
                while server.is_running():
                    cmd = server.poll_commands()
                    if cmd:
                        print(f"Received: {cmd.command_id}")
                        server.send_success(cmd.command_id, {"processed": True})
                    time.sleep(0.5)
            except KeyboardInterrupt:
                server.stop()
                print("\nServer stopped.")
        elif action == "stop":
            server.stop()
            print(f"Server at {ipc_dir} stopped.")

    elif mode == "client":
        ipc_dir = sys.argv[2] if len(sys.argv) > 2 else ".ipc"
        action = sys.argv[3] if len(sys.argv) > 3 else "ping"
        client = IPCClient(ipc_dir)

        if action == "ping":
            resp = client.send_command(CommandType.CUSTOM, {"action": "ping"}, timeout=10.0)
            print(json.dumps(resp.to_dict(), indent=2))
        elif action == "interview":
            args = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
            resp = client.send_interview(
                args.get("agent_id", "unknown"),
                args.get("prompt", ""),
            )
            print(json.dumps(resp.to_dict(), indent=2))
        elif action == "close":
            resp = client.send_close_env()
            print(json.dumps(resp.to_dict(), indent=2))
        elif action == "status":
            alive = client.check_env_alive(ipc_dir)
            print(json.dumps({"alive": alive}, indent=2))

    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    _cli_main()
