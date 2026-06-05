"""
Graph Memory Updater — Atualização de Grafos em Tempo Real.

Inspirado pelo GraphMemoryUpdater do MiroFish-Offline (graph_memory_updater.py).
Modos: start, simulate, stop, stats.

Uso:
    python memory_updater.py start --graph <graph_id>
    python memory_updater.py simulate --graph <graph_id> --rounds 10
    python memory_updater.py stop --simulation <sim_id>
    python memory_updater.py stats
"""

import argparse
import json
import logging
import random
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from queue import Empty, Queue
from typing import Any, Dict, List, Optional, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("memory_updater")

DB_PATH = Path(__file__).resolve().parents[3] / ".reversa" / "code-graph.db"


# ─── Data Classes ─────────────────────────────────────────────────
@dataclass
class AgentActivity:
    """Agent activity record"""
    platform: str
    agent_id: int
    agent_name: str
    action_type: str
    action_args: Dict[str, Any]
    round_num: int
    timestamp: str

    def to_episode_text(self) -> str:
        """Converte atividade em texto narrativo"""
        templates = {
            "CREATE_POST": lambda: f"Posted a post: \"{self.action_args.get('content', '')}\"",
            "LIKE_POST": lambda: self._fmt_like("Liked"),
            "DISLIKE_POST": lambda: self._fmt_like("Disliked"),
            "REPOST": lambda: self._fmt_repost(),
            "QUOTE_POST": lambda: self._fmt_quote(),
            "FOLLOW": lambda: f"Followed user \"{self.action_args.get('target_user_name', '')}\"",
            "CREATE_COMMENT": lambda: self._fmt_comment(),
            "LIKE_COMMENT": lambda: self._fmt_like_comment("Liked"),
            "DISLIKE_COMMENT": lambda: self._fmt_like_comment("Disliked"),
            "SEARCH_POSTS": lambda: f"Searched for \"{self.action_args.get('query', '')}\"",
            "SEARCH_USER": lambda: f"Searched for user \"{self.action_args.get('query', '')}\"",
            "MUTE": lambda: f"Muted user \"{self.action_args.get('target_user_name', '')}\"",
        }
        desc = templates.get(self.action_type, lambda: f"Executed {self.action_type}")()
        return f"{self.agent_name}: {desc}"

    def _fmt_like(self, verb: str) -> str:
        author = self.action_args.get("post_author_name", "")
        content = self.action_args.get("post_content", "")
        if content and author:
            return f"{verb} {author}'s post: \"{content}\""
        elif content:
            return f"{verb} a post: \"{content}\""
        elif author:
            return f"{verb} a post by {author}"
        return f"{verb} a post"

    def _fmt_repost(self) -> str:
        author = self.action_args.get("original_author_name", "")
        content = self.action_args.get("original_content", "")
        if content and author:
            return f"Reposted {author}'s post: \"{content}\""
        elif content:
            return f"Reposted a post: \"{content}\""
        elif author:
            return f"Reposted a post by {author}"
        return "Reposted a post"

    def _fmt_quote(self) -> str:
        author = self.action_args.get("original_author_name", "")
        content = self.action_args.get("original_content", "")
        quote = self.action_args.get("quote_content", "") or self.action_args.get("content", "")
        base = ""
        if content and author:
            base = f"Quoted {author}'s post \"{content}\""
        elif content:
            base = f"Quoted a post \"{content}\""
        elif author:
            base = f"Quoted a post by {author}"
        else:
            base = "Quoted a post"
        if quote:
            base += f", commented: \"{quote}\""
        return base

    def _fmt_comment(self) -> str:
        content = self.action_args.get("content", "")
        author = self.action_args.get("post_author_name", "")
        post = self.action_args.get("post_content", "")
        if content:
            if post and author:
                return f"Commented on {author}'s post \"{post}\": \"{content}\""
            elif post:
                return f"Commented on post \"{post}\": \"{content}\""
            elif author:
                return f"Commented on {author}'s post: \"{content}\""
            return f"Commented: \"{content}\""
        return "Left a comment"

    def _fmt_like_comment(self, verb: str) -> str:
        author = self.action_args.get("comment_author_name", "")
        content = self.action_args.get("comment_content", "")
        if content and author:
            return f"{verb} {author}'s comment: \"{content}\""
        elif content:
            return f"{verb} a comment: \"{content}\""
        elif author:
            return f"{verb} a comment by {author}"
        return f"{verb} a comment"


# ─── MockStorage (para demonstração) ──────────────────────────────
class MockGraphStorage:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                graph_id TEXT,
                agent_name TEXT,
                action_type TEXT,
                platform TEXT,
                round_num INTEGER,
                episode_text TEXT,
                timestamp TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
        conn.close()

    def add_text(self, graph_id: str, combined_text: str) -> str:
        episode_id = f"mem_{uuid.uuid4().hex[:12]}"
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "INSERT INTO memory_activities (graph_id, agent_name, action_type, platform, episode_text, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (graph_id, "__batch__", "__batch__", "__batch__", combined_text[:500], datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()
        return episode_id


# ─── GraphMemoryUpdater ───────────────────────────────────────────
class GraphMemoryUpdater:
    """Atualização de grafo em tempo real com buffer por plataforma"""

    BATCH_SIZE = 5
    SEND_INTERVAL = 0.5
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    PLATFORM_NAMES = {"twitter": "worldinterface1", "reddit": "worldinterface2"}

    def __init__(self, graph_id: str, storage: MockGraphStorage):
        self.graph_id = graph_id
        self.storage = storage
        self._queue: Queue = Queue()
        self._buffers: Dict[str, List[AgentActivity]] = {"twitter": [], "reddit": []}
        self._lock = threading.Lock()
        self._running = False
        self._worker: Optional[threading.Thread] = None
        self.total = 0
        self.sent = 0
        self.failed = 0
        self.skipped = 0

    def start(self):
        if self._running:
            return
        self._running = True
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()
        logger.info(f"MemoryUpdater started: graph_id={self.graph_id}")

    def stop(self):
        self._running = False
        self._flush()
        if self._worker and self._worker.is_alive():
            self._worker.join(timeout=10)
        logger.info(f"MemoryUpdater stopped: {self.total} total, {self.sent} sent, {self.failed} failed, {self.skipped} skipped")

    def add_activity(self, activity: AgentActivity):
        if activity.action_type == "DO_NOTHING":
            self.skipped += 1
            return
        self._queue.put(activity)
        self.total += 1

    def _worker_loop(self):
        while self._running or not self._queue.empty():
            try:
                activity = self._queue.get(timeout=1)
                platform = activity.platform.lower()
                with self._lock:
                    if platform not in self._buffers:
                        self._buffers[platform] = []
                    self._buffers[platform].append(activity)
                    if len(self._buffers[platform]) >= self.BATCH_SIZE:
                        batch = self._buffers[platform][:self.BATCH_SIZE]
                        self._buffers[platform] = self._buffers[platform][self.BATCH_SIZE:]
                        self._send_batch(batch, platform)
                        time.sleep(self.SEND_INTERVAL)
            except Empty:
                pass
            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(1)

    def _send_batch(self, activities: List[AgentActivity], platform: str):
        texts = [a.to_episode_text() for a in activities]
        combined = "\n".join(texts)
        for attempt in range(self.MAX_RETRIES):
            try:
                self.storage.add_text(self.graph_id, combined)
                self.sent += 1
                display = self.PLATFORM_NAMES.get(platform, platform)
                logger.info(f"Sent {len(activities)} {display} activities")
                return
            except Exception as e:
                if attempt < self.MAX_RETRIES - 1:
                    logger.warning(f"Send failed (attempt {attempt+1}): {e}")
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                else:
                    logger.error(f"Send failed after {self.MAX_RETRIES} retries: {e}")
                    self.failed += 1

    def _flush(self):
        while not self._queue.empty():
            try:
                a = self._queue.get_nowait()
                p = a.platform.lower()
                with self._lock:
                    if p not in self._buffers:
                        self._buffers[p] = []
                    self._buffers[p].append(a)
            except Empty:
                break
        with self._lock:
            for plat, buf in self._buffers.items():
                if buf:
                    self._send_batch(buf, plat)
                self._buffers[plat] = []

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            buffer_sizes = {p: len(b) for p, b in self._buffers.items()}
        return {
            "graph_id": self.graph_id,
            "total": self.total,
            "sent": self.sent,
            "failed": self.failed,
            "skipped": self.skipped,
            "queue_size": self._queue.qsize(),
            "buffer_sizes": buffer_sizes,
            "running": self._running,
        }


# ─── MemoryManager ────────────────────────────────────────────────
class MemoryManager:
    _updaters: Dict[str, GraphMemoryUpdater] = {}
    _lock = threading.Lock()

    @classmethod
    def create(cls, sim_id: str, graph_id: str, storage: MockGraphStorage) -> GraphMemoryUpdater:
        with cls._lock:
            if sim_id in cls._updaters:
                cls._updaters[sim_id].stop()
            updater = GraphMemoryUpdater(graph_id, storage)
            updater.start()
            cls._updaters[sim_id] = updater
            return updater

    @classmethod
    def get(cls, sim_id: str) -> Optional[GraphMemoryUpdater]:
        return cls._updaters.get(sim_id)

    @classmethod
    def stop(cls, sim_id: str):
        with cls._lock:
            if sim_id in cls._updaters:
                cls._updaters[sim_id].stop()
                del cls._updaters[sim_id]

    @classmethod
    def stop_all(cls):
        with cls._lock:
            for sid, updater in list(cls._updaters.items()):
                updater.stop()
            cls._updaters.clear()

    @classmethod
    def all_stats(cls) -> Dict[str, Dict]:
        return {sid: u.get_stats() for sid, u in cls._updaters.items()}


# ─── Simulador ────────────────────────────────────────────────────
AGENT_NAMES = ["Carlos", "Maria", "João", "Ana", "Pedro", "Julia", "Lucas", "Beatriz"]
ACTION_TYPES = [
    "CREATE_POST", "LIKE_POST", "REPOST", "QUOTE_POST",
    "FOLLOW", "CREATE_COMMENT", "LIKE_COMMENT", "SEARCH_POSTS", "MUTE",
]
TOPICS = [
    "Regulação de IA é necessária",
    "A tecnologia avançou muito",
    "Precisamos de mais debate público",
    "Impacto econômico da regulação",
    "Experiências internacionais",
    "O papel das universidades",
    "Privacidade vs inovação",
    "Desafios para startups",
]


def simulate_round(updater: GraphMemoryUpdater, round_num: int):
    """Gera atividades simuladas para uma rodada"""
    n_activities = random.randint(2, 5)
    for _ in range(n_activities):
        agent_name = random.choice(AGENT_NAMES)
        agent_id = AGENT_NAMES.index(agent_name)
        platform = random.choice(["twitter", "reddit"])
        action_type = random.choice(ACTION_TYPES)
        topic = random.choice(TOPICS)

        action_args = {"content": topic, "post_content": topic}
        if action_type in ("LIKE_POST", "DISLIKE_POST", "REPOST", "QUOTE_POST"):
            other = random.choice([a for a in AGENT_NAMES if a != agent_name] + [""])
            action_args["post_author_name"] = other
        if action_type == "FOLLOW":
            action_args["target_user_name"] = random.choice([a for a in AGENT_NAMES if a != agent_name])
        if action_type in ("LIKE_COMMENT", "DISLIKE_COMMENT"):
            action_args["comment_content"] = f"Comentário sobre {topic}"
            action_args["comment_author_name"] = random.choice(AGENT_NAMES)
        if action_type in ("SEARCH_POSTS", "SEARCH_USER"):
            action_args["query"] = topic[:20]

        activity = AgentActivity(
            platform=platform,
            agent_id=agent_id,
            agent_name=agent_name,
            action_type=action_type,
            action_args=action_args,
            round_num=round_num,
            timestamp=datetime.now().isoformat(),
        )
        updater.add_activity(activity)

    # DO_NOTHING ocasional
    if random.random() < 0.2:
        activity = AgentActivity(
            platform="twitter", agent_id=0, agent_name="Silent",
            action_type="DO_NOTHING", action_args={}, round_num=round_num,
            timestamp=datetime.now().isoformat(),
        )
        updater.add_activity(activity)


# ─── CLI ──────────────────────────────────────────────────────────
def cmd_start(args):
    storage = MockGraphStorage()
    sim_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    updater = MemoryManager.create(sim_id, args.graph, storage)
    print(f"\n🚀 MemoryUpdater iniciado: sim_id={sim_id}, graph_id={args.graph}")
    print(f"   Batch size: {GraphMemoryUpdater.BATCH_SIZE}")
    print(f"   Para simular: python memory_updater.py simulate --graph {args.graph} --rounds N")
    print(f"   Para parar: python memory_updater.py stop --simulation {sim_id}")
    return {"sim_id": sim_id, "graph_id": args.graph}


def cmd_simulate(args):
    storage = MockGraphStorage()
    sim_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}_batch"
    updater = MemoryManager.create(sim_id, args.graph, storage)

    print(f"\n🎲 Simulando {args.rounds} rodadas...")
    for r in range(1, args.rounds + 1):
        simulate_round(updater, r)
        if r % 3 == 0 or r == args.rounds:
            stats = updater.get_stats()
            print(f"   Rodada {r}/{args.rounds} — Total: {stats['total']}, Enviados: {stats['sent']}, Falhas: {stats['failed']}")
        time.sleep(0.2)

    updater.stop()
    print(f"\n✅ Simulação concluída!")
    print(json.dumps(updater.get_stats(), indent=2))
    return updater.get_stats()


def cmd_stop(args):
    updater = MemoryManager.get(args.simulation)
    if not updater:
        print(f"\n❌ Simulação {args.simulation} não encontrada")
        return None
    updater.stop()
    stats = updater.get_stats()
    MemoryManager.stop(args.simulation)
    print(f"\n⏹️  MemoryUpdater parado: {args.simulation}")
    print(json.dumps(stats, indent=2))
    return stats


def cmd_stats(args):
    all_stats = MemoryManager.all_stats()
    if not all_stats:
        # Mostrar do DB
        db_path = DB_PATH
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            rows = conn.execute(
                "SELECT graph_id, agent_name, action_type, platform, timestamp "
                "FROM memory_activities ORDER BY timestamp DESC LIMIT 20"
            ).fetchall()
            conn.close()
            print(f"\n📊 Últimas atividades no DB ({len(rows)}):\n")
            for r in rows:
                print(f"  [{r[3]}] {r[1]} → {r[2]} ({r[0][:16]}...)")
        else:
            print("\n📊 Nenhum updater ativo")
        return all_stats

    print(f"\n📊 Updaters ativos ({len(all_stats)}):\n")
    for sim_id, stats in all_stats.items():
        print(f"  {sim_id}:")
        for k, v in stats.items():
            print(f"    {k}: {v}")
        print()
    return all_stats


def main():
    parser = argparse.ArgumentParser(description="Graph Memory Updater")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_start = sub.add_parser("start")
    p_start.add_argument("--graph", default="demo", help="Graph ID")
    p_start.set_defaults(func=cmd_start)

    p_sim = sub.add_parser("simulate")
    p_sim.add_argument("--graph", default="demo", help="Graph ID")
    p_sim.add_argument("--rounds", type=int, default=10, help="Number of simulation rounds")
    p_sim.set_defaults(func=cmd_simulate)

    p_stop = sub.add_parser("stop")
    p_stop.add_argument("--simulation", required=True, help="Simulation ID")
    p_stop.set_defaults(func=cmd_stop)

    sub.add_parser("stats").set_defaults(func=cmd_stats)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    main()
