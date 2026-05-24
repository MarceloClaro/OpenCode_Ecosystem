# 1. Imports and API setup
from groq import Groq
import base64
import streamlit as st
import pandas as pd

client = Groq(
    api_key="sua chave",
)

llava_model = 'llava-v1.5-7b-4096-preview'
llama31_model = 'llama-3.1-70b-versatile'

# 2. Image encoding
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# 3. Image to text function
def image_to_text(client, model, base64_image, prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model=model
    )

    return chat_completion.choices[0].message.content

# 4. Short story generation function
def game_generation(client, image_description, age, support_level, stimulus_type):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"Suggest a safe game for a child of {age} years old, with support level {support_level} and focus on {stimulus_type}. The game should use the object described in the image and should not use objects that are dangerous for children, for example, scissors, knives, toothpicks, electrical wires, any sharp object cannot be used. If the object is not dangerous, describe the game in the form of a step-by-step recipe. Note: Write in Portuguese.",
            },
            {
                "role": "user",
                "content": image_description,
            }
        ],
        model=llama31_model
    )
    
    return chat_completion.choices[0].message.content

# 5. Streamlit app
def main():
    st.image("autism.png", width=200)
    st.title("PlayBot - Gerador de Brincadeiras",  anchor="center")
    st.write("Conheça o PlayBot, um assistente inteligente que gera brincadeiras divertidas e educativas para crianças com TEA, utilizando objetos disponíveis em sua casa. Basta tirar uma foto dos itens e o PlayBot sugere atividades interativas e adaptadas às necessidades sensoriais, promovendo aprendizado e diversão de forma simples e prática!")    

    idade = st.number_input("Idade da criança:", min_value=1, max_value=12, step=1)
    nivel_suporte = st.selectbox("Nível de Suporte", ["Nível 1", "Nível 2", "Nível 3"])
    tipo_estimulo = st.selectbox("Tipo de Estimulo", ["Sensorial", "Coordenação motora", "Raciocinio", "Fala"])

    uploaded_file = st.file_uploader("Carregue uma imagem (png ou jpg)", type=["png", "jpg"])
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.read()
        base64_image = base64.b64encode(bytes_data).decode('utf-8')
        prompt = '''
        Describe this image in detail, including the appearance of the object(s).
        '''
        image_description = image_to_text(client, llava_model, base64_image, prompt)

        #st.write("\n--- Image Description ---")
        #st.write(image_description)

        st.write("\n--- Brincadeira ---")
        game_description = game_generation(client, image_description, idade, nivel_suporte, tipo_estimulo)
        st.write(game_description)

        # Save data to CSV
        data = {
            "Idade": idade,
            "Nível de Suporte": nivel_suporte,
            "Tipo de Estimulo": tipo_estimulo            
        }
        df = pd.DataFrame([data])
        df.to_csv("game_data.csv", mode='a', header=False, index=False)

if __name__ == "__main__":
    main()