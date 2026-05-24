from fastapi import FastAPI, Request
import openai
import os
import csv
from openai import OpenAI

client = OpenAI()

app = FastAPI()


# Definir API key da OpenAI via variável de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")

# Carregar informações das pizzas do arquivo CSV
pizzas = []
with open('pizzas.csv', mode='r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        pizzas.append(row)

@app.post("/chatbot")
async def chatbot(request: Request):
    body = await request.json()
    user_message = body.get("message")
    response_text = ""

    if "menu" in user_message.lower():
        response_text = "Temos as seguintes pizzas:\n"
        for pizza in pizzas:
            response_text += f"{pizza['nome']}: {pizza['ingredientes']} - R${pizza['valor']}\n"
    else:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        

    return {"response": response.choices[0].message.content}