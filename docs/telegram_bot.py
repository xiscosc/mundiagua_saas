from telegram.ext import Updater, CommandHandler
from django.conf import settings


def start(bot, update):
    from core.models import User
    import telegram
    token = update.message.chat_id
    bot.send_message(chat_id=token, text="Bienvenido a Mundiagua")
    bot.send_chat_action(chat_id=token, action=telegram.ChatAction.TYPING)
    try:
        user = User.objects.get(telegram_token=token)
        bot.send_message(chat_id=token, text="Bienvenido de nuevo " + user.first_name)
    except Exception:
        bot.send_message(chat_id=token, text="Este dispositvo no esta registrado, por favor registrelo para continuar")


def register(bot, update, args):
    from core.models import User
    from core.utils import is_telegram_token
    import telegram

    token = update.message.chat_id
    bot.send_chat_action(chat_id=token, action=telegram.ChatAction.TYPING)
    incorrect_token_message = "Token incorrecto, compruebe que su token es correcto"
    if is_telegram_token(args[0]):
        data = args[0].split('-')
        try:
            user = User.objects.get(id=int(data[0]))
            if user.get_telegram_auth() == data[1]:
                if user.telegram_token:
                    bot.send_message(chat_id=token, text="Usted ya estaba registrado, se procedera a usar esta nueva cuenta")
                user.telegram_token = token
                user.save()
                bot.send_message(chat_id=token, text="Registro completado. Bienvenido " + user.first_name)
            else:
                bot.send_message(chat_id=token, text=incorrect_token_message)
        except Exception:
            bot.send_message(chat_id=token, text=incorrect_token_message)
    else:
        bot.send_message(chat_id=token, text=incorrect_token_message)


updater = Updater(token=settings.TELEGRAM_TOKEN)
dispatcher = updater.dispatcher
start_handler = CommandHandler('start', start)
register_handler = CommandHandler('register', register, pass_args=True)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(register_handler)
updater.start_polling()