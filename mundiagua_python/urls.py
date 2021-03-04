from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.urls import include, path
from client.views import PublicClientView, RedirectOldClientView
from core.forms import MundiaguaLoginForm, MundiaguaChangePasswordForm
from core.views import IndexView, LogoutView, LoginErrorView, LoginView

urlpatterns = [
    path('spectrum/', admin.site.urls),
    path('intervention/', include(('intervention.urls', 'intervention'), namespace='intervention')),
    path('client/', include(('client.urls', 'client'), namespace='client')),
    path('budget/', include(('budget.urls', 'budget'), namespace='budget')),
    path('repair/', include(('repair.urls', 'repair'), namespace='repair')),
    path('engine/', include(('engine.urls', 'engine'), namespace='engine')),
    path('core/', include(('core.urls', 'core'), namespace='core')),
    path('', include('social_django.urls')),
    path('login/logout/', LogoutView.as_view(), name="logout"),
    path('login/error/', LoginErrorView.as_view()),
    path('login/', LoginView.as_view()),
    path('', IndexView.as_view(), name='home'),
    path('repair-status/<online>/', PublicClientView.as_view(), name="public-status-repair"),
    path('clientes/', RedirectOldClientView.as_view(), name="old-status-repair"),
    path('hijack/', include(('hijack.urls', 'hijack'))),
    path('tinymce/', include('tinymce.urls')),
    path('api/', include('mundiagua_python.api_urls')),
    path(
        'user/password/',
        PasswordChangeView.as_view(
            template_name='password_change.html',
            success_url='/user/password-done/',
            form_class=MundiaguaChangePasswordForm),
        name='password-change'
    ),
    path(
        'user/password-done/',
        PasswordChangeDoneView.as_view(
            template_name='password_change_done.html'
        ),
        name='password-change-done'),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
