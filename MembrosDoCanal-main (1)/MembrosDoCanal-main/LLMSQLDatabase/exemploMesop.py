import mesop as me
import mesop.labs as mel
from mesop import stateclass

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


@stateclass
class State:
    pass

@me.page(
    security_policy=me.SecurityPolicy(
        allowed_iframe_parents=["https://google.github.io"]
    ),
    path="/",
    title="Pizzaria Delicia Chat",
)
def page():
    mel.chat(transform, title="Pizzaria Delicia Chatbot", bot_user="Mesop Bot")


def transform(input: str, history: list[mel.ChatMessage]):
    
    result = agent_executor.invoke("Responda somente em português a questão: "+input)
   
    content = result['output']
    if content:
        yield content


