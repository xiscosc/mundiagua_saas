from django.conf.urls import url
from .views import SearchClientView, CreateAthRepairView, CreateIdegisRepairView, AthRepairView, IdegisRepairView, \
    UpdateStatusRepair, ListRepairView, PreSearchRepairView, SearchRepairView

urlpatterns = [
    url(r'^search-client/$', SearchClientView.as_view(), name="repair-search-client"),
    url(r'^ath/new/(?P<id>\d+)/$', CreateAthRepairView.as_view(), name="repair-ath-new"),
    url(r'^idegis/new/(?P<id>\d+)/$', CreateIdegisRepairView.as_view(), name="repair-idegis-new"),
    url(r'^ath/view/(?P<pk>\d+)/$', AthRepairView.as_view(), name="repair-ath-view"),
    url(r'^idegis/view/(?P<pk>\d+)/$', IdegisRepairView.as_view(), name="repair-idegis-view"),
    url(r'^status/(?P<pk>\d+)/$', UpdateStatusRepair.as_view(), name="repair-update-status"),
    url(r'^list/(?P<type>\d+)/$', ListRepairView.as_view(), name="repair-list"),
    url(r'^psearch/$', PreSearchRepairView.as_view(), name="repair-psearch"),
    url(r'^search/(?P<type>\d+)/$', SearchRepairView.as_view(), name="repair-search"),

]
