#!/usr/bin/env python
import os
import sys
from django.utils import timezone
from datetime import date

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kulik.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

from discount import models
from PIL import Image
from kulik import settings
import os

statuses = [models.STATUS_APPROVED, models.STATUS_PUBLISHED, models.STATUS_READY, models.STATUS_PROJECT, models.STATUS_NEED_REWORK, models.STATUS_TO_APPROVE, models.STATUS_SUSPENDED]

ps = list(models.Product.objects.filter(status__in=statuses, shop__status=models.SHOP_STATUS_PUBLISHED))

for p in ps:
    doubles = models.Product.objects.filter(
        stock_price=p.stock_price,
        normal_price=p.normal_price,
        title=p.title,
        brand=p.brand,
        status__in=statuses,
        body=p.body,
        compound=p.compound,
        link=p.link,
        product_type=p.product_type,
        shop=p.shop,
    ).exclude(pk=p.pk)


    read_doubles = []
    for d in doubles:
        if d in ps:
            ps.remove(d)
        d_images = sorted(list(d.images.all().values_list('image', flat=True)))
        images = sorted(list(p.images.all().values_list('image', flat=True)))

        d_values = sorted(list(d.filter_values.all().values_list('title', flat=True)))
        values = sorted(list(p.filter_values.all().values_list('title', flat=True)))

        eq = True
        if not d_values == values:
            eq = False

        if len(d_images) == len(images):
            for k in range(len(images)):
                try:
                    im1 = Image.open(os.path.join(settings.MEDIA_ROOT, images[k]))
                    im2 = Image.open(os.path.join(settings.MEDIA_ROOT, d_images[k]))
                    if not im1.size == im2.size or not im1.info == im2.info:
                        eq = False
                except:
                    eq = False
        if eq == True:
            read_doubles.append(d)

    if read_doubles:
        read_doubles.append(p)
        print('*****************************')
    for d in read_doubles:
        print(d.pk)




