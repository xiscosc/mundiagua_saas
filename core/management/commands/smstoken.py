import requests
from django.core.cache import cache
from django.core.management import BaseCommand
from django.conf import settings

from core.models import User
from core.utils import send_data_to_user


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            time = cache.get(settings.SMS_TOKEN_EXPIRE_TIME)
            url = settings.SMS_SERVICE_URL + '/user_token'
            body = {'username': settings.SMS_USERNAME, 'password': settings.SMS_PASSWORD}
            r = requests.post(url=url, json=body)
            if r.status_code == 200:
                token = r.json()['token']
                if token:
                    cache.set(settings.SMS_TOKEN_CACHE_KEY, token, time)
                    return

            self.send_error_message()
        except:
            self.send_error_message()

    def send_error_message(self):
        users = User.objects.filter(pk__in=[1, 23])
        for user in users:
            send_data_to_user(user, "ERROR SERVICIO SMS", "Error autenticando servicio SMS")