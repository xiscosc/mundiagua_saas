from django.contrib import admin

# Register your models here.
from core.models import Message

admin.site.register(Message)