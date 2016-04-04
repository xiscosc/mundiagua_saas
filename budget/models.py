from __future__ import unicode_literals

from django.db import models


class Budget(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.User')
    introduction = models.TextField()
    conditions = models.TextField()
    content = models.TextField()
    tax = models.IntegerField(default=21)
    address = models.ForeignKey('client.Address')
    invalid = models.BooleanField(default=False)