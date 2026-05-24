import mesop as me
import mesop.labs as mel
from mesop import stateclass
import requests

API_URL = "https://fabiosantos-ia.hf.space/api/v1/prediction/580665ec-dc1d-41d2-849a-49c4a662d209"

@stateclass
class State:
    pass

@me.page(
    security_policy=me.SecurityPolicy(
        allowed_iframe_parents=["https://google.github.io"]
    ),
    path="/",
    title="Mesop Chatbot da Pizzaria Delicia",
)
def page():
    mel.chat(transform, title="Chatbot da Pizzaria Delicia", bot_user="Mesop Bot")

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
        "question": input_with_history,
    })
    
    if output:
        yield output['text']

   
    