import requests

APIKEY = "SUA_API_KEY"
HEADERS = {
    "Authorization": f"Bearer {APIKEY}",
    "Content-Type": "application/json"
}
BASE = "https://cloud.getwren.ai/api/v1"

def generate_sql(project_id, question, thread_id=None):
    payload = {"projectId": project_id, "question": question}
    if thread_id:
        payload["threadId"] = thread_id
    resp = requests.post(f"{BASE}/generate_sql", headers=HEADERS, json=payload)
    return resp.json()

def run_sql(project_id, sql):
    resp = requests.post(f"{BASE}/run_sql", headers=HEADERS, json={"projectId": project_id, "sql": sql})
    return resp.json()

def stream_explanation(query_id):
    resp = requests.get(f"{BASE}/stream_explanation", headers=HEADERS, params={"id": query_id}, stream=True)
    for chunk in resp.iter_lines():
        if chunk:
            print(chunk.decode())

# Uso:
gen = generate_sql(1, "Liste os 5 maiores pedidos")
print(gen["sql"])
run = run_sql(1, gen["sql"])
print(run["rows"])
stream_explanation(gen["id"])
