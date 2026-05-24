import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

async def main():
    load_dotenv()

    config = {
        "mcpServers": {
            "http": {
                "url": "http://localhost:8000/sse"
            }
        }
    }

    client = MCPClient.from_dict(config)
    
    llm = ChatOpenAI(model="gpt-4o")
    
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    # ✅ ESCOLHA: texto ou imagem
    tipo = "imagem"  # ou "texto"

    if tipo == "texto":
        conteudo = "Parabéns! Você ganhou um prêmio especial. Clique aqui para resgatar."
    else:
        conteudo = "https://idec.org.br/sites/default/files/images/golpe_do_whatsapp.png"  # link público de imagem

    mensagem = f"Utilize a ferramenta analisar_mensagem_conteudo com tipo='{tipo}' e conteúdo='{conteudo}'"
    
    print("🔍 Enviando para análise...")
    resultado = await agent.run(mensagem)
    print("📝 Resultado:")
    print(resultado)

if __name__ == "__main__":
    asyncio.run(main())
