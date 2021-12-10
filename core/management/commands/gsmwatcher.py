from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.cache import cache

import time
import requests
from datetime import datetime

from core.models import User
from core.tasks import send_data_to_user


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        # STATUS 1 - OK, 2 - WARNING, 3 - FAILURE
        status = 1
        user_pks = settings.USERS_IT + settings.USERS_TEC
        users = User.objects.filter(pk__in=user_pks)
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
            cache.set(settings.GSM_WATCH_STATUS_CACHE_KEY, status, settings.GSM_WATCH_TIME * 5)
            cache.set(settings.GSM_WATCH_TIME_CACHE_KEY, datetime.now(), settings.GSM_WATCH_TIME * 5)

    def send_error_message(self, users):
        for user in users:
            send_data_to_user(user, "GSM MICROCOM CAIDO", "Servidor gsm no responde")

    def send_recover_message(self, users):
        for user in users:
            send_data_to_user(user, "GSM MICROCOM FUNCIONANDO", "Servidor gsm recuperado")

