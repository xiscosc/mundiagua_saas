from django.urls import include, path
from rest_framework import routers
from repair.api.public.v1 import views

public_router = routers.DefaultRouter()
public_router.register(r'status', views.RepairStatusViewSet, basename="repair-status")

urlpatterns = [
    path('public/', include(public_router.urls)),
]