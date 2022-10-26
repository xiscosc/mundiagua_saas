import io
import mimetypes
import uuid
import os
from django.db.models import Model

from core.aws.aws_client import _create_amazon_client


def get_s3_upload_signed_url(s3_key: str, upload_buket: str) -> str:
    mimetype = mimetypes.guess_type(s3_key)[0]
    fields = {"Content-Type": mimetype}
    conditions = [["starts-with", "$Content-Type", ""]]
    return _create_amazon_client("s3").generate_presigned_post(
        upload_buket,
        s3_key,
        ExpiresIn=60,
        Fields=fields,
        Conditions=conditions,
    )


def upload_s3_file(s3_key: str, upload_buket: str, file):
    _create_amazon_client("s3").upload_fileobj(io.BytesIO(file), upload_buket, s3_key)


def get_s3_download_signed_url(s3_key: str, upload_buket: str, expiration: int = 120) -> str:
    params = {'Bucket': upload_buket, 'Key': s3_key}
    return _create_amazon_client('s3').generate_presigned_url('get_object', Params=params, ExpiresIn=expiration)


def generate_s3_document_key(m: Model, filename: str) -> str:
    folder = m.__str__()
    id = uuid.uuid1().__str__()
    _, file_extension = os.path.splitext(filename)
    return "%s/%s%s" % (folder, id, file_extension)
