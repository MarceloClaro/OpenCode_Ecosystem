# 3 - Image Processing: URL
from openai import OpenAI 

MODEL="gpt-4o"

client = OpenAI(api_key="coloque sua chave aqui")

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "Você é um assistente útil que responde em Markdown. Me ajude com meu dever de matemática!"},
        {"role": "user", "content": [
            {"type": "text", "text": "Qual é a área do retângulo?"},
            {"type": "image_url", "image_url": {"url": "https://images.educamaisbrasil.com.br/content/banco_de_imagens/guia-de-estudo/d/aplicacao-retangulo-matematica.jpg"}
            }
        ]}
    ],
    temperature=0.0,
)

print(response.choices[0].message.content)

