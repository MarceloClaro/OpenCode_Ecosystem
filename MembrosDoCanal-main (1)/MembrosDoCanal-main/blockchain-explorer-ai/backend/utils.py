import os
import requests
import openai
from dotenv import load_dotenv

load_dotenv()
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def get_transaction_data(address):
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url).json()
    txs = response.get("result", [])
    return txs[:5]  # Retorna as 5 transações mais recentes

def ask_openai(question, transactions):
    tx_summary = "\n".join([f"- {tx['hash']} ({tx['value']} wei, para {tx['to']})" for tx in transactions])
    prompt = f"Essas são as últimas transações do endereço:\n{tx_summary}\n\nPergunta: {question}\nResposta:"
    
    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return completion.choices[0].message.content.strip()
