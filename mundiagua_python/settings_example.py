from settings import *

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

BOWER_COMPONENTS_ROOT = '/Users/xiscosastre/PycharmProjects/mundiagua_python/components/'

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