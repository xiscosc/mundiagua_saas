from django.contrib import admin

# Register your models here.
from intervention.models import Zone, Intervention, InterventionStatus, InterventionSubStatus, Tag, \
    InterventionDocument, InterventionImage

admin.site.register(Zone)
admin.site.register(Intervention)
admin.site.register(InterventionStatus)
admin.site.register(InterventionSubStatus)
admin.site.register(InterventionDocument)
admin.site.register(InterventionImage)
admin.site.register(Tag)
