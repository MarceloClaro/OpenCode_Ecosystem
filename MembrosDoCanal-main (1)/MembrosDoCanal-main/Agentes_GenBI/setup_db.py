# setup_db.py
import argparse
import sqlite3
from pathlib import Path

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto TEXT,
    regiao  TEXT,
    valor   REAL,
    data    TEXT
);
"""

SEED_ROWS = [
    ("Notebook", "Sul",      3500, "2025-06-01"),
    ("Notebook", "Sudeste",  4000, "2025-06-02"),
    ("Celular",  "Nordeste", 2000, "2025-06-05"),
    ("Tablet",   "Norte",    1500, "2025-06-06"),
    ("Notebook", "Sul",      3700, "2025-07-01"),
    ("Celular",  "Sudeste",  2100, "2025-07-02"),
    ("Tablet",   "Nordeste", 1600, "2025-07-03"),
]

def ensure_db(db_path: Path, seed_if_empty: bool = True) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(CREATE_SQL)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM vendas")
    n = cur.fetchone()[0]
    if seed_if_empty and n == 0:
        cur.executemany(
            "INSERT INTO vendas (produto, regiao, valor, data) VALUES (?, ?, ?, ?)",
            SEED_ROWS
        )
        conn.commit()
        print(f"[OK] Tabela 'vendas' criada e populada ({len(SEED_ROWS)} linhas).")
    else:
        print(f"[OK] Tabela 'vendas' criada. Linhas existentes: {n}.")
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inicializa o banco SQLite.")
    parser.add_argument("--db", default="empresa.db", help="Caminho do arquivo SQLite (default: empresa.db)")
    parser.add_argument("--no-seed", action="store_true", help="Não popular com dados de exemplo")
    args = parser.parse_args()

    ensure_db(Path(args.db), seed_if_empty=not args.no_seed)
    print(f"[DONE] Banco pronto em: {Path(args.db).resolve()}")
