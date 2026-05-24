import os
import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer

from tavily import TavilyClient

from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Carrega variáveis de ambiente
load_dotenv()

os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')

# Inicializar cliente ChromaDB
chroma_client = chromadb.Client()
collection_name = "produtos_internet"

# Verificar ou criar a coleção
if collection_name in [col.name for col in chroma_client.list_collections()]:
    collection = chroma_client.get_collection(collection_name)
else:
    collection = chroma_client.create_collection(name=collection_name)

# Modelo de embeddings
embedder_model = SentenceTransformer('BAAI/bge-small-en-v1.5')

api_key = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key)

# Função para buscar informações de produtos na internet
def extract_products(urls, keywords=None):
    
    os.makedirs("temp_products", exist_ok=True)

    for url in urls:
        try:
            st.write(f"Buscando produtos em: {url}")
            response = tavily_client.extract(urls=urls)
            for result in response["results"]:

                product = result['raw_content']
                url = result['url']
                
                details = f"product_name:{product}"

                # Adicionar ao banco vetorial
                embedding = embedder_model.encode(details).tolist()
                collection.add(
                    embeddings=[embedding],
                    ids=[f"{url}"],
                    metadatas=[{"url": url, "content": details}]
                )
            st.write(f"Informações do site {url} foram indexadas com sucesso.")
        except Exception as e:
            st.error(f"Erro ao buscar dados de {url}: {e}")

# Função para buscar produtos similares
def search_products(query, top_k=5):
    query_embedding = embedder_model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    similar_products = [metadata["content"] for metadata in results["metadatas"][0]]
    return similar_products

# Inicializar LLM
llm = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=os.environ['GROQ_API_KEY'],
    model_name="groq/llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=2000,
)

# Agente de Recuperação (mind)
mind = Agent(
    role="Especialista em Produtos",
    goal="Buscar produtos relevantes na internet com base nas preferências do cliente.",
    backstory="Especialista em identificar os melhores produtos em sites confiáveis.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Agente de Personalização (persona)
persona = Agent(
    role="Consultor de Compras",
    goal="Oferecer recomendações personalizadas e ajudar o cliente a escolher o melhor produto.",
    backstory="Consultor amigável e eficiente, que personaliza sugestões para cada cliente.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Tarefas
mind_task = Task(
    description=(
        "1. Analise a consulta do cliente ({question}).\n"
        "2. Use o contexto recuperado ({context}) para identificar produtos relevantes.\n"
        "3. Forneça uma lista de produtos baseados em dados da internet."
    ),
    expected_output="Lista de produtos relevantes com base na consulta ({question}).",
    agent=mind
)

persona_task = Task(
    description=(
        "1. Ajuste a resposta para oferecer recomendações personalizadas e claras.\n"
        "2. Inclua sugestões complementares ou acessórios relevantes para o cliente."
    ),
    expected_output="Recomendações ajustadas em português e personalizadas para o cliente.",
    agent=persona
)

crew = Crew(
    agents=[mind, persona],
    tasks=[mind_task, persona_task],
    process=Process.sequential,
    verbose=True
)

# Streamlit Interface
st.title("Bot Consultor de Produtos com Busca na Internet")
st.write("Busque produtos em sites da internet e receba recomendações personalizadas.")

# Entrada para URLs de sites de produtos
product_urls = st.text_area("Insira as URLs dos sites (uma por linha):", key="product_urls")
keywords = st.text_input("Palavras-chave para filtrar os resultados (opcional):", key="keywords")

if st.button("Buscar Produtos na Internet", key="buscar_internet"):
    if product_urls.strip():
        urls = product_urls.strip().split("\n")
        extract_products(urls, keywords=keywords if keywords else None)
    else:
        st.error("Por favor, insira ao menos uma URL válida.")

query = st.text_input("Digite sua busca por produtos:", key="consulta_produtos")

if st.button("Consultar Produtos", key="consultar_produtos"):
    if query:
        # Recuperar contexto
        st.write("Buscando produtos relevantes...")
        similar_products = search_products(query)
        context = "\n".join(similar_products) if similar_products else "Nenhum produto relevante encontrado."
        
        # Executar tarefas dos agentes
        st.write("Gerando recomendações personalizadas...")
        inputs = {"question": query, "context": context}
        results = crew.kickoff(inputs=inputs)
        st.write(results)
    else:
        st.error("Por favor, insira uma consulta válida.")
