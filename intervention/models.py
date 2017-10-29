# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.core.urlresolvers import reverse_lazy
from django.db import models
from colorfield.fields import ColorField
from django.db.models.signals import post_save
from django.conf import settings

from client.models import SMS
from core.utils import send_data_to_user, create_amazon_client, generate_thumbnail, format_filename
from intervention.tasks import send_intervention_assigned, upload_file


def get_upload_path(type, instance, filename):
    return os.path.join(type, "V%s" % instance.intervention.pk, format_filename(filename))


def get_file_upload_path(instance, filename):
    return get_upload_path('intervention_documents', instance, filename)


def get_images_upload_path(instance, filename):
    return get_upload_path('intervention_images', instance, filename)


class InterventionStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name.encode('utf8')


class InterventionSubStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name.encode('utf8')


class InterventionInfo(models.Model):
    name = models.CharField(max_length=50)
    color = ColorField(default='#FF0000')

    def __str__(self):
        return self.name.encode('utf8')

    def get_is_zone(self):
        return None

    class Meta:
        abstract = True


class Zone(InterventionInfo):
    border = ColorField(default='#FF0000')

    def get_is_zone(self):
        return True

    is_zone = property(get_is_zone)

    def get_pending_interventions(self):
        return Intervention.objects.filter(zone=self, status_id=1).count()

    pending_interventions = property(get_pending_interventions)


class Tag(InterventionInfo):
    def get_is_zone(self):
        return False

    is_zone = property(get_is_zone)

    def get_pending_interventions(self):
        return Intervention.objects.filter(tags=self, status_id=1).count()

    pending_interventions = property(get_pending_interventions)


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

    def get_documents(self):
        return InterventionDocument.objects.filter(intervention=self)

    def get_history_sub(self):
        return InterventionLogSub.objects.filter(intervention=self).order_by("date")

    def is_early_modificalbe(self):
        from datetime import datetime, timedelta
        diff = datetime.today() - self.date.replace(tzinfo=None)
        if timedelta(hours=4) > diff:
            return True
        else:
            return False

    def has_media(self):
        num = self.get_images().count() + self.get_documents().count()
        if num > 0:
            return True
        else:
            return False


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


class InterventionLogSub(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.User')
    sub_status = models.ForeignKey(InterventionSubStatus)
    intervention = models.ForeignKey(Intervention)


class InterventionFile(models.Model):
    intervention = models.ForeignKey(Intervention)
    user = models.ForeignKey('core.User')
    date = models.DateTimeField(auto_now_add=True)
    in_s3 = models.BooleanField(default=False)
    s3_key = models.CharField(max_length=20, default="no_key")

    def file_path(self):
        return None

    def get_bucket(self):
        return None

    def filename(self):
        return os.path.basename(self.file_path())

    def get_extension(self):
        return os.path.splitext(self.filename())[1][1:]

    def upload_to_s3(self):
        import random
        s3 = create_amazon_client('s3')
        rand = int(random.random() * 100) % 9
        key = "V%d_%d_%d.%s" % (self.intervention.pk, self.pk, rand, self.get_extension())
        original_path = os.path.join(settings.MEDIA_ROOT, self.file_path())

        try:
            result = s3.upload_file(original_path, self.get_bucket(), key)
            if result is None:
                self.s3_key = key
                self.in_s3 = True
                self.save()
                print "Removing %s" % original_path
                os.remove(original_path)
        except:
            pass

    class Meta:
        abstract = True

    def download_from_s3(self):
        s3 = create_amazon_client('s3')
        try:
            data = s3.get_object(Bucket=self.get_bucket(), Key=self.s3_key)
            return data['Body']
        except:
            return None


class InterventionImage(InterventionFile):
    image = models.ImageField(upload_to=get_images_upload_path)
    thumbnail = models.ImageField(blank=True, null=True)

    def file_path(self):
        return self.image.name

    def get_bucket(self):
        return settings.S3_IMAGES


class InterventionDocument(InterventionFile):
    document = models.FileField(upload_to=get_file_upload_path)

    def file_path(self):
        return self.document.name

    def get_bucket(self):
        return settings.S3_DOCUMENTS


def post_save_document(sender, **kwargs):
    doc = kwargs['instance']
    if kwargs['created']:
        upload_file.delay("document", doc.pk)


def post_save_image(sender, **kwargs):
    image = kwargs['instance']
    if kwargs['created']:
        image.thumbnail = generate_thumbnail(image)
        image.save()
        upload_file.delay("image", image.pk)


def post_save_intervention(sender, **kwargs):
    intervention = kwargs['instance']
    if kwargs['created']:
        log = InterventionLog(created_by=intervention.created_by, status=intervention.status, intervention=intervention)
        log.save()
    else:
        try:
            if intervention._old_status_id != intervention.status_id or intervention._old_assigned_id != intervention.assigned_id:
                log = InterventionLog(status_id=intervention.status_id, created_by=intervention._current_user,
                                      intervention=intervention)
                if intervention.status_id == settings.ASSIGNED_STATUS:
                    log.assigned = intervention.assigned
                    send_intervention_assigned.delay(intervention.pk)
                log.save()
        except:
            pass


post_save.connect(post_save_intervention, sender=Intervention)
post_save.connect(post_save_document, sender=InterventionDocument)
post_save.connect(post_save_image, sender=InterventionImage)