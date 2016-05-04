from django.conf.urls import url
from .views import HomeView, SearchClientView, CreateInterventionView, InterventionView, UpdateInterventionView

urlpatterns = [
    url(r'^home/$', HomeView.as_view(), name="intervention-home"),
    url(r'^search-client/$', SearchClientView.as_view(), name="intervention-search-client"),
    url(r'^new/(?P<id>\d+)/$', CreateInterventionView.as_view(), name="intervention-intervention-new"),
    url(r'^view/(?P<pk>\d+)/$', InterventionView.as_view(), name="intervention-intervention"),
    url(r'^view/(?P<pk>\d+)/(?P<edited>\d+)/$', InterventionView.as_view(), name="intervention-intervention-edited"),
    url(r'^edit/(?P<pk>\d+)/$', UpdateInterventionView.as_view(), name="intervention-edit"),
]
