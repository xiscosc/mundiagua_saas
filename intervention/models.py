# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mimetypes
import os
from datetime import datetime

from django.urls import reverse_lazy
from django.db import models
from colorfield.fields import ColorField
from django.db.models.signals import post_save
from django.conf import settings
from client.models import SMS
from core.aws.s3_utils import get_s3_download_signed_url, get_s3_upload_signed_post
from core.tasks import send_data_to_user
from core.utils import autolink_intervention


class InterventionStatus(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    def get_allowed_transition_ids(self):
        # PENDIENTE 1
        if self.id == 1:
            return [2, 3, 4, 5]

        # ASIGNADA 2
        if self.id == 2:
            return [1, 2, 3, 4]

        # TERMINADA 3 // ANULADA 4
        if self.id == 3 or self.id == 4:
            return [5]

        # PREPARACION 5
        if self.id == 5:
            return [1, 3, 4]

        return []

    allowed_transition_ids = property(get_allowed_transition_ids)


class InterventionSubStatus(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class InterventionInfo(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    color = ColorField(default='#FF0000')

    def __str__(self):
        return self.name

    def get_is_zone(self):
        return None

    class Meta:
        abstract = True


class Zone(InterventionInfo):
    def get_is_zone(self):
        return True

    def get_pending_interventions(self):
        return Intervention.objects.filter(zone=self, status_id=1).count()

    def get_preparation_interventions(self):
        return Intervention.objects.filter(zone=self, status_id=5).count()

    border = ColorField(default='#FF0000')
    is_zone = property(get_is_zone)
    pending_interventions = property(get_pending_interventions)
    preparation_interventions = property(get_preparation_interventions)


class Tag(InterventionInfo):
    def get_is_zone(self):
        return False

    def get_pending_interventions(self):
        return Intervention.objects.filter(tags=self, status_id=1).count()

    def get_preparation_interventions(self):
        return Intervention.objects.filter(tags=self, status_id=5).count()

    is_zone = property(get_is_zone)
    pending_interventions = property(get_pending_interventions)
    preparation_interventions = property(get_preparation_interventions)


class Intervention(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField(verbose_name="Descripción", db_index=True)
    short_description = models.CharField(verbose_name="Descripción corta", max_length=255, default="", blank=True,
                                         db_index=True)
    address = models.ForeignKey('client.Address', verbose_name="Dirección", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    zone = models.ForeignKey(Zone, default=1, verbose_name="Zona", on_delete=models.CASCADE)
    status = models.ForeignKey(InterventionStatus, default=5, on_delete=models.CASCADE)
    created_by = models.ForeignKey('core.User', related_name='%(class)s_by', on_delete=models.CASCADE)
    assigned = models.ForeignKey('core.User', null=True, related_name='%(class)s_assigned', on_delete=models.CASCADE)
    note = models.TextField(null=True)
    sms = models.ManyToManyField(SMS)
    starred = models.BooleanField(default=False)
    repairs_ath = models.ManyToManyField('repair.AthRepair')
    repairs_idegis = models.ManyToManyField('repair.IdegisRepair')
    repairs_zodiac = models.ManyToManyField('repair.ZodiacRepair')
    budgets = models.ManyToManyField('budget.BudgetStandard')
    tags = models.ManyToManyField(Tag, verbose_name="Etiquetas", blank=True)

    def __str__(self):
        return "V" + str(self.pk)

    def get_history(self):
        return InterventionLog.objects.filter(intervention=self).order_by("date")

    def get_modifications(self):
        return InterventionModification.objects.filter(intervention=self)

    def get_days_since(self):
        delta = datetime.now().date() - self.date.date()
        return delta.days

    def generate_url(self):
        intern_url = str(reverse_lazy('intervention:intervention-view', kwargs={'pk': self.pk}))
        return settings.DOMAIN + intern_url

    def send_to_user(self, user):
        return send_data_to_user(is_link=True, body=self.generate_url(), user=user,
                                 subject=str(self) + " - " + self.address.client.name)

    def count_modifications(self):
        return InterventionModification.objects.filter(intervention=self).count()

    def get_history_sub(self):
        return InterventionLogSub.objects.filter(intervention=self).order_by("date")

    def is_early_modifiable(self):
        from datetime import datetime, timedelta
        diff = datetime.today() - self.date.replace(tzinfo=None)
        return timedelta(hours=4) > diff

    def count_links(self):
        return self.repairs_ath.all().count() + self.repairs_idegis.all().count() + self.budgets.all().count() + self.repairs_zodiac.all().count()

    def has_links(self):
        return self.count_links() > 0

    def has_modifications(self):
        return self.count_modifications() > 0


class InterventionModification(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True)
    created_by = models.ForeignKey('core.User', on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE)


class InterventionLog(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.User', related_name='%(class)s_by', on_delete=models.CASCADE)
    assigned = models.ForeignKey('core.User', null=True, related_name='%(class)s_assigned', on_delete=models.CASCADE)
    status = models.ForeignKey(InterventionStatus, on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE)


class InterventionLogSub(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.User', on_delete=models.CASCADE)
    sub_status = models.ForeignKey(InterventionSubStatus, on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE)


def post_save_intervention_modification(sender, **kwargs):
    intervention_mod = kwargs['instance']
    if kwargs['created']:
        autolink_intervention(intervention_mod.intervention, intervention_mod.note, intervention_mod.created_by)


def post_save_intervention(sender, **kwargs):
    intervention = kwargs['instance']
    if kwargs['created']:
        log = InterventionLog(created_by=intervention.created_by, status=intervention.status, intervention=intervention)
        log.save()
        autolink_intervention(intervention, intervention.description, intervention.created_by)


post_save.connect(post_save_intervention, sender=Intervention)
post_save.connect(post_save_intervention_modification, sender=InterventionModification)
