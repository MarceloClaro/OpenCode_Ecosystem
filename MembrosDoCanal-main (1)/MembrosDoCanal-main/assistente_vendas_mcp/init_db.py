from sqlalchemy import create_engine, Table, Column, String, MetaData, DateTime
from datetime import datetime, timedelta

# Conectar ao banco
engine = create_engine('sqlite:///database/db.sqlite3', connect_args={"check_same_thread": False})
metadata = MetaData()

# Definir a tabela
clients = Table('clients', metadata,
    Column('id', String, primary_key=True),
    Column('name', String),
    Column('last_purchase', DateTime)
)

# Criar tabela se necessário
metadata.create_all(engine)

# Inserir registros dentro de uma transação
with engine.begin() as conn:  # <<<<<<<<<< ATENÇÃO: aqui muda para begin()
    conn.execute(clients.insert(), [
        {"id": "c1", "name": "João Silva", "last_purchase": datetime.now() - timedelta(days=120)},
        {"id": "c2", "name": "Maria Oliveira", "last_purchase": datetime.now() - timedelta(days=30)},
        {"id": "c3", "name": "Carlos Pereira", "last_purchase": datetime.now() - timedelta(days=200)},
    ])

print("✅ Banco de dados inicializado com dados!")
