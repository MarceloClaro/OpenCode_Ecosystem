import sqlite3
import os

DB_PATH = "documents.db"

def init_db():
    """Cria o banco e a tabela caso ainda não existam."""
    if not os.path.exists(DB_PATH):
        print("📦 Criando banco de dados 'documents.db'...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            category TEXT,
            confidence REAL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_classification(filename, category, confidence, content):
    """Salva uma nova classificação."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO classifications (filename, category, confidence, content) VALUES (?, ?, ?, ?)",
        (filename, category, confidence, content),
    )
    conn.commit()
    conn.close()

def get_all_classifications():
    """Lista histórico de classificações."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, filename, category, confidence, created_at FROM classifications ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows
