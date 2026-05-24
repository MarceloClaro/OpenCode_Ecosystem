import streamlit as st
import requests
import json
import os

API_URL = "http://127.0.0.1:8000"
filename = "dataset.json"

st.title("Gerador de Dataset - Qwen2.5-1M")
st.write("Uma ferramenta para garar datasets de treinamento de modelos.")


# Upload do PDF
st.sidebar.header("📂 Enviar Documento PDF")
uploaded_file = st.sidebar.file_uploader("Selecione um arquivo PDF", type=["pdf"])

# Variável global para armazenar o texto extraído
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = None

if uploaded_file and st.sidebar.button("Enviar PDF"):
    try:
        files = {"file": (uploaded_file.name, uploaded_file.read(), "application/pdf")}
        response = requests.post(f"{API_URL}/upload_pdf/", files=files)
        
        if response.status_code == 200:
            st.session_state.extracted_text = response.json().get("extracted_text", "")
            st.sidebar.success("Texto extraído com sucesso!")
        else:
            st.sidebar.error(f"Erro ao processar o PDF: {response.text}")
    except Exception as e:
        st.sidebar.error(f"Ocorreu um erro inesperado: {str(e)}")

example = st.text_area("Forneça um exemplo de registro formatado:")
number_records = st.number_input("Forneça o número de registros:", min_value=1, step=1)

if st.button("Gerar Dataset"):
    if example and number_records and st.session_state.extracted_text:
        try:
            response = requests.post(
                f"{API_URL}/datasetGenerate/",
                json={
                    "example": example,
                    "numberRecords": number_records,
                    "extracted_text": st.session_state.extracted_text
                }
            )

            if response.status_code == 200:
                dataset = response.json().get("response", [])

                if not isinstance(dataset, list):
                    dataset = [dataset]

                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(dataset, f, ensure_ascii=False, indent=4)
                
                st.success(f"Dataset gerado com sucesso! {len(dataset)} registros criados.")
                st.json(dataset)

                with open(filename, "rb") as file:
                    st.download_button("Baixar Dataset como JSON", data=file, file_name="dataset.json", mime="application/json")
            else:
                st.error(f"Erro ao gerar o dataset: {response.text}")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {str(e)}")
    else:
        st.error("Por favor, preencha todos os campos antes de gerar o dataset.")
