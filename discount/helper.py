import string
import random
from django.utils import timezone


def generate_code(size=7, upper=False, chars=None):
    if chars is None:
        chars = string.ascii_lowercase + string.digits
        if upper:
            chars += string.ascii_uppercase
    return ''.join(random.choice(chars) for _ in range(size))

def generate_cache_key(prefix, request, kwargs):
    key_dict = request.POST.copy()
    key_dict.update(kwargs)
    str_parameters = ''
    for key in key_dict:
        str_parameters += "{0}-{1}".format(key, key_dict[key])
    full_key = '{0}-{1}'.format(prefix, str_parameters)
    return full_key



def get_today():
    return timezone.localtime(timezone.now()).date()

def get_local_now():
    return timezone.localtime(timezone.now())

def to_int(val):
    if not val:
        res = 0
    else:
        try:
            res = int(val)
        except:
            res = 0
    return res

def myround(x, base=5):
    return int(base * round(float(x)/base))


def replace_newlines(text):
    text = text.replace('\r\n', ' ').replace('\r', '').replace('\n', '')
    return text


def get_link(link):
    link = link.strip()
    if not link or ' ' in link or ',' in link or ';' in link:
        pass
    elif link and not link[:4] == 'http':
        link = 'http://' + link
    return link


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
