# services/qdrant.py
import os
import requests

QDRANT_URL = os.getenv("QDRANT_URL")

def store_to_qdrant(id_: str, vector: list):
    payload = {
        "points": [
            {
                "id": id_,
                "vector": vector,
                "payload": {}
            }
        ]
    }
    res = requests.put(f"{QDRANT_URL}/collections/houses/points", json=payload)
    res.raise_for_status()
    return res.json()

def search_qdrant(vector: list):
    payload = {
        "vector": vector,
        "top": 5
    }
    res = requests.post(f"{QDRANT_URL}/collections/houses/points/search", json=payload)
    res.raise_for_status()
    return res.json()
