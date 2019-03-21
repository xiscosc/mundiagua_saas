from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.cache import cache

import time
import requests

from core.models import User
from core.utils import send_data_to_user


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        # STATUS 1 - OK, 2 - WARNING, 3 - FAILURE
        status = 1
        users = User.objects.filter(pk__in=[1, 11])
        while True:
            try:
                r = requests.get(settings.GSM_URL)
                if r.status_code == 200:
                    if status == 3:
                        self.send_recover_message(users)
                    status = 1
                else:
                    if status == 1:
                        status = 2
                    elif status == 2:
                        status = 3
                        self.send_error_message(users)
            except:
                if status == 1:
                    status = 2
                elif status == 2:
                    status = 3
                    self.send_error_message(users)
            finally:
                cache.set(settings.GSM_WATCH_CACHE_KEY, status, settings.GSM_WATCH_TIME * 2)
                time.sleep(settings.GSM_WATCH_TIME)

    def send_error_message(self, users):
        for user in users:
            send_data_to_user(user, "GSM MICROCOM CAIDO", "Servidor gsm no responde")

    def send_recover_message(self, users):
        for user in users:
            send_data_to_user(user, "GSM MICROCOM FUNCIONANDO", "Servidor gsm recuperado")

