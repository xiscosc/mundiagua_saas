from django.conf.urls import url
from .views import SearchClientView, CreateBudgetView, CreateLineBudgetView, TypeAheadBudgetView, BudgetDetailView, \
    EditLineBudgetView, ListBudgetView, PreSearchBudgetView, SearchBudgetView, ListBudgetRepairView, \
    CreateBudgetRepairView, CreateLineBudgetRepairView, BudgetRepairDetailView, EditLineBudgetRepairView, \
    BudgetPrintView, BudgetRepairPrintView

urlpatterns = [
    url(r'^search-client/$', SearchClientView.as_view(), name="budget-search-client"),
    url(r'^typeahead/$', TypeAheadBudgetView.as_view(), name="budget-typeahead"),
    url(r'^new/(?P<id>\d+)/$', CreateBudgetView.as_view(), name="budget-new"),
    url(r'^new/lines/(?P<pk>\d+)/$', CreateLineBudgetView.as_view(), name="budget-new-lines"),
    url(r'^edit/lines/(?P<pk>\d+)/$', EditLineBudgetView.as_view(), name="budget-edit-lines"),
    url(r'^view/(?P<pk>\d+)/$', BudgetDetailView.as_view(), name="budget-view"),
    url(r'^list/$', ListBudgetView.as_view(), name="budget-all"),
    url(r'^list/repair/(?P<type>\d+)/(?P<pk>\d+)/$', ListBudgetRepairView.as_view(), name="budget-repair-list"),
    url(r'^new/repair/(?P<type>\d+)/(?P<pk>\d+)/$', CreateBudgetRepairView.as_view(), name="budget-repair-new"),
    url(r'^new/repair/lines/(?P<pk>\d+)/$', CreateLineBudgetRepairView.as_view(), name="budget-repair-new-lines"),
    url(r'^edit/repair/lines/(?P<pk>\d+)/$', EditLineBudgetRepairView.as_view(), name="budget-repair-edit-lines"),
    url(r'^view/repair/(?P<pk>\d+)/$', BudgetRepairDetailView.as_view(), name="budget-repair-view"),
    url(r'^print/(?P<logo>\d+)/(?P<pk>\d+)/$', BudgetPrintView.as_view(), name="budget-print"),
    url(r'^print/repair/(?P<logo>\d+)/(?P<type>\d+)/(?P<pk>\d+)/$', BudgetRepairPrintView.as_view(), name="budget-repair-print"),
    url(r'^psearch/$', PreSearchBudgetView.as_view(), name="budget-psearch"),
    url(r'^search/$', SearchBudgetView.as_view(), name="budget-search"),

]
