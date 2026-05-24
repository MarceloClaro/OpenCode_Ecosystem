import gradio as gr
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

interface = gr.Interface(
    fn=get_response,
    inputs="text",
    outputs="text",
    title="Assistente Virtual",
    description="Forneça uma questão e visualize a resposta do assistente."
)

if __name__ == "__main__":
    interface.launch()