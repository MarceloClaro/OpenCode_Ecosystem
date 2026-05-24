import base64
import io
from typing import List

import ollama
from PIL import Image
from pdf2image import convert_from_bytes


EXTRACTION_PROMPT = (
    "Você é um extrator de dados de DOCUMENTOS FINANCEIROS (boleto, extrato, nota, recibo, contrato). "
    "Analise a imagem e devolva SOMENTE um JSON em português, sem comentários, no formato:\n"
    "{\n"
    '  "tipo_documento": "boleto | extrato | nota_fiscal | recibo | contrato | desconhecido",\n'
    '  "campos": {\n'
    '    "valor": "R$ 0,00",\n'
    '    "vencimento": "YYYY-MM-DD ou vazio",\n'
    '    "cnpj": "",\n'
    '    "cpf": "",\n'
    '    "numero_documento": "",\n'
    '    "banco": "",\n'
    '    "beneficiario": "",\n'
    '    "pagador": "",\n'
    '    "codigo_barras": ""\n'
    "  },\n"
    '  "texto_bruto": "<trechos importantes>\"\n'
    "}\n"
    "Se não identificar um campo, deixe-o vazio. NÃO descreva a imagem; apenas extraia dados."
)

def _qwen_from_pil(image: Image.Image) -> str:
    """Envia uma PIL Image como bytes para o Qwen2.5-VL via Ollama usando generate() com images=[]."""
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    image_bytes = buf.getvalue()

    # IMPORTANTE: use generate() (esta API aceita images=[...])
    resp = ollama.generate(
        model="qwen2.5vl:7b",
        prompt=EXTRACTION_PROMPT,
        images=[image_bytes],   # <-- envio multimodal correto
        options={"temperature": 0}  # respostas mais determinísticas
    )
    # A resposta textual fica em resp["response"]
    return resp.get("response", "").strip()


def extract_data_qwen(file_path: str) -> str:
    """
    Extrai texto e campos financeiros de uma IMAGEM ou PDF usando Qwen2.5-VL:7b (Ollama).
    - PNG/JPG/JPEG: envia a imagem diretamente
    - PDF: converte primeira página em imagem (pode expandir para todas)
    Retorna o JSON (string) gerado pelo modelo ou mensagem de erro legível.
    """
    path = file_path.lower()

    try:
        # ---- IMAGEM ----
        if path.endswith((".png", ".jpg", ".jpeg")):
            with Image.open(file_path) as img:
                result = _qwen_from_pil(img)
            if not result or "It appears you've shared an image" in result:
                return "Falha na extração: resposta irrelevante do modelo."
            return result

        # ---- PDF ----
        if path.endswith(".pdf"):
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()

            # Converte o PDF em memória; processa SOMENTE a 1ª página por performance
            pages: List[Image.Image] = convert_from_bytes(pdf_bytes, dpi=300)
            if not pages:
                return "Nenhuma página encontrada no PDF."

            try:
                first_page = pages[0]
                result = _qwen_from_pil(first_page)
            finally:
                # Libera recursos de todas as páginas (Windows friendly)
                for p in pages:
                    try:
                        p.close()
                    except Exception:
                        pass

            if not result or "It appears you've shared an image" in result:
                return "Falha na extração: resposta irrelevante do modelo."
            return result

        return "Formato de arquivo não suportado. Envie um PDF, PNG, JPG ou JPEG."

    except Exception as e:
        return f"Erro ao processar documento: {e}"

