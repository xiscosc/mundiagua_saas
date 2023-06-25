"""
Django settings for mundiagua_python project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from os.path import join

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

OTHER_APPS = [
    'colorfield',
    'bootstrapform',
    'bootstrap_pagination',
    'async_messages',
    'hijack',
    'hijack.contrib.admin',
    'tinymce',
    'rest_framework',
    'corsheaders',
    'social_django',
]

MY_APPS = [
    'core',
    'client',
    'intervention',
    'budget',
    'repair',
    'engine',
]


INSTALLED_APPS = DJANGO_APPS + OTHER_APPS + MY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'hijack.middleware.HijackUserMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'async_messages.middleware.AsyncMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.login.EnforceLoginMiddleware',
    'core.middleware.staff.StaffMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware'
]

AUTHENTICATION_BACKENDS = {
    'core.auth0login.auth0backend.Auth0',
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
}

PUBLIC_URLS = (
    r'login/*',
    r'uas/*',
    r'privacy/',
    r'complete/*',
    r'admin/',
    r'core/sms-gsm/notify',

    # API URLS ACCESS WILL BE MANAGED IN ANOTHER PLACE
    r'api/*'
)

ROOT_URLCONF = 'mundiagua_python.urls'
WSGI_APPLICATION = 'mundiagua_python.wsgi.application'
NPM_ROOT_PATH = 'static_deps'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'

ASSIGNED_STATUS = 2

AUTH_USER_MODEL = 'core.User'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "media"),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'npm.finders.NpmFinder',
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                "django.template.context_processors.request",
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

JWT_AUTH = {
    'JWT_PAYLOAD_GET_USERNAME_HANDLER':
        'core.auth0authorization.utils.jwt_get_username_from_payload_handler',
    'JWT_DECODE_HANDLER':
        'core.auth0authorization.utils.jwt_decode_token',
    'JWT_ALGORITHM': 'RS256',
    'JWT_AUDIENCE': '',
    'JWT_ISSUER': '',
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
}

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

DEFAULT_NUM_PAGINATOR = 5
DEFAULT_INTERVENTION_PAGINATOR = 13
DEFAULT_REPAIR_PAGINATOR = 16
DEFAULT_BUDGETS_PAGINATOR = 7
DEFAULT_CLIENTS_PAGINATOR = 18
DEFAULT_MODIFICATIONS_PAGINATOR = 18

EMAIL_BACKEND = "django_ses.SESBackend"


NON_STAFF_VIEWS = ('intervention-list-own',
                   'intervention-view',
                   'intervention-forbidden',
                   'intervention-remove-file',
                   'intervention-files',
                   'intervention-file',
                   'intervention-file-download',
                   'client-address-edit-geo',
                   'home',
                   'logout',
                   'login-password',
                   'login',
                   'login-google',
                   'login-google-process',
                   'intervention-image-upload',
                   'intervention-status-job',
                   'changelog',
                   'user-manage',
                   'user-manage-telegram-link-done',
                   'user-manage-telegram-link',
                   'user-manage-telegram-unlink',
                   'user-manage',
                   'password-change',
                   'password-change-done',
                   'sms-gsm-notify',
                   'release'
                   )

TECHNICIAN_VIEWS = (
    'sms-api-all',
    'sms-api-sender',
    'sms-api-id',
    'sms-gsm',
    'sms-gsm-sender',
)

MEDIA_URL = "/media/"

SESSION_COOKIE_AGE = 60 * 60 * 2
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

APP_VERSION = "2023.1"
APP_VERSION_INCLUDES = 20230625
APP_COMPLETE_VERSION = "2023.1.0.20230625"
TEMPLATE_COLOR = '#1d3f72'

# CACHE TIMES IN SEC
CACHE_TIME_CHARTS = 60 * 60
CACHE_TIME_CHART_INCOME = 25 * 60
CACHE_TIME_TYPEAHEAD = 60 * 24 * 60
CACHE_TIME_PHOTOS = 60 * 25
CACHE_TIME_DOCUMENTS = 60 * 10

TINYMCE_DEFAULT_CONFIG = {
    'height': 360,
    'width': '100%',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'modern',
    'plugins': '''
            textcolor save link preview codesample contextmenu
            table lists  insertdatetime  nonbreaking
            contextmenu directionality searchreplace wordcount visualblocks
            visualchars autolink lists  charmap  hr
            anchor pagebreak
            ''',
    'toolbar1': '''
            preview bold italic underline | fontselect,
            fontsizeselect  | forecolor backcolor | alignleft alignright |
            aligncenter alignjustify | indent outdent | bullist numlist table |
            | link | codesample |
            ''',
    'toolbar2': '''
            visualblocks visualchars |
            charmap hr pagebreak nonbreaking anchor |
            ''',
    'contextmenu': 'formats | link',
    'menubar': True,
    'statusbar': True,
}

SMS_TOKEN_CACHE_KEY = 'smstoken'
SMS_TOKEN_EXPIRE_TIME = 60 * 60 * 3

CORS_ALLOW_METHODS = ['GET']
CORS_ORIGIN_REGEX_WHITELIST = [r"^https://\w+\.mundiaguabalear\.com$"]

LOGIN_URL = '/login/'
LOGIN_ERROR_URL = '/login/error-auth/'
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
)
SOCIAL_AUTH_AUTH0_LOGIN_ERROR_URL = "/login/error/"
SOCIAL_AUTH_AUTH0_SCOPE = ['openid', 'profile', 'email']
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/"
