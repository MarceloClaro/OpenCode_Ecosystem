import sqlite3

# Conectar ao banco de dados (ou criar um novo se não existir)
conn = sqlite3.connect('pizzas.db')

# Criar um cursor
cursor = conn.cursor()

# Criar a tabela pizza
cursor.execute('''
    CREATE TABLE pizza (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        tamanho TEXT NOT NULL,
        preco REAL NOT NULL,
        ingredientes TEXT NOT NULL
    )
''')

# Inserir registros na tabela pizza
pizzas = [
    ('Margherita', 'Pequena', 15.99, 'Tomate, Mozzarella, Manjericão'),
    ('Pepperoni', 'Média', 20.99, 'Pepperoni, Mozzarella'),
    ('Quatro Queijos', 'Grande', 25.99, 'Mozzarella, Cheddar, Parmesão, Gorgonzola'),
    ('Frango com Catupiry', 'Pequena', 18.99, 'Frango, Catupiry, Mozzarella'),
    ('Calabresa', 'Média', 19.99, 'Calabresa, Cebola, Mozzarella')
]

cursor.executemany('''
    INSERT INTO pizza (nome, tamanho, preco, ingredientes)
    VALUES (?, ?, ?, ?)
''', pizzas)

# Salvar (commit) as mudanças
conn.commit()

# Fechar a conexão
conn.close()
