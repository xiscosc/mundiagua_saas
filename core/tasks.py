from async_messages import messages
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from core.utils import send_data_to_user


@shared_task
def send_message(ins, body):
    result = send_data_to_user(ins.to_user, ins.subject, body)
    if result:
        messages.success(ins.from_user, "Mensaje a " + ins.to_user.get_full_name() + " enviado correctamente")
    else:
        messages.warning(ins.from_user, "No se ha podido enviar el mensaje a " + ins.to_user.get_full_name())


@shared_task
def send_mail_client(address, subject, body, user):
    email = EmailMultiAlternatives(
        subject,
        body,
        'Mundiagua SL <consultas@mundiaguabalear.com>',
        [address],
    )

    htmly = get_template('email.html')
    html_content = htmly.render({'subject': subject, 'body': body})
    email.attach_alternative(html_content, "text/html")
    result = email.send()

    if result:
        messages.success(user, "Email enviado correctamente a "+ address)
    else:
        messages.warning(user, "Error enviando mail a " + address)


def process_phone(sms):
    phone_processed = sms.phone.phone.replace(" ", "")
    phone_processed = '+34' + phone_processed.replace(".", "")
    if len(phone_processed) == 12:
        return phone_processed
    else:
        return False


def send(sms):
    number = process_phone(sms)
    if number:
        import boto3
        from django.conf import settings
        try:
            sns = boto3.client('sns',
                               aws_access_key_id=settings.AWS_ACCESS_KEY,
                               aws_secret_access_key=settings.AWS_SECRET_KEY,
                               region_name=settings.AWS_REGION
                               )
            result = sns.publish(PhoneNumber=number, Message=sms.body)
            status = int(result['ResponseMetadata']['HTTPStatusCode'])
            if status == 200:
                sms.sent_status_id = 2
                dict = {"success": True}
            else:
                sms.sent_status_id = 3
                dict = {"success": False, "reason": "error"}
        except:
            sms.sent_status_id = 3
            dict = {"success": False, "reason": "error"}
    else:
        sms.sent_status_id = 4
        dict = {"success": False, "reason": "incorrect_phone"}

    sms.save()
    return dict