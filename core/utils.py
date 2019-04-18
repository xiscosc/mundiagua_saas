# UTILS
import hashlib
import os
import re
import string
import time
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.mail import send_mail
from django.core.paginator import InvalidPage
from django.urls import reverse_lazy
from pushbullet import Pushbullet
from pytz import timezone
import telegram

INTERVENTION_REGEX = '[v|V][0-9]+'
IDEGIS_REGEX = '[x|X][0-9]+'
ATH_REGEX = '[a|A][0-9]+'
CLIENT_REGEX = '[c|C][0-9]+'
ENGINE_REGEX = '[e|B][0-9]+'
BUDGET_REGEX = '[p|P][0-9]+'
BUDGET_REGEX_2ND_FORMAT = '[p|P][m|M][0-9][0-9]/[0-9]+'
BUDGET_REGEX_3RD_FORMAT = '[p|P][m|M][0-9][0-9]-[0-9]+'
TELEGRAM_TOKEN_REGEX = '\d+-\w{10}'


def send_data_to_user(user, subject, body, is_link=False, from_user=None):

    result = False
    if user.telegram_token:
        result = send_telegram_message(user.telegram_token, body, subject)

    if not result and user.has_pb():
        try:
            pb = Pushbullet(user.pb_token)
            if is_link:
                push = pb.push_link(title=subject, url=body)
            else:
                push = pb.push_note(subject, body)
            return push
        except:
            return send_mail_m(user, subject, body, is_link=is_link, fallback=True, from_user=from_user)

    if not result and not user.has_pb():
        return send_mail_m(user, subject, body, is_link=is_link, fallback=False, from_user=from_user)

    return result


def generate_md5_id(char, id):
    line = str(time.time()) + str(id) + char + str(time.time())
    hash = hashlib.md5(line.encode("utf-8")).hexdigest()
    hash_numbers = re.sub("[^0-9]", "", hash)
    return char + hash_numbers[:6]


def send_mail_m(user, subject, body, is_link=False, fallback=False, from_user=None):
    ex_body = ""
    if fallback:
        ex_body = "MENSAJE ENVIADO POR SISTEMA DE RECUPERACION - PUSHBULLET HA FALLADO\n\n"
    if is_link:
        ex_body += "Consulta el siguiente enlace: "

    if from_user is None:
        from_email = "intranet@mundiaguabalear.com"
    else:
        from_email = from_user.email
    try:
        return send_mail(subject=subject, message=ex_body + body,
                     from_email=from_email, recipient_list=[user.email])
    except:
        return False


def get_return_from_id(search_text):

    intervention_r = re.compile(INTERVENTION_REGEX)
    intervention_m = intervention_r.match(search_text)
    if intervention_m is not None:
        idstr = intervention_m.group()
        id = int(re.sub("[^0-9]", "", idstr))
        return {"found": True, "url": reverse_lazy('intervention:intervention-view', kwargs={"pk": id})}

    budget_r = re.compile(BUDGET_REGEX)
    budget_m = budget_r.match(search_text)
    if budget_m is not None:
        idstr = budget_m.group()
        id = int(re.sub("[^0-9]", "", idstr))
        return {"found": True, "url": reverse_lazy('budget:budget-view', kwargs={"pk": id})}

    budget_r2 = re.compile(BUDGET_REGEX_2ND_FORMAT)
    budget_m = budget_r2.match(search_text)
    if budget_m is not None:
        idstr = budget_m.group()
        id = int(re.sub("[^0-9]", "", idstr)[2:])
        return {"found": True, "url": reverse_lazy('budget:budget-view', kwargs={"pk": id})}

    budget_r3 = re.compile(BUDGET_REGEX_3RD_FORMAT)
    budget_m = budget_r3.match(search_text)
    if budget_m is not None:
        idstr = budget_m.group()
        id = int(re.sub("[^0-9]", "", idstr)[2:])
        return {"found": True, "url": reverse_lazy('budget:budget-view', kwargs={"pk": id})}

    idegis_r = re.compile(IDEGIS_REGEX)
    idegis_m = idegis_r.match(search_text)
    if idegis_m is not None:
        idstr = idegis_m.group()
        id = int(re.sub("[^0-9]", "", idstr))
        return {"found": True, "url": reverse_lazy('repair:repair-idegis-view', kwargs={"pk": id})}

    ath_r = re.compile(ATH_REGEX)
    ath_m = ath_r.match(search_text)
    if ath_m is not None:
        idstr = ath_m.group()
        id = int(re.sub("[^0-9]", "", idstr))
        return {"found": True, "url": reverse_lazy('repair:repair-ath-view', kwargs={"pk": id})}

    client_r = re.compile(CLIENT_REGEX)
    client_m = client_r.match(search_text)
    if client_m is not None:
        idstr = client_m.group()
        id = int(re.sub("[^0-9]", "", idstr))
        return {"found": True, "url": reverse_lazy('client:client-view', kwargs={"pk": id})}

    engine_r = re.compile(ENGINE_REGEX)
    engine_m = engine_r.match(search_text)
    if engine_m is not None:
        idstr = engine_m.group()
        id = int(re.sub("[^0-9]", "", idstr))
        return {"found": True, "url": reverse_lazy('engine:engine-view', kwargs={"pk": id})}

    return {"found": False, "url": None}


def get_time_zone():
    return timezone(settings.TIME_ZONE)


def has_to_change_password(d):
    return date.today() > (d + relativedelta(years=1, days=1))


def create_amazon_client(service):
    import boto3
    try:
        client = boto3.client(service,
                              aws_access_key_id=settings.AWS_ACCESS_KEY,
                              aws_secret_access_key=settings.AWS_SECRET_KEY,
                              region_name=settings.AWS_REGION
                              )
        return client
    except:
        return None


def generate_thumbnail(intervention_image):
    from PIL import Image, ImageOps
    path_in = os.path.join(settings.MEDIA_ROOT, intervention_image.file_path())
    filename = "%d_th.%s" % (intervention_image.pk, intervention_image.get_extension())
    path_out = os.path.join(settings.MEDIA_ROOT, 'intervention_images', 'th', filename)
    image = Image.open(path_in)
    thumbnail = ImageOps.fit(image, settings.THUMBNAIL_SIZE, Image.ANTIALIAS)
    type = "JPEG"
    if intervention_image.get_extension().lower() == "png":
        type = "PNG"
    thumbnail.save(path_out, type, quality=95)
    return os.path.join('intervention_images', 'th', filename)


def search_objects_in_text(regex, text, trim=False):
    import re
    data = re.compile(regex).findall(text)
    ids = []
    for d in data:
        id = re.sub("[^0-9]", "", d)
        if trim:
            id = id[2:]
        ids.append(int(id))
    return ids


def generate_telegram_auth(id, email):
    now = datetime.now()
    key = str(id) + email + str(now.hour)
    data = hashlib.sha256(key.encode()).hexdigest()
    return data[:5] + data[-5:]


def is_telegram_token(token):
    import re
    data = re.compile(TELEGRAM_TOKEN_REGEX).findall(token)
    return len(data) == 1


def format_filename(s):
    """Take a string and return a valid filename constructed from the string.
Uses a whitelist approach: any characters not present in valid_chars are
removed. Also spaces are replaced with underscores.

Note: this method may produce invalid filenames such as ``, `.` or `..`
When I use this method I prepend a date string like '2009_01_15_19_46_32_'
and append a file extension like '.txt', so I avoid the potential of using
an invalid filename.

"""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ', '_')  # I don't like spaces in filenames.
    return filename


def send_telegram_message(token, message, subject=None):
    s_subject = ''
    if subject:
        s_subject = subject + '\n\n'

    try:
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        bot.send_message(chat_id=token, text=s_subject + message)
        return True
    except:
        return False


def send_telegram_picture(token, img_route):
    try:
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        return bot.send_photo(chat_id=token, photo=open(img_route, 'rb'))
    except:
        return False


def send_telegram_picture_bin(token, img_data):
    try:
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        return bot.send_photo(chat_id=token, photo=img_data)
    except:
        return False


def send_telegram_document(token, doc_route, filename):
    try:
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        return bot.send_document(chat_id=token, document=open(doc_route, 'rb'), filename=filename)
    except:
        return False


def send_telegram_document_bin(token, doc_data, filename):
    try:
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        return bot.send_document(chat_id=token, document=doc_data, filename=filename)
    except:
        return False


def delete_telegram_messages(token, ids, intervention):
    removed = 0
    try:
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
    except:
        return False

    for id in ids:
        try:
            bot.delete_message(chat_id=token, message_id=id)
            removed += 1
        except:
            pass

    if removed > 0:
        bot.send_message(chat_id=token, text="Se han elminado los archivos de " + str(intervention))


def get_page_from_paginator(paginator, page):
    try:
        return paginator.page(page)
    except InvalidPage:
        return paginator.page(paginator.num_pages)


def autolink_intervention(intervention, text, user):
    from async_messages import messages
    added = False
    error = False

    for id in search_objects_in_text(ATH_REGEX, text):
        try:
            intervention.repairs_ath.add(id)
            added = True
        except:
            error = True
    for id in search_objects_in_text(IDEGIS_REGEX, text):
        try:
            intervention.repairs_idegis.add(id)
            added = True
        except:
            error = True
    for id in search_objects_in_text(BUDGET_REGEX, text):
        try:
            intervention.budgets.add(id)
            added = True
        except:
            error = True
    for id in search_objects_in_text(BUDGET_REGEX_2ND_FORMAT, text, trim=True):
        try:
            intervention.budgets.add(id)
            added = True
        except:
            error = True
    for id in search_objects_in_text(BUDGET_REGEX_3RD_FORMAT, text, trim=True):
        try:
            intervention.budgets.add(id)
            added = True
        except:
            error = True

    if added:
        messages.success(user, "Se han autonvinculado presupuestos y/o reparaciones a esta avería")
    if error:
        messages.warning(user, "Ha ocurrido un error durante la autovinculación en esta avería")
