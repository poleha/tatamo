# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multi_image_upload.models
import discount.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('body', models.TextField(null=True, blank=True, verbose_name='Описание')),
                ('all_products_count', models.PositiveIntegerField(db_index=True, blank=True, default=0)),
                ('available_products_count', models.PositiveIntegerField(db_index=True, blank=True, default=0)),
                ('all_products_pks', models.TextField(default='[]', blank=True)),
                ('available_products_pks', models.TextField(default='[]', blank=True)),
                ('image', multi_image_upload.models.MyImageField(null=True, upload_to='discount_brand', blank=True, verbose_name='Изображение')),
                ('user', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=256, verbose_name='Имя')),
                ('email', models.EmailField(max_length=256, verbose_name='E-MAIL')),
                ('body', models.TextField(default='', verbose_name='Комментарий')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FilterValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('filter_type', models.IntegerField(choices=[(5, 'Размер мужской одежды'), (3, 'Размер женской одежды'), (4, 'Размер обуви'), (2, 'Размер десткой одежды'), (1, 'Цвет')], db_index=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='FilterValueToProductType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filter_param', models.IntegerField(choices=[(5, 'Размер мужской одежды'), (3, 'Размер женской одежды'), (4, 'Размер обуви'), (2, 'Размер десткой одежды'), (1, 'Цвет')], db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ModelHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cls', models.CharField(db_index=True, max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('serialized', models.TextField()),
                ('key', models.PositiveIntegerField(db_index=True)),
                ('is_new', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('points', models.IntegerField()),
                ('operation', models.IntegerField(choices=[(1, 'Пополнение'), (2, 'Расход')])),
                ('comment', models.TextField(default='', blank=True)),
                ('period', models.DateField(blank=True)),
                ('action_type', models.IntegerField(null=True, choices=[(1, 'Спецразмещение'), (2, 'Категории')], blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=500, blank=True, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('normal_price', models.IntegerField(db_index=True, verbose_name='Цена до акции')),
                ('stock_price', models.IntegerField(db_index=True, verbose_name='Цена по акции')),
                ('status', models.IntegerField(default=1, choices=[(1, 'Проект'), (2, 'На согласовании'), (3, 'На доработке'), (4, 'Согласована'), (5, 'Действует'), (6, 'Приостановлена'), (7, 'Ожидает старта'), (8, 'Завершена')], db_index=True, blank=True, verbose_name='Статус')),
                ('start_date', models.DateField(db_index=True, verbose_name='Дата начала акции')),
                ('end_date', models.DateField(db_index=True, verbose_name='Дата окончания акции')),
                ('code', models.CharField(default='', max_length=200, blank=True, verbose_name='Код акции')),
                ('body', models.TextField(verbose_name='Описание')),
                ('product_shop_code', models.CharField(default='', max_length=30, blank=True, verbose_name='Артикул')),
                ('compound', models.TextField(default='', max_length=1000, blank=True, verbose_name='Состав')),
                ('shop_comment', models.TextField(default='', blank=True, verbose_name='Комментарий магазина')),
                ('tatamo_comment', models.TextField(default='', blank=True, verbose_name='Комментарий Tatamo')),
                ('publish_time', models.DateTimeField(null=True, blank=True)),
                ('percent', models.PositiveIntegerField(verbose_name='Скидка')),
                ('price_category', models.IntegerField(choices=[(1, 'До 3000'), (2, '3000 - 5000'), (3, '5000 - 10000'), (4, '10000 - 15000'), (5, '15000 - 30000'), (6, '30000 - 50000'), (7, 'Дороже 50000')])),
                ('discount_category', models.IntegerField(choices=[(1, 'До 30%'), (2, '30%-50%'), (3, '50%-80%'), (4, 'Более 80%')])),
                ('ad', models.BooleanField(default=False, db_index=True, verbose_name='Рекламная акция')),
                ('brand', models.ForeignKey(verbose_name='Бренд', related_name='products', to='discount.Brand')),
            ],
            bases=(discount.models.PaymentProductMixin, models.Model, discount.models.ProductVersionMixin),
        ),
        migrations.CreateModel(
            name='ProductAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.PositiveIntegerField(choices=[(1, 'Спецразмещение'), (2, 'Категории')], verbose_name='Вид специального размещения')),
                ('start_date', models.DateField(db_index=True, verbose_name='Дата начала')),
                ('end_date', models.DateField(db_index=True, verbose_name='Дата окончания')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('points_blocked', models.PositiveIntegerField(default=0, blank=True)),
                ('status', models.IntegerField(choices=[(1, 'Проект'), (2, 'Действует'), (3, 'Запланирована'), (4, 'Приостановлена'), (5, 'Завершена')], default=1, verbose_name='Статус')),
                ('start', models.BooleanField(default=False, verbose_name='Подтвердить')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductBanner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(default=1, choices=[(1, 'На согласовании'), (2, 'На доработке'), (3, 'Согласован')], db_index=True, blank=True, verbose_name='Статус')),
                ('tatamo_comment', models.TextField(blank=True, verbose_name='Комментарий Татамо')),
                ('shop_comment', models.TextField(blank=True, verbose_name='Комментарий магазина')),
                ('banner', multi_image_upload.models.MyImageField(upload_to='discount_product_banner', verbose_name='Изображение')),
                ('number', models.PositiveIntegerField(default=1, blank=True)),
                ('product', models.ForeignKey(to='discount.Product')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductChanger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(verbose_name='Описание')),
                ('product_shop_code', models.CharField(default='', max_length=30, blank=True, verbose_name='Артикул')),
                ('compound', models.TextField(default='', max_length=1000, blank=True, verbose_name='Состав')),
                ('shop_comment', models.TextField(default='', blank=True, verbose_name='Комментарий магазина')),
                ('tatamo_comment', models.TextField(default='', blank=True, verbose_name='Комментарий Tatamo')),
                ('status', models.IntegerField(choices=[(1, 'Проект'), (2, 'На согласовании'), (3, 'На доработке'), (4, 'Согласована')], default=1)),
                ('brand', models.ForeignKey(to='discount.Brand', verbose_name='Бренд')),
                ('product', models.ForeignKey(to='discount.Product')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductChangerImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', multi_image_upload.models.MyImageField(upload_to='discount_product', db_index=True, verbose_name='Изображение')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('product_changer', models.ForeignKey(related_name='images', to='discount.ProductChanger')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', multi_image_upload.models.MyImageField(upload_to='discount_product', db_index=True, verbose_name='Изображение')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('weight', models.IntegerField(default=1, db_index=True, verbose_name='Порядок показа')),
                ('product', models.ForeignKey(related_name='images', to='discount.Product')),
            ],
            options={
                'ordering': ['weight'],
            },
        ),
        migrations.CreateModel(
            name='ProductMail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=256)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('subscribed', models.BooleanField(default=False)),
                ('history', models.ForeignKey(to='discount.ModelHistory')),
                ('product', models.ForeignKey(related_name='mails', to='discount.Product')),
                ('user', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductToCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.PositiveIntegerField(null=True, blank=True)),
                ('status', models.IntegerField(choices=[(1, 'В корзине'), (2, 'Код получен'), (3, 'Завершена магазином'), (4, 'Купил(а)'), (5, 'Передумал(а)'), (6, 'Для немедленного добавления'), (7, 'Приостановлена магазином')], db_index=True, default=1)),
                ('comment', models.TextField(default='', blank=True)),
                ('session_key', models.TextField(blank=True)),
                ('product', models.ForeignKey(related_name='cart_products', to='discount.Product')),
                ('user', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='cart_products', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('body', models.TextField(null=True, blank=True, verbose_name='Описание')),
                ('all_products_count', models.PositiveIntegerField(db_index=True, blank=True, default=0)),
                ('available_products_count', models.PositiveIntegerField(db_index=True, blank=True, default=0)),
                ('all_products_pks', models.TextField(default='[]', blank=True)),
                ('available_products_pks', models.TextField(default='[]', blank=True)),
                ('level', models.IntegerField(db_index=True, blank=True)),
                ('has_childs', models.BooleanField(db_index=True, default=False)),
                ('weight', models.PositiveIntegerField(default=1000, blank=True)),
                ('alias', models.SlugField(null=True, blank=True)),
                ('parent', models.ForeignKey(null=True, to='discount.ProductType', related_name='childs', blank=True)),
                ('user', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ['weight', 'title'],
            },
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('body', models.TextField(null=True, blank=True, verbose_name='Описание')),
                ('all_products_count', models.PositiveIntegerField(db_index=True, blank=True, default=0)),
                ('available_products_count', models.PositiveIntegerField(db_index=True, blank=True, default=0)),
                ('all_products_pks', models.TextField(default='[]', blank=True)),
                ('available_products_pks', models.TextField(default='[]', blank=True)),
                ('image', multi_image_upload.models.MyImageField(upload_to='discount_shop', verbose_name='Логотип магазина')),
                ('status', models.IntegerField(default=1, choices=[(1, 'Проект'), (2, 'На согласовании'), (3, 'На доработке'), (4, 'Опубликован')], db_index=True, verbose_name='Статус')),
                ('site', models.CharField(default='', max_length=300, blank=True, verbose_name='Адрес сайта')),
                ('work_time', models.CharField(default='', max_length=500, blank=True, verbose_name='Время работы')),
                ('city', models.CharField(default='', max_length=200, blank=True, verbose_name='Город')),
                ('region', models.CharField(default='', max_length=200, blank=True, verbose_name='Регион')),
                ('area', models.CharField(default='', max_length=200, blank=True, verbose_name='Район')),
                ('street', models.CharField(default='', max_length=300, blank=True, verbose_name='Улица')),
                ('house', models.CharField(default='', max_length=200, blank=True, verbose_name='Дом')),
                ('building', models.CharField(default='', max_length=200, blank=True, verbose_name='Корпус')),
                ('flat', models.CharField(default='', max_length=200, blank=True, verbose_name='Квартира')),
                ('index', models.CharField(default='', max_length=200, blank=True, verbose_name='Индекс')),
                ('settlement', models.CharField(default='', max_length=200, blank=True, verbose_name='Населенный пункт')),
                ('use_custom_adress', models.BooleanField(default=True)),
                ('custom_adress', models.TextField(default='', blank=True, verbose_name='Адрес')),
                ('shop_comment', models.TextField(default='', blank=True, verbose_name='Комментарий магазина')),
                ('tatamo_comment', models.TextField(default='', blank=True, verbose_name='Комментарий Tatamo')),
                ('add_brands', models.TextField(default='', blank=True, verbose_name='Добавление брендов')),
            ],
        ),
        migrations.CreateModel(
            name='ShopPhone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=20, verbose_name='Телефон')),
                ('shop', models.ForeignKey(related_name='phones', to='discount.Shop')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShopsToBrands',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.ForeignKey(to='discount.Brand')),
                ('shop', models.ForeignKey(to='discount.Shop')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShopsToUsers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confirmed', models.BooleanField(default=False, verbose_name='Подтверждено')),
                ('shop', models.ForeignKey(to='discount.Shop')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Менеджер')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShopType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500, blank=True, default='')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('body', models.TextField(default='', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateField(null=True, db_index=True, blank=True, verbose_name='Дата начала действия')),
                ('end_date', models.DateField(null=True, db_index=True, blank=True, verbose_name='Действует до')),
                ('status', models.IntegerField(choices=[(1, 'Завершена'), (2, 'Активна'), (3, 'Запланирована'), (4, 'Отменена')], db_index=True, default=2)),
                ('auto_pay', models.BooleanField(default=False)),
                ('shop', models.ForeignKey(to='discount.Shop')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubscriptionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('period_points', models.PositiveIntegerField()),
                ('max_products', models.PositiveIntegerField()),
                ('available', models.BooleanField(default=True)),
                ('price', models.PositiveIntegerField()),
                ('period_type', models.IntegerField(choices=[(1, 'По дням'), (2, 'Календарный месяц'), (3, 'Календарный день')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TatamoHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(null=True, to='discount.Product', blank=True)),
                ('product_type', models.ForeignKey(to='discount.ProductType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(default='', max_length=100, blank=True, verbose_name='Телефон')),
                ('get_product_changed_messages', models.BooleanField(default=True, verbose_name='Получать уведомления об изменении условий акций')),
                ('active_shop', models.ForeignKey(null=True, verbose_name='Активный магазин', to='discount.Shop', blank=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='subscription',
            name='subscription_type',
            field=models.ForeignKey(to='discount.SubscriptionType'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='shop',
            name='brands',
            field=models.ManyToManyField(through='discount.ShopsToBrands', related_name='shops', to='discount.Brand', blank=True),
        ),
        migrations.AddField(
            model_name='shop',
            name='user',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='shop',
            name='users',
            field=models.ManyToManyField(through='discount.ShopsToUsers', related_name='shops', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='productchanger',
            name='product_type',
            field=models.ForeignKey(verbose_name='Тип товара', related_name='changers', to='discount.ProductType'),
        ),
        migrations.AddField(
            model_name='productaction',
            name='banner',
            field=models.ForeignKey(null=True, verbose_name='Баннер', to='discount.ProductBanner', blank=True),
        ),
        migrations.AddField(
            model_name='productaction',
            name='product',
            field=models.ForeignKey(related_name='actions', to='discount.Product'),
        ),
        migrations.AddField(
            model_name='product',
            name='cart_users',
            field=models.ManyToManyField(through='discount.ProductToCart', related_name='products', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='filter_values',
            field=models.ManyToManyField(related_name='products', db_index=True, blank=True, to='discount.FilterValue'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.ForeignKey(verbose_name='Тип товара', related_name='products', to='discount.ProductType'),
        ),
        migrations.AddField(
            model_name='product',
            name='shop',
            field=models.ForeignKey(verbose_name='Магазин', related_name='products', to='discount.Shop'),
        ),
        migrations.AddField(
            model_name='product',
            name='user',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='product',
            field=models.ForeignKey(null=True, to='discount.Product', blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='product_action',
            field=models.ForeignKey(null=True, to='discount.ProductAction', blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='shop',
            field=models.ForeignKey(to='discount.Shop'),
        ),
        migrations.AddField(
            model_name='payment',
            name='subscription',
            field=models.ForeignKey(null=True, to='discount.Subscription', blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='subscription_type',
            field=models.ForeignKey(null=True, to='discount.SubscriptionType', blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='filtervaluetoproducttype',
            name='product_type',
            field=models.ForeignKey(to='discount.ProductType'),
        ),
        migrations.AddField(
            model_name='comment',
            name='product',
            field=models.ForeignKey(related_name='comments', to='discount.Product'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterIndexTogether(
            name='producttocart',
            index_together=set([('user', 'status'), ('product', 'user')]),
        ),
        migrations.AlterIndexTogether(
            name='productimage',
            index_together=set([('product', 'weight')]),
        ),
        migrations.AlterIndexTogether(
            name='product',
            index_together=set([('status', 'ad')]),
        ),
    ]
