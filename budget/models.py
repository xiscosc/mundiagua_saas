from __future__ import unicode_literals

from django.db import models


class Budget(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.User')
    introduction = models.TextField()
    conditions = models.TextField()
    content = models.TextField()
    tax = models.IntegerField(default=21)
    address = models.ForeignKey('client.Address')
    invalid = models.BooleanField(default=False)

    def get_id(self):
        year = str(self.date.year)[-2:]
        return "PM"+year+"-"+str(self.pk)



class BudgetRepair(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.User')
    introduction = models.TextField()
    conditions = models.TextField()
    content = models.TextField()
    tax = models.IntegerField(default=21)
    idegis_repair = models.OneToOneField('repair.IdegisRepair', null=True)
    ath_repair = models.OneToOneField('repair.AthRepair', null=True)

    def get_repair(self):
        if self.idegis_repair is not None:
            return self.idegis_repair
        else:
            return self.ath_repair

    def get_id(self):
        return "P"+self.get_repair().get_id()