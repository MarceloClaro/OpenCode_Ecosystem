# 2 - Image Processing: Base64
import base64
from openai import OpenAI 

MODEL="gpt-4o"

IMAGE_PATH = "imagens/geladeira-ingredientes.jpg"

client = OpenAI(api_key="coloque sua chave aqui")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

base64_image = encode_image(IMAGE_PATH)

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "Você é um assistante expert em culinária que cria receitas deliciosas e saudáveis."},
        {"role": "user", "content": [
            {"type": "text", "text": "Crie uma receita para mim utilizando os alimentos que aparecem na imagem da minha geladeira, más antes de criar a receita mostre uma lista dos alimentos da minha geladeira."},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}
            }
        ]}
    ],
    temperature=0.0,
)

print(response.choices[0].message.content)