import pytest
from fastapi.testclient import TestClient
import os
import sys

sys.path.append(os.path.abspath("../app"))
sys.path.append(os.path.abspath(".."))
from app.app import app


client = TestClient(app)


def test_set_get_redis():
    r = client.get("/set/testkey/testvalue")
    assert r.status_code == 200

    r2 = client.get("/get/testkey")
    assert r2.json()["value"] == "testvalue"
