# 1. Imports and API setup
from groq import Groq
import base64
import streamlit as st
from tavily import TavilyClient
import pyttsx3


client = Groq(
    api_key="coloque sua chave aqui",
)

llava_model = 'llava-v1.5-7b-4096-preview'
llama31_model = 'llama-3.1-70b-versatile'

#Instantiating your TavilyClient
tavily_client = TavilyClient(api_key="coloque sua chave aqui")


# Inicializar o mecanismo de síntese de voz
tts_engine = pyttsx3.init()


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


def search_internet(query):   
   #Executing the search query and getting the results
    content = tavily_client.search(query, max_foreign=10, search_depth="advanced")["results"]
    return content


# 4. Short story generation function
def analyzer_generation(client, content, food):
    chat_completion = client.chat.completions.create(
                                  
        
        messages=[
            {
                "role": "system",
                "content":  f'You are a food and nutrition expert. '\
                            f'Your sole purpose is to analyze the food and classify, based on its content and the provided food, whether it has a high, medium, or low glycemic index. Note: Write in Portuguese.'\
                       
            },
            {
                "role": "user",
                        "content": f'Information: """{content}"""\n\n' \
                                f'Using the above information, answer the following'\
                                f'query: "{food}" it food has a high, medium, or low glycemic index?',
                               
            }
        ],
        model=llama31_model
    )
    
    return chat_completion.choices[0].message.content

# 5. Streamlit app
def main():      
        
    col1, col2, col3 = st.columns([4, 5, 1])
    col1.image("images.jpg", width=250)
    col2.title("Glycemic Food Analyzer",  anchor="right")    
        
    st.write("Conheça o Glycemic Food Analyzer, um assistente inteligente que analisa o alimento e informa qual é o nível glicemico do alimento.")    

    
    uploaded_file = st.file_uploader("Carregue uma imagem (png ou jpg)", type=["png", "jpg"])

    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.read()
        base64_image = base64.b64encode(bytes_data).decode('utf-8')

        prompt = '''
        Describe this image in detail, including the appearance of the object(s).
        '''
        image_description = image_to_text(client, llava_model, base64_image, prompt)      
        
        query = "What are the glycemic indexes of the foods?"
        content = search_internet(query)
       
        st.write("\n--- Análise do Alimento ---")
        food_description = analyzer_generation(client, content, image_description)
        st.write(food_description)
        tts_engine.say(food_description)
        tts_engine.runAndWait()

       

if __name__ == "__main__":
    main()