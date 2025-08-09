from django.conf.urls import url
from .views import SearchClientView, CreateEngineRepairView, EngineRepairView, UpdateStatusEngineRepair, \
    PrintEngineRepairView, PreSearchEngineRepairView, SearchEngineRepairView, ListEngineRepairView

urlpatterns = [
    # url(r'^search-client/$', SearchClientView.as_view(), name="engine-search-client"),
    # url(r'^new/(?P<id>\d+)/$', CreateEngineRepairView.as_view(), name="engine-new"),
    # url(r'^view/(?P<pk>\d+)/$', EngineRepairView.as_view(), name="engine-view"),
    # url(r'^status/(?P<pk>\d+)/$', UpdateStatusEngineRepair.as_view(), name="engine-update-status"),
    # url(r'^print/(?P<logo>\d+)/(?P<pk>\d+)/$', PrintEngineRepairView.as_view(), name="engine-print"),
    # url(r'^psearch/$', PreSearchEngineRepairView.as_view(), name="engine-psearch"),
    # url(r'^search/$', SearchEngineRepairView.as_view(), name="engine-search"),
    # url(r'^list/$', ListEngineRepairView.as_view(), name="engine-all"),
]
