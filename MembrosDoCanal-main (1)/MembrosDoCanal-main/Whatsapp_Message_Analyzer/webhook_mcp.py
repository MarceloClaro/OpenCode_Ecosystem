from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
from openai import OpenAI
import requests
import base64
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

load_dotenv()

app = FastAPI()

client_openai = OpenAI()

# Config Twilio
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
TWILIO_API_URL = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"

# Configurar cliente e agente MCP
mcp_config = {
    "mcpServers": {
        "http": {
            "url": "http://localhost:8000/sse"
        }
    }
}

mcp_client = MCPClient.from_dict(mcp_config)

llm = ChatOpenAI(model="gpt-4.1-mini")
agent = MCPAgent(llm=llm, client=mcp_client, max_steps=30)

def encode_image_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")

@app.post("/webhook")
async def webhook(request: Request):
    form = await request.form()
    from_number = form.get("From")
    body = form.get("Body")
    media_url = form.get("MediaUrl0")
    content_type = form.get("MediaContentType0")

    print(f"Content-Type: {content_type}")

    if media_url and content_type and "image/jpeg" in content_type:
        try:
            response = requests.get(media_url, auth=(TWILIO_SID, TWILIO_AUTH_TOKEN))
            response.raise_for_status()
            image_bytes = response.content

            # Salvar localmente (debug)
            with open("imagem_recebida_debug.jpg", "wb") as f:
                f.write(image_bytes)

            base64_image = encode_image_to_base64(image_bytes)

            completion = client_openai.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            { "type": "text", "text": "Obter o texto da imagem, descreva o que está na imagem." },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
            )
            conteudo = completion.choices[0].message.content

        except Exception as e:
            return JSONResponse({"status": "erro", "msg": f"⚠️ Erro ao baixar imagem: {str(e)}"})
    else:       
        conteudo = body

    try:
        print(f"[DEBUG] Enviando para MCP: conteúdo={conteudo}")

        mensagem = f"Utilize a ferramenta analisar_mensagem_conteudo com conteúdo='{conteudo}'"
        resultado = await agent.run(mensagem)
        resposta_final = f"🛡️ Análise:\n{resultado}"

    except Exception as e:
        resposta_final = f"⚠️ Erro ao consultar o servidor MCP: {str(e)}"

    partes = [resposta_final[i:i+1500] for i in range(0, len(resposta_final), 1500)]
    for parte in partes:
        send_whatsapp_message(from_number, parte)

    return JSONResponse({"status": "ok"})

def send_whatsapp_message(to, body):
    data = {
        "From": f"whatsapp:{TWILIO_NUMBER}",
        "To": to,
        "Body": body
    }
    auth = (TWILIO_SID, TWILIO_AUTH_TOKEN)
    requests.post(TWILIO_API_URL, data=data, auth=auth)
