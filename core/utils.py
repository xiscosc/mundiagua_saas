# UTILS
import hashlib, re, time
from pushbullet import Pushbullet
from django.core.mail import send_mail


def send_data_to_user(user, subject, body, is_link=False):
    if user.pb_token is not None:
        pb = Pushbullet(user.pb_token)
        if is_link:
            push = pb.push_link(title=subject, url=body)
        else:
            push = pb.push_note(subject, body)
        return push
    else:
        # send email
        ex_body = ""
        if is_link:
            ex_body = "Consulta el siguiente enlace: "

        send_mail(subject=subject, message=ex_body + body,
                      from_email="intranet@mundiaguabalear.com", recipient_list=[user.email])


def generate_md5_id(char, id):
    hash = hashlib.md5(str(time.time())+str(id)+char+str(time.time())).hexdigest()
    hash_numbers = re.sub("[^0-9]", "", hash)
    return char+hash_numbers[:10]