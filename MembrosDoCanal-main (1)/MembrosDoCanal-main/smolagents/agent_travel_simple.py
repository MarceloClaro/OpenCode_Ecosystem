from typing import Optional
from datetime import datetime

from smolagents import CodeAgent, HfApiModel, tool

# Exemplo de dicionário com dados simulados de rotas
SIMULATED_ROUTES = {
    ("Paris", "Louvre Museum"): "15 minutes",
    ("Paris", "Chateau Versailles"): "45 minutes",
    ("Chateau Versailles", "Disneyland Paris"): "1 hour 30 minutes",
    ("Paris", "Notre Dame"): "10 minutes",
    ("Paris", "Eiffel Tower"): "25 minutes",
    ("Louvre Museum", "Arc de Triomphe"): "20 minutes",
    ("Arc de Triomphe", "Sacré-Cœur"): "30 minutes",
    ("Sacré-Cœur", "Disneyland Paris"): "1 hour 15 minutes",
    ("Disneyland Paris", "Fontainebleau"): "1 hour 45 minutes",
}

@tool
def get_travel_duration(
    start_location: str,
    destination_location: str,
    departure_time: Optional[datetime] = None
) -> str:
    """
    Gets the travel time between two places, based on simulated data.

    Args:
        start_location: The place from which you start your ride.
        destination_location: The place of arrival.
        departure_time: The departure time. If not provided,
            assume a default datetime.

    Returns:
        A string with the estimated travel time, for example "45 minutes".
    """
    # Caso não seja fornecido nenhum horário de partida, definimos um por padrão.
    if departure_time is None:
        departure_time = datetime(2025, 1, 6, 11, 0)
    
    # Montamos a tupla que representa a rota
    route_key = (start_location, destination_location)
    
    # Buscamos a duração no dicionário de dados simulados
    if route_key in SIMULATED_ROUTES:
        duration = SIMULATED_ROUTES[route_key]
    else:
        duration = "Route not found in simulated data."

    return duration

agent = CodeAgent(
    tools=[get_travel_duration],
    model=HfApiModel(),
    additional_authorized_imports=["datetime"]
)

if __name__ == "__main__":
    # Fazemos um teste simples
    result = agent.run(
        "Can you give me a nice one-day trip around Paris "
        "with a few locations and the times? Could be in the city "
        "or outside, but should fit in one day. I'm travelling only "
        "via public transportation."
    )
    print(result)
