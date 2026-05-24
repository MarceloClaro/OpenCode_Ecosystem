import streamlit as st
import os
import pandas as pd
from sqlalchemy import create_engine
from db_schema_logic import extract_schema, setup_llm_chain, generate_sql_query

# Define o título da página
st.set_page_config(page_title="Gerador de Consultas SQL", page_icon=":mag:")

def main():
    st.title("Texto para SQL")
    st.write("Gere instruções SQL a partir de linguagem natural")

    # Barra lateral para configurações
    st.sidebar.header("Configuração")
    openai_api_key = st.sidebar.text_input("Chave API da OpenAI", type="password")
    
    # URL padrão para o banco de dados
    default_db_url = "sqlite:///new.db"
    
    # Carregador de arquivos para o banco de dados
    uploaded_file = st.sidebar.file_uploader("Envie um banco de dados SQLite", type=["db", "sqlite"])
    
    # Botão para processar o banco de dados enviado
    process_db = st.sidebar.button("Processar Banco de Dados Enviado")
    
    # Inicializa o estado da sessão
    if 'db_processed' not in st.session_state:
        st.session_state.db_processed = False
    if 'db_url' not in st.session_state:
        st.session_state.db_url = default_db_url
    if 'schema' not in st.session_state:
        st.session_state.schema = None
    if 'temp_db_file' not in st.session_state:
        st.session_state.temp_db_file = None
    
    if uploaded_file is not None and process_db:
    # Define o diretório para armazenar os bancos de dados
        app_directory = "databases"
        os.makedirs(app_directory, exist_ok=True)  # Garante que o diretório exista

        # Define o caminho completo para salvar o banco de dados
        db_path = os.path.join(app_directory, uploaded_file.name)

        # Salva o arquivo no diretório do aplicativo
        with open(db_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        # Atualiza a URL do banco de dados no estado da sessão
        st.session_state.db_url = f"sqlite:///{os.path.abspath(db_path)}"
        st.session_state.db_processed = True

        # Extrai o esquema do banco de dados
        with st.spinner("Extraindo o esquema do banco de dados..."):
            st.session_state.schema = extract_schema(st.session_state.db_url)

        st.sidebar.success(f"Banco de dados salvo em '{db_path}' e processado com sucesso!")
    elif process_db and uploaded_file is None:
        st.sidebar.warning("Por favor, envie um arquivo de banco de dados primeiro.")
    
    
    if not openai_api_key:
        st.warning("Por favor, insira sua chave API da OpenAI na barra lateral.")
        return

    if st.session_state.schema:
        st.subheader("Esquema do Banco de Dados")
        st.code(st.session_state.schema)

        # Configura a cadeia de modelos de linguagem (LLM)
        try:
            chain = setup_llm_chain(openai_api_key)
        except ValueError as e:
            st.error(f"Erro ao configurar o modelo de linguagem: {str(e)}")
            return

        # Entrada do usuário
        user_question = st.text_input("Digite sua operação:")

        if user_question:
            with st.spinner("Gerando SQL..."):
                sql_query = generate_sql_query(chain, st.session_state.schema, user_question)

            st.subheader("Instrução SQL Gerado")
            st.code(sql_query, language="sql")

        if st.button("Executar SQL"):
            try:
                # Criar engine para conexão com o banco de dados
                engine = create_engine(st.session_state.db_url)
                with engine.connect() as connection:
                    sql_query = sql_query.strip()  # Remove espaços extras
                    from sqlalchemy.sql import text
                    stmt = text(sql_query)

                    if sql_query.lower().startswith("select"):
                        # Para SELECT, buscar e exibir os resultados
                        result = connection.execute(stmt)
                        df = pd.DataFrame(result.fetchall(), columns=result.keys())
                        st.subheader("Resultados da Consulta")
                        st.dataframe(df)
                    else:
                        # Para INSERT, UPDATE, DELETE, executar e confirmar a transação
                        with connection.begin():  # Gerencia a transação automaticamente
                            connection.execute(stmt)
                        st.success("SQL executado com sucesso!")

                        # Extração robusta do nome da tabela
                        table_name = None
                        if "update" in sql_query.lower():
                            table_name = sql_query.split(" ")[1]  # Nome da tabela após UPDATE
                        elif "insert into" in sql_query.lower():
                            table_name = sql_query.split(" ")[2]  # Nome da tabela após INSERT INTO
                        elif "delete from" in sql_query.lower():
                            table_name = sql_query.split(" ")[2]  # Nome da tabela após DELETE FROM

                        if table_name:
                            # Obter registros atualizados da tabela
                            query_table = f"SELECT * FROM {table_name.strip(';')}"
                            st.info(f"Registros da tabela '{table_name.strip(';')}':")
                            try:
                                result = connection.execute(text(query_table))
                                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                                st.dataframe(df)
                            except Exception as e:
                                st.warning(f"Não foi possível carregar os registros da tabela '{table_name.strip(';')}': {str(e)}")
                        else:
                            st.warning("Não foi possível identificar a tabela afetada pela consulta.")

            except Exception as e:
                st.error(f"Erro ao executar a consulta: {str(e)}")

    else:
        st.info("Por favor, envie um banco de dados e clique em 'Processar Banco de Dados Enviado' para começar.")
   
if __name__ == "__main__":
    main()

# Função de limpeza para ser chamada quando o aplicativo Streamlit for fechado ou reiniciado
def cleanup():
    if st.session_state.temp_db_file:
        st.session_state.temp_db_file.close()
        os.unlink(st.session_state.temp_db_file.name)
        st.session_state.temp_db_file = None

# Registra a função de limpeza
import atexit
atexit.register(cleanup)


