# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import multi_image_upload.models
import discount.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminMonitorMail',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('keys', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(default='', max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('body', models.TextField(null=True, verbose_name='Описание', blank=True)),
                ('all_products_count', models.PositiveIntegerField(default=0, db_index=True, blank=True)),
                ('available_products_count', models.PositiveIntegerField(default=0, db_index=True, blank=True)),
                ('all_products_pks', models.TextField(default='[]', blank=True)),
                ('available_products_pks', models.TextField(default='[]', blank=True)),
                ('image', multi_image_upload.models.MyImageField(null=True, upload_to='discount_brand', verbose_name='Изображение', blank=True)),
                ('user', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(default='', max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('filter_type', models.IntegerField(db_index=True, choices=[(5, 'Размер мужской одежды'), (3, 'Размер женской одежды'), (4, 'Размер обуви'), (2, 'Размер детской одежды'), (1, 'Цвет')])),
                ('title_int', models.FloatField(default=0, db_index=True, blank=True)),
            ],
            options={
                'ordering': ['title_int', 'title'],
            },
        ),
        migrations.CreateModel(
            name='FilterValueToProductType',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('filter_type', models.IntegerField(db_index=True, choices=[(5, 'Размер мужской одежды'), (3, 'Размер женской одежды'), (4, 'Размер обуви'), (2, 'Размер детской одежды'), (1, 'Цвет')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ModelHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('cls', models.CharField(max_length=100, db_index=True)),
                ('created', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('serialized', models.TextField()),
                ('key', models.PositiveIntegerField(db_index=True)),
                ('is_new', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('hashed', models.CharField(max_length=40, blank=True)),
                ('title', models.CharField(default='', max_length=500, verbose_name='Название', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('normal_price', models.IntegerField(db_index=True, verbose_name='Цена до акции')),
                ('stock_price', models.IntegerField(db_index=True, verbose_name='Цена по акции')),
                ('status', models.IntegerField(default=1, verbose_name='Статус', choices=[(1, 'Проект'), (2, 'На согласовании'), (3, 'На доработке'), (4, 'Согласована'), (5, 'Действует'), (6, 'Приостановлена'), (7, 'Старт запланирован'), (8, 'Завершена'), (9, 'Отменена')], blank=True, db_index=True)),
                ('start_date', models.DateField(db_index=True, verbose_name='Дата начала акции')),
                ('end_date', models.DateField(db_index=True, verbose_name='Дата окончания акции')),
                ('code', models.CharField(default='', max_length=200, verbose_name='Код акции', blank=True, unique=True)),
                ('body', models.TextField(verbose_name='Описание', blank=True)),
                ('product_shop_code', models.CharField(default='', max_length=30, verbose_name='Артикул', blank=True)),
                ('compound', models.TextField(default='', max_length=1000, verbose_name='Состав', blank=True)),
                ('shop_comment', models.TextField(default='', verbose_name='Комментарий магазина', blank=True)),
                ('tatamo_comment', models.TextField(default='', verbose_name='Комментарий Tatamo', blank=True)),
                ('publish_time', models.DateTimeField(null=True, blank=True)),
                ('link', models.CharField(max_length=4000, verbose_name='Ссылка на страницу товара на сайте магазина', blank=True)),
                ('simple_code', models.CharField(max_length=100, verbose_name='Код акции', blank=True)),
                ('use_simple_code', models.BooleanField(default=False, verbose_name='Сгенерировать промокод вручную')),
                ('use_code_postfix', models.BooleanField(default=True, verbose_name='Использовать постфикс для промокода')),
                ('percent', models.PositiveIntegerField(verbose_name='Скидка')),
                ('price_category', models.IntegerField(choices=[(1, 'До 3000'), (2, '3000 - 5000'), (3, '5000 - 10000'), (4, '10000 - 15000'), (5, '15000 - 30000'), (6, '30000 - 50000'), (7, 'Дороже 50000')])),
                ('discount_category', models.IntegerField(choices=[(1, 'До 30%'), (2, '30%-50%'), (3, '50%-80%'), (4, 'Более 80%')])),
                ('ad', models.BooleanField(default=False, db_index=True, verbose_name='Рекламная акция')),
                ('start_after_approve', models.BooleanField(default=True, verbose_name='Стартовать/запланировать акцию автоматически после согласования')),
                ('brand', models.ForeignKey(to='discount.Brand', related_name='products', verbose_name='Бренд')),
            ],
            bases=(discount.models.ProductVersionMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ProductBanner',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('hashed', models.CharField(max_length=40, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(default=1, verbose_name='Статус', choices=[(1, 'На согласовании'), (2, 'На доработке'), (3, 'Согласован')], blank=True, db_index=True)),
                ('tatamo_comment', models.TextField(verbose_name='Комментарий Татамо', blank=True)),
                ('shop_comment', models.TextField(verbose_name='Комментарий магазина', blank=True)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('hashed', models.CharField(max_length=40, blank=True)),
                ('title', models.CharField(default='', max_length=500, verbose_name='Название', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('body', models.TextField(verbose_name='Описание')),
                ('product_shop_code', models.CharField(default='', max_length=30, verbose_name='Артикул', blank=True)),
                ('compound', models.TextField(default='', max_length=1000, verbose_name='Состав', blank=True)),
                ('shop_comment', models.TextField(default='', verbose_name='Комментарий магазина', blank=True)),
                ('tatamo_comment', models.TextField(default='', verbose_name='Комментарий Tatamo', blank=True)),
                ('link', models.CharField(max_length=4000, verbose_name='Ссылка на страницу товара на сайте магазина', blank=True)),
                ('status', models.IntegerField(default=1, choices=[(1, 'Проект'), (2, 'На согласовании'), (3, 'На доработке'), (4, 'Согласована')])),
                ('normal_price', models.IntegerField(db_index=True, verbose_name='Цена до акции')),
                ('stock_price', models.IntegerField(db_index=True, verbose_name='Цена по акции')),
                ('brand', models.ForeignKey(verbose_name='Бренд', to='discount.Brand')),
                ('product', models.ForeignKey(to='discount.Product')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductChangerCondition',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('condition', models.TextField(verbose_name='Условие')),
                ('created', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('product_changer', models.ForeignKey(related_name='conditions', to='discount.ProductChanger')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductChangerImage',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('image', multi_image_upload.models.MyImageField(db_index=True, upload_to='discount_product', verbose_name='Изображение')),
                ('created', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('product_changer', models.ForeignKey(related_name='images', to='discount.ProductChanger')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductCondition',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('condition', models.TextField(verbose_name='Условие')),
                ('product', models.ForeignKey(related_name='conditions', to='discount.Product')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductFields',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('weight', models.PositiveIntegerField(default=0, db_index=True)),
                ('product', models.OneToOneField(to='discount.Product', related_name='product_fields')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('image', multi_image_upload.models.MyImageField(db_index=True, upload_to='discount_product', verbose_name='Изображение')),
                ('created', models.DateTimeField(db_index=True, auto_now_add=True)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('email', models.EmailField(max_length=256)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('subscribed', models.BooleanField(default=False)),
                ('history', models.ForeignKey(to='discount.ModelHistory')),
                ('product', models.ForeignKey(related_name='mails', to='discount.Product')),
                ('user', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductStat',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('session_key', models.TextField(blank=True)),
                ('ip', models.CharField(max_length=15)),
                ('product', models.ForeignKey(to='discount.Product')),
                ('user', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductToCart',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('code', models.PositiveIntegerField(null=True, blank=True)),
                ('status', models.IntegerField(default=1, db_index=True, choices=[(1, 'В корзине'), (2, 'Код получен'), (3, 'Завершена магазином'), (4, 'Купил(а)'), (5, 'Передумал(а)'), (6, 'Для немедленного добавления'), (7, 'Приостановлена магазином'), (8, 'Удалена')])),
                ('comment', models.TextField(default='', blank=True)),
                ('session_key', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('subscription_time', models.DateTimeField(null=True, blank=True)),
                ('product', models.ForeignKey(related_name='cart_products', to='discount.Product')),
                ('user', models.ForeignKey(null=True, related_name='cart_products', blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(default='', max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('body', models.TextField(null=True, verbose_name='Описание', blank=True)),
                ('all_products_count', models.PositiveIntegerField(default=0, db_index=True, blank=True)),
                ('available_products_count', models.PositiveIntegerField(default=0, db_index=True, blank=True)),
                ('all_products_pks', models.TextField(default='[]', blank=True)),
                ('available_products_pks', models.TextField(default='[]', blank=True)),
                ('level', models.IntegerField(db_index=True, blank=True)),
                ('has_childs', models.BooleanField(default=False, db_index=True)),
                ('weight', models.PositiveIntegerField(default=1000, blank=True)),
                ('alias', models.SlugField(null=True, blank=True)),
                ('share_filter_params', models.BooleanField(default=False)),
                ('parent', models.ForeignKey(null=True, related_name='childs', blank=True, to='discount.ProductType')),
                ('user', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['weight', 'title'],
            },
        ),
        migrations.CreateModel(
            name='RelatedProduct',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('product', models.ForeignKey(to='discount.Product', related_name='related_products', verbose_name='Акция')),
                ('related_product', models.ForeignKey(to='discount.Product', related_name='products', verbose_name='Связанная акция')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('hashed', models.CharField(max_length=40, blank=True)),
                ('title', models.CharField(default='', max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('body', models.TextField(null=True, verbose_name='Описание', blank=True)),
                ('all_products_count', models.PositiveIntegerField(default=0, db_index=True, blank=True)),
                ('available_products_count', models.PositiveIntegerField(default=0, db_index=True, blank=True)),
                ('all_products_pks', models.TextField(default='[]', blank=True)),
                ('available_products_pks', models.TextField(default='[]', blank=True)),
                ('image', multi_image_upload.models.MyImageField(upload_to='discount_shop', verbose_name='Логотип магазина')),
                ('status', models.IntegerField(default=1, verbose_name='Статус', choices=[(1, 'Проект'), (2, 'На согласовании'), (3, 'На доработке'), (4, 'Опубликован')], db_index=True)),
                ('site', models.CharField(default='', max_length=300, verbose_name='Адрес сайта', blank=True)),
                ('work_time', models.TextField(default='', verbose_name='Время работы', blank=True)),
                ('city', models.CharField(default='', max_length=200, verbose_name='Город', blank=True)),
                ('region', models.CharField(default='', max_length=200, verbose_name='Регион', blank=True)),
                ('area', models.CharField(default='', max_length=200, verbose_name='Район', blank=True)),
                ('street', models.CharField(default='', max_length=300, verbose_name='Улица', blank=True)),
                ('house', models.CharField(default='', max_length=200, verbose_name='Дом', blank=True)),
                ('building', models.CharField(default='', max_length=200, verbose_name='Корпус', blank=True)),
                ('flat', models.CharField(default='', max_length=200, verbose_name='Квартира', blank=True)),
                ('index', models.CharField(default='', max_length=200, verbose_name='Индекс', blank=True)),
                ('settlement', models.CharField(default='', max_length=200, verbose_name='Населенный пункт', blank=True)),
                ('use_custom_adress', models.BooleanField(default=True)),
                ('custom_adress', models.TextField(default='', verbose_name='Адрес', blank=True)),
                ('shop_comment', models.TextField(default='', verbose_name='Комментарий магазина', blank=True)),
                ('tatamo_comment', models.TextField(default='', verbose_name='Комментарий Tatamo', blank=True)),
                ('add_brands', models.TextField(default='', verbose_name='Добавление брендов', blank=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='ShopPhone',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('confirmed', models.BooleanField(default=False, verbose_name='Подтверждено')),
                ('shop', models.ForeignKey(to='discount.Shop')),
                ('user', models.ForeignKey(verbose_name='Имя пользователя', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShopType',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(default='', max_length=500, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('body', models.TextField(default='', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TatamoHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(null=True, blank=True, to='discount.Product')),
                ('product_type', models.ForeignKey(to='discount.ProductType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('phone', models.CharField(default='', max_length=100, verbose_name='Телефон', blank=True)),
                ('get_product_changed_messages', models.BooleanField(default=True, verbose_name='Получать уведомления об изменении условий акций')),
                ('role', models.PositiveIntegerField(default=1, choices=[(1, 'Пользователь'), (2, 'Менеджер магазина'), (3, 'Менеджер Татамо')], blank=True)),
                ('active_shop', models.ForeignKey(null=True, blank=True, to='discount.Shop', verbose_name='Активный магазин')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='profile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='shop',
            name='brands',
            field=models.ManyToManyField(to='discount.Brand', related_name='shops', blank=True, through='discount.ShopsToBrands'),
        ),
        migrations.AddField(
            model_name='shop',
            name='user',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='shop',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='shops', blank=True, through='discount.ShopsToUsers'),
        ),
        migrations.AddField(
            model_name='productchanger',
            name='product_type',
            field=models.ForeignKey(to='discount.ProductType', related_name='changers', verbose_name='Тип товара'),
        ),
        migrations.AddField(
            model_name='productchanger',
            name='user',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='product',
            name='cart_users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='products', blank=True, through='discount.ProductToCart'),
        ),
        migrations.AddField(
            model_name='product',
            name='filter_values',
            field=models.ManyToManyField(db_index=True, related_name='products', blank=True, to='discount.FilterValue'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.ForeignKey(to='discount.ProductType', related_name='products', verbose_name='Тип товара'),
        ),
        migrations.AddField(
            model_name='product',
            name='shop',
            field=models.ForeignKey(to='discount.Shop', related_name='products', verbose_name='Магазин'),
        ),
        migrations.AddField(
            model_name='product',
            name='user',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='filtervaluetoproducttype',
            name='product_type',
            field=models.ForeignKey(to='discount.ProductType'),
        ),
        migrations.AlterIndexTogether(
            name='filtervalue',
            index_together=set([('title_int', 'title')]),
        ),
        migrations.AddField(
            model_name='comment',
            name='product',
            field=models.ForeignKey(related_name='comments', to='discount.Product'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterIndexTogether(
            name='producttocart',
            index_together=set([('product', 'user'), ('user', 'status')]),
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
