# API URLS
from django.urls import path, include

urlpatterns = [
    path('v1/repairs/', include(('repair.api.public.v1.urls', 'repair'), namespace='api-v1-repairs')),
]