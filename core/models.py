from __future__ import unicode_literals

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save

from core.tasks import send_message


class MyUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, pb_token=None, password=None):

        if not email or not first_name or not last_name:
            raise ValueError('Users must have an email address, username, full_name')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name= last_name,
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
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    first_name = models.CharField(max_length=100, blank=False, null=False)
    last_name = models.CharField(max_length=100, blank=False, null=False)
    email = models.EmailField(unique=True)
    pb_token = models.CharField(max_length=254, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        # The user is identified by their email address
        return self.first_name + " " + self.last_name

    def get_short_name(self):
        # The user is identified by their email address
        return self.first_name

    def __str__(self):  # __unicode__ on Python 2
        return self.get_full_name()

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Message(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    from_user = models.ForeignKey(User, blank=False, related_name='%(class)s_from')
    to_user = models.ForeignKey(User, blank=False, related_name='%(class)s_to', verbose_name="Destinatario")
    subject = models.CharField(max_length=200, blank=False, verbose_name="Asunto")
    body = models.TextField(blank=False, verbose_name="Cuerpo del mensaje")


# SIGNALS

def post_save_message(sender, **kwargs):
    if kwargs['created']:
        ins = kwargs['instance']
        body = ins.body+"\n\n"+ins.from_user.get_full_name()
        send_message.delay(ins, body)


post_save.connect(post_save_message, sender='core.Message')