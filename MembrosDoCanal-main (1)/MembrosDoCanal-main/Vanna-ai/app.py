from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

# Define a classe personalizada que herda da Vanna
class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

# Instancia com o modelo Ollama desejado
vn = MyVanna(config={'model': 'llama3.1:8b'})

# Conecta ao banco de dados SQLite
vn.connect_to_sqlite('vendas_normalizado.db')

from vanna.flask import VannaFlaskApp
app = VannaFlaskApp(vn)
app.run()