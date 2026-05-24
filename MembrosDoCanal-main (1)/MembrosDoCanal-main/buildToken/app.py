import streamlit as st
from crewai import Crew, Process
from tasks import Tasks
from agents import Agents

# Inicializar tarefas e agentes
tasks = Tasks()
agents = Agents()

# Título do app no Streamlit
st.title("Token Build AI")
st.write("ATENÇÃO! É um protótipo apenas para FINS DE ESTUDO NÃO DEVE SER USADO PARA FINS COMERCIAIS")

# Formulário para coletar informações sobre o token
with st.form("token_form"):
    # Campos de entrada separados para cada informação
    token_name = st.text_input("Nome do Token:", "AI Token")
    token_symbol = st.text_input("Símbolo do Token:", "AIT")
    blockchain_platform = st.text_input("Nome da Plataforma Blockchain:", "Binance Smart Chain")
    total_supply = st.text_input("Total Supply:", "1000000")
    
    submitted = st.form_submit_button("Build Token")

    if submitted:
        # Preparar a instrução do token com as informações coletadas
        token_instruction = f"Nome: {token_name}, Símbolo: {token_symbol}, Plataforma: {blockchain_platform}, Total Supply: {total_supply}"

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
            verbose=True,
            process=Process.sequential,
        )

        tokenBuildAI = crew.kickoff()

        # Mostrar resultados
        st.subheader("Result")
        st.write("Final code for the token:")
        st.code(tokenBuildAI)
