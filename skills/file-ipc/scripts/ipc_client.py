"""
File IPC — Cliente de Comunicação via Filesystem.

Inspirado pelo simulation_ipc.py do MiroFish.
Implementa o lado cliente do protocolo File IPC.

Uso:
    from ipc_client import FileIPCClient
    client = FileIPCClient(".ipc")
    cmd_id = client.send_command("ping", {})
    response = client.wait_response(cmd_id, timeout=30)
"""

import os
import json
import time
import uuid
import threading
from pathlib import Path
from datetime import datetime, timezone


class FileIPCClient:
    """Cliente File IPC — envia comandos e aguarda respostas."""

    def __init__(self, ipc_dir=".ipc"):
        self.base = Path(ipc_dir)
        self.commands_dir = self.base / "commands"
        self.responses_dir = self.base / "responses"
        self.archive_dir = self.base / "archive"
        self.locks_dir = self.base / "locks"
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Garante que os diretórios IPC existem."""
        for d in [self.commands_dir, self.responses_dir,
                  self.archive_dir, self.locks_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def _acquire_lock(self, name, timeout=5):
        """Tenta adquirir um lock."""
        lock_path = self.locks_dir / f"{name}.lock"
        start = time.time()
        while time.time() - start < timeout:
            try:
                fd = os.open(str(lock_path),
                             os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return True
            except FileExistsError:
                time.sleep(0.1)
        return False

    def _release_lock(self, name):
        """Libera um lock."""
        lock_path = self.locks_dir / f"{name}.lock"
        if lock_path.exists():
            lock_path.unlink(missing_ok=True)

    def send_command(self, cmd_type, args=None, ttl=300):
        """
        Envia um comando para o servidor.

        Args:
            cmd_type: Tipo do comando (ping, analyze_file, search_pattern, ...)
            args: Dicionário com argumentos do comando
            ttl: Time-to-live em segundos

        Returns:
            ID do comando (string UUID)
        """
        cmd_id = f"cmd-{uuid.uuid4().hex[:12]}"
        command = {
            "id": cmd_id,
            "type": cmd_type,
            "args": args or {},
            "metadata": {
                "agent": os.environ.get("OPENCODE_AGENT", "unknown"),
                "session": os.environ.get("OPENCODE_SESSION", ""),
                "pid": os.getpid(),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ttl": ttl,
        }

        cmd_path = self.commands_dir / f"{cmd_id}.json"
        with open(cmd_path, "w", encoding="utf-8") as f:
            json.dump(command, f, indent=2, ensure_ascii=False)

        return cmd_id

    def wait_response(self, cmd_id, timeout=300, poll_interval=0.2):
        """
        Aguarda a resposta de um comando.

        Args:
            cmd_id: ID do comando
            timeout: Timeout máximo em segundos
            poll_interval: Intervalo inicial de polling (com backoff)

        Returns:
            Dicionário com a resposta, ou None se timeout
        """
        resp_path = self.responses_dir / f"{cmd_id}.json"
        start = time.time()
        attempts = 0

        while time.time() - start < timeout:
            if resp_path.exists():
                # Tenta ler com lock
                if self._acquire_lock(cmd_id, timeout=2):
                    try:
                        with open(resp_path, "r", encoding="utf-8") as f:
                            response = json.load(f)
                        # Arquivar após leitura
                        self._archive(cmd_id)
                        return response
                    finally:
                        self._release_lock(cmd_id)

            # Backoff progressivo
            attempts += 1
            if attempts > 20:
                poll_interval = 1.0
            elif attempts > 5:
                poll_interval = 0.5

            time.sleep(poll_interval)

        # Timeout
        return {
            "id": cmd_id,
            "status": "timeout",
            "result": None,
            "error": f"Timeout after {timeout}s",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": int((time.time() - start) * 1000),
        }

    def send_and_wait(self, cmd_type, args=None, timeout=300):
        """Envia comando e aguarda resposta (operação completa)."""
        cmd_id = self.send_command(cmd_type, args, ttl=timeout)
        return self.wait_response(cmd_id, timeout=timeout)

    def _archive(self, cmd_id):
        """Arquiva comando e resposta processados."""
        cmd_file = self.commands_dir / f"{cmd_id}.json"
        resp_file = self.responses_dir / f"{cmd_id}.json"
        lock_file = self.locks_dir / f"{cmd_id}.lock"

        for f in [cmd_file, resp_file, lock_file]:
            if f.exists():
                dest = self.archive_dir / f.name
                f.rename(dest)

    def cleanup(self, max_age_hours=1):
        """Limpa comandos órfãos mais antigos que max_age_hours."""
        now = time.time()
        for cmd_file in self.commands_dir.glob("*.json"):
            age_hours = (now - cmd_file.stat().st_mtime) / 3600
            if age_hours > max_age_hours:
                cmd_file.unlink(missing_ok=True)
                # Limpa possíveis respostas órfãs
                resp = self.responses_dir / cmd_file.name
                resp.unlink(missing_ok=True)


class FileIPCServer:
    """Servidor File IPC — processa comandos e escreve respostas."""

    def __init__(self, ipc_dir=".ipc", poll_interval=0.5):
        self.base = Path(ipc_dir)
        self.commands_dir = self.base / "commands"
        self.responses_dir = self.base / "responses"
        self.locks_dir = self.base / "locks"
        self.poll_interval = poll_interval
        self.handlers = {}
        self._running = False
        self._ensure_dirs()

    def _ensure_dirs(self):
        for d in [self.commands_dir, self.responses_dir, self.locks_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def on(self, cmd_type):
        """Decorator para registrar handler de comando."""
        def decorator(func):
            self.handlers[cmd_type] = func
            return func
        return decorator

    def register(self, cmd_type, handler):
        """Registra handler para um tipo de comando."""
        self.handlers[cmd_type] = handler

    def _write_response(self, cmd_id, status, result=None, error=None, duration_ms=0):
        """Escreve resposta."""
        response = {
            "id": cmd_id,
            "status": status,
            "result": result,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration_ms,
        }
        resp_path = self.responses_dir / f"{cmd_id}.json"
        with open(resp_path, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=2, ensure_ascii=False)

    def process_command(self, cmd_path):
        """Processa um único comando."""
        try:
            with open(cmd_path, "r", encoding="utf-8") as f:
                command = json.load(f)

            cmd_id = command["id"]
            cmd_type = command["type"]
            args = command.get("args", {})
            start = time.time()

            # Verifica handler
            handler = self.handlers.get(cmd_type)
            if not handler:
                self._write_response(
                    cmd_id, "failed",
                    error=f"No handler for command type: {cmd_type}",
                    duration_ms=int((time.time() - start) * 1000)
                )
                return

            # Executa handler
            result = handler(args)
            duration_ms = int((time.time() - start) * 1000)

            self._write_response(cmd_id, "completed",
                                 result=result, duration_ms=duration_ms)

        except json.JSONDecodeError as e:
            self._write_response("unknown", "failed",
                                 error=f"Invalid JSON: {e}")
        except Exception as e:
            try:
                cmd_id = json.loads(cmd_path.read_text()).get("id", "unknown")
                self._write_response(cmd_id, "failed", error=str(e))
            except Exception:
                pass

    def start(self, poll_interval=None):
        """Inicia o loop de polling do servidor."""
        self._running = True
        interval = poll_interval or self.poll_interval

        print(f"FileIPC Server started (polling {self.commands_dir})")
        print(f"  Handlers: {list(self.handlers.keys())}")

        while self._running:
            # Escaneia comandos pendentes
            for cmd_path in sorted(self.commands_dir.glob("*.json")):
                lock_path = self.locks_dir / f"{cmd_path.stem}.lock"
                try:
                    # Tenta lock
                    fd = os.open(str(lock_path),
                                 os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                    os.close(fd)

                    try:
                        self.process_command(cmd_path)
                        cmd_path.unlink(missing_ok=True)
                    except Exception as e:
                        print(f"  Error processing {cmd_path.name}: {e}")
                    finally:
                        lock_path.unlink(missing_ok=True)

                except FileExistsError:
                    pass  # Outro processo está processando

            time.sleep(interval)

    def stop(self):
        """Para o servidor."""
        self._running = False

    def start_threaded(self, poll_interval=None):
        """Inicia o servidor em uma thread separada."""
        thread = threading.Thread(target=self.start,
                                  args=(poll_interval,),
                                  daemon=True)
        thread.start()
        return thread


# ─── CLI ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python ipc_client.py [server|client] [args...]")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "server":
        server = FileIPCServer()

        @server.on("ping")
        def handle_ping(args):
            return {"pong": True, "time": datetime.now().isoformat()}

        @server.on("analyze_file")
        def handle_analyze(args):
            path = Path(args.get("target", "."))
            if not path.exists():
                raise FileNotFoundError(f"{path} not found")
            if path.is_file():
                return {
                    "file": str(path),
                    "lines": len(path.read_text().splitlines()),
                    "size": path.stat().st_size,
                }
            else:
                files = list(path.rglob("*"))
                return {
                    "directory": str(path),
                    "files": len(files),
                    "total_size": sum(f.stat().st_size for f in files if f.is_file()),
                }

        print("Starting File IPC Server...")
        server.start()

    elif mode == "client":
        client = FileIPCClient()
        cmd_type = sys.argv[2] if len(sys.argv) > 2 else "ping"
        args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}

        print(f"Sending command: {cmd_type}")
        response = client.send_and_wait(cmd_type, args, timeout=30)
        print(f"Response: {json.dumps(response, indent=2)}")

    else:
        print(f"Unknown mode: {mode}")
