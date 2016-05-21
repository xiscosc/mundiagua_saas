from async_messages import message_user, constants
from celery import shared_task

from core.utils import send_data_to_user


@shared_task
def send_message(ins, body):
    result = send_data_to_user(ins.to_user, ins.subject, body)
    if result:
        message_user(ins.from_user, "Mensaje enviado correctamente", constants.SUCCESS)
    else:
        message_user(ins.from_user, "No se ha podido enviar el mensaje", constants.ERROR)