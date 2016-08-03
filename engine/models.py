# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save

from client.models import SMS
from core.utils import generate_md5_id


class EngineStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class EngineRepair(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey('client.Address', verbose_name="Dirección del cliente")
    created_by = models.ForeignKey('core.User')
    status = models.ForeignKey(EngineStatus, default=1)
    model = models.CharField(max_length=100, null=True, blank=True, verbose_name="Modelo")
    year = models.CharField(max_length=25, null=True, blank=True, verbose_name="Año")
    serial_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Número de serie")
    budget = models.ForeignKey('budget.BudgetStandard', null=True)
    description = models.TextField(verbose_name="Descripción")
    technical_service = models.CharField(max_length=125, verbose_name="Servicio técnico", null=True, blank=True)
    intern_description = models.TextField(null=True, blank=True, verbose_name="Descripción interna")
    sms = models.ManyToManyField(SMS)
    online_id = models.CharField(max_length=25, null=True)

    def __str__(self):
        return "E" + str(self.pk)


class EngineRepairLog(models.Model):
    repair = models.ForeignKey(EngineRepair)
    date = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(EngineStatus)

    def __str__(self):
        return self.date.strftime("%d-%m-%Y %H:%M") + " - " + str(self.status)


def post_save_engine_repair(sender, **kwargs):
    if kwargs['created']:
        ins = kwargs['instance']
        log = EngineRepairLog(repair=ins, status=ins.status)
        log.save()
        ins.online_id = generate_md5_id("E", ins.pk)
        ins.save()

post_save.connect(post_save_engine_repair, sender=EngineRepair)
