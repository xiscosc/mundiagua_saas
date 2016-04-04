from __future__ import unicode_literals

from django.db import models
from colorfield.fields import ColorField


class InterventionStatus(models.Model):
    name = models.CharField(max_length=50)


class Zone(models.Model):
    name = models.CharField(max_length=50)
    color = ColorField(default='#FF0000')


class Intervention(models.Model):
    description = models.TextField()
    address = models.ForeignKey('client.Address')
    date = models.DateTimeField(auto_now_add=True)
    zone = models.ForeignKey(Zone)
    status = models.ForeignKey(InterventionStatus, default=1)
    created_by = models.ForeignKey('core.User', related_name='%(class)s_by')
    assigned = models.ForeignKey('core.User', blank=True, related_name='%(class)s_assigned')
    note = models.TextField(blank=True)


class InterventionModification(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey('core.User')
    intervention = models.ForeignKey(Intervention)


class InterventionLog(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.User', related_name='%(class)s_by')
    assigned = models.ForeignKey('core.User', blank=True, related_name='%(class)s_assigned')
    status = models.ForeignKey(InterventionStatus)