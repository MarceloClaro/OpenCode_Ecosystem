from typing import Optional
from smolagents import CodeAgent, HfApiModel, tool

@tool
def get_travel_duration(start_location: str, destination_location: str, departure_time: Optional[int] = None) -> str:
    """Gets the travel time in car between two places.
    
    Args:
        start_location: the place from which you start your ride
        destination_location: the place of arrival
        departure_time: the departure time, provide only a `datetime.datetime` if you want to specify this
    """
    import googlemaps # All imports are placed within the function, to allow for sharing to Hub.
    import os

    gmaps = googlemaps.Client(os.getenv("GMAPS_API_KEY"))

    if departure_time is None:
        from datetime import datetime
        departure_time = datetime(2025, 1, 6, 11, 0)

    directions_result = gmaps.directions(
        start_location,
        destination_location,
        mode="transit",
        departure_time=departure_time
    )
    return directions_result[0]["legs"][0]["duration"]["text"]

agent = CodeAgent(tools=[get_travel_duration], model=HfApiModel(), additional_authorized_imports=["datetime"])

agent.run("Can you give me a nice one-day trip around Paris with a few locations and the times? Could be in the city or outside, but should fit in one day. I'm travelling only via public transportation.")
