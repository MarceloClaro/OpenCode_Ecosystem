import time
import requests
from providers_llm.llama_agent import LlamaAgent

AGENTHUB_URL = "http://localhost:8000"

# ================================
# PERFIL DO AGENTE B (TERCEIRO)
# ================================
AGENT_PROFILE = {
    "agent_id": "Agente de Pesquisa-Acadêmica",
    "description": "Agente especialista em pesquisa acadêmica",
    "skills": ["paper_search", "education_research"],
    "tools": ["llm"],
    "endpoint": "local",
    "cost_model": "free",
    "owner": "user_B",
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
    print("✅ Agent B registered:", r.json())


# ================================
# ATUALIZAR STATUS DO AGENTE
# ================================
def update_status(status):
    requests.patch(
        f"{AGENTHUB_URL}/agents/{AGENT_PROFILE['agent_id']}/status",
        json={"status": status}
    )


# ================================
# BUSCAR COLABORAÇÕES PENDENTES
# ================================
def get_pending_tasks():
    r = requests.get(
        f"{AGENTHUB_URL}/collaboration/pending/{AGENT_PROFILE['agent_id']}"
    )
    return r.json()


# ================================
# EXECUTAR TAREFA COM LLM
# ================================
def execute_task_with_llm(task):
    llm = LlamaAgent(
        agent_id=AGENT_PROFILE["agent_id"],
        system_prompt=(
            "Você é um pesquisador especialista buscas acadêmicas "
            "Sua tarefa é responder com base em artigos acadêmicos e pesquisas recentes."            
        )
    )

    result = llm.run_task(task)
    return result["output"], result["latency_ms"]


# ================================
# ENVIAR RESULTADO AO AGENTHUB
# ================================
def submit_result(collab_id, output, latency_ms):
    requests.post(
        f"{AGENTHUB_URL}/collaboration/complete/{collab_id}",
        json={
            "output": output,
            "latency_ms": latency_ms,
            "success": True,
            "rating": 5
        }
    )


# ================================
# LOOP PRINCIPAL DO AGENTE B
# ================================
def listen_and_work(poll_interval=3):
    print("🟢 Agent B (research-agent) is running")

    while True:
        tasks = get_pending_tasks()

        for task in tasks:
            print(f"🔧 Agent B executing task {task['id']}")

            update_status("busy")

            output, latency = execute_task_with_llm(task["task"])

            submit_result(
                collab_id=task["id"],
                output=output,
                latency_ms=latency
            )

            update_status("available")

            print(f"✅ Task {task['id']} completed")

        time.sleep(poll_interval)


# ================================
# EXECUÇÃO
# ================================
if __name__ == "__main__":
    register_agent()
    listen_and_work()
