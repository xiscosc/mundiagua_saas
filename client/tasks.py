# -*- coding: utf-8 -*-
from async_messages import messages
from celery import shared_task


@shared_task
def send_sms(sms):
    result = sms.send()
    if result['success']:
        messages.success(sms.sender, "SMS a " + sms.phone.client.name + " enviado correctamente")
    else:
        if result['reason'] == "incorrect_phone":
            messages.warning(sms.sender,
                             "Error enviando SMS a " + sms.phone.client.name + ", el número no cumple el formato")
        else:
            messages.warning(sms.sender,
                             "Error enviando SMS a " + sms.phone.client.name + ", puede ser un error " +
                             "temporal o que no hay crédito de SMS")
