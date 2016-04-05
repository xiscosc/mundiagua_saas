from django.conf.urls import url
from .views import CreateClientView, CreateAddressView

urlpatterns = [
    url(r'^new/$', CreateClientView.as_view(), name="client-client-new"),
    url(r'^address/new/(?P<id>\d+)/$', CreateAddressView.as_view(), name="client-address-new"),
]