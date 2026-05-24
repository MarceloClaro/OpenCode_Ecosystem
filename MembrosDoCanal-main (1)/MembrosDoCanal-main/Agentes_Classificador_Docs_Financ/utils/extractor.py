import base64
import io
import concurrent.futures
from PIL import Image
from markitdown import MarkItDown
from .ollama_adapter_MarkItDown import OllamaAdapterMarkItDown

# Modelos padrão (pode ajustar via .env)
VLM_MODEL = "qwen2.5vl:7b"
VLM_TIMEOUT = 300
VLM_MAX_IMG_SIZE = 1280


# 🔹 Inicializa o cliente multimodal (igual ao rag_ui_ollama)
ollama_vlm_client = OllamaAdapterMarkItDown(
    model_name=VLM_MODEL,
    connect_timeout=5.0,
    read_timeout=VLM_TIMEOUT,
    max_side=VLM_MAX_IMG_SIZE,
)

# 🔹 Instância do MarkItDown configurada com o VLM
markit = MarkItDown(
    llm_client=ollama_vlm_client,
    llm_model=VLM_MODEL,
    llm_prompt="Descreva a imagem e extraia todo o texto visível, valores e campos financeiros, em português.",
    timeout=VLM_TIMEOUT,
)


def extract_text_markdown(file_path: str) -> str:
    """
    Extrai texto em Markdown de documentos (PDF, DOCX, etc.).
    Se for imagem (PNG/JPG/JPEG), usa o OllamaAdapterMarkItDown com Qwen2.5-VL.
    """
    path_lower = file_path.lower()
    try:
        # ---- CASO 1: Imagem (usar VLM) ----
        if path_lower.endswith((".png", ".jpg", ".jpeg")):
            with open(file_path, "rb") as f:
                image_bytes = f.read()

            # Converte para base64 data URL
            img = Image.open(io.BytesIO(image_bytes))
            img.thumbnail((VLM_MAX_IMG_SIZE, VLM_MAX_IMG_SIZE))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            data_url = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

            # Usa MarkItDown com cliente VLM (OllamaAdapter)
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(markit.convert, data_url)
                result = future.result(timeout=VLM_TIMEOUT)

            text = result.text_content.strip()
            return text if text else "Nenhum texto foi detectado na imagem."

        # ---- CASO 2: PDF, DOCX, XLSX, etc. ----
        else:
            md = MarkItDown(enable_plugins=False)
            result = md.convert(file_path)
            text = result.text_content.strip()
            return text if text else "Documento sem conteúdo textual extraído."

    except concurrent.futures.TimeoutError:
        return f"⏱️ Tempo limite de {VLM_TIMEOUT}s excedido durante a análise da imagem."
    except Exception as e:
        return f"❌ Erro ao extrair texto: {e}"

