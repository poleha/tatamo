import os
import sys
from django.utils import timezone
from datetime import date
from PIL import Image as PILImage
import io
from urllib.request import urlretrieve
from multi_image_upload.models import save_thumbs, generate_filenames


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kulik.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


from discount import models
from django.db.models import Q
import os
from kulik import settings
from multi_image_upload.models import get_effects
from django.core.files.storage import FileSystemStorage
from datetime import timezone, datetime
from discount.helper import generate_code
from django.db import transaction


#TEST_IMAGE_PATH = os.path.join(settings.BASE_DIR, 'discount', 'load_images')
BASE_IMAGE_PATH = os.path.join(settings.BASE_DIR, 'discount', 'load_images')


class TransactionException(Exception):
    pass


class ProductLoader:
    def __init__(self, file, user, shop=None):
        self.shop = shop
        self.user = user
        self.file = file
        self.errors = {}
        self.products = {}
        self.images = []

        save_path = os.path.join(settings.MEDIA_ROOT, 'discount_product')
        self.storage = FileSystemStorage(save_path)

    def save_image(self, name, line_number):

        try:
            storage = self.storage
            if 'http' in name and ': in name':
                file, message = urlretrieve(name)

            else:
                file = os.path.join(BASE_IMAGE_PATH, name)
            #image = PILImage.open(file)


            new_name, name_jpg, name_ext = generate_filenames(self.storage, name)

            #file_io = io.BytesIO()

            #image = image.convert('RGB')

            #image.save(file_io, 'jpeg')
            #image.save(file_io)
            f = open(file, 'rb')
            storage.save(name_ext, f)
            name = os.path.split(name_jpg)[-1]

            #save_thumbs(storage, thumb_settings, image, upload_to, name):
            save_thumbs(self.storage, settings.PRODUCT_THUMB_SETTINGS, file, '', name)

            self.images.append(name)
        except:
            self.errors[line_number].append('Ошибка при загрузке изображения {0}'.format(name))
            return None

        return 'discount_product/' + name_ext


    def create_single_product(self, line, line_number):
        errors = []
        try:
            line = line.decode()
            print(line)
            line_as_list = line.split(';')
            line_as_list = [elem.strip() for elem in line_as_list]

            try:
                normal_price = int(line_as_list[0])
            except:
                if line_number <= 2:
                    return
                else:
                    errors.append('Цена не указана')
                    normal_price = 100000

            try:
                stock_price = int(line_as_list[1])
            except:
                errors.append('Цена по акции не указана')
                stock_price = 1

            product_type = line_as_list[2]

            try:
                start_date = datetime.strptime(line_as_list[3], '%d.%m.%Y')
            except:
                errors.append('Дата начала акции не указана')
                start_date = max(settings.START_DATE, models.get_today())


            try:
                end_date = datetime.strptime(line_as_list[4], '%d.%m.%Y')
            except:
                errors.append('Дата окончания акции не указана')
                end_date = max(settings.START_DATE, models.get_today())

            brand = line_as_list[5]
            title = line_as_list[6]
            body = line_as_list[7]
            product_shop_code = line_as_list[8]
            compound = line_as_list[9]
            link = line_as_list[10]
            colors = line_as_list[11]
            sizes = line_as_list[12]
            images = line_as_list[13]


            #code = models.Product.generate_unique_code()
            try:
                brand = models.Brand.objects.get(title__iexact=brand)
            except:
                errors.append('Бренд не найден')
                brand = models.Brand.objects.get(title='Татамо')

            if not self.shop:
                shop = line_as_list[14]
                try:
                    shop = models.Shop.objects.get(title__iexact=shop)
                except:
                    errors.append('Магазин не найден')
                    shop = models.Shop.objects.get(title='Татамо')
            else:
                shop = self.shop


            #try:
            #    category = models.ProductType.objects.get(title=category)
            #except:
            #    raise Exception('Категория не найдена')

            try:
                product_type = models.ProductType.objects.get(pk=product_type)
                    #Q(parent=category) |
                    #Q(parent__parent=category) |
                    #Q(parent__parent__parent=category)).filter(
                    #has_childs=False, title=product_type
                #)
            except:
                errors.append('Тип товара не найден')
                product_type = models.ProductType.objects.filter(has_childs=False, filtervaluetoproducttype=None).latest('created')

            try:
                product = models.Product.objects.create(title=title,
                                                    body=body,
                                                    normal_price=normal_price,
                                                    stock_price=stock_price,
                                                    start_date=start_date,
                                                    end_date=end_date,
                                                    #code=code,
                                                    product_type=product_type,
                                                    shop=shop,
                                                    user=self.user,
                                                    ad=False,
                                                    brand=brand,
                                                    status=models.STATUS_PROJECT,
                                                    compound=compound,
                                                    product_shop_code=product_shop_code,
                                                    link=link,

                                                 )
            except models.ValidationError as e:
                errors.append(str(e))
                product = models.Product.objects.filter(shop=models.Shop.objects.get(title='Татамо'))


            top_parent = product_type.get_top_parent()

            try:
                fvtpt = models.FilterValueToProductType.objects.get(filter_type=models.FILTER_TYPE_COLOR, product_type=top_parent)

            except:
                fvtpt = None

            if fvtpt:
                color_names = colors.split(',')
                color_names = [elem.strip().lower() for elem in color_names if elem.strip()]
                for color_name in color_names:
                    try:
                        color = models.FilterValue.objects.get(title__iexact=color_name)
                        product.filter_values.add(color)
                    except:
                        errors.append('Цвет {0} не найден'.format(color_name))

            try:

                fvtpt = models.FilterValueToProductType.objects.get(~Q(filter_type=models.FILTER_TYPE_COLOR), product_type=top_parent)
                size_param = fvtpt.filter_type
            except:
                size_param = None


            if size_param:
                size_names = sizes.split(',')
                size_names = [elem.strip() for elem in size_names if elem.strip()]
                for size_name in size_names:
                    try:
                        size = models.FilterValue.objects.get(title=size_name, filter_type=size_param)
                        product.filter_values.add(size)
                    except:
                        errors.append('Размер {0} не найден'.format(size_name))

            images = images.split(',')
            images = [elem.strip() for elem in images if elem.strip()]

            weight = 0
            try:
                for image in images:
                    weight += 1
                    image_name = self.save_image(image, line_number)
                    if image_name:
                        models.ProductImage.objects.create(
                            product=product,
                            image=image_name,
                            weight=weight,
                                                       )
            except:
                #self.delete_images(product)
                errors.append('Ошибка при загрузке изображений')


        except:
            errors.append('Непредвиденная ошибка')
        if errors:
            print(errors)
            self.errors[line_number] += errors
        else:
            self.products[line_number] = product




    #TODO не нужно
    def delete_product_images(self, product):
        for image in product.images.all():
            self.storage.delete(image.image.short_name)
            for key, value in settings.PRODUCT_THUMB_SETTINGS.items():
                thumb_path = os.path.join(key, image.image.short_name)
                self.storage.delete(thumb_path)

    def delete_images(self):
        for image in self.images:
            self.storage.delete(image)
            for key, value in settings.PRODUCT_THUMB_SETTINGS.items():
                thumb_path = os.path.join(key, image)
                self.storage.delete(thumb_path)

    def load(self):
        try:
            with transaction.atomic():
                line_number = 0
                for line in self.file:
                    line_number += 1
                    #if line_number <= 2:
                    #    continue

                    self.errors[line_number] = []
                    self.create_single_product(line, line_number)

                has_error = any(self.errors.values())
                if has_error:
                    self.delete_images()
                    self.products = {}
                    raise TransactionException('Rolling back transaction')
        except:
            pass
        return (self.errors, self.products)