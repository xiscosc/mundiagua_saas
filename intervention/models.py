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
from core.utils import send_data_to_user, create_amazon_client, format_filename, \
    send_telegram_message, send_telegram_document_with_s3_url, send_telegram_picture_with_s3_url, autolink_intervention
from intervention.tasks import send_intervention_assigned, \
    delete_telegram_messages_from_intervention


class InterventionStatus(models.Model):
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
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class InterventionInfo(models.Model):
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
    description = models.TextField(verbose_name="Descripción")
    short_description = models.CharField(verbose_name="Descripción corta", max_length=255, default="", blank=True)
    address = models.ForeignKey('client.Address', verbose_name="Dirección", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    zone = models.ForeignKey(Zone, default=1, verbose_name="Zona", on_delete=models.CASCADE)
    status = models.ForeignKey(InterventionStatus, default=5, on_delete=models.CASCADE)
    created_by = models.ForeignKey('core.User', related_name='%(class)s_by', on_delete=models.CASCADE)
    assigned = models.ForeignKey('core.User', null=True, related_name='%(class)s_assigned', on_delete=models.CASCADE)
    note = models.TextField(null=True)
    sms = models.ManyToManyField(SMS)
    starred = models.BooleanField(default=False)
    repairs_ath = models.ManyToManyField('repair.AthRepair')
    repairs_idegis = models.ManyToManyField('repair.IdegisRepair')
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

    def get_images(self):
        return InterventionImage.objects.filter(intervention=self)

    def get_documents(self):
        return InterventionDocument.objects.filter(intervention=self)

    def get_no_officer_documents(self):
        return self.get_documents().filter(only_officer=False)

    def get_history_sub(self):
        return InterventionLogSub.objects.filter(intervention=self).order_by("date")

    def is_early_modifiable(self):
        from datetime import datetime, timedelta
        diff = datetime.today() - self.date.replace(tzinfo=None)
        return timedelta(hours=4) > diff

    def count_media(self):
        return self.get_images().count() + self.get_documents().count()

    def has_media(self):
        return self.count_media() > 0

    def count_links(self):
        return self.repairs_ath.all().count() + self.repairs_idegis.all().count() + self.budgets.all().count()

    def has_links(self):
        return self.count_links() > 0

    def has_modifications(self):
        return self.count_modifications() > 0


class InterventionModification(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True)
    created_by = models.ForeignKey('core.User', on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE)


class InterventionLog(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.User', related_name='%(class)s_by', on_delete=models.CASCADE)
    assigned = models.ForeignKey('core.User', null=True, related_name='%(class)s_assigned', on_delete=models.CASCADE)
    status = models.ForeignKey(InterventionStatus, on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE)


class InterventionLogSub(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.User', on_delete=models.CASCADE)
    sub_status = models.ForeignKey(InterventionSubStatus, on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE)


class InterventionFile(models.Model):
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE)
    user = models.ForeignKey('core.User', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    in_s3 = models.BooleanField(default=False)
    s3_key = models.CharField(max_length=120, default=None, null=True)
    telegram_message = models.BigIntegerField(default=None, null=True)
    sent_to_telegram = models.BooleanField(default=False)
    original_name = models.CharField(max_length=120)

    def get_bucket(self):
        return None

    def get_upload_bucket(self):
        return self.get_bucket()

    def filename(self):
        return self.original_name

    def get_extension(self):
        return os.path.splitext(self.filename())[1][1:]

    def get_upload_signed_url(self):
        s3 = create_amazon_client('s3')
        mimetype = mimetypes.guess_type(self.s3_key)[0]
        fields = {'Content-Type': mimetype}
        conditions = [["starts-with", "$Content-Type", ""]]
        return s3.generate_presigned_post(self.get_upload_bucket(), self.s3_key, ExpiresIn=60, Fields=fields,
                                          Conditions=conditions)

    def remove_form_s3(self):
        s3 = create_amazon_client('s3')
        s3.delete_object(Bucket=self.get_bucket(), Key=self.s3_key)

    class Meta:
        abstract = True

    def get_signed_url(self):
        s3 = create_amazon_client('s3')
        try:
            params = {'Bucket': self.get_bucket(), 'Key': self.s3_key}
            return s3.generate_presigned_url('get_object', Params=params, ExpiresIn=120)
        except:
            return None

    def send_file_to_telegram(self):
        pass

    def __str__(self):
        return "V" + str(self.intervention.pk) + " | " + str(self.pk) + " | " + self.filename()


class InterventionImage(InterventionFile):
    thumbnail_s3_key = models.CharField(max_length=120, default=None, null=True)

    def get_bucket(self):
        return settings.S3_IMAGES

    def get_upload_bucket(self):
        return settings.S3_PROCESSING_IMAGES

    def remove_form_s3(self):
        super(InterventionImage, self).remove_form_s3()
        s3 = create_amazon_client('s3')
        s3.delete_object(Bucket=self.get_bucket(), Key=self.thumbnail_s3_key)

    def get_thumbnail_signed_url(self):
        if self.thumbnail_s3_key is None:
            return None

        s3 = create_amazon_client('s3')
        try:
            params = {'Bucket': self.get_bucket(), 'Key': self.thumbnail_s3_key}
            return s3.generate_presigned_url('get_object', Params=params, ExpiresIn=3600)
        except:
            return None

    def send_file_to_telegram(self):
        user = self.intervention.assigned
        if user and user.telegram_token and user != self.user:
            send_telegram_message(user.telegram_token, "Nueva imagen añadida a la avería " + str(
                self.intervention) + " " + self.intervention.address.client.name + " " + self.intervention.generate_url())

            if self.in_s3:
                message = send_telegram_picture_with_s3_url(user.telegram_token, self.get_signed_url())
                if message:
                    self.telegram_message = message.message_id
                    self.sent_to_telegram = True
                    self.save()


class InterventionDocument(InterventionFile):
    only_officer = models.BooleanField(default=True)

    def get_bucket(self):
        return settings.S3_DOCUMENTS

    def send_file_to_telegram(self):
        user = self.intervention.assigned
        if not self.sent_to_telegram and user and user.telegram_token and user != self.user:
            if user.is_officer or not self.only_officer:
                send_telegram_message(user.telegram_token, "Nueva documento añadido a la avería " + str(
                    self.intervention) + " " + self.intervention.address.client.name + " " + self.intervention.generate_url())

                if self.in_s3:
                    message = send_telegram_document_with_s3_url(user.telegram_token, self.get_signed_url(), self.filename())
                    if message:
                        self.telegram_message = message.message_id
                        self.sent_to_telegram = True
                        self.save()


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
    else:
        try:
            if intervention._old_status_id != intervention.status_id or intervention._old_assigned_id != intervention.assigned_id:
                log = InterventionLog(status_id=intervention.status_id, created_by=intervention._current_user,
                                      intervention=intervention)
                if intervention.status_id == settings.ASSIGNED_STATUS:
                    log.assigned = intervention.assigned
                    send_intervention_assigned(intervention.pk)
                log.save()
                if intervention._old_status_id == settings.ASSIGNED_STATUS:
                    delete_telegram_messages_from_intervention(intervention.pk, intervention._old_assigned_id)
        except:
            pass


post_save.connect(post_save_intervention, sender=Intervention)
post_save.connect(post_save_intervention_modification, sender=InterventionModification)
