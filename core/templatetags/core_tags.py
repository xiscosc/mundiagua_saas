import time
from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def template_number():
    num = int(settings.NUMBER_TEMPLATES)
    day = int(time.strftime("%d"))
    img_number = (day % num) + 1
    return str(img_number)


@register.simple_tag
def app_version():
    return str(settings.APP_VERSION)


@register.simple_tag
def app_version_includes():
    return "?v=" + str(settings.APP_VERSION_INCLUDES)


@register.simple_tag
def google_client_id():
    return str(settings.GOOGLE_CLIENT_ID)