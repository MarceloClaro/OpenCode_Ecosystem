import mesop as me
import mesop.labs as mel
from mesop import stateclass
from llama_cpp import Llama


llm = Llama.from_pretrained(
    repo_id="Qwen/Qwen2-0.5B-Instruct-GGUF",
    filename="*q8_0.gguf",
    verbose=False,
     n_ctx=2048,
)

def getResponse(input_text):
    
    result = llm.create_chat_completion(
      messages=[
        {"role": "system", "content": "Você é um assistente que fornece respostas para a questão do usuário."},
        {"role": "user", "content": input_text},        
    ],
    temperature=0.2,)

    return result

@stateclass
class State:
    pass

@me.page(
    security_policy=me.SecurityPolicy(
        allowed_iframe_parents=["https://google.github.io"]
    ),
    path="/",
    title="Chatbot de Demonstração",
)
def page():
    mel.chat(transform, title="Chatbot de Demonstração", bot_user="Mesop Bot")

def transform(input: str, history: list[mel.ChatMessage]):
       
    resultado = getResponse(input)

    for chunk in resultado['choices'][0]['message']['content']:
        content = chunk
        if content:
            yield content
