from fastapi import FastAPI
from pydantic import BaseModel
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# Definição do modelo de dados de entrada
class Question(BaseModel):
    text: str

# Inicializando o FastAPI
app = FastAPI()

# Download e configuração do modelo
model_name_or_path = "FabioSantos/llama3_1_fn"
model_basename = "unsloth.Q8_0.gguf"
model_path = hf_hub_download(repo_id=model_name_or_path, filename=model_basename)
print(f"Model path: {model_path}")

# Configuração do modelo com llama_cpp
lcpp_llm = Llama(
    model_path=model_path,
    n_threads=2,
    n_batch=512,
    n_gpu_layers=-1,
    n_ctx=4096,
)

# Formato de prompt utilizado no fine-tuning
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

def get_response(text: str) -> str:
    # Formatar o prompt usando o mesmo template utilizado no fine-tuning
    formatted_prompt = alpaca_prompt.format(
        "Você é um assistente do serviço de atendimento ao cliente que deve responder as perguntas dos clientes",
        text,
        ""
    )
    response = lcpp_llm(
        prompt=formatted_prompt,
        max_tokens=256,
        temperature=0.5,
        top_p=0.95,
        top_k=50,
        stop=['### Response:'],  # Usar "### Response:" como token de parada
        echo=True
    )
    response_text = response['choices'][0]['text']
    
    # Extrair a resposta após "### Response:"
    if "### Response:" in response_text:
        answer = response_text.split("### Response:")[1].strip()
    else:
        answer = response_text.strip()

    print(f"Final Answer: {answer}")
    return answer


# Endpoint para receber uma questão e retornar a resposta
@app.post("/ask")
def ask_question(question: Question):
    response = get_response(question.text)
    return {"response": response}

# Executa a aplicação
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


