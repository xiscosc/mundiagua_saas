from __future__ import unicode_literals

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save

from core.utils import send_data_to_user


class MyUserManager(BaseUserManager):
    def create_user(self, email, full_name, pb_token=None, password=None):

        if not email or not full_name:
            raise ValueError('Users must have an email address, username, full_name')

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            pb_token=pb_token
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, full_name=None, pb_token=None, password=None):

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            pb_token=pb_token
        )
        user.set_password(password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    full_name = models.CharField(max_length=100, blank=False, null=False)
    email = models.EmailField(unique=True)
    pb_token = models.CharField(max_length=254, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def get_full_name(self):
        # The user is identified by their email address
        return self.full_name

    def get_short_name(self):
        # The user is identified by their email address
        return self.full_name

    def __str__(self):  # __unicode__ on Python 2
        return self.full_name

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
    read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    from_user = models.ForeignKey(User, blank=False, related_name='%(class)s_from')
    to_user = models.ForeignKey(User, blank=False, related_name='%(class)s_to')
    subject = models.CharField(max_length=200, blank=False)
    body = models.TextField(blank=False)


# SIGNALS

def post_save_message(sender, **kwargs):
    if kwargs['created']:
        ins = kwargs['instance']
        body = ins.body+"\n\n"+ins.from_user.full_name
        send_data_to_user(ins.to_user, ins.subject, body)


post_save.connect(post_save_message, sender='core.Message')