from django.conf.urls import url
from .views import SearchClientView, CreateAthRepairView, CreateIdegisRepairView

urlpatterns = [
    url(r'^search-client/$', SearchClientView.as_view(), name="repair-search-client"),
    url(r'^ath/new/(?P<id>\d+)/$', CreateAthRepairView.as_view(), name="repair-ath-new"),
    url(r'^idegis/new/(?P<id>\d+)/$', CreateIdegisRepairView.as_view(), name="repair-idegis-new"),
]