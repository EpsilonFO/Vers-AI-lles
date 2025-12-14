# tools/get_weather.py
import requests
from langchain.tools import tool
import os

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHER_API_KEY", "demo")


# Note: city weather can be either city from and to (Versailles)
@tool(description="Get weather")
def get_weather(city: str) -> str:
    """Returns weather conditions from OpenWeatherMap"""
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric",
        "lang": "fr",
    }
    r = requests.get(url, params=params)

    if r.status_code != 200:
        return f"Erreur: {r.text}"

    data = r.json()
    return f"À {data['name']}, il fait {data['main']['temp']}°C avec {data['weather'][0]['description']}."
