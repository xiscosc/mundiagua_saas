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
