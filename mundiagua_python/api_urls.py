# API URLS
from django.urls import path, include

urlpatterns = [
    path('v1/repairs/', include(('repair.api.urls_v1', 'repair'), namespace='api-v1-repairs')),
    path('v1/core/', include(('core.api.urls_v1', 'core'), namespace='api-v1-core')),
]