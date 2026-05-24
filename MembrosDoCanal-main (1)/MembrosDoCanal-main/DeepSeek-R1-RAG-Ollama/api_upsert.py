from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import nltk
from nltk.tokenize import word_tokenize
from Extractor_text_docs import extract_text_from_pdf, clean_text
from DataBaseManager import store_chunk

nltk.download('punkt')

# Inicializa a aplicação FastAPI
app = FastAPI()

# Modelo de entrada para o diretório
class FolderPath(BaseModel):
    folder: str

# Função para criar chunks
def create_chunks(text, size_chunk=400):
    """Divide o texto em chunks de aproximadamente 400 palavras."""
    palavras = word_tokenize(text)
    chunks = []
    for i in range(0, len(palavras), size_chunk):
        chunk = ' '.join(palavras[i:i + size_chunk])
        chunks.append(chunk)
    return chunks

# Endpoint para processar os documentos
@app.post("/upsert_documents")
async def upsert_documents(data: FolderPath):
    """Processa cada documento PDF no diretório especificado."""
    folder = data.folder
    
    if not os.path.exists(folder):
        raise HTTPException(status_code=404, detail=f"O diretório {folder} não existe.")

    try:
        for name_file in os.listdir(folder):
            if name_file.endswith('.pdf'):
                path_pdf = os.path.join(folder, name_file)
                text = clean_text(extract_text_from_pdf(path_pdf))
                chunks = create_chunks(text, 400)
                for chunk in chunks:
                    store_chunk(chunk, name_file)
        return {"message": "Documentos processados com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar documentos: {str(e)}")
