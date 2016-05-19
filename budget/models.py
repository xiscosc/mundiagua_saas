# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
from django.db import models


class Budget(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.User')
    introduction = models.TextField(verbose_name="Descripción")
    conditions = models.TextField(verbose_name="Condiciones",
                                  default="Para aceptar el presupuesto se tiene que devolver firmado.")
    tax = models.DecimalField(default=21.00, verbose_name="Impuesto", decimal_places=2, max_digits=5)
    address = models.ForeignKey('client.Address', verbose_name="Dirección del cliente")
    invalid = models.BooleanField(default=False, verbose_name="Nulo")

    class Meta:
        abstract = True

    def get_subtotal(self):
        lines = BudgetLineStandard.objects.filter(budget=self)
        stotal = Decimal(0.00)
        for l in lines:
            stotal = stotal + l.total_line()

        return stotal

    def get_tax_import(self):
        return Decimal(self.get_subtotal()) * Decimal(self.tax) * Decimal(0.01)

    def get_total(self):
        return Decimal(self.get_subtotal()) + Decimal(self.get_tax_import())

    def has_discount(self):
        lines = BudgetLineStandard.objects.filter(budget=self)
        dto = Decimal(0.00)
        for l in lines:
            dto = dto + l.discount

        return dto > 0


class BudgetStandard(Budget):

    def __str__(self):
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

    def __str__(self):
        return "P" + self.get_repair().get_id()


class BudgetLine(models.Model):
    product = models.TextField()
    unit_price = models.CharField(max_length=8)
    quantity = models.DecimalField(decimal_places=2, max_digits=20)
    discount = models.DecimalField(default=0.00, decimal_places=2, max_digits=5)

    class Meta:
        abstract = True

    def total_line_without_discount(self):
        return Decimal(self.unit_price) * Decimal(self.quantity)

    def total_discount(self):
        return Decimal(self.total_line_without_discount()) * Decimal(self.discount) * Decimal(0.01)

    def total_line(self):
        return Decimal(self.total_line_without_discount()) - Decimal(self.total_discount())


class BudgetLineStandard(BudgetLine):
    budget = models.ForeignKey(BudgetStandard)


class BudgetLineRepair(BudgetLine):
    budget = models.ForeignKey(BudgetRepair)
