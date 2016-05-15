from django.conf.urls import url
from .views import HomeView, SearchClientView, CreateInterventionView, InterventionView, UpdateInterventionView, \
    ListInterventionView, TerminateIntervention, SearchInterventionView, PreSearchInterventionView, ListModificationView, MorrisInterventionAssigned, MorrisInterventionInput

urlpatterns = [
    url(r'^home/$', HomeView.as_view(), name="intervention-home"),
    url(r'^search-client/$', SearchClientView.as_view(), name="intervention-search-client"),
    url(r'^new/(?P<id>\d+)/$', CreateInterventionView.as_view(), name="intervention-new"),
    url(r'^view/(?P<pk>\d+)/$', InterventionView.as_view(), name="intervention-view"),
    url(r'^edit/(?P<pk>\d+)/$', UpdateInterventionView.as_view(), name="intervention-edit"),
    url(r'^terminate/(?P<pk>\d+)/$', TerminateIntervention.as_view(), name="intervention-terminate"),
    url(r'^list/(?P<intervention_status>\d+)/(?P<user_assigned>\d+)/(?P<zone_assigned>\d+)/$',
        ListInterventionView.as_view(), name="intervention-list"),
    url(r'^psearch/$', PreSearchInterventionView.as_view(), name="intervention-psearch"),
    url(r'^search/$', SearchInterventionView.as_view(), name="intervention-search"),
    url(r'^modifications/$', ListModificationView.as_view(), name="intervention-modifications"),
    url(r'^morris/assigned/$', MorrisInterventionAssigned.as_view(), name="intervention-morris-assigned"),
    url(r'^morris/input/$', MorrisInterventionInput.as_view(), name="intervention-morris-input"),
]
