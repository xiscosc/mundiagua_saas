from django.contrib import admin

# Register your models here.
from client.models import Client, SMS, WhatsAppTemplate

admin.site.register(Client)
admin.site.register(WhatsAppTemplate)
admin.site.register(SMS)
