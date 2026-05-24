from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import ollama
import fitz  # PyMuPDF para leitura de PDFs
from fastapi.responses import JSONResponse
import json

app = FastAPI()

# Modelo de requisição para gerar dataset
class Request(BaseModel):
    example: str
    numberRecords: int
    extracted_text: str  # Adiciona o texto extraído do PDF

async def extract_text_from_pdf(file: UploadFile):
    """Extrai texto de um arquivo PDF"""
    try:
        file_bytes = await file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "\n".join([page.get_text("text") for page in doc]).strip()
        return text
    except Exception as e:
        raise ValueError(f"Erro ao extrair texto do PDF: {str(e)}")

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Recebe um PDF, extrai seu texto e retorna para ser usado no dataset"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são suportados.")
    
    try:
        text = await extract_text_from_pdf(file)
        if not text:
            raise HTTPException(status_code=400, detail="O PDF está vazio ou ilegível.")
        
        return {"message": "Texto extraído com sucesso!", "extracted_text": text}
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

def clean_generated_dataset(dataset):
    """Remove respostas repetidas ou não estruturadas"""
    if isinstance(dataset, str):
        try:
            dataset = json.loads(dataset)
        except json.JSONDecodeError:
            return []

    if not isinstance(dataset, list):
        return []

    seen_questions = set()
    cleaned_data = []
    
    for entry in dataset:
        if isinstance(entry, dict) and "Question" in entry and "Response" in entry:
            question = entry["Question"].strip()
            response = entry["Response"].strip()
            
            if question and response and question not in seen_questions:
                seen_questions.add(question)
                cleaned_data.append(entry)

    return cleaned_data

@app.post("/datasetGenerate/")
def query_llm(request: Request):
    """Gera um dataset com base no conteúdo do PDF"""
    try:
        prompt = (
            f"Baseado no seguinte conteúdo:\n\n"
            f"{request.extracted_text[:2000]}...\n\n"  # Limita o tamanho do texto enviado
            f"Gere {request.numberRecords} registros seguindo este formato de exemplo:\n\n"
            f"{request.example}\n\n"
            f"Não adicione comentários extras e garanta que os dados estejam bem estruturados."
        )

        response = ollama.chat(model="huihui_ai/qwen2.5-1m-abliterated:latest", messages=[{"role": "user", "content": prompt}])

        dataset = clean_generated_dataset(response.get("message", {}).get("content", "[]"))

        return {"response": dataset}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dataset: {str(e)}")
