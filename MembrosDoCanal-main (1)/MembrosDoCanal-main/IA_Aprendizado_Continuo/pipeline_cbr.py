import os
from dotenv import load_dotenv
from indexador_casos import (
    indexar_casos, buscar_caso_similar, adicionar_caso, carregar_casos,
    FAISS_INDEX_PATH, CASES_DB_PATH
)
from casos_iniciais import casos_iniciais
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from tavily import TavilyClient

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Se for primeira execução (bases não existem), indexa casos iniciais
if not os.path.exists(CASES_DB_PATH) or not os.path.exists(FAISS_INDEX_PATH):
    print("Inicializando base de exemplos...")
    indexar_casos(casos_iniciais)

def adaptar_solucao(pergunta, caso):
    prompt = PromptTemplate.from_template(
        "Você é um especialista em resolver problemas por meio do raciocínio baseado em casos.\n"
        "Um usuário relatou o seguinte problema: '{pergunta}'.\n"
        "Um caso semelhante foi resolvido assim: '{caso_problema}', com a solução: '{caso_solucao}'.\n"
        "Adapte essa solução ao novo caso, considerando diferenças possíveis.\n"
        "Não adicione nenhuma informação a mais."
    )
    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.3,
        max_tokens=1000
    )
    chain = prompt | llm
    resposta = chain.invoke({
        "pergunta": pergunta,
        "caso_problema": caso["problema"],
        "caso_solucao": caso["solucao"]
    })
    return resposta.content

def resumir_com_llm(pergunta, snippet, link=""):
    """
    Usa o LLM para gerar uma resposta direta e resumida a partir do trecho encontrado na web.
    """
    prompt = PromptTemplate.from_template(
        "Você é um assistente técnico de TI. Use o texto abaixo, extraído da web, para responder de forma clara e objetiva à pergunta do usuário.\n"
        "Pergunta do usuário: {pergunta}\n"
        "Texto encontrado na web:\n{snippet}\n"
        "Responda diretamente ao usuário, de forma resumida e sem copiar o texto original. Se possível, inclua o passo mais importante. (Fonte: {link})"
    )
    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.2,
        max_tokens=300
    )
    chain = prompt | llm
    resposta = chain.invoke({
        "pergunta": pergunta,
        "snippet": snippet,
        "link": link
    })
    return resposta.content.strip()

def buscar_na_web(pergunta):
    client = TavilyClient(TAVILY_API_KEY)
    tentativas = [
        f"solução técnica {pergunta}",
        f"como resolver {pergunta} computador",
        f"problema {pergunta} informática solução",
        f"troubleshooting {pergunta}"
    ]
    for query in tentativas:
        try:
            response = client.search(query=query)
            if isinstance(response, dict):
                if "results" in response and response["results"]:
                    primeiro = response["results"][0]
                    snippet = primeiro.get("snippet") or primeiro.get("content") or ""
                    link = primeiro.get("url") or ""
                    lista = response["results"]
                    resposta_txt = "\n".join(
                        f"{r.get('title', '[Sem título]')} - {r.get('url', '')}"
                        for r in lista if "url" in r
                    )
                    # Se não houver snippet, usa título como contexto para o LLM
                    if not snippet or len(snippet) <= 30:
                        snippet = primeiro.get("title", "")
                    if snippet and len(snippet) > 10:
                        resposta_direta = resumir_com_llm(pergunta, snippet, link)
                        if resposta_direta and len(resposta_direta) > 30:
                            return (
                                f"Resposta resumida do resultado mais relevante ({link}):\n"
                                f"{resposta_direta}\n\n"
                                f"Principais links:\n{resposta_txt}"
                            )
                    if resposta_txt.strip():
                        return f"Principais links encontrados:\n{resposta_txt}"
                # Fallback para 'answer' direta
                if "answer" in response and response["answer"]:
                    if isinstance(response["answer"], str) and len(response["answer"]) > 50:
                        return response["answer"]
            elif isinstance(response, str) and len(response) > 50:
                return response
        except Exception as e:
            logger.error(f"❌ Falha na busca web: {e}")
            continue
    return "Não foi possível encontrar soluções técnicas relevantes. Recomenda-se consultar a documentação do fabricante ou especialista em TI."



def validar_resposta_web(resposta):
    if not resposta or len(resposta) < 50:
        return False
    irrelevantes = ["significado", "definição", "dicionário", "paciente", "médico", "tratamento", "remédio"]
    relevantes = ["computador", "sistema", "rede", "internet", "software", "hardware", "driver", "configuração", "solução", "problema", "resolver", "passo"]
    texto_lower = resposta.lower()
    if any(p in texto_lower for p in irrelevantes):
        return False
    return sum(p in texto_lower for p in relevantes) > 0

def ciclo_cbr_ti(novo_problema):
    caso_similar = buscar_caso_similar(novo_problema, threshold=0.3)
    if caso_similar:
        print("\n=== Caso mais similar encontrado na base ===")
        print(f"Problema (referência): {caso_similar['problema']}")
        print(f"Solução (referência): {caso_similar['solucao']}")
        resposta = adaptar_solucao(novo_problema, caso_similar)
        print("\n=== Solução Técnica Adaptada ===")
        print(resposta)
        user_feedback = input("\nEssa solução resolveu seu problema? (s/n): ").strip().lower()
        if user_feedback == "s":
            adicionar_caso(novo_problema, resposta, fonte="CBR")
            return resposta
        else:
            print("Buscando solução na web...")
            resposta_web = buscar_na_web(novo_problema)
            if not validar_resposta_web(resposta_web):
                print("❌ Solução da web não parece relevante.")
                resposta_web = "Não foi possível encontrar soluções técnicas relevantes. Recomenda-se consultar a documentação do fabricante ou especialista em TI."
            print("\n=== Solução encontrada na web ===\n", resposta_web)
            user_feedback_web = input("\nA solução da web resolveu seu problema? (s/n): ").strip().lower()
            if user_feedback_web == "s":
                adicionar_caso(novo_problema, resposta_web, fonte="web")
            return resposta_web
    else:
        print("Nenhum caso similar encontrado. Buscando na web...")
        resposta_web = buscar_na_web(novo_problema)
        if not validar_resposta_web(resposta_web):
            print("❌ Solução da web não parece relevante.")
            resposta_web = "Não foi possível encontrar soluções técnicas relevantes. Recomenda-se consultar a documentação do fabricante ou especialista em TI."
        print("\n=== Solução encontrada na web ===\n", resposta_web)
        user_feedback_web = input("\nA solução da web resolveu seu problema? (s/n): ").strip().lower()
        if user_feedback_web == "s":
            adicionar_caso(novo_problema, resposta_web, fonte="web")
        return resposta_web

def mostrar_estatisticas():
    casos = carregar_casos()
    if casos:
        total = len(casos)
        fontes = {}
        for caso in casos:
            fonte = caso.get('fonte', 'desconhecida')
            fontes[fonte] = fontes.get(fonte, 0) + 1
        print(f"\n📊 Estatísticas da Base de Suporte Técnico:")
        print(f"Total de casos: {total}")
        for fonte, count in fontes.items():
            print(f"  - {fonte}: {count} casos")
    else:
        print("📊 Base vazia")

# Interface
if __name__ == "__main__":
    print("💻 Sistema de Suporte Técnico - Aprendizado Contínuo")
    print("Digite 'stats' para ver estatísticas ou 'sair' para encerrar")
    while True:
        print("\nDescreva o problema técnico:")
        novo_problema = input("Problema: ").strip()
        if not novo_problema or novo_problema.lower() in ['sair', 'exit', 'quit']:
            print("Encerrando...")
            break
        elif novo_problema.lower() == 'stats':
            mostrar_estatisticas()
            continue
        ciclo_cbr_ti(novo_problema)

