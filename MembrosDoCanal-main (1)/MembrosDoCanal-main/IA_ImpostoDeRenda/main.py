import streamlit as st
import pdfplumber
from PIL import Image
import tempfile
from ollama_ocr import OCRProcessor
import openai
import xml.etree.ElementTree as ET
import os
import re
from dotenv import load_dotenv

# -------- CONFIGURAÇÕES ----------
ocr = OCRProcessor(
    model_name='qwen2.5vl:7b',
    base_url="http://localhost:11434/api/generate"
)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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

def extract_fields_llm(document_text):
    prompt = f"""
O texto a seguir foi extraído de um informe de rendimentos para imposto de renda de pessoa física do Brasil, podendo estar em formato de tabela ou desorganizado.

Sua tarefa é encontrar e extrair os seguintes campos, mesmo que estejam abreviados, com erros ou fora de ordem:
- nome (nome completo do contribuinte)
- cpf (CPF do contribuinte, com ou sem máscara)
- fonte_pagadora (nome da fonte pagadora, empresa ou banco)
- cnpj (CNPJ da fonte pagadora)
- valor_rendimentos (valor dos rendimentos tributáveis, como salário anual)
- valor_irrf (valor do imposto de renda retido na fonte)
- contribuicao_previdenciaria (valor da contribuição previdenciária oficial)
- rendimentos_isentos (valor da parcela isenta de aposentadoria ou outros rendimentos isentos)
- tipo_rendimento (ex: salário, pró-labore, aposentadoria, pensão)

Responda apenas com o dicionário Python, sem explicação, sem bloco de código, sem comentários.

Texto extraído:
-----------------
{document_text}
-----------------
"""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um extrator inteligente de dados para informes de rendimentos da Receita Federal do Brasil."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    answer = response.choices[0].message.content.strip()

    # Remove blocos de código markdown
    code_block_match = re.search(r"```(?:python)?\s*([\s\S]+?)```", answer)
    if code_block_match:
        answer = code_block_match.group(1).strip()
    dict_match = re.search(r"\{[\s\S]+\}", answer)
    if dict_match:
        answer = dict_match.group(0)
    try:
        campos = eval(answer)
    except Exception as e:
        print("Erro ao avaliar resposta do LLM:", e)
        campos = None
    return campos

def generate_dirpf_xml_multi(informes):
    """Gera XML consolidado agrupando rendimentos por CPF."""
    root = ET.Element("Dirf")
    contribuintes = {}
    for campos in informes:
        cpf = campos.get("cpf", "")
        if cpf not in contribuintes:
            contribuintes[cpf] = {
                "nome": campos.get("nome", ""),
                "cpf": cpf,
                "rendimentos": []
            }
        contribuintes[cpf]["rendimentos"].append(campos)

    for contrib in contribuintes.values():
        contribuinte = ET.SubElement(root, "Contribuinte")
        ET.SubElement(contribuinte, "Nome").text = contrib["nome"]
        ET.SubElement(contribuinte, "CPF").text = contrib["cpf"]

        rendimentos = ET.SubElement(contribuinte, "Rendimentos")
        for campos in contrib["rendimentos"]:
            rendimento = ET.SubElement(rendimentos, "RendimentoTributavel")
            ET.SubElement(rendimento, "FontePagadora").text = campos.get("fonte_pagadora", "")
            ET.SubElement(rendimento, "CNPJ").text = campos.get("cnpj", "")
            ET.SubElement(rendimento, "Tipo").text = campos.get("tipo_rendimento", "")
            ET.SubElement(rendimento, "Valor").text = str(campos.get("valor_rendimentos", "0"))
            ET.SubElement(rendimento, "IRRF").text = str(campos.get("valor_irrf", "0"))
            ET.SubElement(rendimento, "ContribuicaoPrevidenciaria").text = str(campos.get("contribuicao_previdenciaria", ""))
            ET.SubElement(rendimento, "RendimentosIsentos").text = str(campos.get("rendimentos_isentos", ""))

    xml_str = ET.tostring(root, encoding="utf-8", method="xml")
    return xml_str

# --------- STREAMLIT UI ---------
st.title("💡 DIRPF Automático com IA")

uploaded_files = st.file_uploader(
    "Faça upload de um ou mais PDFs de informes de rendimentos",
    type=["pdf"],
    accept_multiple_files=True
)

informes_extraidos = []

if uploaded_files:
    for idx, uploaded_file in enumerate(uploaded_files):
        st.markdown(f"---\n### Informe {idx+1}")

        # Use session_state para cachear o resultado do processamento (evita reprocessar!)
        cache_key = f"campos_{uploaded_file.name}"
        if cache_key not in st.session_state:
            with st.spinner(f"Extraindo texto do PDF {idx+1} com OCR VLM..."):
                document_text = extract_text_vlm_from_pdf(uploaded_file)
            with st.spinner(f"Extraindo campos com IA para o informe {idx+1}..."):
                campos = extract_fields_llm(document_text)
            st.session_state[cache_key] = campos
        else:
            campos = st.session_state[cache_key]

        # Blocos organizados por seções
        if campos:
            st.markdown("#### 1. Fonte Pagadora")
            campos['fonte_pagadora'] = st.text_input("Nome Empresarial", campos.get('fonte_pagadora', ''), key=f"fonte_pagadora_{idx}")
            campos['cnpj'] = st.text_input("CNPJ", campos.get('cnpj', ''), key=f"cnpj_{idx}")

            st.markdown("#### 2. Beneficiário dos Rendimentos")
            campos['nome'] = st.text_input("Nome", campos.get('nome', ''), key=f"nome_{idx}")
            campos['cpf'] = st.text_input("CPF", campos.get('cpf', ''), key=f"cpf_{idx}")

            st.markdown("#### 3. Rendimentos Tributáveis Recebidos de Pessoa Jurídica")
            campos['valor_rendimentos'] = st.text_input("Valor dos Rendimentos", str(campos.get('valor_rendimentos', '')), key=f"valor_rendimentos_{idx}")
            campos['contribuicao_previdenciaria'] = st.text_input("Contribuição Previdenciária Oficial", str(campos.get('contribuicao_previdenciaria', '')), key=f"contrib_previd_{idx}")
            campos['valor_irrf'] = st.text_input("Imposto de Renda Retido na Fonte", str(campos.get('valor_irrf', '')), key=f"valor_irrf_{idx}")

            st.markdown("#### 4. Rendimentos Isentos e Não Tributáveis")
            campos['rendimentos_isentos'] = st.text_input("Parcela isenta de aposentadoria", str(campos.get('rendimentos_isentos', '')), key=f"rend_isentos_{idx}")

            st.markdown("#### 5. Informações Complementares")
            campos['tipo_rendimento'] = st.text_input("Tipo de rendimento", campos.get('tipo_rendimento', ''), key=f"tipo_rend_{idx}")

            informes_extraidos.append(campos)
        else:
            st.warning(f"Falha ao extrair campos do informe {idx+1}. Revise o texto ou preencha manualmente.")

    # Download do XML consolidado (não reprocessa nada! só usa a lista pronta)
    if informes_extraidos:
        xml_data = generate_dirpf_xml_multi(informes_extraidos)
        st.download_button(
            label="⬇️ Baixar XML consolidado para DIRPF",
            data=xml_data,
            file_name="dirpf_informes_consolidado.xml",
            mime="application/xml"
        )

st.info("O sistema consolida todos os informes do mesmo CPF em um único contribuinte no XML. O processamento roda só uma vez por arquivo. O download é instantâneo!")

