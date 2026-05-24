from typing import Annotated
from typing_extensions import TypedDict
# Importa módulos para tipagem avançada em Python. 
# `Annotated` permite adicionar metadados às anotações de tipo.
# `TypedDict` define dicionários fortemente tipados, onde as chaves e tipos de valores são explicitamente especificados.

from langgraph.graph import StateGraph, START, END
# Importa `StateGraph`, uma classe para criar grafos de estados, e `START`, `END`, que representam os nós iniciais e finais de um grafo.

from langgraph.graph.message import add_messages
# Importa a função `add_messages`, usada para manipular mensagens no grafo.

from langchain_groq import ChatGroq
# Importa a classe `ChatGroq`, que é um modelo de linguagem treinado em larga escala (como o GPT) da Groq.

import os
from dotenv import load_dotenv
# Importa `os` para interagir com variáveis de ambiente do sistema operacional.
# Importa `load_dotenv` da biblioteca `dotenv`, que carrega variáveis de ambiente de um arquivo `.env`.

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()
# Carrega as variáveis de ambiente do arquivo `.env` no ambiente de execução. 
# Isso permite configurar chaves de API e outras configurações sem as hardcodar no código.

# Configuração da chave da API Groq e Pinecone a partir do .env
groq_api_key = os.getenv("GROQ_API_KEY")
# Obtém a chave da API `GROQ_API_KEY` a partir das variáveis de ambiente carregadas do arquivo `.env`.

os.environ["GROQ_API_KEY"] = groq_api_key
# Define a variável de ambiente `GROQ_API_KEY` no ambiente atual, garantindo que a chave da API esteja disponível para qualquer outro uso no código.

# Define a estrutura de estado do chatbot usando um TypedDict
class State(TypedDict):
    messages: Annotated[list, add_messages]
    # O estado contém uma lista de mensagens, anotada com a função `add_messages` para manipulação no grafo.

# Inicializa um construtor de grafo de estados com o tipo de estado definido anteriormente
graph_builder = StateGraph(State)

# Inicializa o modelo de linguagem Groq com um modelo específico e temperatura de amostragem de 0.5
llm = ChatGroq(model="llama-3.2-11b-text-preview", temperature=0.5)

# Define a função `chatbot`, que aceita um estado e retorna uma nova mensagem invocando o modelo de linguagem
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}
    # O modelo `llm` é invocado com as mensagens do estado atual, e o resultado é retornado como uma nova mensagem.

# Adiciona o nó `chatbot` ao grafo
graph_builder.add_node("chatbot", chatbot)
# Define o chatbot como um nó no grafo de estados.

# Adiciona uma aresta do início (START) para o nó `chatbot`
graph_builder.add_edge(START, "chatbot")
# Cria uma conexão que indica que a execução do grafo começa no chatbot.

# Adiciona uma aresta do nó `chatbot` até o final (END)
graph_builder.add_edge("chatbot", END)
# Define que, após o chatbot processar, o grafo deve encerrar a execução.

# Compila o grafo de estados configurado
graph = graph_builder.compile()
# Finaliza a construção do grafo, tornando-o pronto para ser usado.

# Define uma função para processar a entrada do usuário e transmitir atualizações do grafo
def stream_graph_updates(user_input: str):
    # Processa a entrada do usuário, criando uma mensagem e passando-a pelo grafo
    for event in graph.stream({"messages": [("user", user_input)]}):
        # Itera sobre os eventos gerados pela execução do grafo com a mensagem do usuário
        for value in event.values():
            # Para cada valor gerado pelo evento, exibe a última mensagem da resposta do assistente
            print("Assistant:", value["messages"][-1].content)

# Loop principal do chatbot
while True:
    try:
        user_input = input("User: ")
        # Captura a entrada do usuário via o teclado
        if user_input.lower() in ["quit", "exit", "q"]:
            # Verifica se o usuário deseja sair com comandos como "quit", "exit" ou "q"
            print("Goodbye!")
            break
        # Se o usuário não pediu para sair, processa a entrada com o chatbot
        stream_graph_updates(user_input)
    except:       
        # Se ocorrer um erro, define uma entrada padrão e processa a mensagem com o chatbot
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break


