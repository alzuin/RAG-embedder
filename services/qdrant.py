# services/qdrant.py
import os
import requests

QDRANT_URL = os.getenv("QDRANT_URL")

def store_to_qdrant(id_: str, vector: list, body: dict = None):
    payload = {
        "points": [
            {
                "id": id_,
                "vector": vector,
                "payload": body
            }
        ]
    }
    res = requests.put(f"{QDRANT_URL}/collections/houses/points", json=payload)
    res.raise_for_status()
    return res.json()

def search_qdrant(vector: list):
    payload = {
        "vector": vector,
        "top": 5,
        "with_payload": True
    }
    res = requests.post(f"{QDRANT_URL}/collections/houses/points/search", json=payload)
    res.raise_for_status()
    return res.json()

def delete_from_qdrant(doc_id: str):
    response = requests.post(f"{QDRANT_URL}/collections/houses/points/delete", json={
        "points": [doc_id]
    })
    response.raise_for_status()
    return response.json()
