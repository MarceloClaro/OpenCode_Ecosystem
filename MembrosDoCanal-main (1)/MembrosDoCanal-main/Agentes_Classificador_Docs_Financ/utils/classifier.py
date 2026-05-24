import json
from typing import Tuple
from ollama import chat  # ou outro client que você já use (ex: openai, google)
import re

# =====================================================
# 🔍 CLASSIFICADOR DE DOCUMENTOS FINANCEIROS COM LLM
# =====================================================

def classify_with_llama(text: str) -> Tuple[str, float]:
    """
    Classifica o conteúdo textual de um documento financeiro.
    Retorna: (categoria, confiança)
    """

    # -----------------------------
    # 1️⃣  Exemplos (few-shots)
    # -----------------------------
    examples = [
        {
            "texto": "Boleto, Cedente, Pagador, Vencimento, BANCO SANTANDER, Banco do Brasil S.A., Código de Barras 34191.79001...",
            "categoria": "Boleto Bancário",
            "motivo": "Presença de código de barras, valores, vencimento e instruções de pagamento."
        },
        {
            "texto": "Nota Fiscal Eletrônica NF-e número 002334 série 1 CNPJ 12.345.678/0001-99",
            "categoria": "Nota Fiscal",
            "motivo": "Possui dados fiscais, CNPJ e número de nota."
        },
        {
            "texto": "Contrato de prestação de serviços celebrado entre...",
            "categoria": "Contrato",
            "motivo": "Contém cláusulas contratuais e assinaturas."
        },
        {
            "texto": "Comprovante de pagamento PIX ID 83d3b12b...",
            "categoria": "Comprovante de Pagamento",
            "motivo": "Inclui informações de transferência, data e valores pagos."
        },
        {
            "texto": "Extrato bancário 01/2024 Conta Corrente Agência 1234 Conta 56789",
            "categoria": "Extrato Bancário",
            "motivo": "Tem estrutura de transações, saldo e movimentações."
        },
    ]

    # -----------------------------
    # 2️⃣  Construção do prompt
    # -----------------------------
    examples_text = "\n\n".join(
        [f"Texto: {ex['texto']}\nCategoria: {ex['categoria']}\nMotivo: {ex['motivo']}" for ex in examples]
    )

    prompt = f"""
Você é um especialista em análise de documentos financeiros.

Sua tarefa é classificar o documento a seguir em uma das categorias:
- Boleto Bancário
- Nota Fiscal
- Comprovante de Pagamento
- Contrato
- Extrato Bancário
- Outro

Analise os exemplos e, com base neles, classifique o texto abaixo.
Responda apenas em JSON, com os campos:

{{
  "categoria": "<categoria>",
  "confianca": <float entre 0 e 1>,
  "justificativa": "<breve justificativa>"
}}

### Exemplos:
{examples_text}

### Documento:
{text[:4000]}
"""

    # -----------------------------
    # 3️⃣  Chamada ao modelo
    # -----------------------------
    try:
        response = chat(
            model="llama3.1:8b",  # ou o modelo que você usa
            messages=[
                {"role": "system", "content": "Você é um classificador financeiro confiável."},
                {"role": "user", "content": prompt},
            ],
            options={"temperature": 0, "top_p": 0.8, "num_predict": 512},
        )

        output = response["message"]["content"].strip()

        # -----------------------------
        # 4️⃣  Extração segura do JSON
        # -----------------------------
        json_match = re.search(r"\{.*\}", output, re.DOTALL)
        if not json_match:
            raise ValueError("Resposta não contém JSON válido.")
        data = json.loads(json_match.group(0))

        categoria = data.get("categoria", "Outro").strip()
        confianca = float(data.get("confianca", 0.5))

        # Sanitização
        if confianca < 0 or confianca > 1:
            confianca = 0.5

        return categoria, confianca

    except Exception as e:
        # fallback seguro
        print(f"[Erro classificador] {e}")
        return "Outro", 0.5

