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
from multi_image_upload.models import save_thumbs
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os


save_path = os.path.join(settings.MEDIA_ROOT)
storage = FileSystemStorage(save_path)

for shop in models.Shop.objects.all():
    try:
        path = shop.image.path
        name = os.path.split(path)[-1]
        save_thumbs(storage, settings.SHOP_THUMB_SETTINGS, path, 'discount_shop',  name)
    except:
        print('shop error', shop.pk)
        pass

for product in models.Product.objects.all():
    for image in product.images.all():
        try:
            path = image.image.path
            name = os.path.split(path)[-1]
            save_thumbs(storage, settings.PRODUCT_THUMB_SETTINGS, path, 'discount_product',  name)
        except:
            print('product error', product.pk)
            pass


for banner in models.ProductBanner.objects.all():
    try:
        path = banner.banner.path
        name = os.path.split(path)[-1]
        save_thumbs(storage, settings.PRODUCT_THUMB_SETTINGS, path, 'discount_product',  name)
    except:
        print('banner error', banner.pk)
        pass
