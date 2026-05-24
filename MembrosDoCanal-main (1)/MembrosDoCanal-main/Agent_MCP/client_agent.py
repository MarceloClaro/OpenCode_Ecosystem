# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import re

# Configurando o modelo com os parâmetros corretos
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key="coloque sua chave aqui"
)

server_params = StdioServerParameters(
    command="python",
    args=["product_server.py"],
)

def generate_pdf_report(question, answer, filename="product_report.pdf"):
    """
    Gera um relatório PDF com a pergunta e resposta do agente.
    """
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Adiciona a pergunta
    elements.append(Paragraph(f"<b>Pergunta:</b> {question}", styles['Normal']))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))
    
    # Processa a resposta para extrair a tabela
    if "|" in answer:
        # Extrai os dados da tabela da resposta
        table_data = []
        for line in answer.split('\n'):
            if '|' in line:
                # Remove espaços em branco extras e caracteres '|' das extremidades
                row = [cell.strip() for cell in line.split('|')[1:-1]]
                if row and not all(cell.startswith('-') for cell in row):
                    table_data.append(row)
        
        if table_data:
            # Cria a tabela
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(table)
    else:
        # Se não houver tabela, adiciona a resposta como texto normal
        elements.append(Paragraph(answer, styles['Normal']))
    
    # Gera o PDF
    doc.build(elements)
    print(f"\nRelatório PDF gerado com sucesso: {filename}")

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # Get tools
            tools = await load_mcp_tools(session) 
            
            # Mostrar as ferramentas disponíveis
            print("\nFerramentas disponíveis no MCP Server:")
            for i, tool in enumerate(tools, 1):
                print(f"{i}. {tool.name}: {tool.description}")
            print("\n" + "="*50 + "\n")
            
            # Create and run the agent
            agent = create_react_agent(model, tools)
            
            # Criando a mensagem de entrada
            question = "Quero uma lista de todos os produtos"
            
            # Executando o agente com o contexto correto
            agent_response = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
            
            # Extrair a resposta final do agente
            messages = agent_response['messages']
            final_message = messages[-1]  # Pega a última mensagem
            final_content = final_message.content if hasattr(final_message, 'content') else "Não foi possível obter uma resposta clara"
            
            # Imprimindo a resposta
            print(f"\nPergunta: {question}")
            print(f"Resposta: {final_content}")
            
            # Gerando o relatório PDF
            generate_pdf_report(question, final_content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
