from typing import List
import streamlit as st
from sentence_transformers import SentenceTransformer
from llama_index.core.llms import ChatMessage
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage
from llama_index.core import Settings
import nest_asyncio
import chromadb

# Aplicar nest_asyncio
nest_asyncio.apply()

# Configuração do LLM
llm = Ollama(model="llama3:latest", request_timeout=420.0)
Settings.llm = llm

# Função para embutir texto
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def embed_text(text: str) -> List[float]:
    embeddings = model.encode([text], convert_to_tensor=True)
    return embeddings.cpu().numpy()[0].tolist()

# Inicializar o cliente ChromaDB
chroma_client = chromadb.Client()

# Verificar ou criar coleção
collection_name = "medical_cases"
collections = chroma_client.list_collections()

if collection_name in [col.name for col in collections]:
    collection = chroma_client.get_collection(collection_name)
else:
    collection = chroma_client.create_collection(name=collection_name)

# Adicionar casos médicos ao ChromaDB
medical_cases = [
    "Caso 1...paciente com febre alta, dor de cabeça e dor muscular. Diagnóstico: Dengue. Tratamento: Hidratação e repouso.",
    "Caso 2...Paciente com tosse persistente, falta de ar e dor no peito. Diagnóstico: Pneumonia. Tratamento: Antibióticos e repouso.",
    "Caso 3...Paciente com dor abdominal intensa, náusea e vômito. Diagnóstico: Apendicite. Tratamento: Cirurgia.",
    "Caso 4...Paciente com dor no peito, sudorese e falta de ar. Diagnóstico: Infarto do miocárdio. Tratamento: Intervenção médica imediata.",
    "Caso 5...Paciente com erupções cutâneas, febre e dor nas articulações. Diagnóstico: Zika. Tratamento: Hidratação e medicação para sintomas."
]

for i, case in enumerate(medical_cases):
    embedding = embed_text(case)
    collection.add(embeddings=[embedding], ids=[f"case_{i}"], metadatas=[{"content": case}])

# Função para buscar casos médicos similares
def search_similar_cases(query: str, top_k: int = 3) -> List[str]:
    query_embedding = embed_text(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    similar_cases = [metadata["content"] for metadata in results['metadatas'][0]]
    return similar_cases

search_similar_cases_tool = FunctionTool.from_defaults(fn=search_similar_cases)

# Função para gerar diagnóstico e tratamento
def generate_diagnosis_and_treatment(new_case: str, similar_cases: List[str]) -> str:
    input_text = f"Sintomas do novo caso médico: {new_case}\n\nCasos Similares: {' '.join(similar_cases)}"
    
    messages = [
        ChatMessage(
            role="system", content="Você é especialista em medicina e fornece diagnósticos e tratamentos de acordo com os sintomas do paciente."
        ),
        ChatMessage(role="user", content=input_text),
        ChatMessage(role="user", content="Você deve fornecer um diagnóstico e tratamento se baseando nos sintomas, diagnóstico e tratamento do caso médico mais similar aos sintomas do novo caso médico.\n"
                    "Não adicione nenhum texto a mais no texto do novo caso.\n"
                    "Na sua resposta deve somente constar a lista dos casos similares e a explicação para o diagnóstico e tratamento."
                    ),
    ]
    resp = llm.chat(messages)
    
    return resp

generate_diagnosis_and_treatment_tool = FunctionTool.from_defaults(fn=generate_diagnosis_and_treatment)


agent = ReActAgent.from_tools(
    [search_similar_cases_tool, generate_diagnosis_and_treatment_tool],
    llm=llm,
    verbose=True,
)

# Interface do usuário com Streamlit
st.title("Assistente de Diagnóstico e Tratamento Médico")

new_case = st.text_area("Insira os sintomas e informações do novo caso")

if st.button("Buscar Casos Similares e Gerar Diagnóstico e Tratamento"):
    if new_case:       
        with st.spinner("Obtendo o diagnóstico e o tratamento..."):
            #diagnosis_and_treatment = agent.chat(f"Procure pelos os casos médicos mais similares a esse novo caso  {new_case}") 
            diagnosis_and_treatment = agent.chat(f"Procure pelos os casos médicos mais similares a esse novo caso  {new_case} visando usá-los para obter o diagnóstico e tratamento do novo caso.") 

            st.subheader("Diagnóstico e Tratamento Gerado")
            st.write(str(diagnosis_and_treatment))
    else:
        st.error("Por favor, insira os sintomas e informações do novo caso.")
