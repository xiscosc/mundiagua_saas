# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save

from async_messages import message_user, constants

from core.models import User


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


class SMS(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User)
    body = models.TextField(max_length=160)
    sent_status = models.IntegerField(default=0) # 0 pending, 1 sent, 2 fail
    phone = models.ForeignKey(Phone)


def post_save_sms(sender, **kwargs):
    sms = kwargs['instance']
    if kwargs['created']:
        phone_processed = sms.phone.phone.replace(" ", "")
        phone_processed = '34'+phone_processed.replace(".", "")
        if len(phone_processed) == 11:
            from sendsms.message import SmsMessage
            message = SmsMessage(
                body=sms.body,
                from_phone=settings.SMS_SENDER,
                to=[phone_processed]
            )
            result = message.send()
            if result == 1:
                sms.sent_status = 1
                message_user(sms.sender, "SMS a " + sms.phone.client.name + " enviado correctamente", constants.SUCCESS)
            else:
                sms.sent_status = 2
                message_user(sms.sender, "Error enviando SMS a " + sms.phone.client.name + ", puede ser un error temporal o que no hay crédito de SMS", constants.ERROR)
            sms.save()



post_save.connect(post_save_sms, sender=SMS)