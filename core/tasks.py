from async_messages import messages
from celery import shared_task
from django.template.loader import get_template

from core.utils import send_data_to_user


@shared_task
def send_message(pk, body):
    from core.models import Message
    ins = Message.objects.get(pk=pk)
    result = send_data_to_user(ins.to_user, ins.subject, body, from_user=ins.from_user)
    if result:
        messages.success(ins.from_user, "Mensaje a " + ins.to_user.get_full_name() + " enviado correctamente")
    else:
        messages.warning(ins.from_user, "No se ha podido enviar el mensaje a " + ins.to_user.get_full_name())


@shared_task
def send_mail_client(address_pk, subject, body, user_pk):
    from core.models import User
    from client.models import Email
    user = User.objects.get(pk=user_pk)
    address = Email.objects.get(pk=address_pk)
    try:
        from django.core.mail import EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject,
            body,
            'Mundiagua SL <consultas@mundiaguabalear.com>',
            [address.email],
        )
        htmly = get_template('email.html')
        html_content = htmly.render({'subject': subject, 'body': body})
        email.attach_alternative(html_content, "text/html")
        result = email.send()
    except:
        result = False

    if result:
        messages.success(user, "Email enviado correctamente a " + address.email)
    else:
        messages.warning(user, "Error enviando mail a " + address.email)


@shared_task
def notify_sms_received():
    from core.models import User
    users = User.objects.filter(is_officer=True)
    for user in users:
        messages.info(user, "Nuevo SMS recibido")
