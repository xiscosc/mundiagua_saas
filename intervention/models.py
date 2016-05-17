# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from async_messages import message_user, constants
from django.core.urlresolvers import reverse_lazy
from django.db import models
from colorfield.fields import ColorField
from django.db.models.signals import post_save
from django.conf import settings

from core.utils import send_data_to_user


class InterventionStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name.encode('utf8')


class Zone(models.Model):
    name = models.CharField(max_length=50)
    color = ColorField(default='#FF0000')

    def __str__(self):
        return self.name.encode('utf8')


class Intervention(models.Model):
    description = models.TextField(verbose_name="Descripción")
    address = models.ForeignKey('client.Address', verbose_name="Dirección")
    date = models.DateTimeField(auto_now_add=True)
    zone = models.ForeignKey(Zone, default=1, verbose_name="Zona")
    status = models.ForeignKey(InterventionStatus, default=1)
    created_by = models.ForeignKey('core.User', related_name='%(class)s_by')
    assigned = models.ForeignKey('core.User', null=True, related_name='%(class)s_assigned')
    note = models.TextField(null=True)

    def __str__(self):
        return "V" + str(self.pk)

    def get_history(self):
        return InterventionLog.objects.filter(intervention=self)

    def get_modifications(self):
        return InterventionModification.objects.filter(intervention=self)

    def generate_url(self):
        intern_url = str(reverse_lazy('intervention:intervention-view', kwargs={'pk': self.pk}))
        return settings.DOMAIN + intern_url

    def send_to_user(self, user):
        return send_data_to_user(is_link=True, body=self.generate_url(), user=user,
                          subject=str(self) + " - " + self.address.client.name)

    def get_num_modifications(self):
        return InterventionModification.objects.filter(intervention=self).count()


class InterventionModification(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True)
    created_by = models.ForeignKey('core.User')
    intervention = models.ForeignKey(Intervention)


class InterventionLog(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.User', related_name='%(class)s_by')
    assigned = models.ForeignKey('core.User', null=True, related_name='%(class)s_assigned')
    status = models.ForeignKey(InterventionStatus)
    intervention = models.ForeignKey(Intervention)


def post_save_intervention(sender, **kwargs):
    intervention = kwargs['instance']
    if kwargs['created']:
        log = InterventionLog(created_by=intervention.created_by, status=intervention.status, intervention=intervention)
        log.save()
    else:
        if intervention._old_status_id != intervention.status_id or intervention._old_assigned_id != intervention.assigned_id:
            log = InterventionLog(status_id=intervention.status_id, created_by=intervention._current_user,
                                  intervention=intervention)
            if intervention.status_id == settings.ASSIGNED_STATUS:
                log.assigned = intervention.assigned
                result_send = intervention.send_to_user(intervention.assigned)
                if not result_send:
                    message_user(intervention._current_user,
                                 "Error enviando " + str(intervention) + " a " + intervention.assigned.get_full_name(),
                                 constants.ERROR)
            log.save()


post_save.connect(post_save_intervention, sender=Intervention)
