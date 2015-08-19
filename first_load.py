#!/usr/bin/env python
import os
import sys
from django.utils import timezone
from datetime import date
from django.conf import settings
import random

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kulik.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


from discount.models import Payment, Shop, Product, User, ProductMail, ModelHistory, ProductType, FilterValue
from discount import models
from discount import tasks
from collections import OrderedDict
from django.db.models import Q

if True:

    ProductType.objects.all().delete()
    models.Brand.objects.all().delete()
    FilterValue.objects.all().delete()
    models.SubscriptionType.objects.all().delete()
    models.Shop.objects.all().delete()
    models.Product.objects.all().delete()



    top_parent = models.ProductType()
    top_parent.title = 'Все'
    top_parent.alias = settings.ALIAS_ALL
    top_parent.save()


    colors_tuple = (
    'бежевый',
    'белый',
    'бирюзовый',
    'бордовый',
    'бронзовый',
    'голубой',
    'горчичный',
    'желтый',
    'зеленый',
    'золотой',
    'коралловый',
    'коричневый',
    'красный',
    'молочный',
    'мультиколор',
    'оранжевый',
    'прозрачный',
    'розовый',
    'серебряный',
    'серый',
    'синий',
    'фиолетовый',
    'фуксия',
    'хаки',
    'черный'
    )

    sizes_man_tuple = (
    42,
    44,
    46,
    48,
    50,
    52,
    54,
    56,
    58,
    60,
    62,
    64,
    66,
    68,
    )

    sizes_women_tuple= (
    38,
    40,
    42,
    44,
    46,
    48,
    50,
    52,
    54,
    56,
    58,
    60,
    62,
    64,
    66,
    68,
    )

    sizes_childs_tuple = (
    28,
    30,
    33,
    34,
    36,
    37,
    39,
    50,
    53,
    56,
    59,
    62,
    68,
    70,
    71,
    74,
    75,
    80,
    85,
    86,
    90,
    92,
    96,
    98,
    100,
    104,
    110,
    116,
    118,
    120,
    122,
    128,
    126,
    130,
    134,
    137,
    140,
    146,
    147,
    152,
    158,
    164,
    170,
    176,
    )


    sizes_shoes_tuple = (
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    27,
    28,
    29,
    29.5,
    30,
    31,
    32,
    32.5,
    33,
    33.5,
    34,
    34.5,
    35,
    35.5,
    36,
    36.5,
    37,
    37.5,
    38,
    39,
    40,
    41,
    42,
    42.5,
    43,
    43.5,
    44,
    44.5,
    45,
    45.5,
    46,
    46.5,
    47,
    47.5,
    48,
    48.5,
    49,
    50.5,
    )



    for elem in colors_tuple:
        FilterValue.objects.create(title=elem, filter_type=models.FILTER_TYPE_COLOR)



    for elem in sizes_childs_tuple:
        FilterValue.objects.create(title=elem, filter_type=models.FILTER_TYPE_SIZE_CHILDS)

    for elem in sizes_women_tuple:
        FilterValue.objects.create(title=elem, filter_type=models.FILTER_TYPE_SIZE_WOMAN)

    for elem in sizes_man_tuple:
        FilterValue.objects.create(title=elem, filter_type=models.FILTER_TYPE_SIZE_MAN)

    for elem in sizes_shoes_tuple:
        FilterValue.objects.create(title=elem, filter_type=models.FILTER_TYPE_SIZE_SHOES)



    with open('categ.csv') as file:
        cats = OrderedDict()
        for line in file:
            line_as_list = line.split(';')
            if line_as_list and line_as_list[0] and line_as_list[0] == 'key':
                continue
            key = int(line_as_list[0])
            cat = {}
            cats[key] = cat

            cat['key'] = key
            cat['name'] = line_as_list[1]
            cat['parent'] = line_as_list[6]


        pt_list=[]
        key_list=[]
        for k in cats:
            cat = cats[k]
            pt = ProductType()
            pt.title = cat['name']
            if cat.get('parent', None):
                parent_elem = cats[int(cat['parent'])]
                parent = ProductType.objects.get(pk=parent_elem['pk'])
                pt.parent = parent
            else:
                pt.parent = top_parent
            print(pt)
            pt.save()
            pt_list.append(pt)
            key_list.append(pt.pk)
            cat['pk'] = pt.pk




    pt = models.ProductType.objects.get(level=1, title='Женщинам')
    models.FilterValueToProductType.objects.create(product_type=pt, filter_type=models.FILTER_TYPE_SIZE_WOMAN)
    models.FilterValueToProductType.objects.create(product_type=pt, filter_type=models.FILTER_TYPE_COLOR)
    pt.weight = 1
    pt.alias = settings.ALIAS_WOMEN
    pt.save()

    pt = models.ProductType.objects.get(level=1, title='Мужчинам')
    models.FilterValueToProductType.objects.create(product_type=pt, filter_type=models.FILTER_TYPE_SIZE_MAN)
    models.FilterValueToProductType.objects.create(product_type=pt, filter_type=models.FILTER_TYPE_COLOR)
    pt.weight = 2
    pt.alias = settings.ALIAS_MEN
    pt.save()

    pt = models.ProductType.objects.get(level=1, title='Детям')
    models.FilterValueToProductType.objects.create(product_type=pt, filter_type=models.FILTER_TYPE_SIZE_CHILDS)
    models.FilterValueToProductType.objects.create(product_type=pt, filter_type=models.FILTER_TYPE_COLOR)
    pt.weight = 3
    pt.alias = settings.ALIAS_CHILDREN
    pt.save()


    pt = models.ProductType.objects.get(level=1, title='Обувь')
    models.FilterValueToProductType.objects.create(product_type=pt, filter_type=models.FILTER_TYPE_SIZE_SHOES)
    models.FilterValueToProductType.objects.create(product_type=pt, filter_type=models.FILTER_TYPE_COLOR)
    pt.weight = 4
    pt.alias = settings.ALIAS_SHOES
    pt.save()

    pt = models.ProductType.objects.get(level=1, title='Аксессуары')
    pt.weight = 5
    pt.alias = settings.ALIAS_ACCESSORIES
    pt.save()


    pt = models.ProductType.objects.get(level=1, title='Товары для дома')
    pt.weight = 6
    pt.alias = settings.ALIAS_HOME
    pt.save()

    pt = models.ProductType.objects.get(level=1, title='Ювелирные изделия')
    pt.weight = 7
    pt.alias = settings.ALIAS_JEWELRY
    pt.save()

    pt = models.ProductType.objects.get(level=1, title='Игрушки')
    pt.weight = 8
    pt.alias = settings.ALIAS_TOYS
    pt.save()

    pt = models.ProductType.objects.get(level=1, title='Спорт')
    pt.weight = 9
    pt.alias = settings.ALIAS_SPORT
    pt.save()

    pt = models.ProductType.objects.get(level=1, title='Красота')
    pt.weight = 10
    pt.alias = settings.ALIAS_BEAUTY
    pt.save()





    models.SubscriptionType.objects.create(
        title='Экспресс',
        period_points=7,
        max_products= 2,
        price=950,
        period_type=models.SUBSCRIPTION_PERIOD_TYPE_DAY,

    )


    models.SubscriptionType.objects.create(
        title='Эконом',
        period_points=1,
        max_products=5,
        price=3900,
        period_type=models.SUBSCRIPTION_PERIOD_TYPE_MONTH,

    )

    models.SubscriptionType.objects.create(
        title='Профессионал',
        period_points=1,
        max_products=30,
        price=12900,
        period_type=models.SUBSCRIPTION_PERIOD_TYPE_MONTH,

    )


    models.SubscriptionType.objects.create(
        title='Супер эконом',
        period_points=1,
        max_products=2,
        price=2500,
        period_type=models.SUBSCRIPTION_PERIOD_TYPE_MONTH,

    )

    models.SubscriptionType.objects.create(
        title='Стандарт',
        period_points=1,
        max_products=10,
        price=6900,
        period_type=models.SUBSCRIPTION_PERIOD_TYPE_MONTH,

    )




    models.SubscriptionType.objects.create(
        title='Бонусный',
        period_points=5,
        max_products=1,
        price=0,
        period_type=models.SUBSCRIPTION_PERIOD_TYPE_DAY,

    )


    models.SubscriptionType.objects.create(
        title='Пробная-2',
        period_points=15,
        max_products=2,
        price=0,
        period_type=models.SUBSCRIPTION_PERIOD_TYPE_DAY,
        available=False,

    )


    models.SubscriptionType.objects.create(
        title='Пробная-5',
        period_points=15,
        max_products=5,
        price=0,
        period_type=models.SUBSCRIPTION_PERIOD_TYPE_DAY,
        available=False,

    )


models.SubscriptionType.objects.create(
        title='Пробная-10',
        period_points=15,
        max_products=10,
        price=0,
        period_type=models.SUBSCRIPTION_PERIOD_TYPE_DAY,
        available=False,

    )



try:
    u = models.User.objects.get(username='tatamo')
except:
    u = models.User.objects.create(username='tatamo', email='admin@tatamo.ru', password='1234567')


s = models.Shop.objects.create(title='Татамо',
                                    status=models.SHOP_STATUS_PROJECT,
                                    image='discount_shop/757v20s7dk0o68j0ft9wl0h0zqgaprj7x71f6f4u79luuox19d.png',
                                    user=u,
                                   )
b = models.Brand.objects.create(title='Татамо')

product_images = [
'discount_product/t4dolelk9yj6sl4cv0v770fdk78guednhmimnn7s44h3dt1gwe.jpg',
'discount_product/dlbyk6rlus353m6d28duuktnnsc0pymc2nlfeq8jr11wbjgg1m.jpg',
'discount_product/w57kasjqguf2945ggo5s9h5ov610uw5jw243pn4ncg6ukl7p73.jpg',
'discount_product/eogoz737c64y6nfzcgudnst3ilpys861y61yne460hx17mect9.jpg',
'discount_product/renrh6uax66zr9mvcej8wob3ccmrxzz6ezwgodsw45xepv2aa6.jpg',
]

banners = [
'discount_product_banner/7hmtc4fdmr6y7vyf5x5eszbcadb5zuxh0d5y3cv4jrwpr6wgqs.jpg',
'discount_product_banner/q4m8wddfe7tvivn0zyp9ep2h2ea4lzy7tjgtk3vtmrwzy1ftkq.jpg',
'discount_product_banner/r0diavzk0vsbu2v6rn1hpz13z672yr2hcoip8rmrva8jn84ode.jpg',

]

models.ShopsToUsers.objects.create(shop=s, user=u, confirmed=True)

categs = models.ProductType.objects.filter(level=1)
for categ in categs:
    pt = models.ProductType.objects.filter(has_childs=False).filter(Q(parent=categ) | Q(parent__parent=categ) | Q(parent__parent__parent=categ)).earliest('created')

    random.shuffle(product_images)
    for image in product_images:
        product = Product.objects.create(title='Рекламная акция Татамо', body='Рекламная акция Татамо',
                                         normal_price=100, stock_price=1,
                                             start_date=models.get_today(),
                                             end_date=models.get_today() + timezone.timedelta(days=365),
                                             code='12345', product_type=pt,
                                            shop=s,
                                            user=u,
                                            ad=True,
                                            brand=b,
                                         status=models.STATUS_PROJECT,
                                         compound=''
                                             )
        models.ProductImage.objects.create(
            product=product,
            image=image,
            weight=1,
                                           )
for banner in banners:

    product = Product.objects.create(title='Рекламная акция Татамо', body='Рекламная акция Татамо',
                                         normal_price=100, stock_price=1,
                                             start_date=models.get_today(),
                                             end_date=models.get_today() + timezone.timedelta(days=365),
                                             code='12345', product_type=pt,
                                            shop=s,
                                            user=u,
                                            ad=True,
                                            brand=b,
                                         status=models.STATUS_PROJECT,
                                         compound=''
                                             )
    models.ProductBanner.objects.create(product=product, banner=banner, status=models.BANNER_STATUS_APPROVED)



from polls.models import Poll, Answer

poll = Poll.objects.create(question='Как Вы узнали о Татамо?')

Answer.objects.create(poll=poll, body='Instagram', weight=1)
Answer.objects.create(poll=poll, body='Facebook', weight=2)
Answer.objects.create(poll=poll, body='Vkontakte', weight=3)
Answer.objects.create(poll=poll, body='От друзей', weight=4)
Answer.objects.create(poll=poll, body='SMS/EMAIL рассылка', weight=5)
Answer.objects.create(poll=poll, body='Статья в интернет или запись в блоге', weight=6)
Answer.objects.create(poll=poll, body='Реклама в интернет', weight=7)
Answer.objects.create(poll=poll, body='Другое', weight=8)


if True:
    #import random
    #************************************
    u = models.User.objects.get(pk=1)
    today = models.get_today()

    for i in range(150):
        print('brand', i)
        models.Brand.objects.create(title='Бренд-{0}'.format(i))

    brands = models.Brand.objects.all()

    for i in range(80):
        print('shop', i)
        s = models.Shop.objects.create(title='Магазин-{0}'.format(i),
                                        status=models.SHOP_STATUS_PUBLISHED,
                                        custom_adress='Москва, улица Намоткина, дом 25-а корпус 8 строение 4 офис 234',
                                        image='discount_shop/n5hpt7yrg7b75165hqwmzqu6xa0kf9qa10h2qojqx284x4wscv.png',
                                        user=u,
                                       )

        sub_pro = models.SubscriptionType.objects.get(title='Профессионал')

        models.Subscription.objects.create(
            shop=s,
            start_date=today,
            end_date=today+timezone.timedelta(days=50),
            subscription_type=sub_pro,
            auto_pay=True,
            user=u,
        )
        models.Payment.increase(s, u, 10000000)

        models.ShopsToBrands.objects.create(brand=random.choice(brands), shop=s)
        models.ShopsToBrands.objects.create(brand=random.choice(brands), shop=s)
        models.ShopsToBrands.objects.create(brand=random.choice(brands), shop=s)

        models.ShopPhone.objects.create(shop=s, phone='8(123)456-78-90')
        models.ShopPhone.objects.create(shop=s, phone='8(123)456-78-90')
        models.ShopPhone.objects.create(shop=s, phone='8(123)456-78-90')



    pts = models.ProductType.objects.filter(has_childs=False)
    shops = models.Shop.objects.all().exclude(title='Татамо')


    for i in range(350):
        print('product', i)

        normal_price = random.choice(range(200, 20000))
        stock_price = random.choice(range(100, normal_price-20))
        product = Product.objects.create(title='Тестовая акция{0}'.format(i), body='Описание описание описаниеОписание описание описаниеОписание описание описаниеОписание описание описаниеОписание описание описаниеОписание описание описание',
                                         normal_price=normal_price, stock_price=stock_price,
                                             start_date=today,
                                             end_date=today + timezone.timedelta(days=100),
                                             code='12345', product_type=random.choice(pts),
                                            shop=random.choice(shops), brand=random.choice(brands),
                                            user=u,
                                         status=models.STATUS_PUBLISHED,
                                         compound='Состав, состав, состав, состав и еще состав, состав. Состав, состав, состав, состав и еще состав, состав.'
                                             )


        for filter_param in product.product_type.available_filters:
            k = 0
            max_num = random.choice(range(10))
            filter_values = list(models.FilterValue.objects.filter(filter_type=filter_param))
            random.shuffle(filter_values)
            for filter_value in filter_values:
                k += 1
                product.filter_values.add(filter_value)
                if k >= max_num: break

        banner = models.ProductBanner.objects.create(product=product, banner='discount_product_banner/bkkyr6vzv618mg5zg43t86c34siix65pvspaewnyhz59auhb6l.jpg', status=models.BANNER_STATUS_APPROVED)
        banner =  models.ProductBanner.objects.create(product=product, banner='discount_product_banner/bkkyr6vzv618mg5zg43t86c34siix65pvspaewnyhz59auhb6l.jpg', status=models.BANNER_STATUS_ON_APPROVE)

        action_category = models.ProductAction.objects.create(start=False, start_date=product.start_date,
                                                                               end_date=product.end_date,
                                                                               action_type=models.ACTION_TYPE_CATEGORY,
                                                                               product=product,
                                                                               )

        action_popular = models.ProductAction.objects.create(start=False, start_date=product.start_date,
                                                                               end_date=product.end_date,
                                                                               action_type=models.ACTION_TYPE_POPULAR,
                                                                               product=product, banner=banner,
                                                                               )
        #product.pay()

        models.ProductImage.objects.create(
            product=product,
            image='discount_product/aj9hmjhlxltwepken1peenkxh9jbomvsbeyvc0yyyi5x8h50un.jpg',
            weight=random.choice(range(10)),
                                           )

        models.ProductImage.objects.create(
            product=product,
            image='discount_product/0w80ecji8mc7dmkpyotzhnx8y7t640y9pvyqxmhy8is42l2fqo.jpg',
           weight=random.choice(range(10)),
                                           )

        models.ProductImage.objects.create(
            product=product,
            image='discount_product/5gf9yradwz66mdk92xed9ybgoh9mnilzysjvicc1o21mzevuak.jpg',
            weight=3,
                                           )

        models.ProductImage.objects.create(
            product=product,
            image='discount_product/lgbhbw5y3ubwkd0o083noo5ker1vmayat7ifvq1k098043fxcr.jpg',
            weight=random.choice(range(10)),
                                           )

        models.ProductImage.objects.create(
            product=product,
            image='discount_product/wmg7jjnuyd7dkjo2st7tmegtl2n1dlkpq2o2nf9g9nr57es4o3.jpg',
            weight=random.choice(range(10)),
                                           )

        models.ProductImage.objects.create(
            product=product,
            image='discount_product/jv7qxolhjdqlk5swppj7y7frk91bnlefloi5fnuospnzr88s6a.jpg',
            weight=random.choice(range(10)),
                                           )

        models.ProductImage.objects.create(
            product=product,
            image='discount_product/y71e2oa250imfq7yo4q9hk6e40lu2i443oeu0ikuwjjrt4op4n.jpg',
            weight=random.choice(range(10)),
                                           )



