from django.contrib import admin

# Register your models here.
from engine.models import EngineRepair, EngineStatus, EngineRepairLog

admin.site.register(EngineRepair)
admin.site.register(EngineStatus)
admin.site.register(EngineRepairLog)
