from .settings import *
import os
import django_heroku

django_heroku.settings(locals())

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NPM_ROOT_PATH = os.path.join(BASE_DIR, 'npm-dependencies')
MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware'] + list(MIDDLEWARE)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

SENDGRID_API_KEY = "key"
DEBUG = os.getenv('DEBUG') == 'True'
DOMAIN = os.getenv('DOMAIN')
ALLOWED_HOSTS = [os.getenv('ALLOWED_HOSTS')]

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_REGION = os.getenv('AWS_REGION')

GMAPS_API_KEY = os.getenv('GMAPS_API_KEY')

BITLY_API_KEY = os.getenv('BITLY_API_KEY')

NUMBER_TEMPLATES = 5

IMAGE_NOT_FOUND = "base/img/image_not_available.png"

NEXMO_KEY = os.getenv('NEXMO_KEY')
NEXMO_SECRET = os.getenv('NEXMO_SECRET')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_NAME = os.getenv('TELEGRAM_NAME')
GSM_URL = "https://gsm.mundiaguabalear.com"
GSM_WATCH_TIME = 5
TIME_RECORD_CACHE_TIME = 60*60*24
S3_IMAGES = os.getenv('S3_IMAGES')
S3_PROCESSING_IMAGES = os.getenv('S3_PROCESSING_IMAGES')
S3_DOCUMENTS = os.getenv('S3_DOCUMENTS')
S3_WHATSAPP = os.getenv('S3_WHATSAPP')

SOCIAL_AUTH_TRAILING_SLASH = False  # Remove trailing slash from routes
SMS_SERVICE_PHONE = os.getenv('SMS_SERVICE_PHONE')
CORS_ORIGIN_ALLOW_ALL = True

SECRET_KEY = os.getenv('SECRET_KEY')

AUTH0_API_IDENTIFIER = os.getenv('AUTH0_API_IDENTIFIER')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')

SOCIAL_AUTH_AUTH0_DOMAIN = AUTH0_DOMAIN
SOCIAL_AUTH_AUTH0_KEY = os.getenv('SOCIAL_AUTH_AUTH0_KEY')
SOCIAL_AUTH_AUTH0_SECRET = os.getenv('SOCIAL_AUTH_AUTH0_SECRET')

JWT_AUTH['JWT_AUDIENCE'] = AUTH0_API_IDENTIFIER
JWT_AUTH['JWT_ISSUER'] = AUTH0_DOMAIN


FB_WHATSAPP_NAMESPACE = os.getenv('FB_WHATSAPP_NAMESPACE')
MESSAGEBIRD_WHATSAPP_CHANNEL = os.getenv('MESSAGEBIRD_WHATSAPP_CHANNEL')
MESSAGEBIRD_API_KEY = os.getenv('MESSAGEBIRD_API_KEY')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
