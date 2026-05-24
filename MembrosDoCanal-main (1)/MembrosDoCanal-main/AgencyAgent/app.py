import os
import json
import requests
from crewai import Agent, Task, Crew
from crewai_tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI

from crewai_tools import tool

google_api_key = "sua chave aqui"


# Set gemini pro as llm
llm = ChatGoogleGenerativeAI(
    model="gemini-pro", verbose=True, temperature=0.1, google_api_key=google_api_key
)


# 1. Create Custom Tool to Get Game Score from API
@tool("Game Score Tool")
def game_score_tool(nome_time: str) -> str:
    """Obtem o resultado de um jogo do Campeonato Brasileiro de um determinado time por meio de uma consulta a Flask API."""
    
    url = f'http://127.0.0.1:5000/placar?time={nome_time}'
    
    response = requests.get(url)

    if response.status_code == 200:
        return json.dumps(response.json(), indent=2)
    else:
        return json.dumps({"error": "API request failed", "status_code": response.status_code}, indent=2)

# 2. Create Agents
researcher = Agent(
    role='Pesquisador',
    goal='Coletar e analisar informações sobre os placares do Campeonato Brasileiro de Futebol.',
    verbose=True,
    backstory=(
        "Como um pesquisador experiente, você tem um olhar atento para detalhes e um "
        "profundo entendimento de análises esportivas. Você é habilidoso em peneirar "
        "placares para encontrar os dados mais relevantes e precisos."
    ),
    tools=[game_score_tool],
    allow_delegation=False,
    llm=llm
)

writer = Agent(
    role='Jornalista Esportivo',
    goal='Redija um artigo jornalístico envolvente baseado nos placares do Campeonato Brasileiro de Futebol',
    verbose=True,
    backstory=(
        "Com um talento para contar histórias, você converte dados estatísticos e resultados de jogos "
        "em narrativas esportivas envolventes. Seus artigos são perspicazes, capturando a emoção "
        "dos jogos e fornecendo uma análise profunda para os entusiastas do esporte."
    ),
    allow_delegation=False,
    llm=llm
)

# 3. Define Tasks
research_task = Task(
    description="Investigue o placar do jogo do Flamengo.",
    expected_output='Um relatório detalhado resumindo os dados.',
    tools=[game_score_tool],
    agent=researcher,
)

writing_task = Task(
    description="Escreva em português um artigo jornalístico detalhado sobre uma partida do Campeonato Brasileiro de Futebol, focando em estatísticas.",
    expected_output='Um artigo envolvente e informativo, adequado para publicação em mídias esportivas.',
    context=[research_task],
    agent=writer,
)

# 4. Run the Crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task]
)

result = crew.kickoff()
print(result)