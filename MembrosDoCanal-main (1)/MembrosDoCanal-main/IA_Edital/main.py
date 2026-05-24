import streamlit as st
import os
import PyPDF2
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_community.document_loaders import UnstructuredFileLoader
import base64
import os
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da chave da API Groq e Pinecone a partir do .env
groq_api_key = os.getenv("GROQ_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")

# Verificar se as chaves foram carregadas corretamente (opcional)
if not groq_api_key or not pinecone_api_key:
    raise ValueError("Chaves de API não foram carregadas corretamente.")

index_name = "edital"
editais_dir = "editais"

# Inicializar Pinecone
pc = Pinecone(api_key=pinecone_api_key)

# Verificar ou criar o índice no Pinecone
if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Obtenha o objeto do índice do Pinecone
index = pc.Index(index_name)

# Inicializar o modelo de embeddings e o retriever
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vector_store = PineconeVectorStore(index=index, embedding=embeddings)

retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 12, "fetch_k": 40, "lambda_mult": 0.1},
)

# Inicializar o LLM
llm = ChatGroq(
    model="llama-3.2-11b-text-preview",
    temperature=0
)

# Memória da conversa com buffer de 4 mensagens
conversational_memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=4,  # Número de mensagens armazenadas na memória
    return_messages=True  # Retorna as mensagens na resposta
)

# Criar a chain de QA
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=False
)

# Função para upsert o PDF
def upsert_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    num_pages = len(reader.pages)
    print(f"O PDF tem {num_pages} páginas.")

    # Se o PDF puder ser lido, use o UnstructuredFileLoader
    loader = UnstructuredFileLoader(pdf_file)
    documents = loader.load()

    # Concatenar o conteúdo dos documentos em um único texto
    concatenated_text = " ".join([doc.page_content for doc in documents])

    # Usar o text splitter no texto concatenado
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1250, chunk_overlap=100)
    texts = text_splitter.split_text(concatenated_text)

    ids = []
    documents = []
    id = 0
    for text in texts:
        document = Document(page_content=text)
        documents.append(document)
        id += 1
        ids.append(str(id))

    vector_store.add_documents(documents=documents, ids=ids)

    return f"Edital {os.path.basename(pdf_file)} processado e armazenado com sucesso!"


# Função para processar o último arquivo PDF no diretório 'editais'
def process_last_pdf():
    pdf_files = [f for f in os.listdir(editais_dir) if f.endswith(".pdf")]
    
    if not pdf_files:
        return "Nenhum arquivo PDF encontrado no diretório."
    
    last_pdf = max(pdf_files, key=lambda f: os.path.getmtime(os.path.join(editais_dir, f)))
    file_path = os.path.join(editais_dir, last_pdf)
    upsert_pdf(file_path)
    
    return f"O arquivo {last_pdf} foi processado e inserido com sucesso!"


# Função para visualizar documentos no diretório 'editais'
def get_all_documents():
    return [file_name for file_name in os.listdir(editais_dir) if file_name.endswith(".pdf")]


# Função para deletar um documento
def delete_document(file_name):
    file_path = os.path.join(editais_dir, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        return f"Documento {file_name} deletado com sucesso!"
    else:
        return "Documento não encontrado."



def displayPDF(file):
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)



# Interface Streamlit
st.title("Assistente de IA para Editais")

# Menu lateral
menu = st.sidebar.selectbox("Menu", ["Consultar IA", "Enviar Edital", "Upsert Edital", "Visualizar Editais"])

# Opção: Fazer pergunta
if menu == "Consultar IA":
    st.header("Consultar")
    query = st.text_input("Digite sua pergunta sobre o edital:")
    if st.button("Obter Resposta"):
        if query:
            response = qa.invoke(query)
            st.write("Resposta:")
            st.write(response["result"])
        else:
            st.error("Por favor, insira uma pergunta.")

# Opção: Enviar Edital
elif menu == "Enviar Edital":
    st.header("Enviar Edital")
    uploaded_pdf = st.file_uploader("Envie um edital (PDF)", type="pdf")
    if uploaded_pdf is not None:
        save_path = os.path.join(editais_dir, uploaded_pdf.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_pdf.getbuffer())
        st.success(f"Arquivo {uploaded_pdf.name} enviado com sucesso!")

# Opção: Processar o último PDF (Upsert)
elif menu == "Upsert Edital":
    st.header("Upsert Edital")
    if st.button("Upsert"):
        process_message = process_last_pdf()
        st.info(process_message)

# Opção: Visualizar documentos
elif menu == "Visualizar Editais":
    st.header("Visualizar Editais")
    documents = get_all_documents()

    if documents:
        for doc in documents:
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(doc)
            
            # Botão para deletar o edital
            if col2.button("Deletar", key=f"delete_{doc}"):
                delete_message = delete_document(doc)
                st.warning(delete_message)
            
            # Botão para visualizar o edital
            if col3.button("Visualizar", key=f"view_{doc}"):
                file_path = os.path.join(editais_dir, doc)
                displayPDF(file_path)
    else:
        st.info("Nenhum documento encontrado no diretório 'editais'.")

   


