"""Tool to search Versailles knowledge base using RAG."""

from langchain.tools import tool
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from rag.retriever import get_retriever


@tool(description="Search Versailles knowledge base for information")
def search_versailles_info(query: str) -> str:
    """
    Search the Versailles knowledge base for information about the château,
    gardens, tickets, opening hours, history, and practical information.

    Args:
        query: The search query (e.g., "horaires d'ouverture", "tarifs billets", "histoire galerie des glaces")

    Returns:
        Relevant information from the Versailles knowledge base
    """
    try:
        retriever = get_retriever()
        context = retriever.retrieve_with_context(query, k=3)

        if (
            not context
            or context == "Aucune information trouvée dans la base de connaissances."
        ):
            return f"Je n'ai pas trouvé d'information spécifique sur '{query}' dans ma base de connaissances. Puis-je vous aider avec autre chose concernant Versailles ?"

        return f"Voici les informations sur '{query}':\n\n{context}"

    except Exception as e:
        return f"Erreur lors de la recherche d'informations: {str(e)}"


@tool(description="Get opening hours for Versailles")
def get_versailles_opening_hours(date: str = None) -> str:
    """
    Get opening hours for the Château de Versailles.

    Args:
        date: Optional date to check specific opening hours

    Returns:
        Opening hours information
    """
    try:
        retriever = get_retriever()
        info = retriever.get_opening_hours_info()

        if date:
            return f"Horaires d'ouverture pour le {date}:\n\n{info}"
        else:
            return f"Horaires d'ouverture du Château de Versailles:\n\n{info}"

    except Exception as e:
        return f"Erreur lors de la récupération des horaires: {str(e)}"


@tool(description="Get ticket information for Versailles")
def get_versailles_ticket_info() -> str:
    """
    Get information about tickets, pricing, and reservations for Versailles.

    Returns:
        Ticket and pricing information
    """
    try:
        retriever = get_retriever()
        info = retriever.get_ticket_info()
        return f"Informations sur les billets et tarifs:\n\n{info}"

    except Exception as e:
        return (
            f"Erreur lors de la récupération des informations sur les billets: {str(e)}"
        )


@tool(description="Get access and transportation information for Versailles")
def get_versailles_access_info() -> str:
    """
    Get information about how to access Versailles and transportation options.

    Returns:
        Access and transportation information
    """
    try:
        retriever = get_retriever()
        info = retriever.get_access_info()
        return f"Informations sur l'accès et les transports:\n\n{info}"

    except Exception as e:
        return f"Erreur lors de la récupération des informations d'accès: {str(e)}"
