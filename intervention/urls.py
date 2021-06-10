from django.conf.urls import url
from django.conf import settings
from django.views.decorators.cache import cache_page

from .views import HomeView, SearchClientView, CreateInterventionView, InterventionView, UpdateInterventionView, \
    ListInterventionView, TerminateIntervention, SearchInterventionView, PreSearchInterventionView, \
    ListModificationView, MorrisInterventionAssigned, MorrisInterventionInput, PrintInterventionView, \
    PrintListInterventionView, MorrisYearVs, OwnListInterventionView, UploadImageView, UploadDocumentView, \
    ToggleStarredInterventionView, BillIntervention, AddStatusJobView, ReportInterventionView, MapInterventionView, \
    MapAssignedInterventionView, ForbiddenInterventionView, EditInterventionView, DocumentView, \
    RemoveFileView, MakeVisibleDocumentView, LinkToInterventionView, ImageUrlView

urlpatterns = [
    url(r'^home/$', HomeView.as_view(), name="intervention-home"),
    url(r'^search-client/$', SearchClientView.as_view(), name="intervention-search-client"),
    url(r'^new/(?P<id>\d+)/$', CreateInterventionView.as_view(), name="intervention-new"),
    url(r'^view/(?P<pk>\d+)/$', InterventionView.as_view(), name="intervention-view"),
    url(r'^edit/(?P<pk>\d+)/$', UpdateInterventionView.as_view(), name="intervention-edit"),
    url(r'^terminate/(?P<pk>\d+)/$', TerminateIntervention.as_view(), name="intervention-terminate"),
    url(r'^bill/(?P<pk>\d+)/$', BillIntervention.as_view(), name="intervention-bill"),
    url(
        r'^list/(?P<intervention_status>\d+)/(?P<user_assigned>\d+)/(?P<zone_assigned>\d+)/(?P<starred>\d+)/(?P<tag_assigned>\d+)/$',
        ListInterventionView.as_view(), name="intervention-list"),
    url(r'^psearch/$', PreSearchInterventionView.as_view(), name="intervention-psearch"),
    url(r'^search/$', SearchInterventionView.as_view(), name="intervention-search"),
    url(r'^modifications/$', ListModificationView.as_view(), name="intervention-modifications"),
    url(r'^morris/assigned/$', cache_page(settings.CACHE_TIME_CHARTS)(MorrisInterventionAssigned.as_view()),
        name="intervention-morris-assigned"),
    url(r'^morris/input/$', cache_page(settings.CACHE_TIME_CHART_INCOME)(MorrisInterventionInput.as_view()),
        name="intervention-morris-input"),
    url(r'^morris/yearvs/$', cache_page(settings.CACHE_TIME_CHARTS)(MorrisYearVs.as_view()),
        name="intervention-morris-yearvs"),
    url(r'^print/(?P<pk>\d+)/$', PrintInterventionView.as_view(), name="intervention-print"),
    url(
        r'^print/list/(?P<intervention_status>\d+)/(?P<user_assigned>\d+)/(?P<zone_assigned>\d+)/(?P<starred>\d+)/(?P<tag_assigned>\d+)/$',
        PrintListInterventionView.as_view(), name="intervention-print-list"),
    url(r'^list/own/$',
        OwnListInterventionView.as_view(), name="intervention-list-own"),
    url(r'^new/image/(?P<pk>\d+)/$', UploadImageView.as_view(), name="intervention-image-upload"),
    url(r'^new/document/(?P<pk>\d+)/$', UploadDocumentView.as_view(), name="intervention-document-upload"),
    url(r'^starred/(?P<pk>\d+)/$', ToggleStarredInterventionView.as_view(), name="intervention-starred"),
    url(r'^status-job/(?P<pk>\d+)/$', AddStatusJobView.as_view(), name="intervention-status-job"),
    url(r'^reports/$', ReportInterventionView.as_view(), name="intervention-reports"),
    url(r'^map/$', MapInterventionView.as_view(), name="intervention-map"),
    url(r'^map/(?P<pk>\d+)/$', MapAssignedInterventionView.as_view(), name="intervention-map-assigned"),
    url(r'^forbidden/$', ForbiddenInterventionView.as_view(), name="intervention-forbidden"),
    url(r'^edit-data/(?P<pk>\d+)/$', EditInterventionView.as_view(), name="intervention-edit-data"),
    url(r'^getimageurl/(?P<key>.+)/$', ImageUrlView.as_view(), name="intervention-view-image-url"),
    url(r'^viewdocument/(?P<key>.+)/$', DocumentView.as_view(), name="intervention-view-document"),
    url(r'^removefile/(?P<pk>\d+)/$', RemoveFileView.as_view(), name="intervention-remove-file"),
    url(r'^makevisibledocument/(?P<pk>\d+)/$', MakeVisibleDocumentView.as_view(), name="intervention-make-document-visible"),
    url(r'^link/(?P<pk>\d+)/$', LinkToInterventionView.as_view(), name="intervention-link")
    ]
