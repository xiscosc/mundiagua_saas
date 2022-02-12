from .settings import *
import sentry_sdk
import os
from sentry_sdk.integrations.django import DjangoIntegration

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

SECRET_KEY = os.environ.get('SECRET_KEY')

# STATIC FILES
DEBUG =  False
NUMBER_TEMPLATES = 10
IMAGE_NOT_FOUND = "base/img/image_not_available.png"

# DATABASES
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_NAME'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': os.environ.get('POSTGRES_PORT'),
    }
}

# DOMAIN CONFIG
DOMAIN = "https://" + os.environ.get('DOMAIN')
ALLOWED_HOSTS = ['in.mundiaguabalear.com', 'in6.mundiagua.cloud', os.environ.get('DOMAIN')]
CSRF_TRUSTED_ORIGINS = ['in.mundiaguabalear.com', 'www.mundiaguabalear.com', 'in6.mundiagua.cloud', os.environ.get('DOMAIN')]
USE_X_FORWARDED_HOST = True

# AWS
AWS_ACCESS_KEY = os.environ.get('AWS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET')
AWS_REGION = os.environ.get('AWS_REGION')
# AWS S3 BUCKETS
S3_DOCUMENTS = os.environ.get('AWS_S3_DOCUMENTS')
S3_IMAGES = os.environ.get('AWS_S3_IMAGES')
S3_PROCESSING_IMAGES = os.environ.get('AWS_S3_IMAGES_PROCESSING')
S3_PDF_UPLOAD = os.environ.get('AWS_S3_PDF')
S3_WHATSAPP = os.environ.get('AWS_S3_WHATSAPP')
# AWS SNS TOPICS
PDF_TOPIC = os.environ.get('AWS_PDF_TOPIC')
TELEGRAM_TOPIC = os.environ.get('AWS_TELEGRAM_TOPIC')
# S3 STATIC SERVING
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
AWS_S3_ACCESS_KEY_ID = AWS_ACCESS_KEY
AWS_S3_SECRET_ACCESS_KEY = AWS_SECRET_KEY
AWS_STORAGE_BUCKET_NAME = "mundiagua-django-static-prod"
AWS_S3_REGION_NAME = AWS_REGION


# EMAIL
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

# GOOGLE MAPS
GMAPS_API_KEY = os.environ.get('GOOGLE_API_KEY')

# TELEGRAM BOT
TELEGRAM_NAME = os.environ.get('TELEGRAM_BOT_NAME')

# GSM SERVICE
GSM_URL = "https://gsm.mundiagua.cloud"
GSM_WATCH_TIME = 60 * 60 * 3

# SMS SERVICE
SMS_USERNAME = os.environ.get('SMS_USERNAME')
SMS_PASSWORD = os.environ.get('SMS_PASSWORD')
SMS_SERVICE_URL = os.environ.get('SMS_SERVICE_URL')
SMS_SERVICE_PHONE = os.environ.get('SMS_SERVICE_PHONE')
USERS_IT = [1, 23]
USERS_TEC = [11]
NEXMO_KEY = os.environ.get('NEXMO_KEY')
NEXMO_SECRET = os.environ.get('NEXMO_SECRET')

# AUTH 0
AUTH0_API_IDENTIFIER = os.environ.get('AUTH0_API_IDENTIFIER')
AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN')
SOCIAL_AUTH_AUTH0_DOMAIN = AUTH0_DOMAIN
SOCIAL_AUTH_AUTH0_KEY = os.environ.get('AUTH0_KEY')
SOCIAL_AUTH_AUTH0_SECRET = os.environ.get('AUTH0_SECRET')
JWT_AUTH['JWT_AUDIENCE'] = AUTH0_API_IDENTIFIER
JWT_AUTH['JWT_ISSUER'] = AUTH0_DOMAIN

# MESSAGEBIRD WHATSAPP
FB_WHATSAPP_NAMESPACE = os.environ.get('MESSAGEBIRD_FB_NAMESPACE')
MESSAGEBIRD_WHATSAPP_CHANNEL = os.environ.get('MESSAGEBIRD_W_CHANNEL')
MESSAGEBIRD_API_KEY = os.environ.get('MESSAGEBIRD_API')
CUSTOMER_REPAIR_URL = "https://customerservice.mundiaguabalear.com/repair/"


#CACHE
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': os.environ.get('MEMCACHED_URL'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': os.environ.get('MEMCACHEDCLOUD_SERVERS'),
        'OPTIONS': {
            'binary': True,
            'username': os.environ.get('MEMCACHEDCLOUD_USERNAME'),
            'password': os.environ.get('MEMCACHEDCLOUD_PASSWORD'),
        }
    }
}

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
    release=APP_COMPLETE_VERSION
)
