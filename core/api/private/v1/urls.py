from django.urls import path
from core.api.private.v1 import views

urlpatterns = [
    path(r'user/allowed', views.UserIsAllowedToLoginView.as_view()),
]
