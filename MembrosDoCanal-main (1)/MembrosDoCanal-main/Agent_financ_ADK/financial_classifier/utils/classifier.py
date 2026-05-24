import ollama
import json
import re

def classify_with_llama(document_text: str):
    """
    Classifica documento financeiro com o modelo Llama 3.1:8b via Ollama.
    Retorna categoria e confiança, com fallback robusto se o modelo não retornar JSON válido.
    """
    prompt = f"""
    Você é um classificador de documentos financeiros.
    Analise o texto abaixo e classifique-o em uma das seguintes categorias:

    - Boleto Bancário
    - Extrato Bancário
    - Nota Fiscal
    - Recibo
    - Contrato Financeiro
    - Declaração de Imposto
    - Outro

    Retorne apenas um JSON no formato:
    {{
      "categoria": "Boleto Bancário",
      "confianca": 0.95
    }}

    Texto:
    {document_text[:6000]}
    """

    try:
        response = ollama.chat(
            model="llama3.1:8b",
            messages=[{"role": "user", "content": prompt}],
        )
        content = response["message"]["content"].strip()

        # 🔹 Tenta ler JSON diretamente
        try:
            result = json.loads(content)
            categoria = result.get("categoria", "Indefinido")
            confianca = float(result.get("confianca", 0.0))
            return categoria, confianca
        except json.JSONDecodeError:
            # 🔹 Fallback: extrai com regex se vier em texto
            match = re.search(r'categoria["\']?\s*[:=]\s*["\']?([A-Za-zÀ-ÿ\s]+)["\']?', content, re.IGNORECASE)
            categoria = match.group(1).strip() if match else "Indefinido"

            conf_match = re.search(r'confianca["\']?\s*[:=]\s*([0-9.]+)', content)
            confianca = float(conf_match.group(1)) if conf_match else 0.5

            return categoria, confianca

    except Exception as e:
        print(f"[Erro Llama] {e}")
        return "Indefinido", 0.0

