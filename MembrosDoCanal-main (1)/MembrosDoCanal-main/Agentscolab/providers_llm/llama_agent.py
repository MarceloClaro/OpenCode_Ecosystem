import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"


class LlamaAgent:
    def __init__(self, agent_id: str, system_prompt: str):
        self.agent_id = agent_id
        self.system_prompt = system_prompt

    def run_task(self, task: str):
        prompt = f"""
SYSTEM:
{self.system_prompt}

TASK:
{task}

RESPONSE:
"""

        start = time.time()

        r = requests.post(
            OLLAMA_URL,
            json={
                "model": "gemma3:latest",
                "prompt": prompt,
                "stream": False
            }
        )

        latency = int((time.time() - start) * 1000)

        response_data = r.json()
        
        # Tratamento de erro se a chave 'response' não existir
        if "response" not in response_data:
            raise KeyError(f"Chave 'response' não encontrada. Resposta recebida: {list(response_data.keys())}")

        # Exibir apenas a resposta, sem tokens e metadados
        print(f"🔍 Resposta Ollama: {response_data['response'][:200]}...")

        return {
            "output": response_data["response"],
            "latency_ms": latency
        }
