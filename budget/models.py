# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Budget(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.User')
    introduction = models.TextField(verbose_name="Descripción")
    conditions = models.TextField(verbose_name="Condiciones",
                                  default="Para aceptar el presupuesto se tiene que devolver firmado.")
    tax = models.IntegerField(default=21, verbose_name="Impuesto")
    address = models.ForeignKey('client.Address', verbose_name="Dirección del cliente")
    invalid = models.BooleanField(default=False)

    class Meta:
        abstract = True


class BudgetStandard(Budget):
    def get_id(self):
        year = str(self.date.year)[-2:]
        return "PM" + year + "-" + str(self.pk)


class BudgetRepair(Budget):
    idegis_repair = models.OneToOneField('repair.IdegisRepair', null=True)
    ath_repair = models.OneToOneField('repair.AthRepair', null=True)

    def get_repair(self):
        if self.idegis_repair is not None:
            return self.idegis_repair
        else:
            return self.ath_repair

    def get_id(self):
        return "P" + self.get_repair().get_id()


class BudgetLine(models.Model):
    product = models.TextField()
    unit_price = models.CharField(max_length=8)
    quantity = models.FloatField()
    discount = models.FloatField(default=0.0)

    class Meta:
        abstract = True


class BudgetLineStandard(BudgetLine):
    budget = models.ForeignKey(BudgetStandard)


class BudgetLineRepair(BudgetLine):
    budget = models.ForeignKey(BudgetRepair)
