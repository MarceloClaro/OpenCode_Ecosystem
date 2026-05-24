from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_groq import ChatGroq

db = SQLDatabase.from_uri("sqlite:///pizzas.db")

llm = ChatGroq(
    temperature=0,
    model="llama3-70b-8192",
    api_key="sua chave aqui"
)

agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)

result = agent_executor.invoke(
    "Responda em português quais são os sabores de pizza?"
)
print(result['output'])

agent_executor.invoke(
    "Insira no banco de dados o sabor de pizza Romeu e Julieta de tamanho grande, preço 30.99 e que possui os ingredientes mussarela, molho de tomate e goiabada."
)

agent_executor.invoke(
    "Alterar o preço da de pizza Romeu e Julieta para 60.99"
)

agent_executor.invoke(
    "Delete a pizza Romeu e Julieta do banco de dados"
)

