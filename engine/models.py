# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save

from client.models import SMS
from core.utils import generate_repair_online_id, get_time_zone


class EngineStatus(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nombre")
    percentage = models.IntegerField(default=0, verbose_name="Porcentaje")

    def __str__(self):
        return self.name


class EngineRepair(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey('client.Address', verbose_name="Dirección del cliente", on_delete=models.CASCADE)
    created_by = models.ForeignKey('core.User', on_delete=models.CASCADE)
    status = models.ForeignKey(EngineStatus, default=1, on_delete=models.CASCADE)
    model = models.CharField(max_length=100, null=True, blank=True, verbose_name="Modelo")
    year = models.CharField(max_length=25, null=True, blank=True, verbose_name="Año")
    serial_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Número de serie")
    budget = models.ForeignKey('budget.BudgetStandard', null=True, on_delete=models.CASCADE)
    description = models.TextField(verbose_name="Descripción")
    technical_service = models.CharField(max_length=125, verbose_name="Servicio técnico", null=True, blank=True)
    intern_description = models.TextField(null=True, blank=True, verbose_name="Descripción interna")
    sms = models.ManyToManyField(SMS)
    online_id = models.CharField(max_length=25, null=True)

    def __str__(self):
        return "E" + str(self.pk)


class EngineRepairLog(models.Model):
    repair = models.ForeignKey(EngineRepair, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(EngineStatus, on_delete=models.CASCADE)

    def __str__(self):
        return self.date.astimezone(get_time_zone()).strftime("%d-%m-%Y %H:%M") + " - " + str(self.status)


def post_save_engine_repair(sender, **kwargs):
    if kwargs['created']:
        ins = kwargs['instance']
        log = EngineRepairLog(repair=ins, status=ins.status)
        log.save()
        ins.online_id = generate_repair_online_id("E")
        ins.save()

post_save.connect(post_save_engine_repair, sender=EngineRepair)
