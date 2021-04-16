from django.urls import include, path

urlpatterns = [
    path('private/', include(('core.api.private.v1.urls', 'core')))
]
