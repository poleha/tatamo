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


"""
ps = models.Product.objects.filter(shop_id__in=[28], status__in=[models.STATUS_APPROVED, models.STATUS_PROJECT])
count = ps.count()

for p in ps:
    p.start_date = timezone.datetime(day=1, year=2015, month=8)
    p.end_date = timezone.datetime(day=15, year=2015, month=8)
    #start = timezone.datetime(day=1, year=2015, month=8).date()
    p.start_after_approve = True
    p.status = models.STATUS_APPROVED
    #if p.start_date < start:
    #    print(p.get_absolute_url(), p.start_date, p.end_date)
    #    p.start_date = start

    try:
        p.save(check_status=False)
        p = p.saved_version
        count -= 1
        print(count)
    except models.ValidationError as e:
        print(e)


"""

"""
t = (
(598, 'http://ilikedress.ru/good/tadashi-shoji-apf2195l/'),
(599, 'http://ilikedress.ru/good/tadashi-shoji-alg1793lx/'),
(600, 'http://ilikedress.ru/good/tadashi-shoji-apa2142l/'),
(601, 'http://ilikedress.ru/good/tadashi-shoji-yv2192l/'),
(602, 'http://ilikedress.ru/good/tadashi-shoji-acz1224my/'),
(603, 'http://ilikedress.ru/good/tadashi-shoji-alx-1812m/'),
(604, 'http://ilikedress.ru/good/tadashi-shoji-alx-1809lx/'),
(605, 'http://ilikedress.ru/good/tadashi-shoji-6l1890l/'),
(606, 'http://ilikedress.ru/good/tadashi-shoji-acz1224l/'),
(607, 'http://ilikedress.ru/good/tadashi-shoji-oc1862l/'),
(608, 'http://ilikedress.ru/good/tadashi-shoji-alt1809ly/'),
(609, 'http://ilikedress.ru/good/tadashi-shoji-fy1125l/'),
(610, 'http://ilikedress.ru/good/tadashi-shoji-3k1527m/'),
(611, 'http://ilikedress.ru/good/terani-couture-151m0352/'),
(612, 'http://ilikedress.ru/good/terani-couture-151m0361/'),
(613, 'http://ilikedress.ru/good/terani-couture-151m0351/'),
(614, 'http://ilikedress.ru/good/terani-couture-151e0277/'),
(615, 'http://ilikedress.ru/good/terani-couture-151e0265/'),
(616, 'http://ilikedress.ru/good/terani-couture-151p0044/'),
(617, 'http://ilikedress.ru/good/terani-couture-151p0113/'),
(618, 'http://ilikedress.ru/good/terani-couture-151p0097/'),
(619, 'http://ilikedress.ru/good/terani-couture-151p0016/'),
(620, 'http://ilikedress.ru/good/terani-couture-p3059/'),
(621, 'http://ilikedress.ru/good/terani-couture-151p0037/'),
(622, 'http://ilikedress.ru/good/terani-couture-151p0027/'),
(623, 'http://ilikedress.ru/good/terani-couture-151p0064/'),
(624, 'http://ilikedress.ru/good/terani-couture-151p0115/'),
(625, 'http://ilikedress.ru/good/terani-couture-151p0102/'),
(626, 'http://ilikedress.ru/good/terani-couture-h1917/'),
(627, 'http://ilikedress.ru/good/terani-couture-151p0116/'),
(628, 'http://ilikedress.ru/good/terani-couture-e3797/'),

)


for k, l in t:
    p = Product.objects.get(pk=k)
    p.link = l
    p.save()
    print(p.link)

"""
"""
from django.db import transaction
s = models.Shop.objects.get(pk=53)
t = s.add_brands

l = t.split(',')
with transaction.atomic():
    for b in l:
        b = b.strip()
        brand, created = models.Brand.objects.get_or_create(title=b)
        stb, created2 = models.ShopsToBrands.objects.get_or_create(shop=s, brand=brand)
        print(brand.title, created, created2)


    #s.add_brands = ''
    s.save()

"""

"""

unique_fields = ['code']

duplicates = (models.Product.objects.values(*unique_fields)
                             .order_by()
                             .annotate(max_id=models.Max('id'),
                                       count_id=models.Count('id'))
                             .filter(count_id__gt=1))
for d in duplicates:
    code = d['code']
    num = 0
    ps = models.Product.objects.filter(code=code)
    print('***************************')
    link = ''
    for p in ps:
        if p.link:
            link = p.link

    for p in ps:
        print(p.code, p.status_text, p.link)
        if p.code == '12345':
            p.code = models.Product.generate_unique_code()
            p.save()
        elif p.status != models.STATUS_READY:
            p.status = models.STATUS_CANCELLED
            p.code = models.Product.generate_unique_code()
            p.save(check_status=False)
        else:
            num += 1
            if num == 1:
                p.link = link
            if not num == 1:
                p.code = models.Product.generate_unique_code()
                p.status = models.STATUS_CANCELLED
                p.save(check_status=False)


"""
#ДОДЕЛАТЬ РАЗНЫЕ СТАТУСЫ ДЛЯ ПРОДУКТИВА
from PIL import Image
from kulik import settings
import os

ps = models.Product.objects.all()

for p in ps:
    doubles = models.Product.objects.filter(
        stock_price=p.stock_price,
        normal_price=p.normal_price,
        title=p.title,
        brand=p.brand,
        #status=models.STATUS_READY,
        body=p.body,
        compound=p.compound,
    ).exclude(pk=p.pk)

    link = ''
    for d in doubles:
        if d.link:
            link = d.link


    read_doubles = []
    for d in doubles:
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
    num = 0

    for d in read_doubles:
        num += 1
        if num == 1:
            if not d.link and link:
                d.link = link
                d.save(check_status=False)
                print('saved_link', d.pk, d.link)
            print('untouched', d.pk)
        else:
            d.status = models.STATUS_CANCELLED
            print('cancelled', d.pk)
            d.save(check_status=False)



