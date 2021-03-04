from __future__ import unicode_literals
from datetime import date

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.signals import post_save

from tinymce import models as tinymce_models

from core.tasks import send_message
from core.utils import has_to_change_password, generate_telegram_auth, send_telegram_message, send_data_to_user


class MyUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, pb_token=None, password=None):
        if not email or not first_name or not last_name:
            raise ValueError('Users must have an email address, username, full_name')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            pb_token=pb_token
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, first_name=None, last_name=None, pb_token=None, password=None):
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            pb_token=pb_token
        )
        user.set_password(password)
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100, blank=False, null=False)
    last_name = models.CharField(max_length=100, blank=False, null=False)
    username = models.CharField(max_length=254, unique=True)
    email = models.EmailField(unique=True)
    pb_token = models.CharField(max_length=254, null=True, blank=True)
    order_in_app = models.IntegerField(default=9)
    is_officer = models.BooleanField(default=True)
    is_technician = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    has_notification = models.IntegerField(default=0)
    last_password_update = models.DateField(default="2015-01-01")
    phone = models.CharField(max_length=9, blank=True, null=True)
    objects = MyUserManager()
    is_google = models.BooleanField(default=False)
    telegram_token = models.CharField(max_length=254, null=True, blank=True, unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        # The user is identified by their email address
        return (self.first_name + " " + self.last_name)

    def get_short_name(self):
        # The user is identified by their email address
        return self.first_name

    def __str__(self):  # __unicode__ on Python 2
        return self.get_full_name()

    def is_staff(self):
        return self.is_superuser

    def has_pb(self):
        if self.pb_token is None or self.pb_token is '' or self.pb_token is u"":
            return False
        else:
            return True

    def has_to_change_password(self):
        if self.is_google:
            return False
        else:
            return has_to_change_password(self.last_password_update)

    def update_change_password(self, commit=False):
        self.last_password_update = date.today()
        if commit:
            self.save()

    def get_assigned_interventions(self):
        from intervention.models import Intervention
        return Intervention.objects.filter(assigned=self, status_id=2).count()

    def get_telegram_auth(self):
        return generate_telegram_auth(self.id, self.email)

    assigned_interventions = property(get_assigned_interventions)


class Message(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    from_user = models.ForeignKey(User, blank=False, related_name='%(class)s_from', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, blank=False, related_name='%(class)s_to', verbose_name="Destinatario",
                                on_delete=models.CASCADE)
    subject = models.CharField(max_length=200, blank=False, verbose_name="Asunto")
    body = models.TextField(blank=False, verbose_name="Cuerpo del mensaje")


class SystemVariable(models.Model):
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


# SIGNALS
def post_save_message(sender, **kwargs):
    if kwargs['created']:
        ins = kwargs['instance']
        ins.to_user.has_notification = 1
        ins.to_user.save()
        body = ins.body + "\n\n" + ins.from_user.get_full_name()
        send_message.delay(ins.pk, body)


post_save.connect(post_save_message, sender='core.Message')
