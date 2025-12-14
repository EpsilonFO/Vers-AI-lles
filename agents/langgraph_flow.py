"""LangGraph flow for routing between LLM and Agent."""

import os
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import after loading env
from agents.agent_multistep import run_agent
from prompts.reservation_prompt import reservation_template


# Define the state of the graph
class State(TypedDict):
    """State passed between nodes in the graph."""

    input_text: str
    response: str
    session_id: Optional[str]


# Initialize LLM with system prompt
llm = ChatMistralAI(
    api_key=os.getenv("MISTRAL_API_KEY"), model="mistral-large-latest", temperature=0.7
)


def llm_node(state: State) -> State:
    """
    Node for direct LLM responses (simple questions, greetings, etc.).

    Args:
        state: Current state with input_text

    Returns:
        Updated state with LLM response
    """
    try:
        # Create a simple prompt for general questions
        prompt = f"""Tu es un assistant virtuel pour le Château de Versailles.
Réponds de manière amicale et informative aux questions générales.

Question: {state['input_text']}

Réponse:"""

        resp = llm.invoke(prompt)
        return {
            "input_text": state["input_text"],
            "response": resp.content,
            "session_id": state.get("session_id", "default_session"),
        }
    except Exception as e:
        return {
            "input_text": state["input_text"],
            "response": f"Erreur lors du traitement: {str(e)}",
            "session_id": state.get("session_id", "default_session"),
        }


def agent_node(state: State) -> State:
    """
    Node for agent-based responses (complex tasks, reservations, tool usage).

    Args:
        state: Current state with input_text

    Returns:
        Updated state with agent response
    """
    try:
        session_id = state.get("session_id", "default_session")

        # Run the agent with the user's message
        resp = run_agent(session_id, state["input_text"])

        return {
            "input_text": state["input_text"],
            "response": resp,
            "session_id": session_id,
        }
    except Exception as e:
        return {
            "input_text": state["input_text"],
            "response": f"Erreur lors du traitement par l'agent: {str(e)}",
            "session_id": state.get("session_id", "default_session"),
        }


def route_input(state: State) -> str:
    """
    Router to decide between LLM and Agent based on input.

    Args:
        state: Current state with input_text

    Returns:
        Name of the next node to execute
    """
    input_lower = state["input_text"].lower()

    # Keywords that trigger agent usage (tasks requiring tools)
    agent_keywords = [
        # Reservation keywords
        "réserver",
        "réservation",
        "booking",
        "book",
        # Versailles specific
        "billet",
        "ticket",
        "tarif",
        "prix",
        "horaire",
        "ouverture",
        "disponibilité",
        "disponible",
        # Transportation
        "train",
        "sncf",
        "rer",
        "metro",
        "bus",
        "transport",
        "trajet",
        "itinéraire",
        "comment aller",
        "comment venir",
        # Accommodation
        "hôtel",
        "hotel",
        "airbnb",
        "logement",
        "hébergement",
        # Practical info
        "parking",
        "restaurant",
        "manger",
        "déjeuner",
        "météo",
        "temps",
        "weather",
        "maps",
        "carte",
        "plan",
        # Search queries
        "cherche",
        "trouve",
        "information sur",
        "parle moi de",
        "histoire",
        "galerie",
        "jardin",
        "trianon",
    ]

    # Check if any agent keyword is in the input
    if any(keyword in input_lower for keyword in agent_keywords):
        return "Agent_Response"

    # Simple greetings and general questions go to LLM
    return "LLM_Response"


# Build the graph
graph = StateGraph(State)

# Add nodes
graph.add_node("LLM_Response", llm_node)
graph.add_node("Agent_Response", agent_node)

# Set conditional entry point
graph.set_conditional_entry_point(
    route_input, {"LLM_Response": "LLM_Response", "Agent_Response": "Agent_Response"}
)

# Connect to END
graph.add_edge("LLM_Response", END)
graph.add_edge("Agent_Response", END)

# Compile the graph
app = graph.compile()


def run_graph(input_text: str, session_id: str = "default_session") -> str:
    """
    Run the LangGraph flow with the given input.

    Args:
        input_text: User's input message
        session_id: Session identifier for conversation tracking

    Returns:
        Response from either LLM or Agent
    """
    try:
        result = app.invoke(
            {"input_text": input_text, "session_id": session_id, "response": ""}
        )
        return result["response"]
    except Exception as e:
        return f"Erreur dans le flux LangGraph: {str(e)}"
