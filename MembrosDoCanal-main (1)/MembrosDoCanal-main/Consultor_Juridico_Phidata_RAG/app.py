import streamlit as st
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.agent import Agent, RunResponse
from phi.vectordb.lancedb import LanceDb, SearchType
from phi.model.groq import Groq
from phi.embedder.sentence_transformer import SentenceTransformerEmbedder

# Configuração da Página
st.set_page_config(page_title="Consulta ao CDC", layout="wide")

st.title("Consulta ao Código de Defesa do Consumidor (CDC)")
st.write("Este aplicativo permite consultar os direitos básicos do consumidor diretamente do CDC.")

# Inicialização do conhecimento
@st.cache_resource
def initialize_knowledge_base():
    knowledge_base = PDFUrlKnowledgeBase(
        urls=["https://www.gov.br/mj/pt-br/assuntos/seus-direitos/consumidor/Anexos/cdc-portugues-2013.pdf"],
        vector_db=LanceDb(
            table_name="recipes",
            uri="tmp/lancedb",
            search_type=SearchType.vector,
            embedder=SentenceTransformerEmbedder(),
        )
    )
    knowledge_base.load(recreate=False)
    return knowledge_base

@st.cache_resource
def initialize_agent(_knowledge_base):  # Use um sublinhado no argumento
    agent = Agent(
        model=Groq(id="llama-3.1-8b-instant"),
        knowledge=_knowledge_base,
        show_tool_calls=False,  # Desativa a exibição de chamadas de ferramentas
        markdown=True,
    )
    return agent

# Carregando o conhecimento e o agente
knowledge_base = initialize_knowledge_base()
agent = initialize_agent(knowledge_base)

# Entrada do usuário
st.header("Faça uma pergunta")
query = st.text_input("Digite sua pergunta sobre o CDC:")

if st.button("Consultar"):
    if query.strip():
        with st.spinner("Consultando o CDC..."):
            # Obtém a resposta do agente
            response: RunResponse = agent.run(query, stream=False)
            
            # Extrai o conteúdo da resposta
            final_response = response.content
            
            # Exibe a resposta no Streamlit
            st.success("Consulta concluída!")
            st.markdown("### Resposta:")
            st.write(final_response)
    else:
        st.error("Por favor, insira uma pergunta válida.")


