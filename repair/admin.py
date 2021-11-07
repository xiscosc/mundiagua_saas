from django.contrib import admin

# Register your models here.
from repair.models import AthRepair, IdegisRepair, ZodiacRepair, ZodiacRepairLog, AthRepairLog, IdegisRepairLog, \
    RepairStatus

admin.site.register(AthRepair)
admin.site.register(AthRepairLog)
admin.site.register(ZodiacRepair)
admin.site.register(ZodiacRepairLog)
admin.site.register(IdegisRepair)
admin.site.register(IdegisRepairLog)
admin.site.register(RepairStatus)
