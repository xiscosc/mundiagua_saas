from django.conf.urls import url
from .views import SearchClientView, CreateBudgetView, CreateLineBudgetView, TypeAheadBudgetView, BudgetDetailView, \
    EditLineBudgetView, ListBudgetView, PreSearchBudgetView, SearchBudgetView

urlpatterns = [
    url(r'^search-client/$', SearchClientView.as_view(), name="budget-search-client"),
    url(r'^typeahead/$', TypeAheadBudgetView.as_view(), name="budget-typeahead"),
    url(r'^new/(?P<id>\d+)/$', CreateBudgetView.as_view(), name="budget-new"),
    url(r'^new/lines/(?P<pk>\d+)/$', CreateLineBudgetView.as_view(), name="budget-new-lines"),
    url(r'^edit/lines/(?P<pk>\d+)/$', EditLineBudgetView.as_view(), name="budget-edit-lines"),
    url(r'^view/(?P<pk>\d+)/$', BudgetDetailView.as_view(), name="budget-view"),
    url(r'^list/$', ListBudgetView.as_view(), name="budget-all"),
    url(r'^psearch/$', PreSearchBudgetView.as_view(), name="budget-psearch"),
    url(r'^search/$', SearchBudgetView.as_view(), name="budget-search"),

]
