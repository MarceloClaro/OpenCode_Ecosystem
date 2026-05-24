import gradio as gr
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# download model
model_name_or_path = "FabioSantos/curso_llama3Finetune_unsloth" # repo id
# 4bit
model_basename = "curso_llama3Finetune_unsloth-unsloth.Q8_0.gguf" # file name

model_path = hf_hub_download(repo_id=model_name_or_path, filename=model_basename)
print(model_path)

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
    
