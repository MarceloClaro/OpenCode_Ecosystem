from googlesearch import search

def search_web(query, num_results=3):
    """Realiza uma busca no Google e retorna os primeiros resultados."""
    try:
        results = list(search(query, num=num_results, stop=num_results, pause=2))
        return "\n".join(results)
    except Exception as e:
        return f"⚠️ Erro ao buscar informações: {e}"
