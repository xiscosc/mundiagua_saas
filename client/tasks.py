# -*- coding: utf-8 -*-
from async_messages import messages
from celery import shared_task
from django.conf import settings
from sendsms.message import SmsMessage


@shared_task
def send_sms(sms, phone_processed):
    message = SmsMessage(
        body=sms.body,
        from_phone=settings.SMS_SENDER,
        to=[phone_processed]
    )
    result = message.send()
    if result == 1:
        sms.sent_status_id = 2
        messages.success(sms.sender, "SMS a " + sms.phone.client.name + " enviado correctamente")
    else:
        sms.sent_status_id = 3
        messages.warning(sms.sender,
                         "Error enviando SMS a " + sms.phone.client.name + ", puede ser un error " +
                                                                           "temporal o que no hay crédito de SMS")

    sms.save()
