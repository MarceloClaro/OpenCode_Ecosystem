# utils.py
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ----------------------------
# SQLite (DB principal)
# ----------------------------
# Cria uma expressão regular (regex) pré-compilada chamada READONLY_BLOCKLIST para procurar palavras-chave “perigosas” dentro de um SQL.
READONLY_BLOCKLIST = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|REPLACE|VACUUM|ATTACH|DETACH|PRAGMA)\b",
    re.IGNORECASE,
)

def get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def validate_sql_readonly(sql: str) -> Tuple[bool, str]:
    s = (sql or "").strip()
    if not s:
        return False, "SQL vazio."
    up = s.lstrip("(").strip().upper()
    if not (up.startswith("SELECT") or up.startswith("WITH")):
        return False, "Somente SELECT/WITH é permitido (read-only)."
    if READONLY_BLOCKLIST.search(up):
        return False, "SQL contém comandos/palavras bloqueadas."
    return True, "OK."

def execute_sql(db_path: str, sql: str, max_rows: int = 300) -> List[Dict[str, Any]]:
    ok, msg = validate_sql_readonly(sql)
    if not ok:
        raise ValueError(msg)

    with get_conn(db_path) as conn:
        cur = conn.execute(sql)
        rows = cur.fetchmany(max_rows)
        return [dict(r) for r in rows]

def init_sample_db(db_path: str) -> None:
    """Cria um DB de exemplo simples para aula."""
    with get_conn(db_path) as conn:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS orders;")
        cur.execute("DROP TABLE IF EXISTS customers;")

        cur.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT NOT NULL
        );
        """)

        cur.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
        """)

        cur.executemany(
            "INSERT INTO customers(customer_id, name, city) VALUES (?, ?, ?);",
            [
                (1, "Ana", "Manaus"),
                (2, "Bruno", "São Paulo"),
                (3, "Carla", "Manaus"),
            ],
        )

        cur.executemany(
            "INSERT INTO orders(order_id, customer_id, amount, created_at) VALUES (?, ?, ?, ?);",
            [
                (101, 1, 120.5, "2026-01-10"),
                (102, 1, 80.0, "2026-01-12"),
                (103, 2, 250.0, "2026-01-13"),
                (104, 3, 60.0, "2026-02-01"),
                (105, 3, 310.0, "2026-02-02"),
            ],
        )
        conn.commit()

def read_schema_sqlite(db_path: str) -> Dict[str, Any]:
    schema: Dict[str, Any] = {"tables": {}, "foreign_keys": []}
    with get_conn(db_path) as conn:
        tables = conn.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
        """).fetchall()

        for t in tables:
            tname = t["name"]
            cols = conn.execute(f"PRAGMA table_info('{tname}')").fetchall()
            schema["tables"][tname] = [
                {"name": c["name"], "type": c["type"], "notnull": bool(c["notnull"]), "pk": bool(c["pk"])}
                for c in cols
            ]
            fks = conn.execute(f"PRAGMA foreign_key_list('{tname}')").fetchall()
            for fk in fks:
                schema["foreign_keys"].append({"from": f"{tname}.{fk['from']}", "to": f"{fk['table']}.{fk['to']}"})
    return schema

def format_schema_for_prompt(schema: Dict[str, Any], max_tables: int = 40, max_cols: int = 120) -> str:
    lines: List[str] = []
    for tname, cols in list((schema.get("tables") or {}).items())[:max_tables]:
        lines.append(f"TABLE {tname}:")
        for c in cols[:max_cols]:
            flags = []
            if c.get("pk"):
                flags.append("PK")
            if c.get("notnull"):
                flags.append("NOT NULL")
            t = c.get("type") or "UNKNOWN"
            lines.append(f"  - {c['name']}: {t}" + (f" ({', '.join(flags)})" if flags else ""))
        lines.append("")
    fks = schema.get("foreign_keys") or []
    if fks:
        lines.append("RELATIONSHIPS (FOREIGN KEYS):")
        for rel in fks[:80]:
            lines.append(f"  - {rel['from']} -> {rel['to']}")
    return "\n".join(lines).strip()

# Checar se o DB principal tem tabelas (para evitar SCHEMA vazio)
def schema_has_tables(db_path: str) -> bool:
    schema = read_schema_sqlite(db_path)
    return bool(schema.get("tables"))

# Garantir DB de exemplo se o banco estiver vazio (ótimo pra aula)
def ensure_sample_db(db_path: str) -> None:
    if not schema_has_tables(db_path):
        init_sample_db(db_path)


# ----------------------------
# Memória mínima (SQLite + TF-IDF)
# ----------------------------

@dataclass
class Lesson:
    id: int
    dialect: str
    intent: str
    title: str
    rule: str
    bad_sql: str
    good_sql: str
    user_note: str

class MemoryStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure()

    def _ensure(self) -> None:
        with get_conn(self.db_path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dialect TEXT NOT NULL,
                intent TEXT NOT NULL,
                title TEXT NOT NULL,
                rule TEXT NOT NULL,
                bad_sql TEXT NOT NULL,
                good_sql TEXT NOT NULL,
                user_note TEXT NOT NULL,
                query_text TEXT NOT NULL
            );
            """)
            conn.commit()

    def add_lesson(
        self,
        *,
        dialect: str,
        intent: str,
        title: str,
        rule: str,
        bad_sql: str,
        good_sql: str,
        user_note: str,
        query_text: str,
    ) -> None:
        with get_conn(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO lessons (dialect, intent, title, rule, bad_sql, good_sql, user_note, query_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (dialect, intent, title, rule, bad_sql, good_sql, user_note, query_text),
            )
            conn.commit()

    def list_lessons(self, dialect: str = "sqlite") -> List[Lesson]:
        with get_conn(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM lessons WHERE dialect = ? ORDER BY id DESC;",
                (dialect,),
            ).fetchall()
        return [Lesson(
            id=r["id"], dialect=r["dialect"], intent=r["intent"], title=r["title"],
            rule=r["rule"], bad_sql=r["bad_sql"], good_sql=r["good_sql"], user_note=r["user_note"]
        ) for r in rows]

    def retrieve(self, query: str, *, dialect: str, intent: str, top_k: int = 4) -> List[Dict[str, Any]]:
        with get_conn(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, title, rule, good_sql, query_text FROM lessons WHERE dialect = ? AND intent = ?;",
                (dialect, intent),
            ).fetchall()

        if not rows:
            with get_conn(self.db_path) as conn:
                rows = conn.execute(
                    "SELECT id, title, rule, good_sql, query_text FROM lessons WHERE dialect = ?;",
                    (dialect,),
                ).fetchall()

        if not rows:
            return []

        corpus = [r["query_text"] for r in rows]
        vect = TfidfVectorizer()
        X = vect.fit_transform(corpus)
        qv = vect.transform([query])
        sims = cosine_similarity(qv, X).flatten()
        idxs = sims.argsort()[::-1][:top_k]

        out: List[Dict[str, Any]] = []
        for i in idxs:
            if sims[i] <= 0.0:
                continue
            r = rows[int(i)]
            out.append({
                "id": r["id"],
                "title": r["title"],
                "rule": r["rule"],
                "good_sql": r["good_sql"],
                "score": float(sims[i]),
            })
        return out


# ----------------------------
# Ollama (mínimo)
# ----------------------------

def call_ollama_generate(
    *,
    prompt: str,
    model: str,
    base_url: str = "http://localhost:11434",
    temperature: float = 0.0,
    num_predict: int = 300,
    timeout: int = 60,
) -> str:
    url = f"{base_url.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return data.get("response", "") or ""

def extract_sql(text: str) -> str:
    t = (text or "").strip()

    if "```" in t:
        parts = t.split("```")
        for p in parts:
            p2 = p.strip()
            if p2.lower().startswith("sql"):
                p2 = p2[3:].strip()
            if p2.upper().startswith("SELECT") or p2.upper().startswith("WITH"):
                return p2.strip()

    m = re.search(r"\b(SELECT|WITH)\b", t, flags=re.IGNORECASE)
    if m:
        return t[m.start():].strip()

    return t


# ----------------------------
# Agente (mínimo)
# ----------------------------

def detect_intent(question: str) -> str:
    q = (question or "").lower()
    if any(x in q for x in ["contar", "quantos", "count"]):
        return "COUNT"
    if any(x in q for x in ["top", "maiores", "maior", "ranking", "mais"]):
        return "TOP_N"
    if any(x in q for x in ["listar", "mostrar", "buscar", "quais", "select"]):
        return "LIST"
    return "GENERIC"

def build_prompt(question: str, schema_text: str, lessons: List[Dict[str, Any]]) -> str:
    if lessons:
        ltxt = "\n".join(
            [f"- {l['title']}: {l['rule']}\n  GOOD_EXAMPLE:\n{l.get('good_sql','')}"
             for l in lessons[:3]]
        )
    else:
        ltxt = "(none)"

    # ✅ Regra extra: evita confusão com a tabela "lessons" do DB de memória
    return f"""
You write SQL for SQLite.

STRICT RULES:
- Output ONLY SQL. No explanations. No markdown.
- READ-ONLY only: SELECT or WITH.
- Use ONLY tables/columns from the schema.
- NEVER use a table named "lessons". It belongs to a separate memory database and is NOT part of the main data.

SCHEMA (main database only):
{schema_text}

MEMORY LESSONS (relevant):
{ltxt}

USER QUESTION:
{question}

SQL:
""".strip()

def agent_answer(
    *,
    question: str,
    db_path: str,
    memory: MemoryStore,
    ollama_model: str,
    ollama_base_url: str,
) -> Dict[str, Any]:
    # ✅ garante que o DB principal não está vazio (senão SCHEMA fica em branco)
    ensure_sample_db(db_path)

    intent = detect_intent(question)
    schema = read_schema_sqlite(db_path)
    schema_text = format_schema_for_prompt(schema)

    lessons = memory.retrieve(question, dialect="sqlite", intent=intent, top_k=4)
    prompt = build_prompt(question, schema_text, lessons)

    raw = call_ollama_generate(
        prompt=prompt,
        model=ollama_model,
        base_url=ollama_base_url,
        temperature=0.0,
        num_predict=350,
    )
    sql = extract_sql(raw)

    ok, msg = validate_sql_readonly(sql)
    if not ok:
        return {
            "ok": False,
            "intent": intent,
            "sql": sql,
            "rows": [],
            "error": msg,
            "prompt": prompt,
            "llm_raw": raw,
            "lessons": lessons,
            "schema_text": schema_text,
        }

    try:
        rows = execute_sql(db_path, sql, max_rows=300)
        return {
            "ok": True,
            "intent": intent,
            "sql": sql,
            "rows": rows,
            "error": None,
            "prompt": prompt,
            "llm_raw": raw,
            "lessons": lessons,
            "schema_text": schema_text,
        }
    except Exception as e:
        return {
            "ok": False,
            "intent": intent,
            "sql": sql,
            "rows": [],
            "error": str(e),
            "prompt": prompt,
            "llm_raw": raw,
            "lessons": lessons,
            "schema_text": schema_text,
        }