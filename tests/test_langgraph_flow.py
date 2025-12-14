import pytest
import os
import sys

sys.path.append(os.path.abspath("../app"))
sys.path.append(os.path.abspath(".."))
from agents.langgraph_flow import run_graph


def test_llm_route():
    response = run_graph("Bonjour")
    assert isinstance(response, str)


def test_agent_route_keywords():
    response = run_graph("Je veux réserver un billet pour Versailles")
    assert isinstance(response, str)
