# memory.py
import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def save_session(session_id: str, data: dict):
    r.set(session_id, json.dumps(data))


def load_session(session_id: str) -> dict:
    val = r.get(session_id)
    if val:
        return json.loads(val)
    return {}
