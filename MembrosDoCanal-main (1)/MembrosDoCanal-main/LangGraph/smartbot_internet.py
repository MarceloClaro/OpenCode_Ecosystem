from typing import Annotated
# Importa o `Annotated`, que permite adicionar metadados a uma anotação de tipo, ajudando a descrever melhor a função dos tipos.

from langchain_community.tools.tavily_search import TavilySearchResults
# Importa a ferramenta de pesquisa `TavilySearchResults`, que permite buscar resultados em tempo real a partir de Tavily.

from typing_extensions import TypedDict
# Importa o `TypedDict`, que permite definir dicionários com chaves e tipos de valores explícitos, para maior tipagem de dados no código.

from langgraph.graph import StateGraph
# Importa a classe `StateGraph`, que cria uma estrutura de grafo de estados para modelar fluxos de trabalho ou conversas.

from langgraph.graph.message import add_messages
# Importa a função `add_messages`, que será usada para manipular as mensagens dentro do grafo.

from langgraph.prebuilt import ToolNode, tools_condition
# Importa a classe `ToolNode`, que representa um nó no grafo que usa ferramentas, e `tools_condition`, uma condição para executar ferramentas no grafo.

from langchain_groq import ChatGroq
# Importa o `ChatGroq`, que é um modelo de linguagem grande (LLM) da Groq, semelhante ao GPT, usado para gerar respostas baseadas em contexto.

import os
from dotenv import load_dotenv
# Importa `os` para interagir com variáveis de ambiente do sistema e `load_dotenv` para carregar variáveis de ambiente de um arquivo `.env`.

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()
# Carrega as variáveis de ambiente do arquivo `.env`, permitindo a configuração de chaves de API e outras variáveis sensíveis.

# Obtém a chave da API Groq e Tavily do arquivo .env
groq_api_key = os.getenv("GROQ_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

# Define as chaves da API no ambiente
os.environ["GROQ_API_KEY"] = groq_api_key
os.environ["TAVILY_API_KEY"] = tavily_api_key
# Configura as chaves da API `GROQ_API_KEY` e `TAVILY_API_KEY` como variáveis de ambiente para que possam ser usadas ao longo do código.

# Define um estado usando `TypedDict`, onde o estado tem uma lista de mensagens
class State(TypedDict):
    messages: Annotated[list, add_messages]
    # A lista de mensagens é anotada com `add_messages`, que processará as mensagens durante a execução do grafo.

# Cria um grafo de estado inicial com o tipo `State`
graph_builder = StateGraph(State)

# Inicializa uma ferramenta de pesquisa Tavily com um máximo de 2 resultados
tool = TavilySearchResults(max_results=2)
tools = [tool]
# Define a lista de ferramentas que estarão disponíveis no fluxo de trabalho, neste caso, a ferramenta `TavilySearchResults`.

# Inicializa o modelo de linguagem `ChatGroq` com um modelo específico e temperatura 0.5
llm = ChatGroq(model="llama-3.1-70b-versatile", temperature=0.5)

# Liga o LLM às ferramentas disponíveis
llm_with_tools = llm.bind_tools(tools)
# O modelo `llm` é combinado com as ferramentas `tools`, permitindo que o LLM chame e interaja com essas ferramentas.

# Define a função `chatbot`, que executa o modelo com base no estado atual
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}
    # A função `chatbot` usa o modelo `llm_with_tools` para processar a lista de mensagens no estado e retorna uma nova mensagem.

# Adiciona um nó "chatbot" ao grafo, que executará a função `chatbot`
graph_builder.add_node("chatbot", chatbot)

# Cria um nó de ferramentas no grafo, incluindo a ferramenta `tool`
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

# Adiciona uma aresta condicional no grafo, conectando o chatbot às ferramentas
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# Se uma ferramenta for chamada no chatbot, a execução do grafo pode continuar dependendo da condição `tools_condition`.

# Sempre que uma ferramenta é chamada, retornamos ao chatbot para decidir o próximo passo
graph_builder.add_edge("tools", "chatbot")
# Define que, depois que uma ferramenta for usada, o fluxo retorna ao nó do chatbot para decidir o próximo passo.

# Define que o ponto de entrada do grafo é o nó "chatbot"
graph_builder.set_entry_point("chatbot")

# Compila o grafo, deixando-o pronto para execução
graph = graph_builder.compile()

# Função que processa o fluxo de trabalho no grafo em tempo real com base na entrada do usuário
def stream_graph_updates(user_input: str):
    # Envia a entrada do usuário como uma mensagem ao grafo e obtém atualizações
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            messages = value["messages"]
            # Captura a resposta mais recente do assistente (última mensagem)
            response = messages[-1].content
    return response
    # Retorna a resposta do assistente.

# Loop principal para capturar a entrada do usuário e interagir com o chatbot
while True:
    try:
        user_input = input("User: ")
        # Pede ao usuário para inserir uma mensagem

        # Se o usuário inserir "quit", "exit" ou "q", o loop termina
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        # Processa a entrada do usuário no grafo e imprime a resposta
        resposta = stream_graph_updates(user_input)
        print(resposta)

    # Se houver um erro (por exemplo, falha ao capturar a entrada), executa este bloco
    except:
        # Usa uma entrada padrão se houver um problema
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        # Processa a entrada padrão no grafo
        stream_graph_updates(user_input)
        break

