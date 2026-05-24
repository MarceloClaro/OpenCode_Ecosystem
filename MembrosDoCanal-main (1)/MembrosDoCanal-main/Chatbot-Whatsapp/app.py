from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import requests

app = FastAPI()

# Dicionário para armazenar o histórico de conversas
conversation_histories = {}

API_URL = "https://fabiosantos-ia.hf.space/api/v1/prediction/a953ea1b-ee34-4ae3-9b25-b82c814dd871"

def query(payload):
    response = requests.post(API_URL, json=payload)
    return response.json()

@app.post("/whatsapp")
async def reply_whatsapp(request: Request):
    form = await request.form()
    incoming_msg = form.get('Body', '').lower()
    from_number = form.get('From')
    
    print(incoming_msg)
    print(from_number)

    # Get the user's conversation history, if it exists
    user_history = conversation_histories.get(from_number, [])

    output = query({
        "question": incoming_msg,
    })
                                
    
    return PlainTextResponse(output['text'], status_code=200)
