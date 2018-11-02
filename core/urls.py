from django.urls import path
from .views import SystemVariableView, SystemVariableUpdateView, ChangeLogView, UserView, RepairStatusSystemView, \
    SystemRepairStatusUpdateView, SystemRepairStatusCreateView, EngineRepairStatusSystemView, \
    SystemEngineRepairStatusUpdateView, SystemEngineRepairStatusCreateView

urlpatterns = [
    path('variable/', SystemVariableView.as_view(), name="variable"),
    path('variable/edit/<pk>', SystemVariableUpdateView.as_view(), name="variable-edit"),
    path('changelog/', ChangeLogView.as_view(), name="changelog"),
    path('user/', UserView.as_view(), name="user-manage"),
    path('repairstatus/', RepairStatusSystemView.as_view(), name="repair-status"),
    path('repairstatus/edit/<pk>', SystemRepairStatusUpdateView.as_view(), name="repair-status-edit"),
    path('repairstatus/new/', SystemRepairStatusCreateView.as_view(), name="repair-status-new"),
    path('enginerepairstatus/', EngineRepairStatusSystemView.as_view(), name="engine-repair-status"),
    path('enginerepairstatus/edit/<pk>', SystemEngineRepairStatusUpdateView.as_view(), name="engine-repair-status-edit"),
    path('enginerepairstatus/new/', SystemEngineRepairStatusCreateView.as_view(), name="engine-repair-status-new"),
]
