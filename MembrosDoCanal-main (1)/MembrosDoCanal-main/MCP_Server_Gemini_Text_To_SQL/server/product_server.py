import sqlite3
from typing import Any, List, Tuple
import logging # Adicionado para logging
import os

from mcp.server.fastmcp import FastMCP

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Inicializa o servidor FastMCP
mcp = FastMCP(
    "product_database_query",
    description="Um servidor para consultar um banco de dados de produtos."
)

# Constantes
DB_NAME = os.path.join(os.path.dirname(__file__), "products.db")

log.info(f"Caminho absoluto do banco de dados: {DB_NAME}")

# --- Ferramenta MCP ---

# IMPORTANTE: Risco de Segurança!
# Executar SQL diretamente de uma fonte externa (como um LLM) é inerentemente
# arriscado devido ao potencial de SQL Injection. Em um ambiente de produção,
# seriam necessárias validações rigorosas, restrições (permitir apenas SELECT),
# ou uma camada de abstração que não exponha SQL bruto.
# Este exemplo simplificado assume que o LLM gerará SQL seguro e apenas SELECT.
@mcp.tool()
async def query_products(sql_query: str) -> str:
    """
    Executa uma consulta SQL SELECT no banco de dados de produtos.

    O banco de dados contém uma tabela chamada 'products' com as seguintes colunas:
    - id (INTEGER, Chave Primária): Identificador único do produto.
    - name (TEXT): Nome do produto.
    - category (TEXT): Categoria do produto (ex: 'Laptop', 'Acessório', 'Monitor').
    - price (REAL): Preço do produto.
    - stock (INTEGER): Quantidade em estoque.

    Args:
        sql_query: Uma string contendo uma consulta SQL SELECT válida para
                   a tabela 'products'. Exemplo:
                   "SELECT name, price FROM products WHERE category = 'Laptop' ORDER BY price DESC LIMIT 5"

    Returns:
        Uma string contendo os resultados da consulta formatados como texto,
        incluindo cabeçalhos de coluna, ou uma mensagem de erro se a consulta falhar
        ou não retornar resultados. Retorna "Consulta inválida. Apenas comandos SELECT são permitidos."
        se a consulta não for um SELECT.
    """
    log.info(f"Recebida consulta SQL: {sql_query}")

    # Verificação básica de segurança (apenas permitir SELECT)
    # Isso é muito rudimentar e pode ser burlado. Não confie nisso em produção!
    if not sql_query.strip().upper().startswith("SELECT"):
        log.warning(f"Consulta não-SELECT bloqueada: {sql_query}")
        return "Consulta inválida. Apenas comandos SELECT são permitidos."

    try:
        # Usar 'with' garante que a conexão seja fechada mesmo se ocorrerem erros
        with sqlite3.connect(DB_NAME) as conn:
            # Configurar row_factory para acessar colunas pelo nome (útil para cabeçalhos)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            log.info(f"Executando consulta no banco de dados: {sql_query}")
            cursor.execute(sql_query)
            results: List[sqlite3.Row] = cursor.fetchall()

            if not results:
                log.info("Consulta executada, nenhum resultado encontrado.")
                return "Nenhum produto encontrado correspondente à sua consulta."

            # Obter nomes das colunas da descrição do cursor
            column_names = [description[0] for description in cursor.description]
            header = " | ".join(column_names)
            separator = "-+-".join(["-" * len(name) for name in column_names])

            # Formatar linhas de resultado
            result_rows = []
            for row in results:
                # Acessa os valores da linha usando os nomes das colunas como chaves
                result_rows.append(" | ".join([str(row[col]) for col in column_names]))

            # Montar a string final de resposta
            formatted_results = f"Resultados da consulta:\n{header}\n{separator}\n" + "\n".join(result_rows)
            log.info(f"Consulta bem-sucedida. Retornando {len(results)} resultados.")
            return formatted_results

    except sqlite3.Error as e:
        log.error(f"Erro ao executar SQL '{sql_query}': {e}", exc_info=True)
        return f"Erro ao executar a consulta no banco de dados: {e}"
    except Exception as e:
        log.error(f"Erro inesperado ao processar a consulta '{sql_query}': {e}", exc_info=True)
        return f"Ocorreu um erro inesperado: {e}"

# --- Execução do Servidor ---
if __name__ == "__main__":
    log.info(f"Iniciando servidor MCP 'product_database_query' no transporte 'stdio'...")
    log.info(f"Conectando ao banco de dados: '{DB_NAME}'")
    # Verifica se o DB existe, caso contrário, instrui o usuário (ou poderia chamar setup_db)
    if not os.path.exists(DB_NAME):
        log.warning(f"Arquivo de banco de dados '{DB_NAME}' não encontrado!")
        print(f"AVISO: O arquivo de banco de dados '{DB_NAME}' não foi encontrado.")      
        # Poderia optar por sair aqui:
        # import sys
        # sys.exit(1)
    else:
         log.info(f"Banco de dados '{DB_NAME}' encontrado.")

    # Inicializa e executa o servidor
    # O transporte 'stdio' é comum para interagir com LLMs via linha de comando/processos
    mcp.run(transport='stdio')
    log.info("Servidor MCP encerrado.")