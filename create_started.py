#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kulik.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


from discount import models
from discount import helper
from discount import forms
from django.utils import timezone
from django.db.models import Max
import random
brand_max_pk = models.Brand.objects.aggregate(Max('pk'))['pk__max']
shop_max_pk = models.Shop.objects.aggregate(Max('pk'))['pk__max']
product_type_max_pk = models.ProductType.objects.aggregate(Max('pk'))['pk__max']


111 = 222
for i in range(1000):
    try:
        normal_price = random.randrange(100, 90000, 1)
        stock_price = random.randrange(1, normal_price-1, 1)
        brand_pk = random.randrange(1, brand_max_pk, 1)
        shop_pk = random.randrange(1, shop_max_pk, 1)
        while True:
            product_type_pk = random.randrange(1, product_type_max_pk, 1)
            product_type = models.ProductType.objects.get(pk=product_type_pk)
            if not product_type.has_childs:
                break

        s = models.Product.objects.get(pk=8)
        s1 = models.Product.objects.get(pk=8)
        s.brand = models.Brand.objects.get(pk=brand_pk)
        s.shop = models.Shop.objects.get(pk=shop_pk)
        s.stock_price = stock_price
        s.normal_price = normal_price
        s.pk = None
        s.code = models.Product.generate_unique_code()
        s.product_type = product_type
        s.save()

        for image in s1.images.all():
            image.product = s
            image.pk = None
            image.save()

        for size in models.Product.sizes.through.objects.filter(product=s1):
            size.product = s
            size.pk = None
            size.save()

        for color in models.Product.colors.through.objects.filter(product=s1):
            color.product = s
            color.pk = None
            color.save()

    except:
        pass
#file =  s.image.image.file



#formset = forms.inlineformset_factory(models.Shop, models.Shop, form=ProductImageForm, min_num=1, validate_min=True, extra=3, exclude=['body'], formset=ProductImageBaseFormsetWithDisabled)
#form.save()
#formset.save()
#for image in s.images.all():
#    image.pk = None
#    image.save()


