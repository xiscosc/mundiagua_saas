from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.core.urlresolvers import resolve



class StaffMiddleware(object):
    """
    Middlware for control staff urls
    """

    def __init__(self):
        if hasattr(settings,'NON_STAFF_VIEWS'):
            non_staff_urls = settings.NON_STAFF_VIEWS
        else:
            non_staff_urls = []
        self.non_staff_urls = tuple(non_staff_urls)

    def process_request(self, request):
        """
        Redirect anonymous users to login_url from non public urls
        """
        if request.user.is_authenticated() and not request.user.is_officer:
            current_url = resolve(request.path_info).url_name
            if current_url not in self.non_staff_urls:
                return HttpResponseForbidden()
