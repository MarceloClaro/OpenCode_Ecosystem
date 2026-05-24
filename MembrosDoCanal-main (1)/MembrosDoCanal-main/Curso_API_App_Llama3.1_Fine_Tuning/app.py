import mesop as me
import mesop.labs as mel
from mesop import stateclass
import requests

API_URL = "https://fabiosantos-api-llama3-1.hf.space/ask"

@stateclass
class State:
    pass

@me.page(
    security_policy=me.SecurityPolicy(
        allowed_iframe_parents=["https://google.github.io"]
    ),
    path="/",
    title="SAC Bot da Loja XYZ IA",
)
def page():
    mel.chat(transform, title="SAC Bot da Loja XYZ IA", bot_user="SAC Bot")

def query(payload):
    response = requests.post(API_URL, json=payload)
    return response.json()

def transform(input: str, history: list[mel.ChatMessage]):
    # Concatena o histórico de mensagens em uma string, separando cada mensagem por uma quebra de linha.
    history_text = "\n".join([f"{msg.role}: {msg.content}" for msg in history])
    
    # Adiciona o histórico de mensagens à questão de entrada.
    input_with_history = f"{history_text}\nuser: {input}"
    print(input_with_history)
    # Realiza a consulta usando a questão com o histórico.
    output = query({
        "text": input_with_history,
    })
    
    if output:
        yield output['response']