from typing import Literal
from mcp.server.fastmcp import FastMCP
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client_openai = OpenAI()

mcp = FastMCP("GolpeDetector")


@mcp.tool()
async def analisar_mensagem_conteudo(conteudo: str) -> str:

    print(f"Conteúdo: {conteudo}")
   
    try:
        completion = client_openai.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "user",
                        "content": f"Você é um especialista em segurança digital. Detecte golpes, fraudes ou spam nesta mensagem de texto: \"{conteudo}\". Explique o porquê da classificação.",
                    }
                ],
                temperature=0.1,
            )
        return completion.choices[0].message.content.strip()

    except Exception as e:
        return f"[❗Erro técnico ao analisar a mensagem: {str(e)}]"

if __name__ == "__main__":
    print("🚀 Servidor FastMCP inicializando...")
    mcp.run(transport="sse")

