import streamlit as st
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from groq import Groq

client = Groq(
    api_key="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",
)

# Inicializar o cliente ChromaDB
chroma_client = chromadb.Client()

# Verificar se a coleção já existe e recuperá-la, ou criar uma nova
collection_name = "documents"
collections = chroma_client.list_collections()

if collection_name in [col.name for col in collections]:
    collection = chroma_client.get_collection(collection_name)
else:
    collection = chroma_client.create_collection(name=collection_name)

# Carregar o modelo sentence-transformers
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def embed_text(text):
    embeddings = model.encode([text], convert_to_tensor=True)
    return embeddings.cpu().numpy()[0]

# Documentos processuais simulados
documents = [
    "Petição inicial do documento 1... Ação de cobrança de dívida.",
    "Sentença inicial do documento 1... O réu é condenado a pagar a dívida.",
    "Recurso do documento 1... O réu recorre alegando prescrição da dívida.",
    "Decisão do juiz do documento 1... O recurso é negado, mantendo a sentença inicial de pagamento da dívida.",
    
    "Petição inicial do documento 2... Ação de indenização por danos morais.",
    "Sentença inicial do documento 2... O autor recebe indenização por danos morais.",
    "Recurso do documento 2... O réu recorre alegando ausência de provas suficientes.",
    "Decisão do juiz do documento 2... O recurso é aceito, e a sentença é revogada devido à insuficiência de provas.",
    
    "Petição inicial do documento 3... Ação de despejo por falta de pagamento.",
    "Sentença inicial do documento 3... O inquilino é despejado por falta de pagamento.",
    "Recurso do documento 3... O inquilino recorre alegando pagamento parcial das dívidas.",
    "Decisão do juiz do documento 3... O recurso é negado, e o despejo é mantido.",
    
    "Petição inicial do documento 4... Ação de guarda de menor.",
    "Sentença inicial do documento 4... A guarda é concedida ao pai.",
    "Recurso do documento 4... A mãe recorre solicitando a guarda compartilhada.",
    "Decisão do juiz do documento 4... O recurso é aceito, e a guarda compartilhada é estabelecida.",
    
    "Petição inicial do documento 5... Ação de partilha de bens.",
    "Sentença inicial do documento 5... Os bens são divididos igualmente entre as partes.",
    "Recurso do documento 5... Uma das partes recorre alegando que contribuiu mais para a aquisição dos bens.",
    "Decisão do juiz do documento 5... O recurso é parcialmente aceito, ajustando a partilha conforme a contribuição de cada parte."
]

# Adicionar documentos ao ChromaDB
for i, doc in enumerate(documents):
    embedding = embed_text(doc).tolist()  # Convertendo o ndarray para uma lista
    collection.add(embeddings=[embedding], ids=[f"doc_{i}"], metadatas=[{"content": doc}])

# Recuperador
def search_similar_documents(query, top_k=3):
    query_embedding = embed_text(query).tolist()  # Convertendo o ndarray para uma lista
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    
    similar_documents = [metadata["content"] for metadata in results['metadatas'][0]]
    return similar_documents

def extract_decision_text(full_text):
    start_marker = "Portanto, eu, [nome do juiz], pronuncio a seguinte sentença:"
    end_marker = "**Data**"
    
    start_index = full_text.find(start_marker)
    end_index = full_text.find(end_marker, start_index)
    
    if start_index != -1 and end_index != -1:
        decision_text = full_text[start_index + len(start_marker):end_index].strip()
    else:
        decision_text = full_text
    
    return decision_text

# Gerador
def generate_decision(new_document, similar_documents):
    input_text = f"Documento novo: {new_document}\n\nDocumentos Similares: {' '.join(similar_documents)}"

    completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "Você é um especialista jurídico que fornece decisões."},
        {"role": "user", "content": input_text},
        {"role": "user", "content": (
            "Forneça uma decisão final tendo somente como base a decisão do documento mais similar recuperado.\n"
            "Não adicione nenhum texto a mais no texto da petição inicial do documento novo.\n"
            "No texto da decisão final deve somente constar a lista dos documentos similares e a explicação para tal decisão."
        )}
    ],
    model="llama3-8b-8192",
)
       
    full_decision = completion.choices[0].message.content
    decision_text = extract_decision_text(full_decision)
    
    return decision_text

# Aplicação Streamlit
st.title("Gerador de Decisões Jurídicas")

new_document = st.text_area("Insira o texto da petição inicial do novo documento")

# Consulta do usuário 
if st.button("Buscar Documentos Similares e Gerar Decisão"):
    if new_document:
        with st.spinner("Buscando documentos similares..."):
            similar_docs = search_similar_documents(new_document)
           
        with st.spinner("Gerando decisão..."):
            decision = generate_decision(new_document, similar_docs)
            st.subheader("Decisão Gerada")
            st.write(decision)
    else:
        st.error("Por favor, insira o texto da petição inicial do novo documento.")
