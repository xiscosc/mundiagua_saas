from .settings import *

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

IMAGE_NOT_FOUND = "base/img/image_not_available.png"

TELEGRAM_TOKEN = ''
TELEGRAM_NAME = 'mundiagua_bot'

GSM_URL = "https://gsm.test.com"
GSM_WATCH_TIME = 300

SMS_USERNAME = ''
SMS_PASSWORD = ''
SMS_SERVICE_URL = ''
USERS_IT = []
USERS_TEC = []
SMS_SERVICE_PHONE = "+34612345678"
CORS_ORIGIN_ALLOW_ALL = True

CELERY_BROKER_TRANSPORT_OPTIONS = {
    'region': AWS_REGION,
    'polling_interval': 30,
    'queue_name_prefix': 'celery-mundiagua-in-EXAMPLE'
}
CELERY_BROKER_URL = "sqs://{aws_access_key}:{aws_secret_key}@".format(
    aws_access_key=safequote(AWS_ACCESS_KEY),
    aws_secret_key=safequote(AWS_SECRET_KEY),
)

NEXMO_KEY = ""
NEXMO_SECRET = ""

SECRET_KEY = 'SECRET KEY'
SOCIAL_AUTH_AUTH0_DOMAIN = 'mundiagua-dev.eu.auth0.com'
SOCIAL_AUTH_AUTH0_KEY = ''
SOCIAL_AUTH_AUTH0_SECRET = ''

AWS_SES_REGION_NAME = AWS_REGION
AWS_SES_ACCESS_KEY_ID = AWS_ACCESS_KEY
AWS_SES_SECRET_ACCESS_KEY = AWS_SECRET_KEY
