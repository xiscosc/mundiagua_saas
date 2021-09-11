# -*- coding: utf-8 -*-
from django.conf import settings
from pyshorteners import Shortener

from client.models import SMS
from repair.models import AthRepair, IdegisRepair


def send_sms_tracking(pk_repair, is_ath, phone_pk, user_pk):
    shortener = Shortener(api_key=settings.BITLY_API_KEY)

    if is_ath == 1:
        repair = AthRepair.objects.get(pk=pk_repair)
    else:
        repair = IdegisRepair.objects.get(pk=pk_repair)

    url_to_short = "https://customerservice.mundiaguabalear.com/?id=" + repair.online_id
    body = u'Su reparación %s ha sido registrada, puede consultar su estado en %s o con el id %s en ' \
           u'nuestra página web' % (repair.__str__(), shortener.bitly.short(url_to_short), repair.online_id)

    sms = SMS(sender_id=user_pk, body=body, phone_id=phone_pk)
    sms.save()
    repair.sms.add(sms)
