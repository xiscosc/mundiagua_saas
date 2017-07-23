"""mundiagua_python URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordChangeDoneView

from core.views import IndexView, NewMessageView, MessagesListView, MessagesSentListView, MessagesAjaxView, \
    ChangeLogView, UserView, GoogleLoginView, GoogleProcessView, GoogleErrorView, LoginPasswordView
from client.views import PublicClientView, RedirectOldClientView
from core.forms import MundiaguaLoginForm, MundiaguaChangePasswordForm

urlpatterns = [
    url(r'^admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    url(r'^spectrum/', include(admin.site.urls)),
    url(r'^intervention/', include('intervention.urls', namespace="intervention")),
    url(r'^client/', include('client.urls', namespace="client")),
    url(r'^budget/', include('budget.urls', namespace="budget")),
    url(r'^repair/', include('repair.urls', namespace="repair")),
    url(r'^engine/', include('engine.urls', namespace="engine")),
    url(r'^user/$', UserView.as_view(), name="user-manage"),
    url(r'^login/$', LoginPasswordView.as_view(template_name='login.html', authentication_form=MundiaguaLoginForm),
        name="login"),
    url(r'^login/google/$', GoogleLoginView.as_view(), name='login-google'),
    url(r'^login/google/process/$', GoogleProcessView.as_view(), name='login-google-process'),
    url(r'^login/google/error/$', GoogleErrorView.as_view(), name='login-google-error'),
    url(r'^logout/$', LogoutView.as_view(template_name="logout.html"), name='logout'),
    url(r'^user/password/$',
        PasswordChangeView.as_view(template_name='password_change.html', success_url='/user/password-done/',
                                   form_class=MundiaguaChangePasswordForm), name='password-change'),
    url(r'^user/password-done/$', PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
        name='password-change-done'),
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^message/new/$', NewMessageView.as_view(), name="message-new"),
    url(r'^message/inbox/$', MessagesListView.as_view(), name="message-inbox"),
    url(r'^message/sent/$', MessagesSentListView.as_view(), name="message-sent"),
    url(r'^message/ajax/$', MessagesAjaxView.as_view(), name="message-ajax"),
    url(r'^repair-status/(?P<online>\w+)/$', PublicClientView.as_view(), name="public-status-repair"),
    url(r'^clientes/$', RedirectOldClientView.as_view(), name="old-status-repair"),
    url(r'^hijack/', include('hijack.urls')),
    url(r'^changelog/$', ChangeLogView.as_view(), name="changelog"),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
