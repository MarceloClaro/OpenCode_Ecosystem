import sqlite3

def create_product_db():
    conn = sqlite3.connect('produtos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            categoria TEXT,
            preco REAL,
            quantidade INTEGER
        )
    ''')
    
    products = [
        ("Camiseta", "Roupas", 29.99, 100),
        ("Calça Jeans", "Roupas", 79.99, 50),
        ("Tênis", "Calçados", 99.99, 30),
        ("Relógio", "Acessórios", 199.99, 20),
        ("Boné", "Acessórios", 19.99, 200),
        ("Mochila", "Acessórios", 49.99, 60),
        ("Celular", "Eletrônicos", 999.99, 15),
        ("Notebook", "Eletrônicos", 1999.99, 10),
        ("Fone de Ouvido", "Eletrônicos", 149.99, 80),
        ("Livro", "Livros", 39.99, 40)
    ]
    
    c.executemany('INSERT INTO produtos (nome, categoria, preco, quantidade) VALUES (?, ?, ?, ?)', products)
    conn.commit()
    conn.close()

create_product_db()
