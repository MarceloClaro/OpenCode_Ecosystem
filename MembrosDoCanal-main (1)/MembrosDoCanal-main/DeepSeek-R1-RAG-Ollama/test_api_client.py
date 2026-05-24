import requests

# Histórico das consultas e respostas
tempo_respostas = []  # Lista para armazenar histórico

# Mostra o histórico de conversas no console
def mostrar_historico():
    """Exibe o histórico de perguntas e respostas."""
    print("\n=== Histórico Atualizado ===")
    for idx, item in enumerate(tempo_respostas, 1):
        print(f"{idx}. Usuário: {item['question']}")
        print(f"   IA: {item['response']}")
    print("=============================================================================\n")

# Faz um upsert(indexação) de documentos 
def test_upsert():
    api_url = "http://127.0.0.1:8002/upsert_documents"  

 # Enviar a consulta combinada com o histórico
    response = requests.post(api_url, json={"folder": "documentos"})    

    if response.status_code == 200:
        resposta = response.json()
        resposta_texto = resposta.get("message", "")
        print(resposta_texto)       

# Testa uma sequencia de consultas
def test_query_endpoint():
    """Teste simples para consultar o índice FAISS via API."""
    # URL do endpoint
    api_url = "http://127.0.0.1:8001/query"  

    # Consultas de teste
    test_queries = [
        "Qual foi a CNN que apresentou o melhor resultado na detecção de defeitos em PCBs?"        
    ]

    #test_queries = [
    #    "Bom dia",
    #    "Qual é o montante da transferência de cada documento?",
    #    "Quantos documentos são do tipo Pagamento a Fornecedores?",
    #    "Você lembra qual foi a primeira resposta?"
    #]

    for query in test_queries:
        print(f"Enviando consulta: {query}")

        # Combinar o histórico de conversas com a consulta atual
        historico = "\n".join([
            f"Pergunta: {item['question']}\nResposta: {item['response']}" for item in tempo_respostas
        ])
        consulta_com_historico = query
        if historico:
            consulta_com_historico = historico + f"\nNova pergunta: {query}"

        # Enviar para API client a consulta combinada com o histórico
        response = requests.post(api_url, json={"question": consulta_com_historico})

        if response.status_code == 200:
            resposta = response.json()
            resposta_texto = resposta.get("resposta", "")
            print("Resposta da API:", resposta_texto)

            # Registrar a consulta e a resposta no histórico
            tempo_respostas.append({"question": query, "response": resposta_texto})

            # Mostrar o histórico atualizado
            mostrar_historico()
        else:
            print(f"Erro {response.status_code}: {response.text}")

# Executar o teste
if __name__ == "__main__":
    #test_upsert()
    test_query_endpoint()
