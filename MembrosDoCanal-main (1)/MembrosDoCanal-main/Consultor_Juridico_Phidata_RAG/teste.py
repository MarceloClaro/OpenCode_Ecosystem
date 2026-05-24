from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.agent import Agent
from phi.vectordb.lancedb import LanceDb, SearchType
from phi.model.groq import Groq
from phi.embedder.sentence_transformer import SentenceTransformerEmbedder
# Load the knowledge base from a PDF
knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://www.gov.br/mj/pt-br/assuntos/seus-direitos/consumidor/Anexos/cdc-portugues-2013.pdf"],    
    vector_db=LanceDb(
        table_name="recipes",
        uri="tmp/lancedb",
        search_type=SearchType.vector,
        embedder=SentenceTransformerEmbedder(),
        #embedder=SentenceTransformerEmbedder(model="all-mpnet-base-v2",dimensions="768"),
    )
)
knowledge_base.load(recreate=False)
# Create the RAG agent
agent = Agent(
    model=Groq(id="llama-3.1-8b-instant"),
    knowledge=knowledge_base,  # Add the knowledge base to the agent
    show_tool_calls=True,
    markdown=True,
)
# Query the agent
agent.print_response("Quais são os direitos básicos do consumidor, de acordo com o Código de Defesa do Consumidor?", stream=True)
#agent.print_response("Quais são os direitos do consumidor em casos de atraso na entrega de produtos, de acordo com o Código de Defesa do Consumidor?", stream=True)
#agent.print_response("Qual é o dever do fornecedor de produtos e serviços potencialmente nocivos ou perigosos à saúde ou segurança, de acordo com o Código de Defesa do Consumidor?", stream=True)
