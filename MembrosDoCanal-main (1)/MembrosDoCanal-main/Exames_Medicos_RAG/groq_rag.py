import os
import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF
from groq import Groq

# Inicializar o cliente ChromaDB
chroma_client = chromadb.Client()

# Verificar se a coleção já existe e recuperá-la, ou criar uma nova
collection_name = "exames"
collections = chroma_client.list_collections()

if collection_name in [col.name for col in collections]:
    collection = chroma_client.get_collection(collection_name)
else:
    collection = chroma_client.create_collection(name=collection_name)

# Carregar o modelo sentence-transformers
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Criar embedding do texto
def embed_text(text):
    embeddings = model.encode([text], convert_to_tensor=True)
    return embeddings.cpu().numpy()[0]

# Ler o arquivo PDF para extrair o texto
def read_pdfs_from_directory(directory):
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            filepath = os.path.join(directory, filename)
            doc = fitz.open(filepath)
            text = ""
            for page in doc:
                text += page.get_text()
            # Limpar o texto preservando a ortografia
            cleaned_text = clean_text(text)
            documents.append((filename, cleaned_text))
    return documents

# Limpar o texto
def clean_text(text):
    # Remove espaços extras e novas linhas desnecessárias
    cleaned_text = ' '.join(text.split())
    return cleaned_text
# Criar o chunk do texto do PDF
def chunk_text(text, chunk_size=512):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

#Upload do arquivo PDF
def process_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        cleaned_text = clean_text(text)
        return cleaned_text
    return None

# Recuperador
def search_similar_documents(query, top_k=5):
    query_embedding = embed_text(query).tolist()  # Convertendo o ndarray para uma lista
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    
    similar_documents = [metadata["content"] for metadata in results['metadatas'][0]]
    return similar_documents

# Carrega API Groq
llm = Groq(
    api_key="sua chave aqui",
)

# Gerador
def generate_decision(new_document, similar_documents):
    input_text = f"Documento novo: {new_document}\n\nDocumentos Similares: {' '.join(similar_documents)}"
    
    result = llm.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "Você é um assistente de saúde que fornece respostas em português para a questão do usuário."
        },
        {
            "role": "user",
            "content": input_text,
        }
    ],
    model="llama3-8b-8192",)

    return result

# Streamlit Interface
st.title("Analisador de Exames Médicos")

uploaded_file = st.file_uploader("Faça upload de um arquivo PDF de exame médico", type=["pdf"])
query = st.text_input("Digite sua consulta", key="consulta1")

result = None

if st.button("Consultar", key="botao1"):
    if uploaded_file is not None and query:
        doc_text = process_uploaded_file(uploaded_file)
        chunks = chunk_text(doc_text)
        for i, chunk in enumerate(chunks):
            embedding = embed_text(chunk).tolist()
            collection.add(embeddings=[embedding], ids=[f"uploaded_chunk_{i}"], metadatas=[{"filename": uploaded_file.name, "content": chunk}])
        
        similar_docs = search_similar_documents(query)
        result = generate_decision(query, similar_docs)
        st.write(result.choices[0].message.content)
    else:
        st.error("Por favor, faça upload de um PDF e digite uma consulta.")
   




