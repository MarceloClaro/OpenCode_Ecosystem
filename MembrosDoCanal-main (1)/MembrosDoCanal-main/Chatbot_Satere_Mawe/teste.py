from ollama import Client

client = Client(host='http://localhost:11434')


response = client.chat(
    model="satere_q8",
    messages=[
        {"role": "user", "content": "Qual a palavra para 'cabeça'?"}
    ]
)

print("Resposta do modelo:")
print(response["message"]["content"])
