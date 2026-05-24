import streamlit as st
from PIL import Image
from gradio_client import Client

# Nome do arquivo para armazenar o contador de acessos
contador_arquivo = "contador_acessos.txt"

# Função para ler o valor atual do contador de acessos
def ler_contador():
    try:
        with open(contador_arquivo, "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0

# Função para atualizar e salvar o contador de acessos
def atualizar_contador():
    total_acessos = ler_contador()
    total_acessos += 1
    with open(contador_arquivo, "w") as file:
        file.write(str(total_acessos))
    return total_acessos

image = Image.open('cf.png')

# Título da aplicação Streamlit
st.title("Chatbot da Constituição do Brasil")
st.image('cf.png', caption='Constituição')

# Criar um campo de entrada de texto para a pergunta
question = st.text_input("Digite sua pergunta:")

# Botão para fazer a previsão
if st.button("Enviar"):
    # Incrementar e obter o contador de acessos
    total_acessos = atualizar_contador()

    # Criar uma instância do cliente Gradio
    client = Client("FabioSantos/chatbot_cf", hf_token="seu token HF aqui")
    
    # Fazer uma previsão com a pergunta inserida
    result = client.predict(question, api_name="/predict")
    
    # Exibir a resposta
    st.write("Resposta do Chatbot:")
    st.write(result)

# Exibir o número total de acessos
st.write(f"Número total de acessos: {ler_contador()}")

# Nota explicativa
st.markdown("*Desenvolvido por Prof.Dr.Fabio Santos (fssilva@uea.edu.br)*")

