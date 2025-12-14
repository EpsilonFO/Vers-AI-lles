# tools/search_train.py
import requests
from langchain.tools import tool


# 4️⃣ SNCF recherche itinéraire
@tool(description="Search Train")
def search_train(from_station: str, to_station: str, date: str, time: str) -> str:
    # API SNCF ou simulation
    return f"Train simulé {from_station} → {to_station} à {time} le {date}"
