import pytesseract
import re
import os
import cv2
import numpy as np
import csv
from PIL import Image, ImageEnhance
from groq import Groq
import streamlit as st
import pandas as pd

# Definir o idioma como português para o Tesseract
custom_config = r'--oem 3 --psm 3 -l por'

# Função para pré-processar a imagem (melhoria do contraste e binarização)
def preprocess_image(image_path):
    image = Image.open(image_path)
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(2)  # Aumenta o contraste
    # Converte para escala de cinza e aplica binarização
    image_cv = cv2.cvtColor(np.array(enhanced_image), cv2.COLOR_RGB2GRAY)
    _, binary_image = cv2.threshold(image_cv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(binary_image)

# Função para corrigir erros comuns de OCR
def correct_ocr_errors(text):
    corrections = {
        "B0": "80",
        "BO3": "803",
        "B03": "803",
        "O0": "00",
        "1O": "10",
        "Ti": "11",
        "o ": "0",
        "1 ": "1",
        "4 ": "4",
        "14:1.": "14/1.",
    }
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    return text

# Função para extrair o CNPJ com regex ajustada para capturar CNPJs mesmo com erros
def extract_cnpj(text):
    # Regex mais tolerante a erros, permitindo espaços ou caracteres incorretos
    cnpj_pattern = r'\b\d{2}\s*\.?\s*\d{3}\s*\.?\s*\d{3}\s*/?\s*\d{4}\s*-?\s*\d{2}\b'
    cnpjs = re.findall(cnpj_pattern, text)
    return [re.sub(r'\s+', '', cnpj) for cnpj in cnpjs]  # Remove os espaços em branco

def extract_valor_total(text):
    valor_pattern = r'\b\d+,\d{2}\b'
    return re.findall(valor_pattern, text)

def extract_data(text):
    date_pattern = r'\b\d{2}/\d{2}/\d{4}\b'
    return re.findall(date_pattern, text)

def process_cupom(output_csv):
    # Criar ou abrir o arquivo CSV para escrita
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Escrever o cabeçalho do CSV
        writer.writerow(['CNPJ', 'Valor Total', 'Data'])
        # Iterar sobre todos os arquivos no diretório de imagens
        for filename in os.listdir("./cupom_fiscal"):
            if filename.endswith('.jpg'):
                
                # Obter o caminho completo do arquivo jpg
                jpg_path = os.path.join("./cupom_fiscal", filename)
                        
                # Pré-processamento da imagem
                processed_image = preprocess_image(jpg_path)
                
                # Extrair texto da imagem
                extracted_text = pytesseract.image_to_string(processed_image, config=custom_config)
                corrected_text = correct_ocr_errors(extracted_text)
                        
                # Extrair CNPJ usando a função ajustada
                cnpj = extract_cnpj(corrected_text)
                print(cnpj)
                valor = extract_valor_total(corrected_text)
                print(valor)
                data = extract_data(corrected_text)
                print(data)                                 
                
                # Escrever dados no CSV
                if cnpj:
                    writer.writerow([cnpj[0], valor[0], data[0]])
                else: 
                    extracted_text = pytesseract.image_to_string(processed_image, config=custom_config)
                    cnpj = extract_cnpj(extracted_text)
                    writer.writerow([cnpj[0], valor[0], data[0]])                
               
# Especificar o nome do arquivo de saída CSV
output_csv = 'Pagamentos.csv'
process_cupom(output_csv)

def ler_csv(caminho_arquivo):
    registros = []
    with open(caminho_arquivo, mode='r', encoding='utf-8') as arquivo_csv:
        leitor_csv = csv.reader(arquivo_csv)
        cabecalho = next(leitor_csv)  # Lê o cabeçalho do CSV
        for linha in leitor_csv:
            registros.append(dict(zip(cabecalho, linha)))
    return registros

# Chama a função para ler o CSV
registros = ler_csv(output_csv)

# Preparar o contexto com as informações extraídas do CSV
pagamentos_extraidos = [f"CNPJ: {registro['CNPJ']}, Valor Total: {registro['Valor Total']}, Data: {registro['Data']}" for registro in registros]

# Carrega API Groq
llm = Groq(
    api_key="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",
)

# Função para gerar a decisão
def generate_decision(questao, pagamentos):
    input_text = f"Questão do usuário: {questao}\n\nPagamentos: {' '.join(pagamentos)}"
    
    result = llm.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "Você é um assistente financeiro que fornece respostas em português para a questão do usuário."
        },
        {
            "role": "user",
            "content": input_text,
        }
    ],
    model="llama3-8b-8192",
    )

    return result.choices[0].message.content

# Função para converter a lista `pagamentos_extraidos` em um DataFrame do pandas
def processar_pagamentos(pagamentos_extraidos):
    dados = []
    for pagamento in pagamentos_extraidos:
        partes = pagamento.split(", ")
        cnpj = partes[0].replace("CNPJ: ", "")
        valor_total = partes[1].replace("Valor Total: ", "")
        data = partes[2].replace("Data: ", "")
        dados.append({"CNPJ": cnpj, "Valor Total": valor_total, "Data": data})
    return pd.DataFrame(dados)

process_cupom(output_csv) 
# Converte a lista em um DataFrame
df_pagamentos = processar_pagamentos(pagamentos_extraidos)

# Frontend do Streamlit
st.title("Assistente de Controle de gastos")

# Certifique-se de que a pasta 'cupom_fiscal' exista
if not os.path.exists("cupom_fiscal"):
    os.makedirs("cupom_fiscal")

uploaded_files = st.file_uploader("Envie as imagens dos cupons fiscais", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Armazenar cada imagem na pasta 'cupom_fiscal'
        file_path = os.path.join("cupom_fiscal", uploaded_file.name) 
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())              

    with st.spinner('Processando os cupons fiscais'):
        process_cupom(output_csv)   
    st.success("Done!")    

questao = st.text_input("Faça uma pergunta sobre seus pagamentos")
if st.button("Enviar"):
    # Exibe o DataFrame como uma tabela no Streamlit
    st.title("Extratos de Pagamentos Extraídos")
    st.table(df_pagamentos) 
    response = generate_decision(questao, pagamentos_extraidos)
    st.write("Resposta do Assistente:")
    st.write(response)

