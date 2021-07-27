from typing import List

import requests
from django.conf import settings

from client.models import WhatsAppTemplate, Phone


def send_whatsapp_template(template: WhatsAppTemplate, placeholders: List[str], phone: Phone):
    params = []
    for placeholder in placeholders:
        params.append({'default': placeholder})

    body = {
        'content': {
            'hsm': {'params': params, 'language': {'code': 'es'}, 'namespace': settings.FB_WHATSAPP_NAMESPACE,
                    'templateName': template.wa_key}},
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
