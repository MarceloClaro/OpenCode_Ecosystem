#!/usr/bin/env python3
"""
ProfileManager — Banco unificado de perfis (SQLite).
Todos os perfis gerados (WhatsApp, simulação, padrão) são persistidos aqui.
A simulação carrega TODOS os perfis disponíveis automaticamente.
"""

import json, os, sqlite3
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

BRAZIL_TZ = timezone(timedelta(hours=-3))

DEFAULT_PROFILES = [
    {"name": "Ministro da Fazenda", "source": "default", "stance": "supportive",
     "activity_level": 0.3, "influence": 3.0, "sentiment_bias": 0.2, "posts_per_hour": 0.3},
    {"name": "Presidente do BC", "source": "default", "stance": "neutral",
     "activity_level": 0.2, "influence": 2.8, "posts_per_hour": 0.2},
    {"name": "CEO Startup IA", "source": "default", "stance": "supportive",
     "activity_level": 0.7, "influence": 2.0, "sentiment_bias": 0.5, "posts_per_hour": 1.5},
    {"name": "Sindicalista", "source": "default", "stance": "critical",
     "activity_level": 0.8, "influence": 1.5, "sentiment_bias": -0.3, "posts_per_hour": 2.0},
    {"name": "Pesquisador Unicamp", "source": "default", "stance": "curious",
     "activity_level": 0.5, "influence": 2.2, "sentiment_bias": 0.1, "posts_per_hour": 0.8},
    {"name": "Jornalista Economico", "source": "default", "stance": "neutral",
     "activity_level": 0.8, "influence": 2.5, "posts_per_hour": 3.0},
]


class ProfileManager:
    """Gerencia banco de perfis unificado para simulação."""

    def __init__(self, db_path: str = ".reversa/profiles.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                source TEXT DEFAULT 'default',
                stance TEXT DEFAULT 'neutral',
                activity_level REAL DEFAULT 0.5,
                influence REAL DEFAULT 1.0,
                sentiment_bias REAL DEFAULT 0.0,
                posts_per_hour REAL DEFAULT 0.5,
                message_count INTEGER DEFAULT 0,
                avg_words REAL DEFAULT 0,
                cognitive_style TEXT,
                top_topics TEXT,
                raw_data TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_profile_name_source ON profiles(name, source)")
        conn.commit()
        conn.close()

        # Seed defaults if empty
        if self.count() == 0:
            self.seed_defaults()

    def seed_defaults(self):
        """Insere perfis padrão iniciais."""
        for p in DEFAULT_PROFILES:
            self.add_or_update(p["name"], source=p["source"],
                stance=p["stance"], activity=p["activity_level"],
                influence=p["influence"], sentiment_bias=p.get("sentiment_bias", 0),
                posts_per_hour=p.get("posts_per_hour", 0.5))

    def add_or_update(self, name: str, source: str = "whatsapp",
                      stance: str = "neutral", activity: float = 0.5,
                      influence: float = 1.0, sentiment_bias: float = 0.0,
                      posts_per_hour: float = 0.5, message_count: int = 0,
                      avg_words: float = 0, cognitive_style: str = None,
                      top_topics: str = None, raw_data: Dict = None) -> bool:
        """Adiciona ou atualiza perfil."""
        conn = sqlite3.connect(self.db_path)
        now = datetime.now(BRAZIL_TZ).isoformat()
        raw_json = json.dumps(raw_data, ensure_ascii=False) if raw_data else None

        existing = conn.execute(
            "SELECT id FROM profiles WHERE name=? AND source=?", (name, source)
        ).fetchone()

        if existing:
            conn.execute("""
                UPDATE profiles SET stance=?, activity_level=?, influence=?,
                sentiment_bias=?, posts_per_hour=?, message_count=?, avg_words=?,
                cognitive_style=?, top_topics=?, raw_data=?, updated_at=?
                WHERE id=?
            """, (stance, activity, influence, sentiment_bias, posts_per_hour,
                  message_count, avg_words, cognitive_style, top_topics, raw_json, now, existing[0]))
        else:
            conn.execute("""
                INSERT INTO profiles (name, source, stance, activity_level, influence,
                sentiment_bias, posts_per_hour, message_count, avg_words,
                cognitive_style, top_topics, raw_data, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (name, source, stance, activity, influence, sentiment_bias,
                  posts_per_hour, message_count, avg_words, cognitive_style,
                  top_topics, raw_json, now, now))
        conn.commit()
        conn.close()
        return True

    def import_whatsapp_profiles(self, profiles: Dict[str, Dict]) -> int:
        """Importa perfis do WhatsAppProfiler para o banco."""
        count = 0
        for name, p in profiles.items():
            topics = [t["topic"] for t in p.get("top_topics", [])]
            self.add_or_update(
                name=name, source="whatsapp",
                stance=p.get("dominant_stance", "neutral"),
                activity=min(p.get("message_count", 10) / 100, 1.0),
                influence=p.get("influence", 1.0),
                sentiment_bias=p.get("avg_sentiment", 0),
                posts_per_hour=p.get("message_count", 10) / 24,
                message_count=p.get("message_count", 0),
                avg_words=p.get("avg_words_per_msg", 0),
                cognitive_style=p.get("cognitive_style"),
                top_topics=",".join(topics),
                raw_data=p,
            )
            count += 1
        return count

    def count(self, source: str = None) -> int:
        conn = sqlite3.connect(self.db_path)
        if source:
            n = conn.execute("SELECT COUNT(*) FROM profiles WHERE source=?", (source,)).fetchone()[0]
        else:
            n = conn.execute("SELECT COUNT(*) FROM profiles").fetchone()[0]
        conn.close()
        return n

    def get_all(self, source: str = None) -> List[Dict]:
        """Retorna todos os perfis."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        if source:
            rows = conn.execute(
                "SELECT * FROM profiles WHERE source=? ORDER BY influence DESC", (source,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM profiles ORDER BY source, influence DESC"
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def to_sim_profiles(self, max_count: int = None) -> List[Dict]:
        """Converte perfis para formato SimAgent."""
        profiles = self.get_all()
        if max_count:
            profiles = profiles[:max_count]

        result = []
        for p in profiles:
            result.append({
                "name": p["name"],
                "labels": [p["source"]],
                "activity_config": {
                    "activity_level": p["activity_level"],
                    "influence_weight": p["influence"],
                    "stance": p["stance"],
                    "sentiment_bias": p["sentiment_bias"],
                    "posts_per_hour": p["posts_per_hour"],
                }
            })
        return result

    def get_summary(self) -> Dict[str, Any]:
        """Resumo de todos os perfis."""
        conn = sqlite3.connect(self.db_path)
        total = conn.execute("SELECT COUNT(*) FROM profiles").fetchone()[0]
        by_source = {}
        for row in conn.execute("SELECT source, COUNT(*) FROM profiles GROUP BY source").fetchall():
            by_source[row[0]] = row[1]
        by_stance = {}
        for row in conn.execute("SELECT stance, COUNT(*) FROM profiles GROUP BY stance").fetchall():
            by_stance[row[0]] = row[1]
        conn.close()
        return {
            "total": total,
            "by_source": by_source,
            "by_stance": by_stance,
            "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
        }

    def clear_source(self, source: str):
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM profiles WHERE source=?", (source,))
        conn.commit()
        conn.close()


# Singleton
_profile_manager = None

def get_profile_manager(db_path: str = ".reversa/profiles.db") -> ProfileManager:
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = ProfileManager(db_path)
    return _profile_manager


# ═══════════════════════════════════════════════════════════════════
# Test
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pm = ProfileManager()
    print("=" * 50)
    print("ProfileManager")
    print("=" * 50)
    print(f"Total profiles: {pm.count()}")
    summary = pm.get_summary()
    print(f"By source: {summary['by_source']}")
    print(f"By stance: {summary['by_stance']}")
    for p in pm.get_all()[:10]:
        print(f"  {p['name']}: {p['stance']} [{p['source']}] inf={p['influence']:.2f}")
    print("OK")
