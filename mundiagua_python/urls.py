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
from django.contrib.auth.views import login, logout

from core.views import IndexView, NewMessageView, MessagesListView, MessagesSentListView, MessagesAjaxView

urlpatterns = [
    url(r'^admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    url(r'^spectrum/', include(admin.site.urls)),
    url(r'^intervention/', include('intervention.urls', namespace="intervention")),
    url(r'^client/', include('client.urls', namespace="client")),
    url(r'^budget/', include('budget.urls', namespace="budget")),
    url(r'^repair/', include('repair.urls', namespace="repair")),
    url(r'^engine/', include('engine.urls', namespace="engine")),
    url(r'^login/$', login, name='login', kwargs={'template_name': 'login.html'}),
    url(r'^logout/$', logout, name='logout', kwargs={'template_name': 'logout.html'}),
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^message/new/$', NewMessageView.as_view(), name="message-new"),
    url(r'^message/inbox/$', MessagesListView.as_view(), name="message-inbox"),
    url(r'^message/sent/$', MessagesSentListView.as_view(), name="message-sent"),
    url(r'^message/ajax/$', MessagesAjaxView.as_view(), name="message-ajax"),
    url(r'^hijack/', include('hijack.urls')),
]


if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)