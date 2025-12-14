import pytest
import os
import sys

sys.path.append(os.path.abspath(".."))
sys.path.append(os.path.abspath("../agents"))
from agents.agent_multistep import run_agent


def test_run_agent_basic():
    session_id = "test_session"
    message = "Je veux réserver Versailles pour 2 personnes."

    response = run_agent(session_id, message)

    assert isinstance(response, str)
    assert len(response) > 0
