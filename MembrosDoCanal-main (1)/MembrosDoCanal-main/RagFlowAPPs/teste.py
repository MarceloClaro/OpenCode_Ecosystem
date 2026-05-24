import requests
import json

# Configuração do endpoint e headers
chat_id = "dfb323e030f511f082463238eb959721"
api_key = "ragflow-g3MjE2NWNlMzBmNjExZjBhMWQ0MzIzOG"
uri = f"http://localhost/api/v1/chats_openai/{chat_id}/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Corpo da requisição
body = {
    "model": "model",
    "messages": [
        {
            "role": "user",
            "content": "Qual modelo de CNN apresentou o melhor resultado?"
        }
    ],
    "stream": True
}

# Enviar requisição
response = requests.post(uri, headers=headers, data=json.dumps(body), stream=True)

# Exibir resposta
for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
