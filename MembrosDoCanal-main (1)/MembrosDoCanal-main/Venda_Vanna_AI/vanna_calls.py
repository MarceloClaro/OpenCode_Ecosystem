import streamlit as st

from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

# Define a classe personalizada que herda da Vanna
class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)


@st.cache_resource(ttl=3600)
def setup_vanna():
    # Instancia com o modelo Ollama desejado
    vn = MyVanna(config={'model': 'llama3.1:8b'})

    # Conecta ao banco de dados SQLite
    vn.connect_to_sqlite('vendas_normalizado.db')

    # Carrega todos os DDLs das tabelas existentes e treina com eles
    df_ddl = vn.run_sql("SELECT type, sql FROM sqlite_master WHERE sql is not null")

    for ddl in df_ddl['sql'].to_list():
        vn.train(ddl=ddl)
    
    vn.train(documentation="A tabela 'produto' contém informações dos produtos.")
    vn.train(documentation="A tabela 'categoria' contém as categorias dos produtos.")
    vn.train(documentation="A tabela 'vendas' contém a quantidade de vendas, a data de vendas dos produtos.")
    vn.train(documentation="A tabela 'produto' se conecta à tabela 'vendas' pela coluna produto_id usando INNER JOIN.")
    vn.train(documentation="A tabela 'produto' se conecta à tabela 'categoria' pela coluna categoria_id usando INNER JOIN.")     
    return vn


@st.cache_data(show_spinner="Aguarde estou pensando ...")
def generate_sql_cached(question: str):
    vn = setup_vanna()
    return vn.generate_sql(question=question, allow_llm_to_see_data=True)


@st.cache_data(show_spinner="Running SQL query ...")
def run_sql_cached(sql: str):
    vn = setup_vanna()
    return vn.run_sql(sql=sql)

@st.cache_data(show_spinner="Checking if we should generate a chart ...")
def should_generate_chart_cached(question, sql, df):
    vn = setup_vanna()
    return vn.should_generate_chart(df=df)

@st.cache_data(show_spinner="Generando o gráfico ...")
def generate_plotly_code_cached(question, sql, df):
    vn = setup_vanna()
    code = vn.generate_plotly_code(question=question, sql=sql, df=df)
    return code

@st.cache_data(show_spinner="Running Plotly code ...")
def generate_plot_cached(code, df):
    vn = setup_vanna()
    return vn.get_plotly_figure(plotly_code=code, df=df)


