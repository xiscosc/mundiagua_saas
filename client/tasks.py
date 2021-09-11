# -*- coding: utf-8 -*-
from async_messages import messages


def send_sms(pk):
    from client.models import SMS
    sms = SMS.objects.get(pk=pk)
    result = sms.send()
    if result['success']:
        messages.success(sms.sender, "SMS a " + sms.phone.client.name + " enviado correctamente")
    else:
        if result['reason'] == "incorrect_phone":
            message_error = "Error enviando SMS a " + sms.phone.client.name + ", no cumple el formato"

        else:
            message_error = "Error enviando SMS a " + sms.phone.client.name + ", contacte con el administrador"

        messages.warning(sms.sender, message_error)
