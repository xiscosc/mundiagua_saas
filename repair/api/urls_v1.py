from django.urls import include, path

urlpatterns = [
    path('public/', include(('repair.api.public.v1.urls', 'repair')))
]