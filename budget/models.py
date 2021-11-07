# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
from django.db import models
from django.db.models.signals import post_save

from core.utils import search_objects_in_text, INTERVENTION_REGEX
from intervention.models import Intervention


class Budget(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.User', on_delete=models.CASCADE)
    introduction = models.TextField(verbose_name="Descripción")
    conditions = models.TextField(verbose_name="Condiciones",
                                  default="Para aceptar el presupuesto se tiene que devolver firmado.")
    tax = models.DecimalField(default=21.00, verbose_name="Impuesto", decimal_places=2, max_digits=5)
    address = models.ForeignKey('client.Address', verbose_name="Dirección del cliente", on_delete=models.CASCADE)
    invalid = models.BooleanField(default=False, verbose_name="Nulo")

    class Meta:
        abstract = True

    def get_lines(self):
        pass

    def get_subtotal(self):
        lines = self.get_lines()
        stotal = Decimal(0.00)
        for l in lines:
            stotal = stotal + l.total_line()

        return stotal

    def get_tax_import(self):
        return Decimal(self.get_subtotal()) * Decimal(self.tax) * Decimal(0.01)

    def get_total(self):
        return Decimal(self.get_subtotal()) + Decimal(self.get_tax_import())

    def has_discount(self):
        lines = self.get_lines()
        dto = Decimal(0.00)
        for l in lines:
            dto = dto + l.discount

        return dto > 0


class BudgetStandard(Budget):

    def __str__(self):
        year = str(self.date.year)[-2:]
        return "PM" + year + "-" + str(self.pk)

    def get_lines(self):
        return BudgetLineStandard.objects.filter(budget_id=self.pk).order_by("id")


class BudgetRepair(Budget):
    idegis_repair = models.ForeignKey('repair.IdegisRepair', null=True, on_delete=models.CASCADE)
    ath_repair = models.ForeignKey('repair.AthRepair', null=True, on_delete=models.CASCADE)
    zodiac_repair = models.ForeignKey('repair.ZodiacRepair', null=True, on_delete=models.CASCADE)
    intern_id = models.IntegerField(default=1)

    def get_repair(self):
        if self.idegis_repair is not None:
            return self.idegis_repair
        elif self.ath_repair is not None:
            return self.ath_repair
        elif self.zodiac_repair is not None:
            return self.zodiac_repair
        else:
            raise NotImplementedError()

    def __str__(self):
        return "P" + str(self.get_repair()) + "-" + str(self.intern_id)

    def get_lines(self):
        return BudgetLineRepair.objects.filter(budget_id=self.pk).order_by("id")


class BudgetLine(models.Model):
    product = models.TextField()
    unit_price = models.DecimalField(decimal_places=2, max_digits=20)
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
    budget = models.ForeignKey(BudgetStandard, on_delete=models.CASCADE)


class BudgetLineRepair(BudgetLine):
    budget = models.ForeignKey(BudgetRepair, on_delete=models.CASCADE)


def link_to_intervention(instance):
    from async_messages import messages
    added = False
    error = False
    ids = search_objects_in_text(INTERVENTION_REGEX, instance.introduction)
    ids = ids + search_objects_in_text(INTERVENTION_REGEX, instance.conditions)

    for id in ids:
        try:
            Intervention.objects.get(pk=int(id)).budgets.add(instance)
            added = True
        except:
            error = True

    if added:
        messages.success(instance.created_by, "Se han autonvinculado avería(s) a este presupuesto")
    if error:
        messages.warning(instance.created_by, "Ha ocurrido un error durante la autovinculación en este presupuesto")


def post_save_budget_standard(sender, **kwargs):
    link_to_intervention(kwargs['instance'])


post_save.connect(post_save_budget_standard, sender=BudgetStandard)
