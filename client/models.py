from __future__ import unicode_literals

from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    intern_code = models.CharField(max_length=20, blank=True)
    dni = models.CharField(max_length=20, blank=True)


class Phone(models.Model):
    alias = models.CharField(max_length=30)
    phone = models.CharField(max_length=30)
    client = models.ForeignKey(Client)


class Address(models.Model):
    alias = models.CharField(max_length=30)
    address = models.TextField(blank=False)
    client = models.ForeignKey(Client)
    latitude = models.CharField(max_length=25, blank=True)
    longitude = models.CharField(max_length=25, blank=True)
    default_zone = models.ForeignKey('intervention.Zone', null=True)

    def get_url_gmaps(self):

        if self.latitude and self.longitude:
            return "https://maps.google.com/maps?q=loc:"+self.latitude+","+self.longitude
        else:
            return False