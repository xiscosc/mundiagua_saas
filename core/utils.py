# UTILS
import re
import string
import requests
import uuid

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import InvalidPage
from django.urls import reverse_lazy
from pytz import timezone

INTERVENTION_REGEX = '[v|V][0-9]+'
IDEGIS_REGEX = '[x|X][0-9]+'
ZODIAC_REGEX = '[z|Z][0-9]+'
ATH_REGEX = '[a|A][0-9]+'
CLIENT_REGEX = '[c|C][0-9]+'
ENGINE_REGEX = '[e|B][0-9]+'
BUDGET_REGEX = '[p|P][0-9]+'
BUDGET_REGEX_2ND_FORMAT = '[p|P][m|M][0-9][0-9]/[0-9]+'
BUDGET_REGEX_3RD_FORMAT = '[p|P][m|M][0-9][0-9]-[0-9]+'


def generate_repair_online_id(char):
    return (char + str(uuid.uuid4())[:6]).upper()


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

    zodiac_r = re.compile(ZODIAC_REGEX)
    zodiac_m = zodiac_r.match(search_text)
    if zodiac_m is not None:
        idstr = zodiac_m.group()
        id = int(re.sub("[^0-9]", "", idstr))
        return {"found": True, "url": reverse_lazy('repair:repair-zodiac-view', kwargs={"pk": id})}

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


def create_nexmo_client():
    import nexmo
    return nexmo.Client(key=settings.NEXMO_KEY, secret=settings.NEXMO_SECRET)


def encode_nexmo_body(body):
    import unidecode
    import re
    encoded_body = unidecode.unidecode(body).upper()
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    urls = [x[0] for x in re.findall(regex, body)]
    for url in urls:
        encoded_body = encoded_body.replace(url.upper(), url)

    return encoded_body


def check_nexmo_message_sent(api_result):
    if 'message-count' in api_result and int(api_result['message-count']) > 0:
        if 'messages' in api_result:
            if 'status' in api_result['messages'][0] and int(api_result['messages'][0]['status']) == 0:
                return True
    return False


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


def get_page_from_paginator(paginator, page):
    try:
        return paginator.page(page)
    except InvalidPage:
        return paginator.page(paginator.num_pages)


def get_sms_token():
    token = cache.get(settings.SMS_TOKEN_CACHE_KEY)
    if token:
        return token
    else:
        url = settings.SMS_SERVICE_URL + '/user_token'
        body = {'username': settings.SMS_USERNAME, 'password': settings.SMS_PASSWORD}
        r = requests.post(url=url, json=body)
        if r.status_code == 200:
            token = r.json()['token']
            if token:
                cache.set(settings.SMS_TOKEN_CACHE_KEY, token, settings.SMS_TOKEN_EXPIRE_TIME)
                return token
    
    return None
        
    

def get_sms_api(url, limit=0, offset=0):
    host = settings.SMS_SERVICE_URL + url
    headers = {'Authorization': get_sms_token()}
    params = {'limit': limit, 'offset': offset}
    r = requests.get(url=host, headers=headers, params=params)
    return r.status_code, r.json()


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
    for id in search_objects_in_text(ZODIAC_REGEX, text):
        try:
            intervention.repairs_zodiac.add(id)
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
