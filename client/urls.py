from django.conf.urls import url
from .views import CreateClientView, CreateAddressView, CreatePhoneView, ClientView, EditClientView, EditAddressView,\
    EditPhoneView, DeletePhoneView, DeleteAddresView

urlpatterns = [
    url(r'^new/$', CreateClientView.as_view(), name="client-client-new"),
    url(r'^view/(?P<pk>\d+)/$', ClientView.as_view(), name="client-client"),
    url(r'^edit/(?P<pk>\d+)/$', EditClientView.as_view(), name="client-client-edit"),
    url(r'^address/new/(?P<id>\d+)/$', CreateAddressView.as_view(), name="client-address-new"),
    url(r'^address/add/(?P<id>\d+)/$', CreateAddressView.as_view(), name="client-address-add"),
    url(r'^address/edit/(?P<pk>\d+)/$', EditAddressView.as_view(), name="client-address-edit"),
    url(r'^address/delete/(?P<pk>\d+)/$', DeleteAddresView.as_view(), name="client-address-delete"),
    url(r'^phone/new/(?P<id>\d+)/$', CreatePhoneView.as_view(), name="client-phone-new"),
    url(r'^phone/delete/(?P<pk>\d+)/$', DeletePhoneView.as_view(), name="client-phone-delete"),
    url(r'^phone/edit/(?P<pk>\d+)/$', EditPhoneView.as_view(), name="client-phone-edit"),
]