# TODO: link with trajectory
# tools/google_maps_tool.py
from langchain.tools import tool
import urllib.parse


@tool(description="Get map")
def google_maps_route(origin: str, destination: str, mode: str = "transit") -> str:
    """
    Génère un lien Google Maps pour un itinéraire.

    origin: point de départ (ex: "Gare de Lyon, Paris")
    destination: point d'arrivée (ex: "Château de Versailles")
    mode: transit / driving / walking / bicycling (défaut: transit)
    """
    base_url = "https://www.google.com/maps/dir/?api=1"

    # Encodage pour URL
    origin_enc = urllib.parse.quote(origin)
    destination_enc = urllib.parse.quote(destination)

    # Construire le lien
    url = f"{base_url}&origin={origin_enc}&destination={destination_enc}&travelmode={mode}"

    return f"Voici le lien pour votre trajet : {url}"
