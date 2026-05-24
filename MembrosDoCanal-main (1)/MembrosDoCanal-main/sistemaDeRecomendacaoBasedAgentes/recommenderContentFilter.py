import os
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import FileReadTool

MusicCatalogue_tool = FileReadTool(file_path='./MusicCatalogue.txt')
MusicHistory_tool = FileReadTool(file_path='./MusicHistory.txt')

# Correctly load the Google API key from an environment variable
google_api_key = os.getenv("GOOGLE_API_KEY")  
google_api_key = "sua chave aqui"

# Set gemini pro as llm
llm = ChatGoogleGenerativeAI(
    model="gemini-pro", verbose=True, temperature=0.1, google_api_key=google_api_key
)

# Define your agents with roles and goals
researcher = Agent(
  role='Recomendador Personalizado de músicas',
  goal='Recomendar músicas para um usuário usando o seu histórico de músicas escutadas',
  backstory="""Você é um Recomendador Personalizado de músicas, 
  Você tem uma alta competência técnica para usar técnicas de filtramgem de informação para recomendar músicas para os usuários.""",
  verbose=True,
  allow_delegation=False,
  llm=llm,   
)

# Create tasks for your agents
task1 = Task(
  description="""Obter o catálogo de músicas disponíveis.""",
  agent=researcher,
  tools=[MusicCatalogue_tool],  
  expected_output="Lista de músicas disponíveis"  
)

# Create tasks for your agents
task2 = Task(
  description="""Obter o histórico de músicas escutadas pelo usuário.""",
  agent=researcher,
  tools=[MusicHistory_tool],  
  expected_output="Histórico de músicas"  
)

# Create tasks for your agents
task3 = Task(
  description="""Inferir o gênero de música preferido pelo usuário.
  Para essa tarefa use o histórico de músicas que usuário escutou para inferir qual é o gênero de música de seu interesse.""",
  agent=researcher,  
  context=[task2],  
  expected_output="Gênero de música inferido"  
)

# Create tasks for your agents
task4 = Task(
  description="""Gerar uma lista de músicas, contendo somente as músicas que foram selecionadas do catálogo de músicas fornecido como contexto.
  Para essa tarefa use o histórico de músicas que usuário escutou para inferir qual é o gênero de música de seu interesse. 
  Selecione no catálogo de músicas somente as músicas do gênero de música inferido, e que não estejam no histórico de músicas que usuário escutou.""",
  agent=researcher,  
  context=[task1, task2, task3],  
  expected_output="Lista de músicas selecionadas"  
)

task5 = Task(
  description="""Apresenta lista final de músicas recomendadas para usuário.
  Forneça uma lista final de recomendação com os nomes e gêneros somente das músicas que foram selecionadas do catálogo de músicas disponíveis.""",
  agent=researcher,  
  context=[task4],  
  expected_output="Lista final de músicas recomendadas"  
)

# Instantiate your crew with a sequential process
crew = Crew(
  agents=[researcher],
  tasks=[task1, task2, task3, task4, task5],
  verbose=2
)

# Get your crew to work!
result = crew.kickoff()

print(result)
