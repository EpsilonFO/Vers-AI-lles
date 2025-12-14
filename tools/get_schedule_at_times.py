# tools/get_schedule_at_times.py
import pandas as pd
from langchain.tools import tool


@tool(description="Get metro schedule")
def get_schedules_at_time(
    stop_id: str, line_id: str, transport_type: str, hour: str
) -> str:
    """
    stop_id: l'arrêt RATP
    line_id: numéro de ligne
    transport_type: metro, rer, bus, tram
    hour: format "HH:MM"
    """
    # Fichier GTFS téléchargé
    df = pd.read_csv(f"gtfs/{transport_type}_stop_times.csv")

    # Filtrer par stop et ligne
    df_filtered = df[(df["stop_id"] == stop_id) & (df["trip_id"].str.contains(line_id))]

    # Filtrer par heure
    df_filtered = df_filtered[df_filtered["departure_time"].str.startswith(hour)]

    if df_filtered.empty:
        return (
            f"Aucun passage trouvé pour {transport_type} {line_id} à {stop_id} à {hour}"
        )

    horaires = ", ".join(df_filtered["departure_time"].tolist())
    return f"Passages pour {transport_type} {line_id} à {stop_id} à {hour} : {horaires}"
