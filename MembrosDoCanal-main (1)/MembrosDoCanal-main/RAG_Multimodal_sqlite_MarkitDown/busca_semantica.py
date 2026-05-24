# To run this script, you need to install the following packages:
# uv pip install ollama sqlite-vec numpy
#
# Please make sure Ollama is running and you have pulled the 'embeddinggemma:latest' model, `ollama pull embeddinggemma:latest`.

import sqlite3
import sqlite_vec
from sqlite_vec import serialize_float32
import ollama
import numpy as np
import sys

# Configuration
DB_FILE = "gemma_embeddings.db"
MODEL_NAME = "embeddinggemma:latest"
EMBEDDING_DIM = 768
SAMPLE_TEXTS = [
    "O céu é azul por causa da dispersão de Rayleigh.",
    "A fotossíntese é o processo usado pelas plantas para converter energia luminosa em energia química.",
    "O Império Romano foi o período pós-republicano da Roma antiga.",
    "Inteligência artificial é a inteligência demonstrada por máquinas.",
    "A mudança climática é uma alteração de longo prazo nos padrões médios do clima.",
]

def get_db_connection():
    """Estabelece uma conexão com o banco de dados SQLite e carrega a extensão sqlite-vec."""
    
    # Cria uma conexão com o arquivo de banco de dados definido na variável DB_FILE
    # (se o arquivo não existir, o SQLite criará um novo automaticamente)
    db = sqlite3.connect(DB_FILE)

    # Permite o carregamento de extensões dinâmicas (necessário para usar a sqlite-vec)
    db.enable_load_extension(True)

    # Carrega a extensão sqlite-vec na instância do banco de dados.
    # Essa extensão adiciona suporte a vetores e operações de similaridade no SQLite.
    sqlite_vec.load(db)

    # Desativa novamente o carregamento de extensões por segurança
    db.enable_load_extension(False)

    # Executa uma consulta para verificar a versão atual da extensão sqlite-vec carregada
    version_info = db.execute("select vec_version()").fetchone()[0]

    # Exibe a versão no console para confirmar o carregamento correto
    print(f"Using sqlite-vec version: {version_info}")

    # Retorna o objeto de conexão 'db', que será usado para executar comandos SQL posteriormente
    return db



def setup_database(db):
    """Sets up the database tables and populates them with sample data embeddings if the database is empty."""
    try:
        count = db.execute("SELECT COUNT(*) FROM vec_items").fetchone()[0]
        if count > 0:
            print("Database already contains data. Skipping setup.")
            return
    except sqlite3.OperationalError:
        # This error means the table doesn't exist, so we proceed with setup
        pass

    print("Setting up a new database...")
    # Create the necessary tables
    db.execute(
        f"CREATE VIRTUAL TABLE vec_items USING vec0(embedding float[{EMBEDDING_DIM}], content TEXT)"
    )

    print("Embedding and storing sample texts...")
    embeddings_response = ollama.embed(model=MODEL_NAME, input=SAMPLE_TEXTS)
    # Use a transaction to insert all data at once for efficiency
    with db:
        for text, embedding in zip(SAMPLE_TEXTS, embeddings_response.embeddings):
            # Convert the embedding to a NumPy array of 32-bit floats for sqlite-vec
            db.execute(
                "INSERT INTO vec_items(embedding, content) VALUES (?, ?)",
                (serialize_float32(embedding), text),
            )
    print("Database setup complete.")


def main():
    """Main function to run the interactive semantic search script."""
    db = get_db_connection()
    setup_database(db)
    print("Digite uma consulta para encontrar o texto mais semelhante no banco de dados.")

    try:
        while True:
            query = input("\nDigite uma consulta de pesquisa (ou 'exit' para sair): ")
            if query.lower() == "exit":
                break
            if not query.strip():
                continue

            query_embedding_response = ollama.embed(model=MODEL_NAME, input=query)
            # Perform the vector search
            rows = db.execute(
                """
                SELECT
                    content,
                    distance
                FROM vec_items
                WHERE embedding MATCH ?
                AND k = 3
                ORDER BY distance
                """,
                [serialize_float32(query_embedding_response.embeddings[0])],
            ).fetchall()

            # Display the results
            print("\nOs 3 textos mais semelhantes:")
            print("Menor distância significa que estão mais próximos e são mais semelhantes.")
            for i, (content, distance) in enumerate(rows):
                print(f"{i+1}. {content} (distância: {distance:.4f})")

    except KeyboardInterrupt:
        print("\nSaindo...")
    finally:
        db.close()
        print("Conexão com o banco de dados fechada.")


if __name__ == "__main__":
    main()
