from rest_framework import routers
from repair.api.public.v1 import views

router = routers.DefaultRouter()
router.register(r'status', views.RepairStatusViewSet, basename="repair-status")
urlpatterns = router.urls
