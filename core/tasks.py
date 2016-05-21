from async_messages import messages
from celery import shared_task

from core.utils import send_data_to_user


@shared_task
def send_message(ins, body):
    result = send_data_to_user(ins.to_user, ins.subject, body)
    if result:
        messages.success(ins.from_user, "Mensaje a "+ ins.to_user.get_full_name() + " enviado correctamente")
    else:
        messages.warning(ins.from_user, "No se ha podido enviar el mensaje a "+ ins.to_user.get_full_name())