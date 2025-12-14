# tools/book_airbnb.py
import requests
from langchain.tools import tool


# 7️⃣ Réservation Airbnb
@tool(description="Run reservation for airbnb")
def book_airbnb(listing_id: str) -> str:
    return f"Réservation Airbnb {listing_id} confirmée !"
