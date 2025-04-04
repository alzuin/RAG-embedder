# services/bedrock.py
import os
import json
import boto3

bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "eu-west-2"))

def get_embedding(text: str):
    body = json.dumps({"inputText": text})
    response = bedrock.invoke_model(
        body=body,
        modelId="amazon.titan-embed-text-v1",
        accept="application/json",
        contentType="application/json"
    )
    parsed = json.loads(response["body"].read())
    return parsed["embedding"]
