import json
from typing import Any

import boto3
from botocore.client import Config

from app.config import get_settings

_s3_client = None


def get_s3_client():
    global _s3_client
    if _s3_client is None:
        settings = get_settings()
        _s3_client = boto3.client(
            "s3",
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
            region_name="us-east-1",
        )
    return _s3_client


def _bucket() -> str:
    return get_settings().MINIO_BUCKET


def put_json(key: str, obj: dict) -> None:
    """Upload a JSON-serialisable dict to MinIO."""
    data = json.dumps(obj).encode("utf-8")
    get_s3_client().put_object(
        Bucket=_bucket(),
        Key=key,
        Body=data,
        ContentType="application/json",
    )


def get_json(key: str) -> dict:
    """Download and parse a JSON object from MinIO."""
    response = get_s3_client().get_object(Bucket=_bucket(), Key=key)
    return json.loads(response["Body"].read())


def put_bytes(key: str, data: bytes, content_type: str) -> None:
    """Upload raw bytes to MinIO."""
    get_s3_client().put_object(
        Bucket=_bucket(),
        Key=key,
        Body=data,
        ContentType=content_type,
    )


def get_presigned_url(key: str, expires: int = 3600) -> str:
    """Generate a pre-signed GET URL for a MinIO object."""
    return get_s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": _bucket(), "Key": key},
        ExpiresIn=expires,
    )
