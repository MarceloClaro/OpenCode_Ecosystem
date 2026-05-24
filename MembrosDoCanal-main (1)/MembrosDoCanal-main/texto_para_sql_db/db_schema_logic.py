from langchain import OpenAI, LLMChain
from langchain.prompts import PromptTemplate
from sqlalchemy import create_engine, inspect

def extract_schema(db_url):
    """
    Extrai o esquema do banco de dados sem acessar os dados reais.
    
    Parâmetros:
        db_url (str): URL do banco de dados no formato SQLAlchemy.

    Retorna:
        str: Esquema do banco de dados formatado como texto.
    """
    engine = create_engine(db_url)  # Cria uma conexão com o banco de dados.
    inspector = inspect(engine)  # Inicializa o inspetor para acessar metadados do banco.
    
    schema_info = []
    for table_name in inspector.get_table_names():  # Obtém os nomes das tabelas no banco.
        columns = inspector.get_columns(table_name)  # Obtém as colunas de cada tabela.
        schema_info.append(f"Table: {table_name}")  # Adiciona o nome da tabela ao esquema.
        for column in columns:
            # Adiciona as informações das colunas (nome e tipo de dado) ao esquema.
            schema_info.append(f"  - {column['name']} ({column['type']})")
    
    return "\n".join(schema_info)  # Retorna o esquema como uma string formatada.

def setup_llm_chain(openai_api_key):
    """
    Configura os componentes do LangChain para gerar consultas SQL.

    Parâmetros:
        openai_api_key (str): Chave da API do OpenAI para acessar o modelo de linguagem.

    Retorna:
        LLMChain: Uma cadeia de modelos de linguagem configurada para processar solicitações.
    """
    llm = OpenAI(temperature=0, openai_api_key=openai_api_key)  # Inicializa o modelo OpenAI.

    # Modelo do prompt que será utilizado para gerar as consultas SQL.
    prompt_template = """
    Você é um assistente de IA que gera consultas SQL com base nas solicitações dos usuários.
    Você tem acesso ao seguinte esquema do banco de dados:

    {schema}

    Com base APENAS nesse esquema, gere uma consulta SQL para responder à seguinte pergunta:

    {question}

    Se a pergunta não puder ser respondida usando APENAS o esquema fornecido,
    responda com "I cannot answer this question based on the given schema."

    SQL Query:
    """

    # Cria um modelo de prompt com as variáveis `schema` e `question`.
    prompt = PromptTemplate(
        input_variables=["schema", "question"],
        template=prompt_template,
    )

    # Retorna a cadeia de modelos configurada.
    return LLMChain(llm=llm, prompt=prompt)

def generate_sql_query(chain, schema, question):
    """
    Gera uma consulta SQL com base no esquema do banco e na pergunta do usuário.

    Parâmetros:
        chain (LLMChain): A cadeia de modelos configurada para gerar SQL.
        schema (str): Esquema do banco de dados formatado.
        question (str): Pergunta do usuário em linguagem natural.

    Retorna:
        str: Consulta SQL gerada.
    """
    return chain.run(schema=schema, question=question)
