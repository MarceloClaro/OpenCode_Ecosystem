import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from groq import Groq
from streamlit_geolocation import streamlit_geolocation 
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import time

client = Groq(
    api_key="sua chave aqui",
)

# Carrega o DataFrame de promoções
promotions_df = pd.read_csv("promotions.csv")

# Função para obter a localização do usuário
def get_user_location():
    try:
        location = get_geolocation()
        
        time.sleep(9)
       
        latitude = location['coords']['latitude']
        longitude = location['coords']['longitude']

        return latitude, longitude
    except Exception as e:
        st.write(f"Aguarde um pouco...: {e}")
        return None, None
    

# Função para encontrar promoções
def find_promotions():
    promotions = []
    for index, row in promotions_df.iterrows():
        promotions.append(row)
    return promotions


# Função para criar o mapa com folium
def create_map(user_latitude, user_longitude, nearby_promotions):
    try:
        st.subheader("Mapa de Ofertas")
        # Cria o mapa centrado na localização do usuário
        promo_map = folium.Map(location=[user_latitude, user_longitude], zoom_start=12)

        # Adiciona um marcador para a localização do usuário (com uma cor diferente)
        folium.Marker(
            location=[user_latitude, user_longitude],
            popup="Sua Localização",
            icon=folium.Icon(color="red", icon="user"),
        ).add_to(promo_map)

        # Adiciona marcadores para promoções
        for _, promotion in nearby_promotions.iterrows():
            folium.Marker(
                location=[promotion["latitude"], promotion["longitude"]],
                popup=f"{promotion['product']} em {promotion['store']} ({promotion['discount']}% de desconto)",
                icon=folium.Icon(color="blue", icon="shopping-cart"),
            ).add_to(promo_map)

        return promo_map
    except Exception as e:
        st.error(f"Tente novamente carregar a página")
        return None

# Função para o chat com o LLM
def chat_with_llm(user_latitude, user_longitude, promotions):
    # Inicia o chat
    st.subheader("Chat com o Especialista em Promoções")
    user_input = st.text_input("Digite a sua pergunta sobre ofertas:")
    
    # Formata as promoções próximas para o prompt do LLM
    promotions_str = "\n".join(
        f"Promoção {i+1}: {row['product']} em {row['store']} cujo endereço é: {row['endereco']} ({row['discount']}% de desconto)"
        for i, row in enumerate(promotions)
    )

    # Processa a pergunta do usuário
    if user_input:
        # Cria o prompt para o LLM
        prompt = f"""
        Você é um especialista em recomendação de produtos baseado em promoções.Deve responder somente perguntas sobre ofertas e promoções.
        Promoções próximas:
        {promotions_str}
        Um usuário em ({user_latitude}, {user_longitude}) fez a seguinte pergunta:
        {user_input}
        
        Responda à pergunta do usuário de forma útil e informativa.
        """
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é especialista em recomendação de produtos baseado em promoções"},
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192",
        )
        
        # Exibe a resposta do LLM
        st.write(chat_completion.choices[0].message.content)

# Interface do Streamlit
st.title("OfertasBot")
st.write("O OfertasBot, tem o objetivo de se tornar o Waze das ofertas e promoções.")
st.write("O seu novo assistente pessoal para economizar em grande estilo! Com a inteligência do nosso chatbot, você receberá recomendações exclusivas de promoções e descontos em produtos que realmente interessam a você. Basta conversar com o OfertasBot e deixar que ele encontre as melhores ofertas em tempo real, de acordo com suas preferências e localização. Nunca foi tão fácil fazer compras inteligentes! Colabore com a comunidade adicionado ofertas.")
# Menu de opções
option = st.sidebar.selectbox("Selecione uma opção", ["Mapa", "Adicionar Promoção", "Chat com OfertasBot"])

# Executa a função correspondente à opção selecionada
if option == "Mapa":
    
    # Obtém a localização do usuário
    user_latitude, user_longitude = get_user_location()     
    # Cria o mapa interativo com Folium
    promo_map = create_map(float(user_latitude), float(user_longitude), promotions_df)
    # Exibe o mapa na interface Streamlit
    st_data = st_folium(promo_map, width=725)
    
elif option == "Adicionar Promoção":
    #user_latitude, user_longitude = get_user_location()
    st.subheader("Adicionar Nova Promoção")
    product = st.text_input("Produto")
    store = st.text_input("Loja")
    discount = st.number_input("Desconto (%)", min_value=0, max_value=100)
    
    st.write("Clique no botão para obter a localização:")
    geolocator = streamlit_geolocation()
    
    promotion_latitude = geolocator['latitude']
    promotion_longitude = geolocator['longitude']

    endereco = st.text_input("Forneça o Endereço algum ponto de referência")
    
    # Adiciona a nova promoção ao banco de dados
    if st.button("Adicionar"):
        new_promotion = {
            "product": product,
            "store": store,
            "discount": discount,
            "latitude": float(promotion_latitude),
            "longitude": float(promotion_longitude),
            "endereco":endereco,
        }
        promotions_df = pd.concat([promotions_df, pd.DataFrame([new_promotion])], ignore_index=True)
        promotions_df.to_csv("promotions.csv", index=False)
        st.success("Promoção adicionada com sucesso!")

elif option == "Chat com OfertasBot":
    # Obtém a localização do usuário
    #user_latitude, user_longitude = get_user_location()
    # Inicia o chat com o LLM
    user_latitude, user_longitude = get_user_location()

    chat_with_llm(float(user_latitude), float(user_longitude),find_promotions())



