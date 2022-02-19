from async_messages import messages
from core.utils import create_nexmo_client, encode_nexmo_body, check_nexmo_message_sent


def send_sms(sms):
    if sms.sent_status_id != 1:
        raise Exception("SMS %d ya fue enviado una vez" % sms.id)
    number = sms.process_phone_for_nexmo()
    if number:
        try:
            result = create_nexmo_client().send_message({
                'from': 'MUNDIAGUA',
                'to': number,
                'text': encode_nexmo_body(sms.body),
            })

            if check_nexmo_message_sent(result):
                sms.sent_status_id = 2
                result = {"success": True}
            else:
                sms.sent_status_id = 3
                result = {"success": False, "reason": "error"}
        except:
            sms.sent_status_id = 3
            result = {"success": False, "reason": "error"}
    else:
        sms.sent_status_id = 4
        result = {"success": False, "reason": "incorrect_phone"}

    sms.save()
    if result['success']:
        messages.success(sms.sender, "SMS a " + sms.phone.client.name + " enviado correctamente")
    else:
        if result['reason'] == "incorrect_phone":
            message_error = "Error enviando SMS a " + sms.phone.client.name + ", no cumple el formato"

        else:
            message_error = "Error enviando SMS a " + sms.phone.client.name + ", contacte con el administrador"

        messages.warning(sms.sender, message_error)