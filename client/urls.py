from django.conf.urls import url
from .views import CreateClientView, CreateAddressView, CreatePhoneView, ClientView, EditClientView, EditAddressView, \
    EditPhoneView, DeletePhoneView, DeleteAddresView, SendSMSView, AllClientsView, PreSearchClientView, \
    SearchClientView, AddressGeoUpdateView, SendEmailView, SearchClientToReplaceView, SearchClientToMergeView, \
    ClientMergeView, CreateEmailView, EditEmailView, DeleteEmailView

urlpatterns = [
    url(r'^new/$', CreateClientView.as_view(), name="client-new"),
    url(r'^view/(?P<pk>\d+)/$', ClientView.as_view(), name="client-view"),
    url(r'^edit/(?P<pk>\d+)/$', EditClientView.as_view(), name="client-edit"),
    url(r'^address/new/(?P<id>\d+)/$', CreateAddressView.as_view(), name="client-address-new"),
    url(r'^address/add/(?P<id>\d+)/$', CreateAddressView.as_view(), name="client-address-add"),
    url(r'^address/edit/(?P<pk>\d+)/$', EditAddressView.as_view(), name="client-address-edit"),
    url(r'^address/edit/geo/(?P<pk>\d+)/$', AddressGeoUpdateView.as_view(), name="client-address-edit-geo"),
    url(r'^address/delete/(?P<pk>\d+)/$', DeleteAddresView.as_view(), name="client-address-delete"),
    url(r'^phone/new/(?P<id>\d+)/$', CreatePhoneView.as_view(), name="client-phone-new"),
    url(r'^phone/add/(?P<id>\d+)/$', CreatePhoneView.as_view(), name="client-phone-add"),
    url(r'^phone/delete/(?P<pk>\d+)/$', DeletePhoneView.as_view(), name="client-phone-delete"),
    url(r'^phone/edit/(?P<pk>\d+)/$', EditPhoneView.as_view(), name="client-phone-edit"),
    url(r'^email/new/(?P<id>\d+)/$', CreateEmailView.as_view(), name="client-email-new"),
    url(r'^email/edit/(?P<pk>\d+)/$', EditEmailView.as_view(), name="client-email-edit"),
    url(r'^email/delete/(?P<pk>\d+)/$', DeleteEmailView.as_view(), name="client-email-delete"),
    url(r'^sms/send/$', SendSMSView.as_view(), name="client-sms-send"),
    url(r'^email/send/$', SendEmailView.as_view(), name="client-email-send"),
    url(r'^all/$', AllClientsView.as_view(), name="client-all"),
    url(r'^psearch/$', PreSearchClientView.as_view(), name="client-psearch"),
    url(r'^search/$', SearchClientView.as_view(), name="client-search"),
    url(r'^merge/step1/$', SearchClientToReplaceView.as_view(), name="client-merge-step1"),
    url(r'^merge/step2/(?P<pk>\d+)/$', SearchClientToMergeView.as_view(), name="client-merge-step2"),
    url(r'^merge/step3/(?P<pk1>\d+)/(?P<pk2>\d+)/$', ClientMergeView.as_view(), name="client-merge-step3"),
]
