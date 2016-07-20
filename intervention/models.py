# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.db import models
from colorfield.fields import ColorField
from django.db.models.signals import post_save
from django.conf import settings
from easy_thumbnails.fields import ThumbnailerImageField

from client.models import SMS
from core.utils import send_data_to_user
from intervention.tasks import send_intervention_assigned


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
    sms = models.ManyToManyField(SMS)

    def __str__(self):
        return "V" + str(self.pk)

    def get_history(self):
        return InterventionLog.objects.filter(intervention=self).order_by("date")

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

    def get_images(self):
        return InterventionImage.objects.filter(intervention=self)


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


class InterventionImage(models.Model):
    image = ThumbnailerImageField(upload_to='intervention_images', resize_source=dict(quality=85, size=(1620,0), upscale=False))
    intervention = models.ForeignKey(Intervention)
    user = models.ForeignKey('core.User')


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
                send_intervention_assigned.delay(intervention)
            log.save()


post_save.connect(post_save_intervention, sender=Intervention)
