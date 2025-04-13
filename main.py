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
        # Handle routes with IDs (DELETE and PUT operations)
        if route.startswith("/embedding-api/"):
            doc_id = route.split("/")[-1]
            if not doc_id:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Missing ID in URL"})
                }

            if http_method == "DELETE":
                result = delete_from_qdrant(doc_id)
                return {
                    "statusCode": 200,
                    "body": json.dumps({"result": result})
                }

            elif http_method == "PUT":
                body = json.loads(event.get("body", "{}"))
                body["id"] = doc_id  # Ensure ID from URL is used
                combined = combine_fields(body)
                embedding = get_embedding(combined)
                result = store_to_qdrant(doc_id, embedding, body)

                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "result": result,
                        "id": doc_id,
                        "updated": True
                    })
                }

        # Handle base /embedding-api endpoint (GET and POST operations)
        elif route == "/embedding-api":
            if http_method == "GET":
                # Search operation
                query_params = event.get("queryStringParameters", {}) or {}
                query = query_params.get("query")
                if not query:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "Missing 'query' parameter"})
                    }

                embedding = get_embedding(query)
                result = search_qdrant(embedding)
                return {
                    "statusCode": 200,
                    "body": json.dumps({"result": result})
                }

            elif http_method == "POST":
                # Create operation
                body = json.loads(event.get("body", "{}"))
                doc_id = body.get("id") or context.aws_request_id
                combined = combine_fields(body)
                embedding = get_embedding(combined)
                result = store_to_qdrant(doc_id, embedding, body)

                return {
                    "statusCode": 201,  # Created
                    "body": json.dumps({
                        "result": result,
                        "id": doc_id
                    })
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