# 1. Imports and API setup
from groq import Groq
import base64
import streamlit as st
import pandas as pd

client = Groq(
    api_key="sua chave aqui",
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
def analyzer_generation(client, image_description):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"You are a food and nutrition expert, you analyze Food by Photo: The user takes a photo of a plate of food, and the app describes the ingredients, possible calories, classify whether the food is healthy or unhealthy, and offers suggestions on how to make the meal healthier or more balanced. Note: Write in Portuguese.",
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
    st.image("images.jpg", width=200)
    st.title("FoodBot - Análisador de Alimentos",  anchor="center")
    st.write("Conheça o FoodBot, um assistente inteligente que o usuário tira uma foto de um prato de comida, e o app descreve os ingredientes, possíveis calorias, e oferece sugestões de como tornar a refeição mais saudável ou equilibrada.")    

    
    uploaded_file = st.file_uploader("Carregue uma imagem (png ou jpg)", type=["png", "jpg"])
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.read()
        base64_image = base64.b64encode(bytes_data).decode('utf-8')
        prompt = '''
        Describe this image in detail, including the appearance of the object(s).  Note: Write in Portuguese.
        '''
        image_description = image_to_text(client, llava_model, base64_image, prompt)

        #st.write("\n--- Image Description ---")
        #st.write(image_description)

        st.write("\n--- Análise do Alimento ---")
        food_description = analyzer_generation(client, image_description)
        st.write(food_description)

       

if __name__ == "__main__":
    main()