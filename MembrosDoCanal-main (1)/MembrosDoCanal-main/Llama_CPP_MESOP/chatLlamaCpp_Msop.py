import mesop as me
import mesop.labs as mel
from mesop import stateclass
from llama_cpp import Llama
import os

# Defina o caminho para o diretório onde o modelo GGUF está armazenado
model_directory = r"C:\Users\Fabio\.cache\lm-studio\models\TheBloke\llmFineTune"
model_filename = "curso_llama3Finetune_unsloth-unsloth.Q8_0.gguf"  # Substitua pelo nome real do arquivo do modelo

# Inicializando o modelo Llama quantizado GGUF a partir do diretório local
model_path = os.path.join(model_directory, model_filename)

lcpp_llm = Llama(
    model_path=model_path,
    n_threads=2, # CPU cores
    n_batch=512, # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
    n_gpu_layers=-1, # Change this value based on your model and your GPU VRAM pool.
    n_ctx=4096, # Context window
)

prompt_template = "Responda as questões.\nHuman: {prompt}\nAssistant:\n"

def get_response(text):
    prompt = prompt_template.format(prompt=text)
    response = lcpp_llm(
    prompt=prompt,
    max_tokens=256,
    temperature=0.5,
    top_p=0.95,
    top_k=50,
    stop = ['<|end_of_text|>'], # Dynamic stopping when such token is detected.
    echo=True # return the prompt
)
    return response['choices'][0]['text'].split('Assistant:\n')[1]


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
       
    stream = get_response(input)

    for chunk in stream:
        content = chunk
        if content:
            yield content
