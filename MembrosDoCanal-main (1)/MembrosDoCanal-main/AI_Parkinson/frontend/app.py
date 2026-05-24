import streamlit as st
import requests

st.title("Ferramenta para Detecção de Doença de Parkinson")

uploaded_file = st.file_uploader("Carregar um vídeo", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # Exibe um spinner enquanto o vídeo é enviado e processado
    with st.spinner("Processando o vídeo... isso pode levar alguns minutos."):
        # Enviar o vídeo para o backend
        files = {"video": (uploaded_file.name, uploaded_file, "video/mp4")}
        response = requests.post("http://localhost:8000/upload_video/", files=files)
        
        if response.status_code == 200:
            st.success("Resumo gerado com sucesso!")
            # Exibir o resumo
            summary = response.json().get("summary")
            st.write("Resumo do Vídeo:")
            st.write(summary)
        else:
            st.error("Erro ao gerar resumo.")
