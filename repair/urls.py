from django.conf.urls import url

from .views import SearchClientView, CreateAthRepairView, CreateIdegisRepairView, AthRepairView, IdegisRepairView, \
    UpdateStatusRepair, ListRepairView, PreSearchRepairView, SearchRepairView, PrintRepairView, ToggleStarredRepairView, \
    LinkInterventionView, UnlinkInterventionView, CreateZodiacRepairView, ZodiacRepairView, RepairFilesView, \
    RepairFileView, RepairFileDownloadView

urlpatterns = [
    url(r'^search-client/$', SearchClientView.as_view(), name="repair-search-client"),
    url(r'^ath/new/(?P<id>\d+)/$', CreateAthRepairView.as_view(), name="repair-ath-new"),
    url(r'^idegis/new/(?P<id>\d+)/$', CreateIdegisRepairView.as_view(), name="repair-idegis-new"),
    url(r'^zodiac/new/(?P<id>\d+)/$', CreateZodiacRepairView.as_view(), name="repair-zodiac-new"),
    url(r'^ath/view/(?P<pk>\d+)/$', AthRepairView.as_view(), name="repair-ath-view"),
    url(r'^idegis/view/(?P<pk>\d+)/$', IdegisRepairView.as_view(), name="repair-idegis-view"),
    url(r'^zodiac/view/(?P<pk>\d+)/$', ZodiacRepairView.as_view(), name="repair-zodiac-view"),
    url(r'^status/(?P<pk>\d+)/$', UpdateStatusRepair.as_view(), name="repair-update-status"),
    url(r'^list/(?P<type>all|idegis|ath|zodiac)/(?P<status_id>\d+)/(?P<budget>\d+)/(?P<starred>\d+)/$',
        ListRepairView.as_view(), name="repair-list"),
    url(r'^psearch/$', PreSearchRepairView.as_view(), name="repair-psearch"),
    url(r'^search/(?P<type>all|idegis|ath|zodiac)/(?P<starred>\d+)/$', SearchRepairView.as_view(),
        name="repair-search"),
    url(r'^print/(?P<logo>\d+)/(?P<type>idegis|ath|zodiac)/(?P<pk>\d+)/$', PrintRepairView.as_view(),
        name="repair-print"),
    url(r'^starred/(?P<type>idegis|ath|zodiac)/(?P<pk>\d+)/$', ToggleStarredRepairView.as_view(),
        name="repair-starred"),
    url(r'^link/(?P<pk>\d+)/(?P<type>idegis|ath|zodiac)/$', LinkInterventionView.as_view(),
        name="repair-link-intervention"),
    url(r'^unlink/(?P<pk>\d+)/(?P<type>idegis|ath|zodiac)/(?P<pk_intervention>\d+)/(?P<to_repair>\d+)/$',
        UnlinkInterventionView.as_view(),
        name="repair-unlink-intervention"),
    url(r'^files/(?P<pk>\d+)/(?P<type>idegis|ath|zodiac)/(?P<file_type>document|image)/$',
        RepairFilesView.as_view(), name="repair-files"),
    url(r'files/(?P<pk>\d+)/(?P<type>idegis|ath|zodiac)/(?P<file_type>document|image)/(?P<file_id>[0-9a-f-]+)/$',
        RepairFileView.as_view(), name="repair-file"),
    url(r'files/(?P<pk>\d+)/(?P<type>idegis|ath|zodiac)/(?P<file_type>document|image)/(?P<file_id>[0-9a-f-]+)/download/$',
        RepairFileDownloadView.as_view(), name="repair-file-download")
]
