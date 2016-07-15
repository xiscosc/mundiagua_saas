from async_messages import messages
from celery import shared_task
from django.core.mail import send_mail

from core.utils import send_data_to_user


@shared_task
def send_message(ins, body):
    result = send_data_to_user(ins.to_user, ins.subject, body)
    if result:
        messages.success(ins.from_user, "Mensaje a " + ins.to_user.get_full_name() + " enviado correctamente")
    else:
        messages.warning(ins.from_user, "No se ha podido enviar el mensaje a " + ins.to_user.get_full_name())


@shared_task
def send_mail_client(client, subject, body):
    return send_mail(subject=subject, message=body,
                     from_email="consultas@mundiaguabalear.com", recipient_list=[client.email])
