import requests
import json
from langchain.tools import tool

BASE_URL = "https://api-ratp.pierre-grimaud.fr/v4"

@tool("get_next_passages", return_direct=False)
def get_next_passages(query: str) -> str:
    """
    Obtenir les prochains passages d'un transport.
    Query doit être un JSON string du type :
    {"stop": "Châtelet", "line": "72", "transport_type": "bus"}
    """
    try:
        params = json.loads(query)
        stop = params.get("stop")
        line = params.get("line")
        transport_type = params.get("transport_type", "bus")
    except Exception as e:
        return f"Erreur parsing input JSON : {e}"

    url = f"{BASE_URL}/schedules/{transport_type}/{line}/{stop}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except Exception as e:
        return f"Erreur API RATP : {e}"

    data = resp.json()
    if "result" not in data or "schedules" not in data["result"]:
        return f"Aucun horaire disponible pour {transport_type} {line} à {stop}."

    schedules = data["result"]["schedules"]
    formatted = [f"{s.get('message')} vers {s.get('destination')}" for s in schedules]

    return f"Prochains passages pour {transport_type.upper()} ligne {line} à {stop} : " + "; ".join(formatted)
