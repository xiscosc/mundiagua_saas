from settings import *

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

BOWER_COMPONENTS_ROOT = '/Users/xiscosastre/PycharmProjects/mundiagua_python/components/'
MEDIA_ROOT = '/home/xiscosastre/mundiagua_saas/media/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mundiagua_py',
        'USER': 'xiscosastre',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '',
    }
}

SENDGRID_API_KEY = "key"

DEBUG = True
DOMAIN = "https://www.example.com"
ALLOWED_HOSTS = ['.example.com']

AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""
AWS_REGION = "eu-west-1"

GMAPS_API_KEY = ""
GOOGLE_CLIENT_ID = "ff.apps.googleusercontent.com"


NUMBER_TEMPLATES = 5

LOGIN_URL = "/login/"
