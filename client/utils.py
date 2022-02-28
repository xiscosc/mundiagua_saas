import os
import uuid
import mimetypes
from typing import List

import requests
from django.conf import settings

from core.utils import create_amazon_client


def send_whatsapp_template(template, placeholders: List[str], phone, file_name, s3_key):

    hsm = {'language': {'code': 'es'}, 'namespace': settings.FB_WHATSAPP_NAMESPACE, 'templateName': template.wa_key}
    if s3_key is None or file_name is None:
        hsm['params'] = []
        for placeholder in placeholders:
            hsm['params'].append({'default': placeholder})
    else:
        params = []
        for placeholder in placeholders:
            params.append({'type': 'text', 'text': placeholder})

        url = get_whatsapp_download_signed_url(s3_key)
        hsm['components'] = [
            {'type': 'header', 'parameters': [{'type': 'document', 'document': {'url': url, 'caption': file_name}}]},
            {'type': 'body', 'parameters': params},
        ]

    body = {
        'content': {'hsm': hsm},
        'from': settings.MESSAGEBIRD_WHATSAPP_CHANNEL,
        'type': 'hsm',
        'to': phone.full_international_format().replace(" ", "")
    }

    headers = {
        'Authorization': 'AccessKey ' + settings.MESSAGEBIRD_API_KEY,
        'Content-Type': 'application/json; charset=utf-8'
    }

    r = requests.post("https://conversations.messagebird.com/v1/send", json=body, headers=headers)
    return r.status_code, r.json()


def get_whatsapp_upload_signed_url(s3_key: str):
    s3 = create_amazon_client('s3')
    mimetype = mimetypes.guess_type(s3_key)[0]
    fields = {'Content-Type': mimetype}
    conditions = [["starts-with", "$Content-Type", ""]]
    return s3.generate_presigned_post(settings.S3_WHATSAPP, s3_key, ExpiresIn=60, Fields=fields, Conditions=conditions)


def get_whatsapp_download_signed_url(s3_key: str):
    s3 = create_amazon_client('s3')
    s3_params = {'Bucket': settings.S3_WHATSAPP, 'Key': s3_key}
    return s3.generate_presigned_url('get_object', Params=s3_params, ExpiresIn=600)


def generate_whatsapp_document_s3_key(filename):
    _, file_extension = os.path.splitext(filename)
    if file_extension != ".pdf":
        raise Exception("WhatsApp - Trying to send non pdf: {}".format(file_extension))
    return "%s%s" % (uuid.uuid1().__str__(), file_extension)


def get_zone_using_interventions(address):
    from django.db import connection
    from intervention.models import Zone
    select = '''select i.zone_id as zid, count(*) c from client_address a
                inner join intervention_intervention i on i.address_id = a.id
                where address_id = %s
                group by zid
                order by c desc
                limit 1;
                ''' % address.pk

    with connection.cursor() as cursor:
        cursor.execute(select)
        first_row=cursor.fetchone()
        if first_row:
            return Zone.objects.get(pk=first_row[0])
        else:
            return None
