import streamlit as st
import pdfplumber
import tempfile
from ollama_ocr import OCRProcessor
import openai
import xml.etree.ElementTree as ET
import os
import re

# ------ CONFIGURAÇÃO ------
ocr = OCRProcessor(
    model_name='qwen2.5vl:7b',
    base_url="http://localhost:11434/api/generate"
)
openai.api_key = "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"

TIPOS_INFORME = {
    "empregador": [
        ("nome", "Nome completo"),
        ("cpf", "CPF"),
        ("fonte_pagadora", "Nome Empresarial"),
        ("cnpj", "CNPJ"),
        ("valor_rendimentos", "Valor dos Rendimentos"),
        ("contribuicao_previdenciaria", "Contribuição Previdenciária"),
        ("valor_irrf", "IRRF"),
        ("tipo_rendimento", "Tipo de rendimento"),
    ],
    "bancario": [
        ("titular", "Titular da Conta"),
        ("cpf", "CPF do Titular"),
        ("banco", "Banco"),
        ("agencia", "Agência"),
        ("conta", "Conta"),
        ("saldo_3112", "Saldo em 31/12"),
        ("saldo_0101", "Saldo em 01/01"),
        ("rendimentos", "Rendimentos de Aplicações"),
    ],
    "corretora": [
        ("titular", "Titular"),
        ("cpf", "CPF do Titular"),
        ("corretora", "Nome da Corretora"),
        ("cnpj_corretora", "CNPJ da Corretora"),
        ("saldo_3112", "Saldo em 31/12"),
        ("posicao_acoes", "Posição em Ações"),
        ("rendimento_renda_variavel", "Rendimentos Renda Variável"),
    ],
    "outros": []
}

def extract_text_vlm_from_pdf(file):
    all_text = []
    with pdfplumber.open(file) as pdf:
        for idx, page in enumerate(pdf.pages):
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
                pil_img = page.to_image(resolution=300).original
                pil_img.save(tmp_img.name)
                temp_filename = tmp_img.name
            texto_pagina = ocr.process_image(
                image_path=temp_filename,
                format_type="markdown",
                custom_prompt="""Extract all visible Portuguese text from the image. Return all text as it appears, including tables, numbers, and field names, in reading order. Do not translate or summarize.""",
                language="Portuguese"
            )
            all_text.append(f"--- Página {idx+1} ---\n{texto_pagina}")
            try:
                os.unlink(temp_filename)
            except Exception as e:
                print(f"Erro ao deletar arquivo temporário: {e}")
    return "\n\n".join(all_text)

def detecta_tipo_informe(texto_extraido):
    prompt = f"""A seguir está o texto extraído de um comprovante de rendimento. 
Classifique o tipo do informe. Escolha apenas uma opção: empregador, bancario, corretora, outros.
Retorne apenas a categoria.
Texto:
{texto_extraido}
"""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um classificador de tipo de informe para DIRPF."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    tipo = response.choices[0].message.content.strip().lower()
    return tipo if tipo in TIPOS_INFORME else "outros"

def extract_fields_llm(document_text, tipo):
    if tipo in TIPOS_INFORME and TIPOS_INFORME[tipo]:
        lista_campos = "\n".join([f"- {k} ({v})" for k, v in TIPOS_INFORME[tipo]])
    else:
        lista_campos = "- informe_livre (texto do informe completo)"

    prompt = f"""
O texto a seguir foi extraído de um comprovante de rendimento do tipo '{tipo}' para imposto de renda de pessoa física do Brasil.

Sua tarefa é encontrar e extrair os seguintes campos:
{lista_campos}

Responda apenas com um dicionário Python (chave:valor), sem explicação, sem bloco de código, sem comentários.

Texto extraído:
-----------------
{document_text}
-----------------
"""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um extrator de dados de informes para DIRPF."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    answer = response.choices[0].message.content.strip()
    code_block_match = re.search(r"```(?:python)?\s*([\s\S]+?)```", answer)
    if code_block_match:
        answer = code_block_match.group(1).strip()
    dict_match = re.search(r"\{[\s\S]+\}", answer)
    if dict_match:
        answer = dict_match.group(0)
    try:
        campos = eval(answer)
    except Exception:
        campos = {}
    return campos

def generate_xml_multi_tipo(informes):
    root = ET.Element("Dirf")
    for info in informes:
        tipo = info.get("_tipo", "outros")
        bloco = ET.SubElement(root, tipo.capitalize())
        for k, v in info.items():
            if k != "_tipo":
                ET.SubElement(bloco, k).text = str(v)
    xml_str = ET.tostring(root, encoding="utf-8", method="xml")
    return xml_str

# --- STREAMLIT UI ---
st.title("💡 DIRPF Automático (Multi-informe, detecção automática do tipo)")

uploaded_files = st.file_uploader(
    "Faça upload de um ou mais PDFs de informes (empregador, banco, corretora, etc)",
    type=["pdf"],
    accept_multiple_files=True
)

informes_extraidos = []

if uploaded_files:
    for idx, uploaded_file in enumerate(uploaded_files):
        st.markdown(f"---\n### Informe {idx+1}")

        cache_key = f"campos_{uploaded_file.name}"
        if cache_key not in st.session_state:
            with st.spinner(f"Extraindo texto do PDF {idx+1} com OCR VLM..."):
                document_text = extract_text_vlm_from_pdf(uploaded_file)
            with st.spinner(f"Detectando tipo do informe..."):
                tipo_informe = detecta_tipo_informe(document_text)
            with st.spinner(f"Extraindo campos para o informe {idx+1} ({tipo_informe})..."):
                campos = extract_fields_llm(document_text, tipo_informe)
            campos["_tipo"] = tipo_informe
            st.session_state[cache_key] = campos
        else:
            campos = st.session_state[cache_key]
            tipo_informe = campos.get("_tipo", "outros")

        st.info(f"**Tipo de informe detectado:** `{tipo_informe.capitalize()}`")
        # Destaca os campos obrigatórios não extraídos
        campos_tipo = TIPOS_INFORME.get(tipo_informe, [])
        missing_fields = [label for key, label in campos_tipo if not campos.get(key)]
        if missing_fields:
            st.warning("Não foi possível extrair os seguintes campos: " + ", ".join(missing_fields) + ". Preencha manualmente:")

        # Formulário dinâmico, só mostra os campos relevantes para o tipo
        for key, label in campos_tipo:
            highlight = not campos.get(key)
            campos[key] = st.text_input(
                label,
                campos.get(key, ""),
                key=f"{key}_{idx}",
                help="Campo obrigatório." if highlight else None,
                placeholder=f"Preencha o {label}" if highlight else None,
            )
            if highlight:
                st.markdown(f'<span style="color:red;font-size:small;">Campo não extraído automaticamente</span>', unsafe_allow_html=True)

        informes_extraidos.append(campos)

    if informes_extraidos:
        xml_data = generate_xml_multi_tipo(informes_extraidos)
        st.download_button(
            label="⬇️ Baixar XML consolidado de informes",
            data=xml_data,
            file_name="informes_consolidados.xml",
            mime="application/xml"
        )

st.info("O sistema detecta automaticamente o tipo de informe (empregador, bancário, corretora, etc) e mostra apenas os campos relevantes para cada caso. Preencha o que faltar e gere o XML consolidado!")
