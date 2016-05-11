from django.conf.urls import url
from .views import HomeView, SearchClientView, CreateInterventionView, InterventionView, UpdateInterventionView, ListInterventionView, TerminateIntervention

urlpatterns = [
    url(r'^home/$', HomeView.as_view(), name="intervention-home"),
    url(r'^search-client/$', SearchClientView.as_view(), name="intervention-search-client"),
    url(r'^new/(?P<id>\d+)/$', CreateInterventionView.as_view(), name="intervention-new"),
    url(r'^view/(?P<pk>\d+)/$', InterventionView.as_view(), name="intervention-view"),
    url(r'^edit/(?P<pk>\d+)/$', UpdateInterventionView.as_view(), name="intervention-edit"),
    url(r'^terminate/(?P<pk>\d+)/$', TerminateIntervention.as_view(), name="intervention-terminate"),
    url(r'^list/(?P<intervention_status>\d+)/(?P<user>\d+)/(?P<zone>\d+)/(?P<page>\d+)/$', ListInterventionView.as_view(), name="intervention-list"),
]
