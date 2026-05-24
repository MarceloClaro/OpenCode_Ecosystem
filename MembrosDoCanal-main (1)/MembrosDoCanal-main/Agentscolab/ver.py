import sqlite3
import json

conn = sqlite3.connect("agenthub.db")
cur = conn.cursor()

cur.execute("SELECT id, status, output FROM collaborations")
rows = cur.fetchall()

for r in rows:
    print("\n--- COLLAB ---")
    print("ID:", r[0])
    print("STATUS:", r[1])
    print("OUTPUT:\n")
    print(json.dumps(r[2], ensure_ascii=False, indent=2))
