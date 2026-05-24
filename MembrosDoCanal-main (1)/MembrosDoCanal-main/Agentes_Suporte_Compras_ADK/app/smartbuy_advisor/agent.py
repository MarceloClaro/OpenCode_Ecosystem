from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool, google_search

# 1. Agente de busca de opniões, avaliações, reclamações
def build_search_agent():
    return LlmAgent(
        name="ReviewSearcher",
        model="gemini-2.0-flash",
        description="Search for customer reviews, complaints and ratings on the web about a product or service. Use sites like reclameaqui.com.",
        tools=[google_search]
    )

# 2. Agente que analisa o sentimento geral das opiniões
def build_sentiment_analyzer():
    return LlmAgent(
        name="SentimentAnalyzer",
        model="gemini-2.0-flash",
        description="Analyzes customer feedback and summarizes sentiment into pros, cons, and red flags."
    )

# 3. Agente que toma decisão com base nos dados anteriores
def build_purchase_advisor(search_agent, sentiment_analyzer):
    return LlmAgent(
        name="PurchaseAdvisor",
        model="gemini-2.0-flash",
        instruction=(
            "Given the results of online reviews and sentiment analysis, provide a recommendation in portuguese language for the user. "
            "Include a final verdict: ✅RECOMENDADO / ⚠️CAUTELA / ❌NÂO RECOMENDADO. "            
            "If the number of the Cons outweigh the number of the Pros, the final verdict should be ❌NÂO RECOMENDADO."
            "Structure the response in: Summary, Pros, Cons, and Final Recommendation."
        ),
        tools=[
            agent_tool.AgentTool(agent=search_agent),
            agent_tool.AgentTool(agent=sentiment_analyzer)
        ]
    )


root_agent = build_purchase_advisor(build_search_agent(), build_sentiment_analyzer())

