from django.conf import settings
from django.core.management.base import BaseCommand

import time
import requests

from core.models import User
from core.utils import send_data_to_user


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        # STATUS 1 - OK, 2 - WARNING, 3 - FAILURE
        status = 1
        admin_user = User.objects.get(pk=1)
        while True:
            try:
                r = requests.get(settings.GSM_URL)
                if r.status_code == 200:
                    if status == 3:
                        self.send_recover_message(admin_user)
                    status = 1
                else:
                    if status == 1:
                        status = 2
                    elif status == 2:
                        status = 3
                        self.send_error_message(admin_user)
            except:
                if status == 1:
                    status = 2
                elif status == 2:
                    status = 3
                    self.send_error_message(admin_user)
            finally:
                time.sleep(settings.GSM_WATCH_TIME)

    def send_error_message(self, user):
        send_data_to_user(user, "GSM MICROCOM CAIDO", "Servidor gsm no responde")

    def send_recover_message(self, user):
        send_data_to_user(user, "GSM MICROCOM FUNCIONANDO", "Servidor gsm recuperado")

