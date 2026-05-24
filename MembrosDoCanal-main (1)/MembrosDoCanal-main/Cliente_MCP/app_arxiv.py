import asyncio
from flask import Flask, request, jsonify
from flask import render_template  
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

app = Flask(__name__)
# Parâmetros do servidor MCP (ajuste o caminho se necessário)
server_params = StdioServerParameters(
    command="python",
    args=["../server/server_arxiv.py"],
    env=None,
)

# Função assíncrona para consultar o MCP
async def search_arxiv(query):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            await load_mcp_tools(session)
            response = await session.call_tool("search_arxiv", arguments={"query": query})
          
            return response.model_dump()  
            

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Rota Flask para requisição HTTP
@app.route("/arxiv", methods=["GET"])
def arxiv_route():
    query = request.args.get("query")

    # Executa a função assíncrona
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(search_arxiv(query))

    #return jsonify(result)
    # Extrai os textos dos resultados
    texts = [item["text"] for item in result.get("content", [])]

    # Renderiza o template HTML com os artigos
    return render_template("arxiv_results.html", articles=texts)

if __name__ == "__main__":
    app.run(debug=True)

