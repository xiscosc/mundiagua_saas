from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from client.views import RedirectOldClientView
from core.views import IndexView, LogoutView, PrivacyView, LoginErrorView, LoginErrorAuthView, LoginView,\
    RedirectLoginView

urlpatterns = [
    path('spectrum/', admin.site.urls),
    path('intervention/', include(('intervention.urls', 'intervention'), namespace='intervention')),
    path('client/', include(('client.urls', 'client'), namespace='client')),
    path('budget/', include(('budget.urls', 'budget'), namespace='budget')),
    path('repair/', include(('repair.urls', 'repair'), namespace='repair')),
    path('engine/', include(('engine.urls', 'engine'), namespace='engine')),
    path('core/', include(('core.urls', 'core'), namespace='core')),
    path('uas/', include('social_django.urls')),
    path('privacy/', PrivacyView.as_view(), name="privacy"),
    path('login/logout/', LogoutView.as_view(), name="logout"),
    path('login/error/', LoginErrorView.as_view()),
    path('login/error-auth/', LoginErrorAuthView.as_view()),
    path('login/google/', RedirectLoginView.as_view()),
    path('login/password/', RedirectLoginView.as_view()),
    path('login/', LoginView.as_view(), name="login"),
    path('', IndexView.as_view(), name='home'),
    path('clientes/', RedirectOldClientView.as_view(), name="old-status-repair"),
    path('hijack/', include(('hijack.urls', 'hijack'))),
    path('tinymce/', include('tinymce.urls')),
    path('api/', include('mundiagua_python.api_urls')),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)