"""
Process Lifecycle Manager — P11
Gerencia processos background com suporte cross-platform e tracking de estado.
Inspirado pelo SimulationRunner do MiroFish-Offline.
"""

import os
import sys
import json
import time
import threading
import subprocess
import signal
import atexit
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from datetime import datetime


class RunnerStatus(str, Enum):
    """Estados possíveis de um processo gerenciado."""
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessState:
    """Estado de um processo gerenciado, persistível em JSON."""

    def __init__(self, process_id: str):
        self.process_id = process_id
        self.status = RunnerStatus.IDLE
        self.pid: Optional[int] = None
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.current_step: int = 0
        self.total_steps: int = 0
        self.progress_percent: float = 0.0
        self.error: Optional[str] = None
        self.log_path: Optional[str] = None
        self.sub_status: Dict[str, bool] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "process_id": self.process_id,
            "status": self.status.value,
            "pid": self.pid,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "progress_percent": self.progress_percent,
            "error": self.error,
            "log_path": self.log_path,
            "sub_status": self.sub_status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessState":
        state = cls(data["process_id"])
        state.status = RunnerStatus(data.get("status", "idle"))
        state.pid = data.get("pid")
        state.started_at = data.get("started_at")
        state.completed_at = data.get("completed_at")
        state.current_step = data.get("current_step", 0)
        state.total_steps = data.get("total_steps", 0)
        state.progress_percent = data.get("progress_percent", 0.0)
        state.error = data.get("error")
        state.log_path = data.get("log_path")
        state.sub_status = data.get("sub_status", {})
        return state

    def __repr__(self) -> str:
        return (f"<ProcessState {self.process_id}: {self.status.value} "
                f"step={self.current_step}/{self.total_steps} "
                f"progress={self.progress_percent:.1f}%>")


class ProcessRunner:
    """
    Gerencia um processo background com:

    - Inicialização com subprocess.Popen e start_new_session
    - Monitoramento via thread daemon
    - Terminação cross-platform (taskkill /T no Windows, killpg no Unix)
    - Tracking de progresso via parsing de logs
    - Persistência de estado em JSON
    - Limpeza automática de recursos

    Uso:
        state = ProcessRunner.start("exp1", ["python", "train.py"], total_steps=100)
        print(ProcessRunner.get_state("exp1").to_dict())
        ProcessRunner.stop("exp1")
    """

    _processes: Dict[str, subprocess.Popen] = {}
    _states: Dict[str, ProcessState] = {}
    _monitor_threads: Dict[str, threading.Thread] = {}
    _stop_events: Dict[str, threading.Event] = {}
    _lock = threading.Lock()
    IS_WINDOWS = sys.platform == "win32"

    _state_dir: Optional[str] = None

    @classmethod
    def configure(cls, state_dir: str = None) -> None:
        """Define diretório para persistência de estados."""
        cls._state_dir = state_dir
        if state_dir and not os.path.exists(state_dir):
            os.makedirs(state_dir, exist_ok=True)

    @classmethod
    def _state_path(cls, process_id: str) -> str:
        base = cls._state_dir or os.path.join(os.getcwd(), ".process-states")
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, f"{process_id}.json")

    @classmethod
    def _save_state(cls, process_id: str) -> None:
        """Persiste estado em JSON."""
        state = cls._states.get(process_id)
        if not state:
            return
        path = cls._state_path(process_id)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)
        except OSError as e:
            print(f"[WARN] Falha ao salvar estado de {process_id}: {e}")

    @classmethod
    def start(
        cls,
        process_id: str,
        cmd: List[str],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        total_steps: int = 100,
        log_dir: Optional[str] = None,
    ) -> ProcessState:
        """
        Inicia um processo em background.

        Args:
            process_id: Identificador único do processo.
            cmd: Comando e argumentos (ex: ["python", "script.py"]).
            cwd: Diretório de trabalho do processo.
            env: Variáveis de ambiente adicionais.
            total_steps: Total de passos esperados (para cálculo de progresso).
            log_dir: Diretório para arquivos de log.

        Returns:
            ProcessState com status=STARTING ou FAILED se erro.
        """
        with cls._lock:
            if process_id in cls._processes:
                raise RuntimeError(f"Processo '{process_id}' já está em execução")

            state = ProcessState(process_id)
            state.status = RunnerStatus.STARTING
            state.total_steps = total_steps
            state.started_at = datetime.now().isoformat()
            cls._states[process_id] = state

        if not log_dir:
            log_dir = os.path.join(os.getcwd(), ".process-logs", process_id)
        os.makedirs(log_dir, exist_ok=True)

        log_path = os.path.join(log_dir, f"{process_id}.log")
        state.log_path = log_path

        proc_env = os.environ.copy()
        proc_env["PYTHONUTF8"] = "1"
        proc_env["PYTHONIOENCODING"] = "utf-8"
        if env:
            proc_env.update(env)

        try:
            log_file = open(log_path, "w", encoding="utf-8")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                cwd=cwd or os.getcwd(),
                env=proc_env,
                encoding="utf-8",
                errors="replace",
                start_new_session=True,
                bufsize=1,
            )
            log_file.close()
            log_file = open(log_path, "a", encoding="utf-8")

            state.pid = process.pid
            state.status = RunnerStatus.RUNNING

            with cls._lock:
                cls._processes[process_id] = process
                cls._stop_events[process_id] = threading.Event()
                cls._save_state(process_id)

            monitor = threading.Thread(
                target=cls._monitor,
                args=(process_id, log_file),
                daemon=True,
                name=f"mon-{process_id}",
            )
            with cls._lock:
                cls._monitor_threads[process_id] = monitor
            monitor.start()

            return state

        except (OSError, subprocess.SubprocessError) as e:
            state.status = RunnerStatus.FAILED
            state.error = str(e)
            cls._save_state(process_id)
            return state

    @classmethod
    def _monitor(cls, process_id: str, log_file) -> None:
        """
        Thread de monitoramento: lê stdout do processo, atualiza estado,
        detecta tokens de progresso [PROGRESS:X/Y] e finaliza ao término.
        """
        process = cls._processes.get(process_id)
        state = cls._states.get(process_id)
        stop_event = cls._stop_events.get(process_id)

        if not process or not state or not stop_event:
            return

        last_save = time.time()
        poll_interval = 2.0
        progress_pattern = "[PROGRESS:"
        action_log_pattern = '"event_type"'

        try:
            while True:
                if stop_event.is_set():
                    break

                exit_code = process.poll()
                if exit_code is not None:
                    state.status = (
                        RunnerStatus.COMPLETED
                        if exit_code == 0
                        else RunnerStatus.FAILED
                    )
                    state.completed_at = datetime.now().isoformat()
                    state.progress_percent = 100.0 if exit_code == 0 else state.progress_percent

                    rest = process.stdout.read() if process.stdout else ""
                    if rest and log_file and not log_file.closed:
                        log_file.write(rest)
                        log_file.flush()

                    if exit_code != 0:
                        tail = cls._tail_log(state.log_path, 2000) if state.log_path else ""
                        state.error = state.error or f"exit_code={exit_code}"
                        if tail:
                            state.error += f" | tail: {tail[:500]}"
                    break

                if state.status == RunnerStatus.PAUSED:
                    time.sleep(poll_interval)
                    continue

                line = process.stdout.readline() if process.stdout else ""
                if line:
                    if log_file and not log_file.closed:
                        log_file.write(line)
                        log_file.flush()

                    line_stripped = line.strip()

                    if progress_pattern in line_stripped:
                        try:
                            content = line_stripped.split(progress_pattern)[1].split("]")[0]
                            parts = content.split("/")
                            if len(parts) == 2:
                                state.current_step = int(parts[0])
                                state.total_steps = max(state.total_steps, int(parts[1]))
                        except (ValueError, IndexError):
                            pass

                    if action_log_pattern in line_stripped:
                        try:
                            action_data = json.loads(line_stripped)
                            event_type = action_data.get("event_type", "")
                            if event_type == "simulation_end":
                                platform = action_data.get("platform", "unknown")
                                state.sub_status[platform] = True
                            elif event_type == "round_end":
                                state.current_step = action_data.get("round", state.current_step)
                        except json.JSONDecodeError:
                            pass

                    if state.total_steps > 0:
                        state.progress_percent = (
                            state.current_step / state.total_steps
                        ) * 100.0

                now = time.time()
                if now - last_save >= 5.0:
                    cls._save_state(process_id)
                    last_save = now

                time.sleep(0.1)

        except Exception as e:
            state.status = RunnerStatus.FAILED
            state.error = str(e)
        finally:
            if state:
                cls._save_state(process_id)
            if log_file and not log_file.closed:
                log_file.close()
            with cls._lock:
                cls._states.pop(process_id, None)
                cls._processes.pop(process_id, None)
                cls._monitor_threads.pop(process_id, None)
                cls._stop_events.pop(process_id, None)

    @classmethod
    def _tail_log(cls, log_path: Optional[str], n_chars: int = 2000) -> str:
        """Lê os últimos N caracteres de um arquivo de log."""
        if not log_path or not os.path.exists(log_path):
            return ""
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(0, os.SEEK_END)
                size = f.tell()
                read_size = min(size, n_chars)
                f.seek(size - read_size)
                return f.read(read_size)
        except OSError:
            return ""

    @classmethod
    def stop(cls, process_id: str, timeout: int = 10) -> Optional[ProcessState]:
        """
        Finaliza um processo.

        Windows: taskkill /T /PID
        Unix: killpg(SIGTERM) → killpg(SIGKILL)
        Fallback: process.terminate() → process.kill()
        """
        state = cls._states.get(process_id)
        if not state:
            state = cls._load_state(process_id)
            if not state:
                return None

        state.status = RunnerStatus.STOPPING
        cls._save_state(process_id)

        process = cls._processes.get(process_id)
        stop_event = cls._stop_events.get(process_id)

        if not process:
            state.status = RunnerStatus.STOPPED
            cls._save_state(process_id)
            return state

        try:
            if cls.IS_WINDOWS and state.pid:
                try:
                    subprocess.run(
                        ["taskkill", "/T", "/PID", str(state.pid)],
                        capture_output=True,
                        timeout=timeout,
                    )
                except subprocess.TimeoutExpired:
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(state.pid)],
                        capture_output=True,
                        timeout=5,
                    )
            elif not cls.IS_WINDOWS and state.pid:
                try:
                    pgid = os.getpgid(state.pid)
                    os.killpg(pgid, signal.SIGTERM)
                    process.wait(timeout=timeout)
                except (ProcessLookupError, subprocess.TimeoutExpired):
                    try:
                        os.killpg(pgid, signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        pass
            else:
                process.terminate()
                try:
                    process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired) as e:
            state.error = f"stop_error: {e}"
        finally:
            pass

        if stop_event:
            stop_event.set()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)

        state.status = RunnerStatus.STOPPED
        state.completed_at = datetime.now().isoformat()
        cls._save_state(process_id)

        with cls._lock:
            cls._processes.pop(process_id, None)
            cls._monitor_threads.pop(process_id, None)
            cls._stop_events.pop(process_id, None)

        return state

    @classmethod
    def pause(cls, process_id: str, timeout: float = 5.0) -> Optional[ProcessState]:
        """
        Pausa um processo em execução.
        Unix: envia SIGSTOP. Windows: não suporta nativamente.
        """
        state = cls._states.get(process_id)
        if not state or state.status != RunnerStatus.RUNNING:
            return state

        process = cls._processes.get(process_id)
        if not process:
            return state

        try:
            if not cls.IS_WINDOWS and state.pid:
                os.killpg(os.getpgid(state.pid), signal.SIGSTOP)
            else:
                process.suspend() if hasattr(process, "suspend") else None
            state.status = RunnerStatus.PAUSED
            cls._save_state(process_id)
        except (OSError, ProcessLookupError) as e:
            state.error = f"pause_error: {e}"

        return state

    @classmethod
    def resume(cls, process_id: str) -> Optional[ProcessState]:
        """
        Retoma um processo pausado.
        Unix: envia SIGCONT. Windows: resume via Popen.
        """
        state = cls._states.get(process_id)
        if not state or state.status != RunnerStatus.PAUSED:
            return state

        process = cls._processes.get(process_id)
        if not process:
            return state

        try:
            if not cls.IS_WINDOWS and state.pid:
                os.killpg(os.getpgid(state.pid), signal.SIGCONT)
            else:
                process.resume() if hasattr(process, "resume") else None
            state.status = RunnerStatus.RUNNING
            cls._save_state(process_id)
        except (OSError, ProcessLookupError) as e:
            state.error = f"resume_error: {e}"

        return state

    @classmethod
    def get_state(cls, process_id: str) -> Optional[ProcessState]:
        """Retorna o estado atual (in-memory ou de arquivo)."""
        state = cls._states.get(process_id)
        if not state:
            state = cls._load_state(process_id)
        return state

    @classmethod
    def _load_state(cls, process_id: str) -> Optional[ProcessState]:
        """Carrega estado de arquivo JSON."""
        path = cls._state_path(process_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return ProcessState.from_dict(json.load(f))
        except (json.JSONDecodeError, OSError):
            return None

    @classmethod
    def get_actions(
        cls, process_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Parseia o arquivo de log e extrai ações registradas.

        Cada ação contém: agent_id, action_type, args, confidence, timestamp.
        """
        state = cls.get_state(process_id)
        if not state or not state.log_path:
            return []

        actions: List[Dict[str, Any]] = []
        if not os.path.exists(state.log_path):
            return actions

        try:
            with open(state.log_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if "action_type" in data or data.get("event_type") == "agent_action":
                            actions.append({
                                "agent_id": data.get("agent_id", "unknown"),
                                "action_type": data.get("action_type", data.get("event_type")),
                                "args": data.get("args", {}),
                                "confidence": data.get("confidence", 0.7),
                                "timestamp": data.get("timestamp", datetime.now().isoformat()),
                            })
                            if len(actions) >= limit:
                                break
                    except json.JSONDecodeError:
                        continue
        except OSError:
            pass

        return actions

    @classmethod
    def get_timeline(cls, process_id: str) -> List[Dict[str, Any]]:
        """Retorna timeline de eventos do processo."""
        state = cls.get_state(process_id)
        if not state:
            return []

        timeline: List[Dict[str, Any]] = [
            {"time": state.started_at or "N/A", "event": "started"},
        ]

        if not state.log_path or not os.path.exists(state.log_path):
            timeline.append({
                "time": state.completed_at or "N/A",
                "event": state.status.value,
            })
            return timeline

        try:
            with open(state.log_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        event_type = data.get("event_type", "")
                        if event_type in ("round_end", "simulation_end", "error", "checkpoint"):
                            timeline.append({
                                "time": data.get("timestamp", datetime.now().isoformat()),
                                "event": event_type,
                                "detail": data.get("round", data.get("platform", data.get("message", ""))),
                            })
                    except json.JSONDecodeError:
                        if "[PROGRESS:" in line:
                            timeline.append({
                                "time": datetime.now().isoformat(),
                                "event": "progress",
                                "detail": line.strip(),
                            })
        except OSError:
            pass

        timeline.append({
            "time": state.completed_at or datetime.now().isoformat(),
            "event": state.status.value,
        })

        return timeline

    @classmethod
    def get_agent_stats(cls, process_id: str) -> Dict[str, Any]:
        """Agrega estatísticas por agente a partir do log."""
        actions = cls.get_actions(process_id, limit=10000)

        stats: Dict[str, Dict[str, Any]] = {}
        total_by_type: Dict[str, int] = {}

        for action in actions:
            agent = action.get("agent_id", "unknown")
            atype = action.get("action_type", "unknown")

            if agent not in stats:
                stats[agent] = {"total": 0, "by_type": {}, "confidence_sum": 0.0}
            stats[agent]["total"] += 1
            stats[agent]["by_type"][atype] = stats[agent]["by_type"].get(atype, 0) + 1
            stats[agent]["confidence_sum"] += action.get("confidence", 0.7)

            total_by_type[atype] = total_by_type.get(atype, 0) + 1

        for agent, s in stats.items():
            s["confidence_avg"] = round(s["confidence_sum"] / s["total"], 2) if s["total"] > 0 else 0.0
            del s["confidence_sum"]

        return {
            "total_actions": len(actions),
            "unique_agents": len(stats),
            "agents": stats,
            "by_type": total_by_type,
        }

    @classmethod
    def cleanup_logs(cls, process_id: str) -> None:
        """Remove arquivos de log do processo."""
        state = cls._states.get(process_id)
        if state and state.log_path and os.path.exists(state.log_path):
            try:
                os.remove(state.log_path)
            except OSError:
                pass

        state_path = cls._state_path(process_id)
        if os.path.exists(state_path):
            try:
                os.remove(state_path)
            except OSError:
                pass

    @classmethod
    def cleanup_all(cls) -> None:
        """Finaliza todos os processos ativos e limpa recursos."""
        with cls._lock:
            process_ids = list(cls._processes.keys())

        for pid in process_ids:
            cls.stop(pid, timeout=3)

        with cls._lock:
            for event in cls._stop_events.values():
                event.set()
            cls._processes.clear()
            cls._states.clear()
            cls._monitor_threads.clear()
            cls._stop_events.clear()

    @classmethod
    def list_processes(cls) -> List[Dict[str, Any]]:
        """Lista todos os processos gerenciados (in-memory + arquivo)."""
        result = [s.to_dict() for s in cls._states.values()]

        if cls._state_dir and os.path.exists(cls._state_dir):
            for fname in os.listdir(cls._state_dir):
                if fname.endswith(".json"):
                    pid = fname[:-5]
                    if pid not in cls._states:
                        state = cls._load_state(pid)
                        if state:
                            result.append(state.to_dict())

        return result

    @classmethod
    def demo(cls) -> None:
        """Modo demo: simula ciclo de vida completo de um processo."""
        print("=" * 60)
        print("  Process Lifecycle Manager — Modo Demo")
        print("=" * 60)

        import tempfile

        demo_id = f"demo-{int(time.time())}"
        demo_dir = tempfile.mkdtemp(prefix="plm-demo-")
        dummy_script = os.path.join(demo_dir, "dummy_worker.py")

        with open(dummy_script, "w", encoding="utf-8") as f:
            f.write(r'''import sys, time, json
total = int(sys.argv[1]) if len(sys.argv) > 1 else 10
for i in range(total):
    log = {"event_type": "round_end", "round": i + 1, "total": total, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")}
    print(json.dumps(log), flush=True)
    print(f"[PROGRESS:{i + 1}/{total}]", flush=True)
    time.sleep(0.1)
log = {"event_type": "simulation_end", "platform": "demo", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")}
print(json.dumps(log), flush=True)
''')

        print(f"\n[1/6] Iniciando processo dummy com 5 passos...")
        state = cls.start(
            process_id=demo_id,
            cmd=[sys.executable, dummy_script, "5"],
            cwd=demo_dir,
            total_steps=5,
        )
        print(f"      PID={state.pid}, Status={state.status.value}")

        time.sleep(0.5)

        print(f"\n[2/6] Status após 0.5s:")
        s = cls.get_state(demo_id)
        print(f"      {s}")

        time.sleep(1.0)

        print(f"\n[3/6] Pausando processo...")
        cls.pause(demo_id)
        s = cls.get_state(demo_id)
        print(f"      Status={s.status.value}, Step={s.current_step}")

        time.sleep(0.5)

        print(f"\n[4/6] Retomando processo...")
        cls.resume(demo_id)
        s = cls.get_state(demo_id)
        print(f"      Status={s.status.value}")

        time.sleep(1.5)

        print(f"\n[5/6] Status final:")
        s = cls.get_state(demo_id)
        if s:
            print(f"      {s}")
            print(f"      sub_status={s.sub_status}")
        else:
            print(f"      (processo já finalizou)")

        print(f"\n[6/6] Ações detectadas:")
        actions = cls.get_actions(demo_id)
        print(f"      Total de ações: {len(actions)}")
        for a in actions[:5]:
            print(f"      - {a['event_type'] if 'event_type' in a else a['action_type']} "
                  f"(round={a.get('round', a.get('args', {}).get('round', '?'))})")

        print(f"\nTimeline:")
        timeline = cls.get_timeline(demo_id)
        for t in timeline:
            print(f"      [{t['time'][:19]}] {t['event']} {t.get('detail', '')}")

        print(f"\nEstatísticas:")
        stats = cls.get_agent_stats(demo_id)
        print(f"      Total ações: {stats['total_actions']}")
        print(f"      Por tipo: {stats['by_type']}")

        cls.cleanup_logs(demo_id)
        try:
            os.remove(dummy_script)
            os.rmdir(demo_dir)
        except OSError:
            pass

        print(f"\n{'=' * 60}")
        print(f"  Demo concluída com sucesso!")
        print(f"  Process ID: {demo_id}")
        print(f"{'=' * 60}")


atexit.register(ProcessRunner.cleanup_all)


if __name__ == "__main__":
    ProcessRunner.demo()
