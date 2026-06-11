import boto3
import json
from botocore.config import Config
from app.config import get_settings

def _client():
    s = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=s.MINIO_ENDPOINT,
        aws_access_key_id=s.MINIO_ACCESS_KEY,
        aws_secret_access_key=s.MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

def put_json(key: str, obj: dict) -> None:
    s = get_settings()
    _client().put_object(Bucket=s.MINIO_BUCKET, Key=key, Body=json.dumps(obj).encode(), ContentType="application/json")

def get_json(key: str) -> dict:
    s = get_settings()
    resp = _client().get_object(Bucket=s.MINIO_BUCKET, Key=key)
    return json.loads(resp["Body"].read())

def put_bytes(key: str, data: bytes, content_type: str) -> None:
    s = get_settings()
    _client().put_object(Bucket=s.MINIO_BUCKET, Key=key, Body=data, ContentType=content_type)

def get_presigned_url(key: str, expires: int = 3600) -> str:
    s = get_settings()
    return _client().generate_presigned_url("get_object", Params={"Bucket": s.MINIO_BUCKET, "Key": key}, ExpiresIn=expires)
