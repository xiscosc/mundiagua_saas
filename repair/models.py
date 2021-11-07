# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from enum import Enum
from django.db import models
from django.db.models.signals import post_save

from budget.models import BudgetRepair
from client.models import SMS
from intervention.models import Intervention
from core.utils import generate_repair_online_id, get_time_zone, INTERVENTION_REGEX, search_objects_in_text


class RepairType(Enum):
    ATH = 'ath'
    IDEGIS = 'idegis'
    ZODIAC = 'zodiac'
    ALL = 'all'


class RepairStatus(models.Model):
    name = models.CharField(max_length=50, verbose_name='Nombre')
    description = models.TextField(verbose_name='Descripción')
    percentage = models.IntegerField(default=0, verbose_name='Porcentaje de reparación completada')

    def __str__(self):
        return self.name


class Repair(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey('client.Address', verbose_name="Dirección del cliente", on_delete=models.CASCADE)
    created_by = models.ForeignKey('core.User', on_delete=models.CASCADE)
    status = models.ForeignKey(RepairStatus, default=1, on_delete=models.CASCADE)
    online_id = models.CharField(max_length=25, null=True)
    model = models.CharField(max_length=100, null=True, blank=True, verbose_name="Modelo")
    year = models.CharField(max_length=25, null=True, blank=True, verbose_name="Año")
    serial_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Número de serie")
    notice_maker_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="Nº Aviso del fabricante")
    budget = models.ForeignKey('budget.BudgetStandard', null=True, on_delete=models.CASCADE)
    description = models.TextField(verbose_name="Descripción")
    intern_description = models.TextField(null=True, blank=True, verbose_name="Descripción interna")
    warranty = models.BooleanField(default=False, verbose_name="Garantía")
    sms = models.ManyToManyField(SMS)
    starred = models.BooleanField(default=False)

    class Meta:
        abstract = True

    @property
    def private_id(self):
        return self.__str__()

    @property
    def type(self):
        raise NotImplementedError()

    @property
    def type_str(self):
        return self.type.value


class AthRepair(Repair):
    bypass = models.BooleanField(default=False, verbose_name="ByPass")
    connector = models.BooleanField(default=False, verbose_name='Connector 1"')
    transformer = models.BooleanField(default=False, verbose_name="Transformador")

    def __str__(self):
        return "A"+str(self.pk)

    @property
    def type(self):
        return RepairType.ATH

    def get_budgets(self):
        return BudgetRepair.objects.filter(ath_repair=self)


class IdegisRepair(Repair):
    ph = models.BooleanField(default=False, verbose_name="Sonda PH")
    orp = models.BooleanField(default=False, verbose_name="Sonda ORP")
    electrode = models.BooleanField(default=False, verbose_name="Electrodo")

    def __str__(self):
        return "X" + str(self.pk)

    def get_budgets(self):
        return BudgetRepair.objects.filter(idegis_repair=self)

    @property
    def type(self):
        return RepairType.IDEGIS


class ZodiacRepair(Repair):
    def __str__(self):
        return "Z" + str(self.pk)

    @property
    def type(self):
        return RepairType.ZODIAC

    def get_budgets(self):
        return BudgetRepair.objects.filter(zodiac_repair=self)


class RepairLog(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(RepairStatus, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return self.date.astimezone(get_time_zone()).strftime("%d-%m-%Y %H:%M") + " - " + str(self.status)


class AthRepairLog(RepairLog):
    repair = models.ForeignKey(AthRepair, on_delete=models.CASCADE)


class IdegisRepairLog(RepairLog):
    repair = models.ForeignKey(IdegisRepair, on_delete=models.CASCADE)


class ZodiacRepairLog(RepairLog):
    repair = models.ForeignKey(ZodiacRepair, on_delete=models.CASCADE)


# SIGNALS

def link_to_intervention(instance):
    from async_messages import messages
    added = False
    error = False
    ids = search_objects_in_text(INTERVENTION_REGEX, instance.intern_description)
    ids = ids + search_objects_in_text(INTERVENTION_REGEX, instance.description)

    for id in ids:
        try:
            if instance.type == RepairType.ATH:
                Intervention.objects.get(pk=int(id)).repairs_ath.add(instance)
            elif instance.type == RepairType.IDEGIS:
                Intervention.objects.get(pk=int(id)).repairs_idegis.add(instance)
            elif instance.type == RepairType.ZODIAC:
                Intervention.objects.get(pk=int(id)).repairs_zodiac.add(instance)
            else:
                raise NotImplementedError()
            added = True
        except:
            error = True

    if added:
        messages.success(instance.created_by, "Se han autonvinculado avería(s) a esta reparación")
    if error:
        messages.warning(instance.created_by, "Ha ocurrido un error durante la autovinculación en esta reparación")


def post_save_ath_repair(sender, **kwargs):
    ins = kwargs['instance']
    if kwargs['created']:
        log = AthRepairLog(repair=ins, status=ins.status)
        log.save()
        ins.online_id = generate_repair_online_id("A")
        ins.save()
    link_to_intervention(ins)


def post_save_idegis_repair(sender, **kwargs):
    ins = kwargs['instance']
    if kwargs['created']:
        log = IdegisRepairLog(repair=ins, status=ins.status)
        log.save()
        ins.online_id = generate_repair_online_id("X")
        ins.save()
    link_to_intervention(ins)


def post_save_zodiac_repair(sender, **kwargs):
    ins = kwargs['instance']
    if kwargs['created']:
        log = ZodiacRepairLog(repair=ins, status=ins.status)
        log.save()
        ins.online_id = generate_repair_online_id("Z")
        ins.save()
    link_to_intervention(ins)


post_save.connect(post_save_ath_repair, sender=AthRepair)
post_save.connect(post_save_idegis_repair, sender=IdegisRepair)
post_save.connect(post_save_zodiac_repair, sender=ZodiacRepair)
