import sqlite3

def create_db():
    conn = sqlite3.connect('futebol_jogos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS jogos (
            nome_time TEXT,
            jogo_id TEXT,
            status TEXT,
            time_da_casa TEXT,
            time_da_casa_gols INTEGER,
            time_visitante TEXT,
            time_visitante_gols INTEGER
        )
    ''')
    games = [
        ("Flamengo", "Jogo 1 Copa Brasil", "Final", "Flamengo", 1, "Amazonas FC", 0),
        ("Palmeiras", "Jogo 2 Campeonato Brasileiro", "Final", "Palmeiras", 0, "Flamengo", 0),
        ("Corinthians", "Jogo 3 Campeonato Brasileiro", "Final", "Corinthians", 0, "Fortaleza", 0),
        ("São Paulo", "Jogo 4 Campeonato Brasileiro", "Final", "São Paulo", 3, "EC Vitória", 1)
    ]
    c.executemany('INSERT INTO jogos (nome_time, jogo_id, status, time_da_casa, time_da_casa_gols, time_visitante, time_visitante_gols) VALUES (?, ?, ?, ?, ?, ?, ?)', games)
    conn.commit()
    conn.close()

create_db()