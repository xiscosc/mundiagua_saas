from django.contrib import admin

# Register your models here.
from core.models import Message, User

admin.site.register(Message)
admin.site.register(User)