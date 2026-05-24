from google.adk.agents import Agent 
from rag_utils import query_vectorstore
from tavily import TavilyClient
import os

# Defina sua chave de API do Tavily
os.environ["TAVILY_API_KEY"] = "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"  # ou carregue de .env

def web_search(query: str) -> dict:
    """
    Realiza uma busca na web usando Tavily Search API.

    Args:
        query (str): Pergunta ou tópico a ser pesquisado.

    Returns:
        dict: {'status': 'success', 'result': resposta} ou {'status': 'error', 'error_message': msg}
    """
    try:
        client = TavilyClient()
        result = client.search(
            query=query,
            search_depth="basic",  # ou "advanced" para busca mais profunda
            include_answer=True,
            max_results=3
        )

        resposta = ""

        if result.get("answer"):
            resposta += f"Resposta direta:\n{result['answer']}\n\n"

        if result.get("results"):
            resposta += "Principais resultados:\n"
            for r in result["results"]:
                resposta += f"- {r['title']}: {r['url']}\n  {r['content']}\n\n"

        return {"status": "success", "result": resposta.strip()}

    except Exception as e:
        return {"status": "error", "error_message": f"Erro ao realizar busca Tavily: {e}"}



def rag_tool(query: str) -> dict:
    """
    Busca informações relevantes nos documentos locais (FAISS + Embeddings).
    
    Args:
        query (str): Pergunta ou tópico a ser pesquisado.
    
    Returns:
        dict: {'status': 'success', 'result': resposta} ou {'status': 'error', 'error_message': msg}
    """
    try:
        resposta = query_vectorstore(query)        
        return {"status": "success", "result": f"Documentos relevantes encontrados:\n\n{resposta}"}
    except Exception as e:
        return {"status": "error", "error_message": f"Erro ao consultar base de dados vetorial: {e}"}

rag_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='Você é um assistente de RAG.',
    instruction=(
        'Responda às perguntas dos usuários em português do Brasil. '
        'Se for possível, use a ferramenta rag_tool. '
        'Se a pergunta for sobre informações atuais, use a ferramenta google_search. '        
    ),
    tools=[rag_tool, web_search])

#
