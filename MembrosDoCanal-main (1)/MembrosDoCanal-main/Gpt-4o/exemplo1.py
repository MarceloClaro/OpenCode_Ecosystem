from openai import OpenAI 

MODEL="gpt-4o"
client = OpenAI(api_key="coloque sua chave aqui")

# 1 - Basic Chat

completion = client.chat.completions.create(
  model=MODEL,
  messages=[
    {"role": "system", "content": "Você é um assistente útil. Me ajude com meu dever de matemática!"},
    {"role": "user", "content": "Olá! Você poderia resolver 2+2?"}
  ]
)

print("Assistant: " + completion.choices[0].message.content)