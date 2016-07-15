# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save

from budget.models import BudgetRepair
from client.models import SMS
from core.utils import generate_md5_id


class RepairStatus(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name


class Repair(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey('client.Address', verbose_name="Dirección del cliente")
    created_by = models.ForeignKey('core.User')
    status = models.ForeignKey(RepairStatus, default=1)
    online_id = models.CharField(max_length=25, null=True)
    model = models.CharField(max_length=100, null=True, blank=True, verbose_name="Modelo")
    year = models.CharField(max_length=25, null=True, blank=True, verbose_name="Año")
    serial_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Número de serie")
    notice_maker_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="Nº Aviso del fabricante")
    budget = models.ForeignKey('budget.BudgetStandard', null=True)
    description = models.TextField(verbose_name="Descripción")
    intern_description = models.TextField(null=True, blank=True, verbose_name="Descripción interna")
    warranty = models.BooleanField(default=False, verbose_name="Garantía")
    sms = models.ManyToManyField(SMS)
    token = models.CharField(max_length=256, null=True, blank=True, default=None)

    class Meta:
        abstract = True


class AthRepair(Repair):
    bypass = models.BooleanField(default=False, verbose_name="ByPass")
    connector = models.BooleanField(default=False, verbose_name='Connector 1"')
    transformer = models.BooleanField(default=False, verbose_name="Transformador")

    def __str__(self):
        return "A"+str(self.pk)

    def is_ath(self):
        return 1


class IdegisRepair(Repair):
    ph = models.BooleanField(default=False, verbose_name="Sonda PH")
    orp = models.BooleanField(default=False, verbose_name="Sonda ORP")
    electrode = models.BooleanField(default=False, verbose_name="Electrodo")

    def __str__(self):
        return "X" + str(self.pk)

    def get_budget(self):
        if self.budget is not None:
            return self.budget
        else:
            try:
                return BudgetRepair.objects.get(idegis_repair=self)
            except BudgetRepair.DoesNotExist:
                return None

    def is_ath(self):
        return 0


class RepairLog(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(RepairStatus)

    class Meta:
        abstract = True

    def __str__(self):
        return self.date.strftime("%d-%m-%Y %H:%M") + " - " + str(self.status)


class AthRepairLog(RepairLog):
    repair = models.ForeignKey(AthRepair)


class IdegisRepairLog(RepairLog):
    repair = models.ForeignKey(IdegisRepair)


# SIGNALS


def post_save_ath_repair(sender, **kwargs):
    if kwargs['created']:
        ins = kwargs['instance']
        log = AthRepairLog(repair=ins, status=ins.status)
        log.save()
        ins.online_id = generate_md5_id("A", ins.pk)
        ins.save()
    else:
        pass


def post_save_idegis_repair(sender, **kwargs):
    if kwargs['created']:
        ins = kwargs['instance']
        log = IdegisRepairLog(repair=ins, status=ins.status)
        log.save()
        ins.online_id = generate_md5_id("X", ins.pk)
        ins.save()
    else:
        pass

post_save.connect(post_save_ath_repair, sender=AthRepair)
post_save.connect(post_save_idegis_repair, sender=IdegisRepair)