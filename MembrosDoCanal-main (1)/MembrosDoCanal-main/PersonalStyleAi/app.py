import json
import streamlit as st
from crewai import Agent, Task, Crew
from crewai_tools import BaseTool, tool
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverSinglestepScheduler
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import os

#os.environ["OPENAI_API_KEY"] = "NA"

#llm = ChatOpenAI(
#    model = "llama3",
#    base_url = "http://localhost:1234/v1")


# Chave da API do Google
google_api_key = "sua chave aqui"

# Define o LLM como gemini pro
llm = ChatGoogleGenerativeAI(
    model="gemini-pro", verbose=True, temperature=0.1, google_api_key=google_api_key
)

# Variável global para armazenar o perfil do usuário
global user_profile
user_profile = ""

# Função para atualizar o perfil do usuário
def atualizar_perfil_usuario(descricao):
    global user_profile
    user_profile = descricao
    with open("perfil_usuario.json", "w") as perfil_file:
        json.dump({"descricao": descricao}, perfil_file)

# Função para carregar o perfil do usuário
def carregar_perfil_usuario():
    global user_profile
    try:
        with open("perfil_usuario.json", "r") as perfil_file:
            user_profile = json.load(perfil_file)["descricao"]
    except FileNotFoundError:
        user_profile = ""

@tool("Generate image")
def generate_image(prompt: str, output_path: str = "output.png"):
    """
    Gera uma imagem baseada no prompt fornecido e salva no caminho especificado.

    Args:
        prompt (str): O prompt para gerar a imagem.
        output_path (str): O caminho onde a imagem será salva.
    """
    # Carregar o modelo.
    pipe = StableDiffusionXLPipeline.from_pretrained("sd-community/sdxl-flash", torch_dtype=torch.float16, variant="fp16").to("cuda")

    # Garantir que o scheduler use "trailing" timesteps.
    pipe.scheduler = DPMSolverSinglestepScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")

    # Gerar a imagem.
    image = pipe(prompt, num_inference_steps=7, guidance_scale=3).images[0]

    # Salvar a imagem.
    image.save(output_path)

@tool("Obter roupas do catálogo")
def extrair_roupas_catalogo() -> str:
    """
    Extrai e retorna as roupas do catálogo.

    Returns:
        str: Os itens masculinos e femininos do catálogo.
    """
    with open("catalogo.json", 'r') as arquivo:
        catalogo = json.load(arquivo)
        
    itens_masculinos = catalogo['itens_masculinos']
    itens_femininos = catalogo['itens_femininos']
    
    return itens_masculinos, itens_femininos

@tool("Obter o perfil do usuário")
def obter_perfil_usuario() -> str:
    """
    Retorna o perfil do usuário.

    Returns:
        str: A descrição do perfil do usuário.
    """
    carregar_perfil_usuario()
    return user_profile

# Criação dos Agentes
personalStyle = Agent(
    role='Você é especialista em moda e personal style',
    goal='Você deve fornecer um look personalizado de acordo com o perfil da pessoa e roupas disponíveis no catálogo, em seguida crie uma imagem do look',
    verbose=True,
    backstory=(
        "Como especialista em moda você sabe qual é a combinação de itens de roupa que "
        "são adequadas a personalidade de uma pessoa. Você é capaz de criar looks personalizados "
        "seguindo as tendâncias da moda."
    ),
    allow_delegation=False,
    llm=llm
)

# Definição das Tarefas
personalStyle_task0 = Task(
    description="Obter o perfil do usuário.",
    expected_output='uma descrição de quem é o usuário e quais são os seus interesses',
    tools=[obter_perfil_usuario],
    agent=personalStyle,
)

personalStyle_task1 = Task(
    description="Obter os dados do catálogo de roupas.",
    expected_output='Os dados das roupas.',
    tools=[extrair_roupas_catalogo],
    agent=personalStyle,
)

personalStyle_task2 = Task(
    description="Gera uma imagem do look que foi criado.",
    expected_output='um arquivo output.png que possui a imagem do look',
    tools=[generate_image],
    context=[personalStyle_task0, personalStyle_task1],
    agent=personalStyle,
)

# Execução do Crew
def executar_crew():
    crew = Crew(
        agents=[personalStyle],
        tasks=[personalStyle_task0, personalStyle_task1, personalStyle_task2]
    )
    result = crew.kickoff()
    return result

# Interface com Streamlit
st.title("AI Personal Stylist")
st.header("Descreva seu perfil e interesses:")

descricao = st.text_area("Descrição do perfil", user_profile)

if st.button("Cadastrar Perfil"):
    atualizar_perfil_usuario(descricao)
    st.success("Perfil cadastrado com sucesso!")

if st.button("Executar Estilista Pessoal"):
    with st.spinner("Gerando o look..."):
        resultado = executar_crew()
        st.write("Resultado:", resultado)
        st.image("output.png")

if __name__ == "__main__":
    carregar_perfil_usuario()

