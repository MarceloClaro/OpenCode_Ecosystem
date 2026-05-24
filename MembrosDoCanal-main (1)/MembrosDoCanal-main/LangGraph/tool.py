import os
os.environ["TAVILY_API_KEY"] = "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"

from langchain_community.tools.tavily_search import TavilySearchResults

tool = TavilySearchResults(max_results=2)
tools = [tool]
print(tool.invoke("Quem foi Pelé?"))