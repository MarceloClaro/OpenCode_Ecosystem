import base64
from threading import Lock
import time
import cv2
import numpy as np
import openai
from cv2 import imencode
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.messages import SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from pyaudio import PyAudio, paInt16
from speech_recognition import Microphone, Recognizer, UnknownValueError
import mss
from PIL import Image

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Função para capturar a tela do computador
def capture_screen():
    print("Capturando a tela...")
    sct = mss.mss()  # Inicializa a ferramenta de captura de tela
    monitor = sct.monitors[1]  # Seleciona o monitor a ser capturado
    screenshot = sct.grab(monitor)  # Captura a tela do monitor especificado
    img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)  # Converte para imagem PIL
    img_np = np.array(img)  # Converte a imagem PIL para array numpy
    frame = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)  # Converte a imagem de RGB para BGR

    _, buffer = imencode(".jpeg", frame)  # Codifica a imagem em formato JPEG
    return base64.b64encode(buffer)  # Retorna a imagem codificada em base64

# Função para criar um assistente que responde com base na imagem capturada e um prompt
def create_assistant(model):
    SYSTEM_PROMPT = """
    Você é um assistente espirituoso que usará a imagem fornecida pelo usuário para responder às suas perguntas.
    Use poucas palavras nas suas respostas. Vá direto ao ponto. Não use emoticons ou emojis. Não faça perguntas ao usuário.
    Seja amigável e prestativo. Mostre um pouco de personalidade. Não seja muito formal, sempre responda em português.
    """

    # Define o template do prompt para o assistente
    prompt_template = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            (
                "human",
                [
                    {"type": "text", "text": "{prompt}"},
                    {
                        "type": "image_url",
                        "image_url": "data:image/jpeg;base64,{image_base64}",
                    },
                ],
            ),
        ]
    )

    chain = prompt_template | model | StrOutputParser()  # Cria a cadeia de processamento do modelo
    chat_message_history = ChatMessageHistory()  # Inicializa o histórico de mensagens

    # Cria um objeto que gerencia a execução com histórico de mensagens
    runnable_with_message_history = RunnableWithMessageHistory(
        chain,
        lambda _: chat_message_history,
        input_messages_key="prompt",
        history_messages_key="chat_history",
    )

    # Função para gerar uma resposta do assistente
    def answer(prompt, image):
        if not prompt:
            return

        print("Gerando resposta para o prompt:", prompt)
        response = runnable_with_message_history.invoke(
            {"prompt": prompt, "image_base64": image.decode()},
            config={"configurable": {"session_id": "unused"}},
        ).strip()

        print("Response:", response)

        if response:
            tts(response)  # Converte a resposta em fala

    # Função para converter texto em fala
    def tts(response):
        print("Convertendo resposta para fala...")
        player = PyAudio().open(format=paInt16, channels=1, rate=24000, output=True)

        with openai.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            response_format="pcm",
            input=response,
        ) as stream:
            for chunk in stream.iter_bytes(chunk_size=1024):
                player.write(chunk)

    return answer  # Retorna a função answer

# Função de callback para processar o áudio reconhecido
def audio_callback(recognizer, audio, assistant_answer):
    print("Processando áudio...")
    try:
        prompt = recognizer.recognize_whisper(audio, model="base", language="english")  # Reconhece o áudio usando Whisper
        print("Prompt reconhecido:", prompt)
        encoded_image = capture_screen()  # Captura a tela e codifica a imagem
        if encoded_image:
            assistant_answer(prompt, encoded_image)  # Passa o prompt e a imagem para o assistente

    except UnknownValueError:
        print("Erro ao processar o áudio.")  # Mensagem de erro caso o áudio não seja reconhecido

# Função principal
def main():
    # Utiliza o modelo GPT-4o da OpenAI
    model = ChatOpenAI(model="gpt-4o")

    assistant_answer = create_assistant(model)  # Cria o assistente

    recognizer = Recognizer()  # Inicializa o reconhecedor de fala
    microphone = Microphone()  # Inicializa o microfone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)  # Ajusta para ruído ambiente
        print("Ajustando para ruído ambiente...")

    # Inicia a escuta em segundo plano para reconhecimento de fala
    stop_listening = recognizer.listen_in_background(microphone, lambda recognizer, audio: audio_callback(recognizer, audio, assistant_answer))
    print("Iniciando escuta em segundo plano...")

    try:
        while True:
            time.sleep(0.1)  # Mantém o programa rodando
    except KeyboardInterrupt:
        stop_listening(wait_for_stop=False)  # Para a escuta em segundo plano
        print("Parando escuta em segundo plano...")

if __name__ == "__main__":
    main()  # Executa a função principal

