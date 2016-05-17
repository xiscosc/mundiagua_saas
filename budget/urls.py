from django.conf.urls import url
from .views import SearchClientView, CreateBudgetView

urlpatterns = [
    url(r'^search-client/$', SearchClientView.as_view(), name="budget-search-client"),
    url(r'^new/(?P<id>\d+)/$', CreateBudgetView.as_view(), name="budget-new"),
]