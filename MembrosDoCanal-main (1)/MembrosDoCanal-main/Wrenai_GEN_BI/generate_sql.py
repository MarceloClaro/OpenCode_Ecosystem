import requests

# === Primeira requisição: gerar o SQL ===
url_generate_sql = "https://cloud.getwren.ai/api/v1/generate_sql"

payload_generate = {
    "projectId": "7740",
    "question": "Quero uma lista de nomes de clients",    
    "returnSqlDialect": False
}

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer sk-2gYYEEFX7DAmRw"  # Substitua por uma variável de ambiente para maior segurança
}

response_generate = requests.post(url_generate_sql, json=payload_generate, headers=headers)

# Verifica se foi bem-sucedido
if response_generate.status_code != 200:
    print("Erro ao gerar SQL:", response_generate.text)
    exit()

# Extrai o SQL da resposta JSON
sql_response = response_generate.json()
sql = sql_response.get("sql")

print("SQL gerado:", sql)

# === Segunda requisição: executar o SQL ===
url_run_sql = "https://cloud.getwren.ai/api/v1/run_sql"

payload_run = {
    "projectId": "7740",
    "sql": sql,   
    "limit": 1000
}

response_run = requests.post(url_run_sql, json=payload_run, headers=headers)

# Exibe o resultado final
if response_run.status_code == 200:
    print("Resultado da consulta:")
    print(response_run.text)
else:
    print("Erro ao executar SQL:", response_run.status_code, response_run.text)
