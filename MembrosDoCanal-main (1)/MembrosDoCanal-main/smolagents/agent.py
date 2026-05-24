from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel

agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=HfApiModel())
#Quantos segundos levaria para um leopardo correr a toda velocidade pela Pont des Arts?
agent.run("How many seconds would it take for a leopard at full speed to run through Pont des Arts?")