from django.conf.urls import url
from .views import CreateClientView, CreateAddressView, CreatePhoneAddress, ClientView, EditClientView, EditAddressView, EditPhoneView

urlpatterns = [
    url(r'^new/$', CreateClientView.as_view(), name="client-client-new"),
    url(r'^(?P<pk>\d+)/$', ClientView.as_view(), name="client-client"),
    url(r'^edit/(?P<pk>\d+)/$', EditClientView.as_view(), name="client-client-edit"),
    url(r'^address/new/(?P<id>\d+)/$', CreateAddressView.as_view(), name="client-address-new"),
    url(r'^address/add/(?P<id>\d+)/$', CreateAddressView.as_view(), name="client-address-add"),
    url(r'^address/edit/(?P<pk>\d+)/$', EditAddressView.as_view(), name="client-address-edit"),
    url(r'^phone/new/(?P<id>\d+)/$', CreatePhoneAddress.as_view(), name="client-phone-new"),
    url(r'^phone/edit/(?P<pk>\d+)/$', EditPhoneView.as_view(), name="client-phone-edit"),
]