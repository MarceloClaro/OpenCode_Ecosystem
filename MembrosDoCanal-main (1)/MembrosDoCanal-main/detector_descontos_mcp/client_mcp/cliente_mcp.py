import asyncio
import base64
from mcp_use import MCPClient, MCPAgent
from langchain_openai import ChatOpenAI
import fitz  # PyMuPDF
# Insira sua chave da OpenAI aqui
OPENAI_API_KEY = ""

async def main():
    config = {
        "mcpServers": {
            "http": {
                "url": "http://localhost:8000/mcp"
            }
        }
    }

    client = MCPClient.from_dict(config)
    
    llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)

    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=30
    )

    pdf_path = input("Informe o caminho do extrato bancário em PDF: ")

    # Realiza OCR localmente (já que não pode usar files=)
    texto = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            texto += page.get_text()

    comando = f"Avalie os descontos do seguinte extrato bancário:\n\n{texto}"

    result = await agent.run(comando)

    print("\n✅ Resultado final:\n")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())


