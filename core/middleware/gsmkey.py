from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache


class GsmKey(MiddlewareMixin):

    def process_request(self, request):
        status = cache.get(settings.GSM_WATCH_STATUS_CACHE_KEY)
        if status is None:
            request.gsm_status = 0
        else:
            request.gsm_status = status
        return
