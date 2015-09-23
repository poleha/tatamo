#!/usr/bin/env python
import os
import sys
from django.utils import timezone
from datetime import date

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kulik.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

from django.core.cache import cache
from discount import models
from discount import tasks
from collections import OrderedDict
from django.db.models import Q


shops = models.Shop.objects.filter(status=models.SHOP_STATUS_PUBLISHED)

res = []

for shop in shops:
    products_count = shop.products.filter(status=models.STATUS_SUSPENDED).count()
    if products_count > 0:
        for user in shop.users.all():
            res.append((user.email, user.profile.phone, user.first_name, products_count))

#print(res)

for elem in res:
    mail, phone, name, products_count = elem
    print('{0}, {1}, {2}'.format(mail, '', name), products_count)