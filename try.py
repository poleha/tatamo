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
ps = models.Product.objects.filter(shop_id__in=[50], status__in=[models.STATUS_APPROVED, models.STATUS_PROJECT])
count = ps.count()

for p in ps:
    #p.start_date = timezone.datetime(day=5, year=2015, month=8)
    #p.end_date = timezone.datetime(day=15, year=2015, month=9)
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
        print('left', count)
    except models.ValidationError as e:
        print(e)

"""
"""

t = (
(304	,'vk.com/betrendywear'),
(305	,'vk.com/betrendywear'),
(307	,'vk.com/betrendywear'),
(308	,'vk.com/betrendywear'),

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



"""
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
        status=models.STATUS_READY,
        body=p.body,
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

    for d in reversed(read_doubles):
        num += 1
        if num == 1:
            if not d.link and link:
                d.link = link
                d.save()
                print('saved_link', d.pk, d.link)
            print('untouched', d.pk)
        else:
            d.status = models.STATUS_CANCELLED
            print('cancelled', d.pk)
            #d.save(check_status=False)



"""

"""

from discount.tasks import _recalc_product_weights
_recalc_product_weights()


ps = models.Product.objects.filter(pk__in=[51, 52, 53]).order_by('id')
for p in ps:
    fields = p.product_fields
    fields.weight = p.id
    fields.save()

"""
"""
a = models.ProductType.objects.get(pk=1)

family_look, created = models.ProductType.objects.get_or_create(title='Family Look', parent=a)

c, created = models.ProductType.objects.get_or_create(title='Детям', parent=family_look)
m, created = models.ProductType.objects.get_or_create(title='Мужчинам', parent=family_look)
w, created = models.ProductType.objects.get_or_create(title='Женщинам', parent=family_look)
f, created = models.ProductType.objects.get_or_create(title='Комплект для ребенка и родителей', parent=family_look)

cats = [c, m, w, f]

names = (
    'Брюки и комбинезоны/джинсы',
    'Верхняя одежда',
    'Джемперы и кардиганы/толстовки и олимпийки',
    'Комплекты/Боди',
    'Платья и сарафаны',
    'Футболки и поло',
    'Блузы и рубашки',
    'Нижнее белье/купальники',
    'Носки и колготки',
    'Одежда для спорта',
    'Юбки',
    'Нижнее белье/плавки и шорты для плавания',
    'Рубашки',
    'Шорты'
         )

for cat in cats:
    for name in names:
        models.ProductType.objects.get_or_create(title=name, parent=cat)



old_f_w = models.ProductType.objects.get(pk=254)
old_f_c = models.ProductType.objects.get(pk=270)

ps = models.Product.objects.filter(product_type__in=old_f_w.get_all_childs_with_self())

for p in ps:
    if p.shop_id == 49:
        p.product_type, created = models.ProductType.objects.get_or_create(title=p.product_type.title, parent=f)
    else:
        p.product_type, created = models.ProductType.objects.get_or_create(title=p.product_type.title, parent=w)
    p.save()


ps = models.Product.objects.filter(product_type__in=old_f_c.get_all_childs_with_self())

for p in ps:
    if p.shop_id == 49:
        p.product_type, created = models.ProductType.objects.get_or_create(title=p.product_type.title, parent=f)
    else:
        p.product_type, created = models.ProductType.objects.get_or_create(title=p.product_type.title, parent=c)
    p.save()


from kulik import settings
ps = models.ProductType.objects.get(alias=settings.ALIAS_CHILDREN).all_products.filter(shop_id=36)

for p in ps:
    p.product_type, created = models.ProductType.objects.get_or_create(title=p.product_type.title, parent=c)
    p.save()


ps = models.ProductType.objects.get(alias=settings.ALIAS_WOMEN).all_products.filter(shop_id=36)

for p in ps:
    p.product_type, created = models.ProductType.objects.get_or_create(title=p.product_type.title, parent=w)
    p.save()

#ps = models.Product.objects.all()
#for p in ps:
#    p.apply_storage_params()


#family_look, created = models.ProductType.objects.get_or_create(title='Family Look', parent=a)

#c, created = models.ProductType.objects.get_or_create(title='Детям', parent=family_look)
#m, created = models.ProductType.objects.get_or_create(title='Мужчинам', parent=family_look)
#w, created = models.ProductType.objects.get_or_create(title='Женщинам', parent=family_look)
#f, created = models.ProductType.objects.get_or_create(title='Комплект для ребенка и родителей', parent=family_look)

models.FilterValueToProductType.objects.get_or_create(product_type=c, filter_type=models.FILTER_TYPE_SIZE_CHILDS)
models.FilterValueToProductType.objects.get_or_create(product_type=c, filter_type=models.FILTER_TYPE_COLOR)

models.FilterValueToProductType.objects.get_or_create(product_type=m, filter_type=models.FILTER_TYPE_SIZE_MAN)
models.FilterValueToProductType.objects.get_or_create(product_type=m, filter_type=models.FILTER_TYPE_COLOR)

models.FilterValueToProductType.objects.get_or_create(product_type=w, filter_type=models.FILTER_TYPE_SIZE_WOMAN)
models.FilterValueToProductType.objects.get_or_create(product_type=w, filter_type=models.FILTER_TYPE_COLOR)

models.FilterValueToProductType.objects.filter(product_type=f).delete()
models.FilterValueToProductType.objects.get_or_create(product_type=f, filter_type=models.FILTER_TYPE_COLOR)

f.save()
c.save()
m.save()
w.save()

pts = models.ProductType.objects.all()
for pt in pts:
    models.Product.save_product_storage_elem(pt, 'product_type')
    print(pt.title)

pks = [270, 254]

for pk in pks:
    try:
        pt = models.ProductType.objects.get(pk=pk)
        if pt.all_products_count == 0:
            pt.delete()
    except:
        print('nothing to delete')

"""

#ALIAS_MEN = 'men'
#ALIAS_WOMEN = 'women'
#ALIAS_CHILDREN = 'children'
#ALIAS_SHOES = 'shoes'
#ALIAS_BEAUTY = 'beauty'
#ALIAS_HOME = 'home'
#ALIAS_JEWELRY = 'jewelry'
#ALIAS_TOYS = 'toys'
#ALIAS_ACCESSORIES = 'accessories'
#ALIAS_SPORT = 'sport'
#ALIAS_ALL = 'all'

"""

for pt in models.ProductType.objects.filter(share_filter_params=True):
    pt.share_filter_params = False
    pt.save()

from kulik import settings
men = models.ProductType.objects.get(alias=settings.ALIAS_MEN)
women = models.ProductType.objects.get(alias=settings.ALIAS_WOMEN)
children = models.ProductType.objects.get(alias=settings.ALIAS_CHILDREN)
shoes = models.ProductType.objects.get(alias=settings.ALIAS_MEN)
fl = models.ProductType.objects.get(title='Family Look')
fl.alias = settings.ALIAS_FAMILY_LOOK

men.filtervaluetoproducttype_set.get_or_create(filter_type=models.FILTER_TYPE_SIZE_MAN)
men.filtervaluetoproducttype_set.get_or_create(filter_type=models.FILTER_TYPE_COLOR)
men.share_filter_params = True
men.save()

women.filtervaluetoproducttype_set.get_or_create(filter_type=models.FILTER_TYPE_SIZE_WOMAN)
women.filtervaluetoproducttype_set.get_or_create(filter_type=models.FILTER_TYPE_COLOR)
women.share_filter_params = True
women.save()

children.filtervaluetoproducttype_set.get_or_create(filter_type=models.FILTER_TYPE_SIZE_CHILDS)
children.filtervaluetoproducttype_set.get_or_create(filter_type=models.FILTER_TYPE_COLOR)
children.share_filter_params = True
children.save()

shoes.filtervaluetoproducttype_set.get_or_create(filter_type=models.FILTER_TYPE_SIZE_SHOES)
shoes.filtervaluetoproducttype_set.get_or_create(filter_type=models.FILTER_TYPE_COLOR)
shoes.share_filter_params = True
shoes.save()

fl.filtervaluetoproducttype_set.all().delete()
fl.filtervaluetoproducttype_set.get_or_create(filter_type=models.FILTER_TYPE_COLOR)
fl.share_filter_params = False
fl.save()


n =  (
    models.ProductType.objects.get(alias=settings.ALIAS_BEAUTY),
models.ProductType.objects.get(alias=settings.ALIAS_HOME),
models.ProductType.objects.get(alias=settings.ALIAS_JEWELRY),
models.ProductType.objects.get(alias=settings.ALIAS_TOYS),
models.ProductType.objects.get(alias=settings.ALIAS_ACCESSORIES),
models.ProductType.objects.get(alias=settings.ALIAS_SPORT),
                               )
for e in n:
    e.share_filter_params = False
    e.filtervaluetoproducttype_set.all().delete()





for c in fl.childs.all():
    c.share_filter_params = True
    c.filtervaluetoproducttype_set.get_or_create(filter_type=models.FILTER_TYPE_COLOR)
    if c.title == 'Женщинам':
        c.filtervaluetoproducttype_set.get_or_create(filter_type=models.FILTER_TYPE_SIZE_WOMAN)
    elif c.title == 'Детям':
        c.filtervaluetoproducttype_set.get_or_create(filter_type=models.FILTER_TYPE_SIZE_CHILDS)
    if c.title == 'Мужчинам':
        c.filtervaluetoproducttype_set.get_or_create(filter_type=models.FILTER_TYPE_SIZE_MAN)
    c.save()


pts = models.ProductType.objects.all()
for pt in pts:
    models.Product.save_product_storage_elem(pt, 'product_type')
    pt.save()
    print(pt.title)

"""

#models.ProductType.objects.filter(title='Девочки и мальчики 2-6 лет').delete()
#models.ProductType.objects.filter(title='Девочки и мальчики 6+ лет').delete()

"""

from kulik import settings

children = models.ProductType.objects.get(alias=settings.ALIAS_CHILDREN)

e1, created = models.ProductType.objects.get_or_create(title='Девочки и мальчики 2-6 лет', parent=children)
e2, created = models.ProductType.objects.get_or_create(title='Девочки и мальчики 6+ лет', parent=children)

es = (e1, e2)

t = (
'Блузы и рубашки',
'Брюки и комбинезоны/джинсы',
'Верхняя одежда',
'Джемперы и кардиганы/толстовки и олимпийки',
'Нижнее белье/купальники',
'Носки и колготки',
'Одежда для спорта',
'Футболки и поло',
)


for e in es:
    for el in t:
        models.ProductType.objects.get_or_create(title=el, parent=e)


"""
"""
end_date = timezone.datetime(day=15, year=2015, month=9)

ps = models.Product.objects.filter(shop_id__in=[58, 73, 59, 43, 28, 54, 10, 16, 5], status__in=[models.STATUS_PUBLISHED, models.STATUS_READY], end_date__lt=end_date)
count = ps.count()

for p in ps:
    #p.start_date = timezone.datetime(day=5, year=2015, month=8)
    p.end_date = end_date
    #start = timezone.datetime(day=1, year=2015, month=8).date()
    #p.start_after_approve = True
    #p.status = models.STATUS_APPROVED
    #if p.start_date < start:
    #    print(p.get_absolute_url(), p.start_date, p.end_date)
    #    p.start_date = start

    try:
        p.save()
        #p = p.saved_version
        count -= 1
        print('left', count)
    except models.ValidationError as e:
        print(e)
"""

end_date = timezone.datetime(day=15, year=2015, month=9)
#start_date = timezone.datetime(day=15, year=2015, month=8)
ps = models.Product.objects.filter(shop_id__in=[64, 26, 66, 83, 27, 82], status=models.STATUS_PUBLISHED, end_date__lt=end_date)
count = ps.count()


for p in ps:
    #p.start_date = start_date
    p.end_date = end_date
    #p.use_code_postfix = False
    #start = timezone.datetime(day=1, year=2015, month=8).date()
    #p.start_after_approve = True
    #p.status = models.STATUS_APPROVED
    #if p.start_date < start:
    #    print(p.get_absolute_url(), p.start_date, p.end_date)
    #    p.start_date = start

    try:
        p.save()
        #p = p.saved_version
        count -= 1
        print(p.shop, 'left', count, p.status_text)
    except models.ValidationError as e:
        print(e)






