# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    email = models.EmailField(null=True, blank=True)
    intern_code = models.CharField(max_length=20, null=True, blank=True, verbose_name="COD Interno")
    dni = models.CharField(max_length=20, null=True, blank=True, verbose_name="DNI/CIF")

    def __str__(self):
        return self.name.encode('utf8')

    def get_phones(self):
        return Phone.objects.filter(client=self)

    def get_addresses(self):
        return Address.objects.filter(client=self)

    def get_first_address(self):
        return self.get_addresses().first()


class Phone(models.Model):
    alias = models.CharField(max_length=30)
    phone = models.CharField(max_length=30, verbose_name="Teléfono")
    client = models.ForeignKey(Client)

    def __str__(self):
        return (self.alias + " - " + self.phone).encode('utf8')


class Address(models.Model):
    alias = models.CharField(max_length=30)
    address = models.TextField(verbose_name="Dirección")
    client = models.ForeignKey(Client)
    latitude = models.CharField(max_length=25, null=True, blank=True)
    longitude = models.CharField(max_length=25, null=True, blank=True)
    default_zone = models.ForeignKey('intervention.Zone', null=True)

    def get_url_gmaps(self):

        if self.latitude is not None and self.longitude is not None and self.latitude is not "" \
                and self.longitude is not "":
            return "https://maps.google.com/maps?q=loc:" + self.latitude + "," + self.longitude
        else:
            return False

    def __str__(self):
        return ("(" + self.alias + ") - " + self.address).encode('utf8')
