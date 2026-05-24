

import os
import PyPDF2
import pytesseract
from PIL import Image
from qdrant_client import QdrantClient, models
import google.generativeai as genai
from dotenv import load_dotenv
import uuid

load_dotenv()

# Configuração
QDRANT_PATH = "./vector_store"
COLLECTION_NAME = "documentos"
# Garanta que o caminho para o executável do Tesseract está correto
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Inicialização dos clientes
qdrant_client = QdrantClient(path=QDRANT_PATH)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_text_from_pdf(file_path):
    """Extrai texto de um arquivo PDF."""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Erro ao ler PDF {file_path}: {e}")
    return text

def get_text_from_image(file_path):
    """Extrai texto de uma imagem usando Tesseract OCR."""
    try:
        return pytesseract.image_to_string(Image.open(file_path))
    except Exception as e:
        print(f"Erro ao ler imagem {file_path}: {e}")
        return ""

def get_text_chunks(text):
    """Divide o texto em chunks menores."""
    chunk_size = 1000
    chunk_overlap = 100
    chunks = []
    for i in range(0, len(text), chunk_size - chunk_overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

def get_embeddings(text, model="models/embedding-001"):
    """Gera embeddings para o texto usando o Gemini."""
    try:
        return genai.embed_content(
            model=model,
            content=text,
            task_type="retrieval_document"
        )['embedding']
    except Exception as e:
        print(f"Erro ao gerar embedding: {e}")
        return None

def setup_qdrant():
    """Configura a coleção no Qdrant, se não existir."""
    try:
        qdrant_client.get_collection(collection_name=COLLECTION_NAME)
        print("Coleção já existe no Qdrant.")
    except Exception:
        qdrant_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
        )
        print("Coleção criada no Qdrant.")

def index_document(file_path, filename):
    """Processa e indexa um documento (PDF ou imagem)."""
    file_extension = os.path.splitext(filename)[1].lower()
    text = ""
    if file_extension == ".pdf":
        text = get_text_from_pdf(file_path)
    elif file_extension in [".png", ".jpg", ".jpeg"]:
        text = get_text_from_image(file_path)
    else:
        print(f"Formato de arquivo não suportado: {file_extension}")
        return

    if not text.strip():
        print(f"Nenhum texto extraído de {filename}. O arquivo pode estar vazio ou ser uma imagem sem texto.")
        return

    chunks = get_text_chunks(text)
    points = []
    for chunk in chunks:
        embedding = get_embeddings(chunk)
        if embedding:
            points.append(
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={"text": chunk, "source": filename}
                )
            )

    if points:
        try:
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=points,
                wait=True
            )
            print(f"Documento {filename} indexado com {len(points)} chunks.")
        except Exception as e:
            print(f"Erro ao inserir dados no Qdrant: {e}")

def search_documents(query):
    """Busca por documentos relevantes no Qdrant."""
    if not query:
        return []
    embedding = get_embeddings(query, model="models/embedding-001")
    if not embedding:
        return []
        
    hits = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        limit=5
    )
    return [hit.payload for hit in hits]

def get_rag_response(query, context_payloads):
    """Gera uma resposta usando o Gemini com o contexto do RAG."""
    if not context_payloads:
        return "Não encontrei informação relevante nos documentos para responder a sua pergunta."

    context_texts = [payload['text'] for payload in context_payloads]
    sources = sorted(list(set([payload['source'] for payload in context_payloads])))

    prompt = f"""
    Você é um assistente de IA especialista em análise de documentos. Sua tarefa é responder à pergunta do usuário de forma clara e concisa, baseando-se exclusivamente no contexto fornecido.
    Se a informação não estiver no contexto, afirme que não foi possível encontrar a resposta nos documentos.
    Ao final da sua resposta, liste os nomes dos arquivos que serviram como fonte.

    Contexto extraído dos documentos:
    ---
    {' '.join(context_texts)}
    ---

    Pergunta do usuário: {query}
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        response_text = response.text
        if sources:
            response_text += f"\n\n**Fontes:** {', '.join(sources)}"
        
        return response_text
    except Exception as e:
        return f"Ocorreu um erro ao gerar a resposta: {e}"

