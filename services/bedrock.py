# services/bedrock.py
import os
import json
import boto3

EMBED_MODEL_ID = os.getenv("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")

bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "eu-west-2"))

def get_embedding(text: str):
    body = json.dumps({"inputText": text})
    response = bedrock.invoke_model(
        body=body,
        modelId=EMBED_MODEL_ID,
        accept="application/json",
        contentType="application/json"
    )
    parsed = json.loads(response["body"].read())
    return parsed["embedding"]
