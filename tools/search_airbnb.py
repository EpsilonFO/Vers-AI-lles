# tools/search_airbnb.py
import requests
from langchain.tools import tool


# 6️⃣ Airbnb recherche logement
@tool(description="Search Airbnb")
def search_airbnb(city: str, checkin: str, checkout: str, guests: int) -> str:
    return f"Logements Airbnb disponibles à {city} du {checkin} au {checkout} pour {guests} personnes."
