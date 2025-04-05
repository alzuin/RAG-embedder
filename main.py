# main.py
import os
import json
import logging

from services.bedrock import get_embedding
from services.qdrant import store_to_qdrant, search_qdrant, delete_from_qdrant

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def combine_fields(payload):
    fields = [str(v) for k, v in payload.items() if k != "id"]
    return ". ".join(fields)

def handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    route = event.get("path", "/")
    http_method = event.get("httpMethod", "GET")

    try:
        body = json.loads(event.get("body", "{}"))

        if route == "/embedding-api/upload" and http_method == "POST":
            doc_id = body.get("id") or context.aws_request_id
            combined = combine_fields(body)
            embedding = get_embedding(combined)
            result = store_to_qdrant(doc_id, embedding, body)

            return {
                "statusCode": 200,
                "body": json.dumps({"result": result})
            }

        elif route == "/embedding-api/search" and http_method == "POST":
            query = body.get("query")
            if not query:
                raise ValueError("Missing 'query' field")

            embedding = get_embedding(query)
            result = search_qdrant(embedding)

            return {
                "statusCode": 200,
                "body": json.dumps({"result": result})
            }
        elif route == "/embedding-api/delete" and http_method == "POST":
            doc_id = body.get("id")
            if not doc_id:
                raise ValueError("Missing 'id' field")

            result = delete_from_qdrant(doc_id)
            return {
                "statusCode": 200,
                "body": json.dumps({"result": result})
            }
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Route not found"})
        }

    except Exception as e:
        logger.exception("Lambda failed")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }