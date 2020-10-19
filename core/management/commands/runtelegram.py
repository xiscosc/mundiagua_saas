from functools import wraps

from django.core.management.base import BaseCommand
from telegram.ext import Updater, CommandHandler
from telegram import ChatAction
from django.conf import settings


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


@send_typing_action
def start(update, context):
    from core.models import User
    token = update.message.chat_id
    update.message.reply_text("Bienvenido a Mundiagua")
    try:
        user = User.objects.get(telegram_token=token)
        update.message.reply_text("Bienvenido de nuevo " + user.first_name)
    except Exception:
        update.message.reply_text("Este dispositvo no esta registrado, por favor registrelo para continuar, "
                              "ejemplo: /register 123-1a2b3c4d5")


@send_typing_action
def register(update, context):
    from core.models import User
    from core.utils import is_telegram_token
    token = update.message.chat_id
    incorrect_token_message = "Token incorrecto, compruebe que su token es correcto. " \
                              "Recuerde que el token puede cambiar cada cierto tiempo."

    if len(context.args) == 0:
        update.message.reply_text("Debe proporcionar un token de registro, "
                                  "ejemplo: /register 123-1a2b3c4d5")
        return

    if is_telegram_token(context.args[0]):
        data = context.args[0].split('-')
        try:
            user = User.objects.get(id=int(data[0]))
            if user.get_telegram_auth() == data[1]:
                if user.telegram_token:
                    update.message.reply_text("Usted ya estaba registrado, se procedera a usar esta nueva cuenta")
                user.telegram_token = token
                user.save()
                update.message.reply_text("Registro completado. Bienvenido " + user.first_name)
            else:
                update.message.reply_text(incorrect_token_message)
        except Exception:
            update.message.reply_text(incorrect_token_message)
    else:
        update.message.reply_text(incorrect_token_message)


class Command(BaseCommand):
    help = 'Starts telegram bot listener'

    def handle(self, *args, **options):
        updater = Updater(token=settings.TELEGRAM_TOKEN)
        dispatcher = updater.dispatcher
        start_handler = CommandHandler('start', start)
        register_handler = CommandHandler('register', register, pass_args=True)
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(register_handler)
        updater.start_polling()
