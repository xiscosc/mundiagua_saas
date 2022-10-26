import boto3
from django.conf import settings


def _create_amazon_client(service: str) -> boto3.client:
    try:
        client = boto3.client(
            service,
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=settings.AWS_REGION,
        )
        return client
    except:
        return None
