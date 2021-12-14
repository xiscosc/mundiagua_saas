from __future__ import unicode_literals

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from tinymce import models as tinymce_models


class MyUserManager(BaseUserManager):
    def create_user(self, username, email, first_name, last_name, password=None):
        if not username or not email or not first_name or not last_name:
            raise ValueError('Users must have an email address, username, full_name')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username=None, email=None, first_name=None, last_name=None, password=None):
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100, blank=False, null=False)
    last_name = models.CharField(max_length=100, blank=False, null=False)
    username = models.CharField(max_length=254, unique=True)
    email = models.EmailField(unique=True)
    order_in_app = models.IntegerField(default=9)
    is_officer = models.BooleanField(default=True)
    is_technician = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_password_update = models.DateField(default="2015-01-01")
    phone = models.CharField(max_length=9, blank=True, null=True)
    objects = MyUserManager()
    telegram_token = models.CharField(max_length=254, null=True, blank=True, unique=True)
    external_messaging_id = models.UUIDField(null=True, default=None)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def get_full_name(self):
        # The user is identified by their email address
        return self.first_name + " " + self.last_name

    def get_short_name(self):
        # The user is identified by their email address
        return self.first_name

    def __str__(self):  # __unicode__ on Python 2
        return self.get_full_name()

    def is_staff(self):
        return self.is_superuser

    def has_company_email(self):
        return self.email.endswith("@mundiaguabalear.com")

    def get_assigned_interventions(self):
        from intervention.models import Intervention
        return Intervention.objects.filter(assigned=self, status_id=2).count()

    assigned_interventions = property(get_assigned_interventions)


class SystemVariable(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=15, blank=False, null=False)
    key = models.CharField(max_length=25, blank=False, null=False, unique=True)
    description = models.TextField(blank=True, null=True)
    rich_text = models.BooleanField(default=False)
    value = tinymce_models.HTMLField(blank=True, null=True, verbose_name="Valor de la variable")
    plain_value = models.TextField(blank=True, null=True, verbose_name="Valor de la variable")

    def get_value(self):
        if self.rich_text:
            return self.value
        else:
            return self.plain_value

    def __str__(self):  # __unicode__ on Python 2
        return self.type + " - " + self.key
