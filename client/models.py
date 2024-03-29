from django.db import models
from client.tasks import send_sms
from client.utils import get_zone_using_interventions
from core.models import User


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="Nombre")
    intern_code = models.CharField(max_length=45, null=True, blank=True, verbose_name="COD Interno")
    dni = models.CharField(max_length=45, null=True, blank=True, verbose_name="DNI/CIF")
    blocked = models.BooleanField(default=False, verbose_name="Bloqueado")

    def __str__(self):
        if not self.blocked:
            return self.name
        else:
            return "BLOQUEADO - " + self.name

    def get_phones(self):
        return Phone.objects.filter(client=self)

    def get_emails(self):
        return Email.objects.filter(client=self)

    def get_addresses(self):
        return Address.objects.filter(client=self)

    def get_first_address(self):
        return self.get_addresses().first()


class Email(models.Model):
    id = models.AutoField(primary_key=True)
    alias = models.CharField(max_length=45)
    email = models.EmailField()
    client = models.ForeignKey(Client, related_name="emails", on_delete=models.CASCADE)

    def __str__(self):
        return self.alias + " - " + self.email


class Phone(models.Model):
    id = models.AutoField(primary_key=True)
    alias = models.CharField(max_length=45)
    international_code = models.CharField(max_length=10, default=34, verbose_name="Código país")
    phone = models.CharField(max_length=45, verbose_name="Teléfono")
    client = models.ForeignKey(Client, related_name="phones", on_delete=models.CASCADE)

    def __str__(self):
        return self.alias + " - " + self.phone

    def full_international_format(self):
        return "+" + self.international_code + " " + self.phone

    def is_mobile(self):
        try:
            if int(self.international_code) == 34:
                if int(self.phone[0]) == 9 or int(self.phone[0]) == 8:
                    return False

            return True
        except:
            return False

    def printable(self):
        if self.international_code == "34":
            return self.phone
        else:
            return self.full_international_format()


class Address(models.Model):
    id = models.AutoField(primary_key=True)
    alias = models.CharField(max_length=45)
    address = models.TextField(verbose_name="Dirección")
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    latitude = models.CharField(max_length=45, null=True, blank=True)
    longitude = models.CharField(max_length=45, null=True, blank=True)
    #default_zone = models.ForeignKey('intervention.Zone', null=True, on_delete=models.CASCADE)

    def calculate_default_zone(self):
        return get_zone_using_interventions(self)

    def get_url_gmaps(self):

        if self.latitude is not None and self.longitude is not None and self.latitude != "" \
                and self.longitude != "":
            return "https://maps.google.com/maps?q=loc:" + self.latitude + "," + self.longitude
        else:
            return False

    def get_geo(self):
        if self.latitude is not None and self.longitude is not None and self.latitude != "" \
                and self.longitude != "":
            return [self.latitude, self.longitude]
        else:
            return False

    def __str__(self):
        return "(" + self.alias + ") - " + self.address

    def printable(self):
        return self.address


class SMSStatus(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class SMS(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(max_length=160)
    sent_status = models.ForeignKey(SMSStatus, default=1, on_delete=models.CASCADE)
    phone = models.ForeignKey(Phone, on_delete=models.CASCADE)

    def process_phone(self):
        phone_processed = self.phone.phone.replace(" ", "")
        i_code = '+' + self.phone.international_code
        phone_processed = i_code + phone_processed.replace(".", "")
        return phone_processed

    def process_phone_for_nexmo(self):
        phone_processed = self.phone.international_code + self.phone.phone
        return phone_processed.replace(".", "").replace(" ", "")

    def send(self):
        send_sms(self)

    def __str__(self):
        return self.date.__str__() + " - " + self.sender.__str__()
