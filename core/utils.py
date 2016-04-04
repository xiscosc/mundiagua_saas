# UTILS
import hashlib, re, time
from pushbullet import Pushbullet


def send_data_to_user(user, subject, body, is_link=False):
    if user.pb_token is not None:
        pb = Pushbullet(user.pb_token)
        if is_link:
            push = pb.push_link(title=subject, url=body)
        else:
            push = pb.push_note(subject, body)
    else:
        # send email
        pass


def generate_md5_id(char, id):
    hash = hashlib.md5(str(time.time())+str(id)+char+str(time.time())).hexdigest()
    hash_numbers = re.sub("[^0-9]", "", hash)
    return char+hash_numbers[:10]