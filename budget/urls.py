from django.conf.urls import url
from .views import SearchClientView, CreateBudgetView, CreateLineBudgetView

urlpatterns = [
    url(r'^search-client/$', SearchClientView.as_view(), name="budget-search-client"),
    url(r'^new/(?P<id>\d+)/$', CreateBudgetView.as_view(), name="budget-new"),
    url(r'^new/lines/(?P<pk>\d+)/$', CreateLineBudgetView.as_view(), name="budget-new-lines"),
]