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
from discount.models import Payment, Shop, Product, User, ProductMail, ModelHistory, ProductType
from discount import models
from discount import tasks
from collections import OrderedDict
from django.db.models import Q

#s = Shop.objects.get(pk=2)

tasks._save_product_storages()
