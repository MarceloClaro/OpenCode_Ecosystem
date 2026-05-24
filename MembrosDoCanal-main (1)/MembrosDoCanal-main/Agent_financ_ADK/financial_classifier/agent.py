from google.adk.agents.llm_agent import Agent
from utils.extractor import extract_text_markdown
from utils.classifier import classify_with_llama
from database import save_classification

def classify_document_tool(file_path: str) -> dict:
    """Fluxo completo de extração + classificação + persistência."""
    print(f"📂 Processando documento: {file_path}")

    # 1. Extração
    text = extract_text_markdown(file_path)
    if text.startswith("Erro"):
        return {"status": "erro", "message": text}

    # 2. Classificação
    category, confidence = classify_with_llama(text)

    # 3. Persistência
    save_classification(file_path, category, confidence, text)

    return {
        "status": "sucesso",
        "arquivo": file_path,
        "categoria": category,
        "confianca": confidence,
    }

root_agent = Agent(
    model="llama3.1:8b",
    name="financial_classifier_agent",
    description="Classifica documentos financeiros com MarkItDown e Llama 3.1.",
    instruction="Use a ferramenta classify_document_tool para analisar e classificar documentos financeiros.",
    tools=[classify_document_tool],
)

