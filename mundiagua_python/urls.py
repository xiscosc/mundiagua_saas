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
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login, logout

from core.views import IndexView, NewMessageView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^intervention/', include('intervention.urls', namespace="intervention")),
    url(r'^client/', include('client.urls', namespace="client")),
    url(r'^budget/', include('budget.urls', namespace="budget")),
    url(r'^repair/', include('repair.urls', namespace="repair")),
    url(r'^login/$', login, name='login', kwargs={'template_name': 'login.html'}),
    url(r'^logout/$', logout, name='logout', kwargs={'template_name': 'logout.html'}),
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^message/new/$', NewMessageView.as_view(), name="message-new")
]

