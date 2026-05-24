import time
import requests
from providers_llm.llama_agent import LlamaAgent   # opcional, só se quiser gerar resposta final

AGENTHUB_URL = "http://localhost:8000"

# ================================
# PERFIL DO AGENTE A
# ================================
AGENT_PROFILE = {
    "agent_id": "Agente Escritor-Educacional",
    "description": "Agente escritor que solicita ajuda a especialistas",
    "skills": ["writing papers", "education_content"],
    "tools": ["llm"],
    "endpoint": "local",
    "cost_model": "free",
    "owner": "user_A",
    "status": "available"
}

# ================================
# REGISTRO NO AGENTHUB
# ================================
def register_agent():
    r = requests.post(
        f"{AGENTHUB_URL}/agents",
        json=AGENT_PROFILE
    )
    print("✅ Agent A registered:", r.json())


# ================================
# BUSCAR AGENTE ESPECIALISTA DISPONÍVEL
# ================================
def find_specialist(skill):
    r = requests.get(
        f"{AGENTHUB_URL}/agents/search",
        params={
            "skill": skill,
            "status": "available"
        }
    )
    agents = r.json()

    if not agents:
        raise Exception("❌ Nenhum agente especialista disponível")

    specialist = agents[0]
    print(f"🔍 Especialista encontrado: {specialist['agent_id']}")
    return specialist


# ================================
# SOLICITAR COLABORAÇÃO
# ================================
def request_help(to_agent, task):
    payload = {
        "from_agent": AGENT_PROFILE["agent_id"],
        "to_agent": to_agent,
        "task": task,
        "expected_output": "Resumo técnico"
    }

    r = requests.post(
        f"{AGENTHUB_URL}/collaboration/request",
        json=payload
    )

    collab_id = r.json()["collaboration_id"]
    print(f"🤝 Colaboração criada (ID={collab_id})")
    return collab_id


# ================================
# AGUARDAR RESPOSTA DO AGENTE B
# ================================
def wait_for_result(collab_id, timeout=180):
    print("⏳ Aguardando resposta do agente especialista...")

    start = time.time()

    while time.time() - start < timeout:
        r = requests.get(
            f"{AGENTHUB_URL}/collaboration/{collab_id}"
        )
        collab = r.json()

        if collab["status"] == "completed":
            print("📥 Resposta recebida!")
            return collab["output"]

        time.sleep(2)

    raise TimeoutError("⏰ Timeout aguardando resposta do Agente B")


# ================================
# (OPCIONAL) GERAR RESPOSTA FINAL COM LLM
# ================================
def generate_final_answer(output_from_b):
    llama = LlamaAgent(
        agent_id=AGENT_PROFILE["agent_id"],
        system_prompt="Você é um redator educacional."
    )

    prompt = f"""
Use o conteúdo abaixo para gerar uma resposta final clara e educacional.

CONTEÚDO DO AGENTE ESPECIALISTA:
{output_from_b}

RESPOSTA FINAL:
"""

    result = llama.run_task(prompt)
    
    # Se a resposta for um dicionário com 'response', extrai apenas o texto
    if isinstance(result["output"], dict) and "response" in result["output"]:
        return result["output"]["response"]
    
    return result["output"]


# ================================
# FLUXO PRINCIPAL DO AGENTE A
# ================================
def main():
    register_agent()

    # 1. Agente A precisa de ajuda
    task = "Preciso de informações sobre aplicações de LLMs para educação inclusiva de crianças."

    # 2. Procura especialista disponível
    specialist = find_specialist(skill="paper_search")

    # 3. Solicita colaboração
    collab_id = request_help(
        to_agent=specialist["agent_id"],
        task=task
    )

    # 4. Aguarda resultado do Agente B
    output_from_b = wait_for_result(collab_id)

    print("\n==============================")
    print("📄 RESULTADO DO AGENTE B")
    print("==============================")
    print(output_from_b)

    # 5. (Opcional) Gerar resposta final
    print("\n==============================")
    print("🧠 RESPOSTA FINAL DO AGENTE A")
    print("==============================")

    final_answer = generate_final_answer(output_from_b)
    print(final_answer)


# ================================
# EXECUÇÃO
# ================================
if __name__ == "__main__":
    main()
