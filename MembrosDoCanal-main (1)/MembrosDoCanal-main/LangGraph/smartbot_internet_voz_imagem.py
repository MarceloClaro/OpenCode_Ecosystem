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

# Importar bibliotecas para processamento de imagens
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# Importar biblioteca para tradução
from deep_translator import GoogleTranslator

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

# Inicializar o modelo de legendagem de imagens
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Inicializar o tradutor
translator = GoogleTranslator(source='en', target='pt')

def generate_caption(image_path):
    image = Image.open(image_path).convert('RGB')
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    # Traduzir a descrição para o português
    translated_caption = translator.translate(caption)
    return translated_caption

llm = ChatGroq(model="llama-3.1-70b-versatile", temperature=0.5)
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# Sempre que uma ferramenta é chamada, retornamos ao chatbot para decidir o próximo passo
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile()

def stream_graph_updates(messages):
    for event in graph.stream({"messages": messages}):
        for value in event.values():
            messages = value["messages"]
            # Capturar a resposta do assistente
            response = messages[-1].content
    return response

while True:
    try:
        # Pedir ao usuário para dizer 'voz' ou 'imagem'
        print("Olá! Como vai você? Diga 'voz' para conversar comigo ou 'imagem' para me fazer perguntas sobre uma imagem, ou 'sair' para encerrar.")
        tts_engine.say("Olá! Como vai você? Diga 'voz' para conversar comigo ou 'imagem' para me fazer perguntas sobre uma imagem, ou 'sair' para encerrar.")
        tts_engine.runAndWait()
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
        try:
            input_type = recognizer.recognize_google(audio, language='pt-BR').lower()
            print(f"Você escolheu: {input_type}")
            if input_type == 'sair':
                print("Até logo!")
                tts_engine.say("Até logo!")
                tts_engine.runAndWait()
                break
            elif input_type == 'voz':
                # Capturar entrada de voz do usuário
                print("Você pode falar agora...")
                tts_engine.say("Você pode falar agora...")
                tts_engine.runAndWait()
                with sr.Microphone() as source:
                    audio = recognizer.listen(source)
                try:
                    user_input = recognizer.recognize_google(audio, language='pt-BR')
                    print(f"Você disse: {user_input}")
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
                messages = [("user", user_input)]
            elif input_type == 'imagem':
                # Definir imagens pré-definidas para facilitar a seleção via voz
                image_options = {
                    'imagem 1': 'imagens/bola.jpg',
                    'imagem 2': 'caminho/para/imagem2.jpg',
                    'imagem 3': 'caminho/para/imagem3.jpg',
                }

                print("Diga o nome da imagem que deseja enviar (por exemplo, 'imagem um'):")
                tts_engine.say("Diga o nome da imagem que deseja enviar, por exemplo, imagem um.")
                tts_engine.runAndWait()
                with sr.Microphone() as source:
                    audio = recognizer.listen(source)
                try:
                    image_choice = recognizer.recognize_google(audio, language='pt-BR').lower()
                    print(f"Você escolheu: {image_choice}")
                    image_path = image_options.get(image_choice)
                    print(image_path)
                    if image_path is None:
                        print("Imagem não encontrada. Por favor, tente novamente.")
                        tts_engine.say("Imagem não encontrada. Por favor, tente novamente.")
                        tts_engine.runAndWait()
                        continue
                    print("Processando a imagem...")
                    caption = generate_caption(image_path)
                    print(f"Descrição da imagem: {caption}")
                    # Perguntar ao usuário se deseja fazer uma pergunta sobre a imagem
                    print("Você quer fazer uma pergunta sobre a imagem? Diga 'sim' ou 'não':")
                    tts_engine.say("Você quer fazer uma pergunta sobre a imagem? Diga 'sim' ou 'não'.")
                    tts_engine.runAndWait()
                    with sr.Microphone() as source:
                        audio = recognizer.listen(source)
                    try:
                        resposta = recognizer.recognize_google(audio, language='pt-BR').lower()
                        print("Resposta:"+resposta)
                        if resposta == 'sim':
                            print("Por favor, faça sua pergunta sobre a imagem:")
                            tts_engine.say("Por favor, faça sua pergunta sobre a imagem.")
                            tts_engine.runAndWait()
                            with sr.Microphone() as source:
                                audio = recognizer.listen(source)
                            user_question = recognizer.recognize_google(audio, language='pt-BR')
                            messages = [("user", f"Descrição da imagem: {caption}"), ("user", user_question)]
                        else:
                            messages = [("user", f"Descrição da imagem: {caption}")]
                    except sr.UnknownValueError:
                        print("Desculpe, não entendi sua resposta. Por favor, tente novamente.")
                        tts_engine.say("Desculpe, não entendi sua resposta. Por favor, tente novamente.")
                        tts_engine.runAndWait()
                        continue
                except sr.UnknownValueError:
                    print("Desculpe, não entendi o nome da imagem. Por favor, tente novamente.")
                    tts_engine.say("Desculpe, não entendi o nome da imagem. Por favor, tente novamente.")
                    tts_engine.runAndWait()
                    continue
                except Exception as e:
                    print(f"Erro ao processar a imagem: {e}")
                    tts_engine.say("Erro ao processar a imagem.")
                    tts_engine.runAndWait()
                    continue
            else:
                print("Opção inválida. Por favor, tente novamente.")
                tts_engine.say("Opção inválida. Por favor, tente novamente.")
                tts_engine.runAndWait()
                continue

            resposta = stream_graph_updates(messages)
            print(f"Assistente: {resposta}")
            # Converter a resposta em fala
            tts_engine.say(resposta)
            tts_engine.runAndWait()
        except sr.UnknownValueError:
            print("Desculpe, não entendi sua escolha. Por favor, tente novamente.")
            tts_engine.say("Desculpe, não entendi sua escolha. Por favor, tente novamente.")
            tts_engine.runAndWait()
            continue
        except sr.RequestError as e:
            print(f"Erro no serviço de reconhecimento de voz; {e}")
            tts_engine.say("Erro no serviço de reconhecimento de voz.")
            tts_engine.runAndWait()
            continue
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        tts_engine.say("Ocorreu um erro.")
        tts_engine.runAndWait()
        break

