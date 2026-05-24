# server.py
from fastmcp import FastMCP
import requests
from typing import List

CMC_API_KEY = "6efcc6cf-ae65-49d0-8a6a-8bfc77e374f3"

mcp = FastMCP("CoinMarketCap MCP 🔗")

BASE_URL = "https://pro-api.coinmarketcap.com/v1"
HEADERS = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': CMC_API_KEY,
}

@mcp.tool
def get_crypto_price(symbols: List[str]) -> str:
    """
    Retorna os preços em USD para os símbolos fornecidos (ex: BTC, ETH, SOL).
    """
    url = f"{BASE_URL}/cryptocurrency/quotes/latest"
    params = {
        'symbol': ','.join(symbols),
        'convert': 'USD',
    }

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        return f"Erro ao acessar CoinMarketCap: {response.status_code}"

    data = response.json().get("data", {})
    if not data:
        return "Nenhum dado retornado."

    result = []
    for symbol in symbols:
        coin = data.get(symbol.upper())
        if coin:
            name = coin['name']
            price = coin['quote']['USD']['price']
            result.append(f"{name} ({symbol.upper()}): ${price:,.2f}")
        else:
            result.append(f"{symbol.upper()}: não encontrado.")

    return "\n".join(result)

@mcp.tool
def get_crypto_info(symbol: str) -> str:
    """
    Retorna informações gerais sobre a moeda: nome, descrição, site, logo e data de adição.
    """
    url = f"{BASE_URL}/cryptocurrency/info"
    params = {
        'symbol': symbol.upper(),
    }

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        return f"Erro ao buscar informações: {response.status_code}"

    data = response.json().get("data", {}).get(symbol.upper())
    if not data:
        return f"Moeda {symbol.upper()} não encontrada."

    name = data.get("name", "N/A")
    description = data.get("description", "Sem descrição disponível.")
    logo = data.get("logo", "Sem logo.")
    website = data.get("urls", {}).get("website", ["N/A"])[0]
    date_added = data.get("date_added", "N/A")

    info = (
        f"🪙 {name} ({symbol.upper()})\n"
        f"🌐 Site: {website}\n"
        f"🖼️ Logo: {logo}\n"
        f"📅 Adicionada em: {date_added}\n"
        f"📘 Descrição: {description[:300]}{'...' if len(description) > 300 else ''}"
    )

    return info

if __name__ == "__main__":
    #mcp.run(transport="streamable-http", host="127.0.0.1", port=8001, path="/mcp")
    mcp.run(transport="sse", host="127.0.0.1", port=8001)
