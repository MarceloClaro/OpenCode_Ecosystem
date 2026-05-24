from typing import Annotated

from langchain_community.tools.tavily_search import TavilySearchResults
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_groq import ChatGroq

import os
from dotenv import load_dotenv

# Importar bibliotecas para reconhecimento e síntese de voz
import speech_recognition as sr
import pyttsx3

# Inicializar o reconhecedor de voz e o mecanismo de síntese de voz
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Configurar a voz para português
voices = tts_engine.getProperty('voices')
for voice in voices:
    if 'portuguese' in voice.name.lower() or 'português' in voice.name.lower():
        tts_engine.setProperty('voice', voice.id)
        break

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

os.environ["GROQ_API_KEY"] = groq_api_key
os.environ["TAVILY_API_KEY"] = tavily_api_key

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

tool = TavilySearchResults(max_results=2)
tools = [tool]

llm = ChatGroq(model="llama-3.1-70b-versatile", temperature=0.5)
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# Sempre que uma ferramenta é chamada, retornamos ao chatbot para decidir o próximo passo
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile()

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            messages = value["messages"]
            # Capturar a resposta do assistente
            response = messages[-1].content
    return response

while True:
    try:
        # Capturar entrada de voz do usuário
        with sr.Microphone() as source:
            print("Você pode falar agora...")
            audio = recognizer.listen(source)
        try:
            user_input = recognizer.recognize_google(audio, language='pt-BR')
            print(f"Você disse: {user_input}")
            if user_input.lower() in ["sair", "parar", "fechar"]:
                print("Até logo!")
                tts_engine.say("Até logo!")
                tts_engine.runAndWait()
                break
        except sr.UnknownValueError:
            print("Desculpe, não entendi o que você disse. Por favor, tente novamente.")
            tts_engine.say("Desculpe, não entendi o que você disse. Por favor, tente novamente.")
            tts_engine.runAndWait()
            continue
        except sr.RequestError as e:
            print(f"Erro no serviço de reconhecimento de voz; {e}")
            tts_engine.say("Erro no serviço de reconhecimento de voz.")
            tts_engine.runAndWait()
            continue

        resposta = stream_graph_updates(user_input)
        print(f"Assistente: {resposta}")
        # Converter a resposta em fala
        tts_engine.say(resposta)
        tts_engine.runAndWait()
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        tts_engine.say("Ocorreu um erro.")
        tts_engine.runAndWait()
        break
