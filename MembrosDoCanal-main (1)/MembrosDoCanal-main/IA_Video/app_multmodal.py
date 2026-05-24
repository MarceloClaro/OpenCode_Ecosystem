import streamlit as st 
import cv2
import base64
import os
import tempfile
from groq import Groq
from dotenv import load_dotenv
import os

# Carregar variáveis do arquivo .env
load_dotenv()

# Acessar a variável de ambiente
groq_api_key = os.getenv("GROQ_API_KEY")

if groq_api_key:
    print("Chave de API carregada com sucesso!")
else:
    print("Erro: Chave de API não encontrada.")

# OpenAI API key
client = Groq(
    api_key=groq_api_key,
)

# Função para criar diretório, caso não exista
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Função para extrair frames do vídeo e representar em base64
def process_video(video_path, seconds_per_frame=10):
    base64Frames = []
    
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    frames_to_skip = int(fps * seconds_per_frame)
    curr_frame = 0

    while curr_frame < total_frames - 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        curr_frame += frames_to_skip
    video.release()
   
    return base64Frames

# Função para converter imagem base64 para descrição de texto
def image_to_text(base64_image):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail, including the appearance of the object(s). Note: write in Portuguese."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }           
        ],
         model="llama-3.2-11b-vision-preview"
    )

    return chat_completion.choices[0].message.content

# Função para analisar o frame
def analyzer_generation(content, question):
    chat_completion = client.chat.completions.create(                                  
        
        messages=[
            {
                "role": "system",
                "content":  f'You are a video analyzer expert. '\
                            f'Its only objective is to analyze the video and based on its content answer the user question. Note: Write in Portuguese.'\
                       
            },
            {
                "role": "user",
                        "content": f'Information: """{content}"""\n\n' \
                                f'Using the above information, answer the following'\
                                f'question "{question}"',
                               
            }
        ],
        model='llama-3.2-11b-vision-preview'
    )
    
    return chat_completion.choices[0].message.content

# Interface Streamlit
st.title("Analizador de Vídeo com IA")

# Inicializando o estado da sessão para armazenar dados persistentes
if 'video_description' not in st.session_state:
    st.session_state['video_description'] = None
if 'base64Frames' not in st.session_state:
    st.session_state['base64Frames'] = []

# Carregamento de arquivo
uploaded_video = st.file_uploader("Envie o vídeo no formato MP4", type=["mp4"])

if uploaded_video is not None:
    # Criar o diretório 'videos' se não existir
    ensure_directory_exists("videos")

    # Salvar o vídeo no diretório 'videos/'
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4", dir="videos") as temp_file:
        temp_file.write(uploaded_video.read())
        video_file_path = temp_file.name

    if st.button("Processar Vídeo"):
        with st.spinner('Processando vídeo...'):
            st.session_state['base64Frames'] = process_video(video_file_path, seconds_per_frame=1)
            st.session_state['video_description'] = None  # Resetar a descrição ao reprocessar o vídeo

if st.session_state['base64Frames']:
    num_frames = len(st.session_state['base64Frames'])
    st.write(f"Quantidade de frames extraídos: {num_frames}")

    # Selecionar frame a ser processado
    frame_index = st.selectbox("Selecione o número do frame a ser processado:", range(num_frames))
    selected_frame = st.session_state['base64Frames'][frame_index]

    st.write(f"Frame Selecionado ({frame_index + 1}):")
    st.image(f"data:image/jpg;base64,{selected_frame}")

    if st.button("Gerar Descrição do Frame"):
        st.session_state['video_description'] = image_to_text(selected_frame)

if st.session_state['video_description']:
    st.write("Descrição do Frame:")
    st.write(st.session_state['video_description'])

    # Seção de Perguntas e Respostas
    st.write("Faça uma pergunta sobre o frame:")
    question = st.text_input("Sua pergunta:")
    
    if st.button("Obter Resposta"):
        if question:
            answer = analyzer_generation(st.session_state['video_description'], question)
            st.write("Resposta:")
            st.markdown(answer)
        else:
            st.warning("Por favor, insira uma pergunta antes de clicar em Obter Resposta.")
