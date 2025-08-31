from django.urls import path
from .views import SystemVariableView, SystemVariableUpdateView, ChangeLogView, UserView, RepairStatusSystemView, \
    SystemRepairStatusUpdateView, SystemRepairStatusCreateView, EngineRepairStatusSystemView, \
    SystemEngineRepairStatusUpdateView, SystemEngineRepairStatusCreateView, GetAllSmsView, GetSmsBySenderView, \
    GetSmsView, SMSListView, SMSSenderListView, NotifySmsView, LinkUserTelegramView, UnlinkUserTelegramView, \
    LinkUserTelegramDoneView

urlpatterns = [
    path('variable/', SystemVariableView.as_view(), name="variable"),
    path('variable/edit/<pk>', SystemVariableUpdateView.as_view(), name="variable-edit"),
    path('changelog/', ChangeLogView.as_view(), name="changelog"),
    path('user/', UserView.as_view(), name="user-manage"),
    # path('user/telegram/unlink', UnlinkUserTelegramView.as_view(), name="user-manage-telegram-unlink"),
    # path('user/telegram/link', LinkUserTelegramView.as_view(), name="user-manage-telegram-link"),
    # path('user/telegram/link/done', LinkUserTelegramDoneView.as_view(), name="user-manage-telegram-link-done"),
    path('repairstatus/', RepairStatusSystemView.as_view(), name="repair-status"),
    path('repairstatus/edit/<pk>', SystemRepairStatusUpdateView.as_view(), name="repair-status-edit"),
    path('repairstatus/new/', SystemRepairStatusCreateView.as_view(), name="repair-status-new"),
    path('enginerepairstatus/', EngineRepairStatusSystemView.as_view(), name="engine-repair-status"),
    path('enginerepairstatus/edit/<pk>', SystemEngineRepairStatusUpdateView.as_view(),
         name="engine-repair-status-edit"),
    path('enginerepairstatus/new/', SystemEngineRepairStatusCreateView.as_view(), name="engine-repair-status-new"),
    # path('sms-api/sms/all/list', GetAllSmsView.as_view(), name="sms-api-all"),
    # path('sms-api/sms/sender/<sender>', GetSmsBySenderView.as_view(), name="sms-api-sender"),
    # path('sms-api/sms/<id>', GetSmsView.as_view(), name="sms-api-id"),
    # path('sms-gsm', SMSListView.as_view(), name="sms-gsm"),
    # path('sms-gsm/sender/<sender>', SMSSenderListView.as_view(), name="sms-gsm-sender"),
    # path('sms-gsm/notify', NotifySmsView.as_view(), name="sms-gsm-notify"),
]
