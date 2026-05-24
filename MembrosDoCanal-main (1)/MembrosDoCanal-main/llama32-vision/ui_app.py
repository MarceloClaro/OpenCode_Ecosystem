import base64
import io
from PIL import Image
import streamlit as st
from groq import Groq

# Inicialize o cliente Groq
client = Groq(api_key="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")

def encode_image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def get_ocr_output_from_image(image_base64: str, language: str, model: str = "llama-3.2-90b-vision-preview") -> str:
    """Envia uma imagem ao modelo Llama OCR e retorna o texto extraído e traduzido."""
    prompt = f"Traduza para o {language} o que está escrito na imagem. Não descreva a imagem, apenas traduza."
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                        },
                    },
                ],
            }
        ],
        model=model,
    )
    return chat_completion.choices[0].message.content

def ask_about_translation(question: str, translated_text: str, model: str = "llama-3.2-90b-vision-preview") -> str:
    """Permite ao usuário fazer perguntas sobre o texto traduzido sem alterar o texto original."""
    prompt = f"O texto traduzido é: '{translated_text}'. {question}"
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model=model,
    )
    return chat_completion.choices[0].message.content

# Interface do Streamlit
st.title("Bot Tradutor Multimodal e Multilíngue com LLama 3.2 - Vision")
st.write("Envie uma imagem para extrair e traduzir texto, e faça perguntas sobre o conteúdo traduzido.")

# Carregamento de imagem
uploaded_file = st.file_uploader("Escolha uma imagem...", type=["jpg", "jpeg", "png"])

# Seleção do idioma para tradução
language = st.selectbox("Escolha o idioma para tradução:", ["português", "inglês", "espanhol", "francês", "alemão"])

if uploaded_file is not None:
    # Exibe a imagem carregada
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagem carregada", use_container_width=True)

    # Converte a imagem para base64 e envia ao modelo OCR
    with st.spinner("Processando a imagem..."):
        base64_image = encode_image_to_base64(image)
        ocr_text = get_ocr_output_from_image(base64_image, language)

        # Armazena o texto traduzido original em uma variável de sessão, sem sobrescrever
        if 'translated_text' not in st.session_state:
            st.session_state['translated_text'] = ocr_text

    # Exibe o texto extraído e traduzido
    st.subheader("Texto extraído e traduzido:")
    st.write(st.session_state['translated_text'])

# Permite ao usuário fazer perguntas sobre o texto traduzido
if 'translated_text' in st.session_state:
    question = st.text_input("Faça uma pergunta sobre o texto traduzido:")
    if question:
        with st.spinner("Respondendo à sua pergunta..."):
            answer = ask_about_translation(question, st.session_state['translated_text'])
            st.subheader("Resposta:")
            st.write(answer)


