import streamlit as st
from PIL import Image
import torch
from transformers import AutoProcessor, LlavaForConditionalGeneration
import csv
import os

# Configurações iniciais
model_id = "xtuner/llava-phi-3-mini-hf"
csv_file = "dados_criancas.csv"

# Função para carregar o modelo e o processador
@st.cache_resource
def load_model_and_processor():
    model = LlavaForConditionalGeneration.from_pretrained(
        model_id, 
        torch_dtype=torch.float16, 
        low_cpu_mem_usage=True
    ).to(0)
    processor = AutoProcessor.from_pretrained(model_id)
    return model, processor

model, processor = load_model_and_processor()

# Função para salvar os dados em um CSV com codificação UTF-8
def save_to_csv(name, age, support_level, stimulus_type, file_path):
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Nome", "Idade", "Nível de Suporte", "Tipo de Estímulo"])
        writer.writerow([name, age, support_level, stimulus_type])

# Frontend usando Streamlit
st.title("Sugestão de Brincadeiras para Crianças Autistas")

st.write("Envie uma imagem de um objeto que você possui e personalize a sugestão de brincadeira.")

# Entrada do usuário para nome, idade, nível de suporte e tipo de estímulo
name = st.text_input("Nome da criança:", value="João")
age = st.number_input("Idade da criança:", min_value=1, max_value=18, value=6)
support_level = st.selectbox("Nível de suporte do autismo:", ["Leve", "Moderado", "Severo"])
stimulus_type = st.text_input("Tipo de estímulo:", value="Raciocínio, Sensorial, Fala, Coordenação Motora, Andar")

# Upload de imagem
uploaded_file = st.file_uploader("Envie uma imagem do objeto...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Exibe a imagem enviada
    raw_image = Image.open(uploaded_file)
    st.image(raw_image, caption='Imagem enviada', use_column_width=False)

    # Botão para gerar a resposta
    if st.button("Gerar Sugestão de Brincadeira"):
        with st.spinner("Processando..."):
            prompt = f"<|user|>\n<image>\nQual brincadeira segura você sugere e explica em forma de uma receita passo a passo que utiliza o objeto dessa imagem para {name}, uma criança de {age} anos com autismo de nível {support_level} que responde bem a estímulos {stimulus_type}?<|end|>\n<|assistant|>\n"
            inputs = processor(prompt, raw_image, return_tensors='pt').to(0, torch.float16)
            output = model.generate(**inputs, max_new_tokens=500, do_sample=False)
            suggestion = processor.decode(output[0][2:], skip_special_tokens=True)

        # Salvar os dados no CSV com codificação UTF-8
        save_to_csv(name, age, support_level, stimulus_type, csv_file)
        
        st.success("Sugestão de Brincadeira:")
        st.write(suggestion)

