import streamlit as st
import os

# Definir a chave da API do OpenAI (considerar uma forma segura de gerenciar essa chave em produção)
os.environ["OPENAI_API_KEY"] = "sua chave aqui"

from crewai import Crew
from tasks import Tasks
from agents import Agents

# Inicializar tarefas e agentes
tasks = Tasks()
agents = Agents()

# Título do app no Streamlit
st.title("Token Build AI")

# Formulário para coletar informações sobre o token
with st.form("token_form"):
    token_name_supply = st.text_input("Enter the name of the Token, blockchain platform and the total supply:", "TokenName, Blockchain platform name, 1000000")
    submitted = st.form_submit_button("Build Token")

    if submitted:
        # Extrair nome do token e total de suprimento do input
        token_instruction = token_name_supply

        # Criar Agentes
        senior_engineer_agent = agents.senior_engineer_agent()
        qa_engineer_agent = agents.qa_engineer_agent()

        # Criar Tarefas
        code_game = tasks.code_task(senior_engineer_agent, token_instruction)
        review_game = tasks.review_task(qa_engineer_agent, token_instruction)

        # Criar equipe responsável pela cópia
        crew = Crew(
            agents=[
                senior_engineer_agent,
                qa_engineer_agent,		
            ],
            tasks=[
                code_game,
                review_game		
            ],
            verbose=True
        )

        tokenBuildAI = crew.kickoff()

        # Mostrar resultados
        st.subheader("Result")
        st.write("Final code for the token:")
        st.code(tokenBuildAI)
