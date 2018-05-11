from django.http import HttpResponseForbidden
from django.conf import settings
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin


class StaffMiddleware(MiddlewareMixin):
    """
    Middlware for control staff urls
    """
    def process_request(self, request):
        """
        Ban non staff users in staff urls
        """
        if request.user.is_authenticated and not request.user.is_officer:
            if hasattr(settings, 'NON_STAFF_VIEWS'):
                non_staff_urls = settings.NON_STAFF_VIEWS
                current_url = resolve(request.path_info).url_name
                if current_url not in non_staff_urls:
                    return HttpResponseForbidden()
            else:
                return HttpResponseForbidden()
