import pytest
import os
import sys

sys.path.append(os.path.abspath("../memory"))
sys.path.append(os.path.abspath(".."))
from memory.memory import save_session, load_session


def test_save_load_session():
    session_id = "test_session"
    data = {"last_interaction": "test"}

    save_session(session_id, data)
    loaded = load_session(session_id)

    assert loaded["last_interaction"] == "test"
