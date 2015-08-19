#!/usr/bin/env python
import os
import sys
from django.utils import timezone
from datetime import date

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kulik.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


from discount.models import Transaction, Shop, Product, User, ProductMail, ModelHistory, ProductType, Color, Size, MenuItem
from discount import models
from discount import views
from discount import tasks
from collections import OrderedDict
from django.db.models import Q

from django.utils import timezone

start = timezone.now()

for i in range(50):
    ps = Product.objects.all()
    for p in ps:
        k = p.sizes.all()



end = timezone.now()
delta = end - start

print(delta)


