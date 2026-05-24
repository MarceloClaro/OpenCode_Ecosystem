import os
import streamlit as st
import google.generativeai as genai
from IPython.display import Markdown

# Configurar a API do Google Generative AI
genai.configure(api_key="coloque_sua_chave_aqui")

# Função para salvar o arquivo no diretório videos
def save_uploaded_file(uploaded_file):
    video_dir = "videos"
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)
    file_path = os.path.join(video_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# Função para resumir o vídeo e gerar um quiz
def summarize_and_generate_quiz(video_path):
    st.write(f"Uploading file: {video_path}...")
    
    # Upload do vídeo para a API
    video_file = genai.upload_file(path=video_path)
    st.write(f"Completed upload: {video_file.uri}")

    # Criar o prompt para resumo e quiz
    prompt = "Summarize this video. Then create a quiz with answer key based on the information in the video."

    # Escolher o modelo Gemini
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    # Fazer a solicitação de inferência ao modelo LLM
    st.write("Making LLM inference request...")
    response = model.generate_content([video_file, prompt], request_options={"timeout": 600})

    # Exibir a resposta do modelo
    return response.text

# Interface do Streamlit
st.title("Upload de Vídeo e Geração de Quiz")

# Input do usuário para fazer upload do vídeo
uploaded_file = st.file_uploader("Faça o upload de um vídeo", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # Salvar o arquivo no diretório 'videos'
    file_path = save_uploaded_file(uploaded_file)
    st.success(f"Arquivo salvo: {file_path}")

    # Botão para processar o vídeo
    if st.button("Processar vídeo"):
        # Chamar a função para resumir o vídeo e gerar o quiz
        with st.spinner("Processando o vídeo, por favor aguarde..."):
            result = summarize_and_generate_quiz(file_path)
            st.markdown(result)
