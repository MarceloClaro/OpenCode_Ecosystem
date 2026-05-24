import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from crewai import Crew, Task, Agent
from crewai.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()

# LLM object and API Key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("TAVILY_API_KEY")

llm = ChatOpenAI(
    openai_api_base="https://api.openai.com/v1/chat/completions",
    openai_api_key=os.environ['OPENAI_API_KEY'],
    model_name="gpt-4o-mini",
    temperature=0.1,
    max_tokens=1000,
)

web_search_tool = TavilySearchResults(k=10)

@tool("BuscadorWeb")
def buscadorWeb_tool(tema: str) -> str:
    """Realiza busca na web de reportagens que abordam o tema da notícia."""
    return web_search_tool.run(tema)

# Configuração dos agentes
Retriever_Agent = Agent(
    role="Recuperador",
    goal="Responsável por recuperar ou coletar preços.",
    backstory=(
        "Responsável por encontrar preços de produtos ou serviços em fontes diversas como sites de vendas e marketplaces." 
        "Executa web scrapting para obter preços de produtos."   
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm,
)

Data_Analyst_Agent = Agent(
    role="Responsável pela análise de dados.",
    goal="Processar as informações coletadas eliminando duplicatas e identificando padrões.",
    backstory=(
        "Responsável por processar as informações coletadas eliminando duplicatas e identificando padrões."
        "Avaliar fatores como preço, características do produto ou serviço"
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm,
)

Filtering_Agent = Agent(
    role="Responsável pela filtragem dos produtos e serviços.",
    goal="Aplicar regras para priorizar as melhores ofertas.",
    backstory=(
        "Responsável por aplicar critérios ou regras para priorizar ou filtrar as melhores ofertas de produtos e serviços."
        "Permite personalização com base em critérios do usuário, como menor preço ou melhor avaliação. "
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm,
)

Answer_Agent = Agent(
    role="Responsável por apresenta os resultados para o chatbot.",
    goal="Apresentar a lista final de produtos ou serviços.",
    backstory=(
        "Responsável por apresentar a lista final de produtos ou serviços."
        "Pode oferecer explicações sobre as escolhas para aumentar a transparência. "
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm,
)

retriever_task = Task(
    description=("Encontrar preços de produtos ou serviços que são de interesse {interesse} do usuário, e ofertados em fontes diversas como sites de vendas e marketplaces."
    ),
    expected_output=("Uma lista de preços de produtos ou serviços que são de interesse {interesse} do usuário, e ofertados em sites de vendas e marketplaces."),
    agent=Retriever_Agent,
    tools=[buscadorWeb_tool],
    
)

data_analyst_agent_task = Task(
    description=("Processar as informações coletadas pelo 'retriever_task' eliminando duplicatas e identificando padrões."
    ),
    expected_output=("Preços de produtos ou serviços sem duplicatas que estão em ofetas."),
    agent=Data_Analyst_Agent,
    context=[retriever_task],
)

filtering_agent_task = Task(
    description=("Filtrar as informações processadas pelo 'data_analyst_agent_task'."
    ),
    expected_output=("Aplicar critérios ou regras para priorizar ou filtrar as melhores ofertas de produtos e serviços."),
    agent=Filtering_Agent,
    context=[data_analyst_agent_task],
)

answer_Agent_task = Task(
    description=("Gerar a lista final de produtos ou serviços."
    ),
    expected_output=("lista final de ofertas de produtos ou serviços filtrados, links das fontes, e explicações sobre as escolhas para aumentar a transparência."),
    agent=Answer_Agent,
    context=[filtering_agent_task],
)

rag_crew = Crew(
    agents=[Retriever_Agent, Data_Analyst_Agent, Filtering_Agent, Answer_Agent],
    tasks=[retriever_task, data_analyst_agent_task, filtering_agent_task, answer_Agent_task],
    verbose=True,
)


# Streamlit Interface
col1, col2, col3 = st.columns([1, 2, 1])  # ajuste as proporções conforme necessário
with col1:
    st.write("")
with col2:
    st.image("ofertaschat.png", caption="", use_container_width=True)
with col3:
    st.write("")
st.markdown("Informe o produto ou serviço de interesse, e o chatbot buscará na web, processará e filtrará as melhores ofertas disponíveis.")

# Entrada do usuário
user_input = st.text_input("Digite o produto ou serviço de interesse", placeholder="Ex: Preços de Onix 2025 que estão em ofertas")

if st.button("Buscar Ofertas"):
    if user_input:        
        with st.spinner('Processando sua solicitação...'):
            inputs = {"interesse": user_input}
            crew_output = rag_crew.kickoff(inputs=inputs)
            
            st.subheader("Resultados Filtrados")
            st.markdown(crew_output)
    else:
        st.error("Por favor, insira um interesse válido.")
