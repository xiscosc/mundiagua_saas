from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save

from budget.models import BudgetRepair
from core.utils import generate_md5_id


class RepairStatus(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()


class AthRepair(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey('client.Address')
    created_by = models.ForeignKey('core.User')
    status = models.ForeignKey(RepairStatus, default=1)
    online_id = models.CharField(max_length=25, null=True)
    model = models.BooleanField(default=False)
    year = models.CharField(max_length=25, null=True)
    serial_number = models.CharField(max_length=100, null=True)
    notice_maker_number = models.CharField(max_length=50, null=True)
    budget = models.ForeignKey('budget.Budget', null=True)
    description = models.TextField()
    intern_description = models.TextField(null=True)
    warranty = models.CharField(max_length=100, null=True)
    bypass = models.BooleanField(default=False)
    connector = models.BooleanField(default=False)
    transformer = models.BooleanField(default=False)

    def get_id(self):
        return "A"+str(self.pk)

    def get_budget(self):
        if self.budget is not None:
            return self.budget
        else:
            try:
                return BudgetRepair.objects.get(ath_repair=self)
            except BudgetRepair.DoesNotExist:
                return None


class IdegisRepair(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey('client.Address')
    created_by = models.ForeignKey('core.User')
    status = models.ForeignKey(RepairStatus, default=1)
    online_id = models.CharField(max_length=25, null=True)
    model = models.BooleanField(default=False)
    year = models.CharField(max_length=25, null=True)
    serial_number = models.CharField(max_length=100, null=True)
    notice_maker_number = models.CharField(max_length=50, null=True)
    budget = models.ForeignKey('budget.Budget', null=True)
    description = models.TextField()
    intern_description = models.TextField(null=True)
    warranty = models.CharField(max_length=100, null=True)
    ph = models.BooleanField(default=False)
    orp = models.BooleanField(default=False)
    electrode = models.BooleanField(default=False)

    def get_id(self):
        return "X" + str(self.pk)

    def get_budget(self):
        if self.budget is not None:
            return self.budget
        else:
            try:
                return BudgetRepair.objects.get(idegis_repair=self)
            except BudgetRepair.DoesNotExist:
                return None

class AthRepairLog(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    repair = models.ForeignKey(AthRepair)
    status = models.ForeignKey(RepairStatus)


class IdegisRepairLog(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    repair = models.ForeignKey(IdegisRepair)
    status = models.ForeignKey(RepairStatus)


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