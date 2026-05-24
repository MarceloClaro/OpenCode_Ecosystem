
import sqlite3
import os
from datetime import datetime, timedelta

def setup_database():
    """
    Resets and populates the database with product, supplier, and opportunity data.
    """
    db_path = 'database/estoque.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Banco de dados antigo removido.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # --- Tabela de Produtos ---
    cursor.execute("""
    CREATE TABLE produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        quantidade INTEGER NOT NULL,
        preco REAL NOT NULL,
        demanda_mensal INTEGER NOT NULL,
        data_ultima_venda DATE,
        data_cadastro DATE NOT NULL
    )
    """)

    # --- Tabela de Fornecedores ---
    cursor.execute("""
    CREATE TABLE fornecedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_fornecedor TEXT NOT NULL,
        produto_id INTEGER NOT NULL,
        preco_unidade REAL NOT NULL,
        prazo_entrega_dias INTEGER NOT NULL,
        contato_email TEXT,
        FOREIGN KEY (produto_id) REFERENCES produtos (id)
    )
    """)

    # --- Tabela de Oportunidades de Venda ---
    cursor.execute("""
    CREATE TABLE oportunidades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa_lead TEXT NOT NULL,
        produto_id INTEGER NOT NULL,
        quantidade_proposta INTEGER NOT NULL,
        status TEXT NOT NULL, -- 'Em Negociação', 'Ganha', 'Perdida'
        data_criacao DATE NOT NULL,
        FOREIGN KEY (produto_id) REFERENCES produtos (id)
    )
    """)

    # --- Dados dos Produtos ---
    hoje = datetime.now()
    dados_produtos = [
        (1, 'Laptop Gamer Pro', 15, 7500.00, 20, (hoje - timedelta(days=10)).strftime('%Y-%m-%d'), '2023-01-15'),
        (2, 'Mouse Sem Fio Ergonômico', 120, 180.00, 150, (hoje - timedelta(days=5)).strftime('%Y-%m-%d'), '2023-02-20'),
        (3, 'Teclado Mecânico RGB', 8, 450.00, 50, (hoje - timedelta(days=25)).strftime('%Y-%m-%d'), '2023-03-10'),
        (4, 'Monitor Ultrawide 34"', 40, 2800.00, 35, (hoje - timedelta(days=3)).strftime('%Y-%m-%d'), '2023-01-30'),
        (5, 'Headset Gamer 7.1', 90, 650.00, 100, (hoje - timedelta(days=1)).strftime('%Y-%m-%d'), '2023-04-05'),
        (6, 'Webcam Full HD', 5, 320.00, 60, (hoje - timedelta(days=100)).strftime('%Y-%m-%d'), '2022-11-20'),
        (7, 'Impressora Multifuncional', 30, 1200.00, 25, (hoje - timedelta(days=150)).strftime('%Y-%m-%d'), '2022-09-01'),
        (8, 'SSD NVMe 1TB', 60, 850.00, 80, (hoje - timedelta(days=95)).strftime('%Y-%m-%d'), '2023-01-05'),
        (9, 'Cadeira Gamer Confort', 25, 1800.00, 20, (hoje - timedelta(days=200)).strftime('%Y-%m-%d'), '2022-07-15'),
        (10, 'Placa de Vídeo RTX 3060', 4, 2500.00, 15, (hoje - timedelta(days=120)).strftime('%Y-%m-%d'), '2022-12-01'),
        (11, 'HD Externo 2TB', 80, 450.00, 40, (hoje - timedelta(days=180)).strftime('%Y-%m-%d'), '2022-05-10'),
        (12, 'Roteador Wi-Fi 6', 45, 700.00, 50, (hoje - timedelta(days=110)).strftime('%Y-%m-%d'), '2022-10-25')
    ]
    cursor.executemany("INSERT INTO produtos VALUES (?, ?, ?, ?, ?, ?, ?)", dados_produtos)

    # --- Dados dos Fornecedores ---
    dados_fornecedores = [
        ('PC Peças Express', 1, 6800.00, 7, 'vendas@pcpecasexpress.com'),
        ('Mega Hardware BR', 1, 6750.00, 15, 'contato@megahardware.com'),
        ('Atacado Tech', 3, 380.00, 5, 'comercial@atacadotech.com'),
        ('ImportaTudo', 3, 350.00, 20, 'vendas@importatudo.com'),
        ('Webcam World', 6, 250.00, 10, 'contato@webcamworld.com'),
        ('Distribuidora Global', 6, 260.00, 3, 'global@distribuidora.com'),
        ('GPU Masters', 10, 2200.00, 12, 'gpu@masters.com'),
        ('Info Parts Atacado', 10, 2150.00, 25, 'contato@infoparts.com')
    ]
    cursor.executemany("INSERT INTO fornecedores (nome_fornecedor, produto_id, preco_unidade, prazo_entrega_dias, contato_email) VALUES (?, ?, ?, ?, ?)", dados_fornecedores)

    # --- Dados de Oportunidades (Exemplo) ---
    dados_oportunidades = [
        ('LogiMax Transportes', 12, 50, 'Em Negociação', (hoje - timedelta(days=2)).strftime('%Y-%m-%d')),
        ('InovaTech Soluções', 1, 10, 'Em Negociação', (hoje - timedelta(days=5)).strftime('%Y-%m-%d'))
    ]
    cursor.executemany("INSERT INTO oportunidades (empresa_lead, produto_id, quantidade_proposta, status, data_criacao) VALUES (?, ?, ?, ?, ?)", dados_oportunidades)

    conn.commit()
    conn.close()
    print("Banco de dados 'estoque.db' recriado com as tabelas 'produtos', 'fornecedores' e 'oportunidades'.")

if __name__ == '__main__':
    setup_database()
