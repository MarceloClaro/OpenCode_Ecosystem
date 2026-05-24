import yfinance as yf
from google.adk.agents import Agent

def get_currency_exchange_rate(from_currency: str, to_currency: str):
    ticker = f"{from_currency.upper()}{to_currency.upper()}=X"  # Ex: USDBRL=X
    data = yf.Ticker(ticker)
    todays_data = data.history(period='1d')
    if not todays_data.empty:
        price = todays_data['Close'][0]
        return {
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "rate": price
        }
    else:
        return {"error": "Exchange rate not available."}

currency_agent = Agent(
    name="yahoo_currency_agent",
    model="gemini-2.0-flash",
    description="Agent that fetches currency exchange rates using Yahoo Finance data.",
    instruction="Always use the get_currency_exchange_rate tool to convert between currencies.",
    tools=[get_currency_exchange_rate],
)

root_agent = currency_agent
