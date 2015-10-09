from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from multi_image_upload.models import MyImageField
from django.core.urlresolvers import reverse
from django.utils import timezone
import discount.helper as helper
from django.core import serializers
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.core.cache import cache
# from markitup.fields import MarkupField
from django.forms import ValidationError
from django.conf import settings
import datetime
from collections import OrderedDict
from django.db.models import Sum, Max
from discount.helper import get_today, get_local_now
#from threading import Lock
from django.db.models.manager import BaseManager
from django.db.models import Q, When, Case, IntegerField, Count
import json
from django.core.cache.utils import make_template_fragment_key
from django.utils.html import format_html
from copy import copy
from django.db import transaction
from django.core.exceptions import NON_FIELD_ERRORS
from random import shuffle
import hashlib
from contact_form.models import ContactForm, STATUS_CREATED
from django.db.models.signals import post_save, m2m_changed, pre_save
import random

class ErrorDict():
    def __init__(self):
        self.errors = {}

    def append(self, key, val):
        if not key in self.errors:
            self.errors[key] = []
        if not val in self.errors[key]:
            self.errors[key].append(val)




def set_conditional_cache(key, value, condition, expires=None):
    condition_key = '__condition__{0}'.format(key)
    cache.set(condition_key, condition, expires)
    cache.set(key, value, expires)


def get_conditional_cache(key, condition):
    condition_key = '__condition__{0}'.format(key)
    stored_condition = cache.get(condition_key)
    if not stored_condition == condition:
        cache.delete_many([key, condition_key])
    return cache.get(key)


def request_with_empty_guest(request):
    # ptc_count = models.ProductToCart.get_full_cart_queryset(request).count()
    if hasattr(request, 'user'):
        if not request.user.is_authenticated() and not ProductToCart.request_has_cart(request):
            return True
    return False


class TatamoModelMixin(models.Model):
    class Meta:
        abstract=True
    @property
    def saved_version(self):
        if self.pk:
            v = type(self).objects.get(pk=self.pk)
        else:
            v = None
        return v




PRICE_CATEGORY_1 = 1
PRICE_CATEGORY_2 = 2
PRICE_CATEGORY_3 = 3
PRICE_CATEGORY_4 = 4
PRICE_CATEGORY_5 = 5
PRICE_CATEGORY_6 = 6
PRICE_CATEGORY_7 = 7
PRICE_CATEGORIES = (
    (PRICE_CATEGORY_1, 'До 3000'), (PRICE_CATEGORY_2, '3000 - 5000'), (PRICE_CATEGORY_3, '5000 - 10000'),
    (PRICE_CATEGORY_4, '10000 - 15000'), (PRICE_CATEGORY_5, '15000 - 30000'),
    (PRICE_CATEGORY_6, '30000 - 50000'), (PRICE_CATEGORY_7, 'Дороже 50000'))

DISCOUNT_CATEGORY_1 = 1
DISCOUNT_CATEGORY_2 = 2
DISCOUNT_CATEGORY_3 = 3
DISCOUNT_CATEGORY_4 = 4
DISCOUNT_CATEGORIES = (
    (DISCOUNT_CATEGORY_1, 'До 30%'), (DISCOUNT_CATEGORY_2, '30%-50%'), (DISCOUNT_CATEGORY_3, '50%-80%'),
    (DISCOUNT_CATEGORY_4, 'Более 80%'))

STATUS_NEW = '__NEW__'
STATUS_PROJECT = 1  # Only shop
STATUS_TO_APPROVE = 2  # Only shop
STATUS_NEED_REWORK = 3  # Only shop
STATUS_APPROVED = 4  # NEW, Only shop
STATUS_PUBLISHED = 5  # Everyone
STATUS_SUSPENDED = 6  # Everyone в фильтрах - нет, по ссылке - да
STATUS_READY = 7  # Only shop
STATUS_FINISHED = 8  # NEW
STATUS_CANCELLED = 9

PRODUCT_STATUSES = (
    (STATUS_PROJECT, 'Проект'), (STATUS_TO_APPROVE, 'На согласовании'), (STATUS_NEED_REWORK, 'На доработке'),
    (STATUS_APPROVED, 'Согласована'),
    (STATUS_PUBLISHED, 'Действует'), (STATUS_SUSPENDED, 'Приостановлена'),
    (STATUS_READY, 'Старт запланирован'), (STATUS_FINISHED, 'Завершена'),(STATUS_CANCELLED, 'Отменена'))


CHANGER_STATUSES = (
    (STATUS_PROJECT, 'Проект'), (STATUS_TO_APPROVE, 'На согласовании'), (STATUS_NEED_REWORK, 'На доработке'),
    (STATUS_APPROVED, 'Согласована'))



AVAILABLE_STATUSES = {
        STATUS_NEW: [STATUS_PROJECT, STATUS_TO_APPROVE],
        STATUS_PROJECT: [STATUS_TO_APPROVE, STATUS_CANCELLED],
        STATUS_TO_APPROVE: [STATUS_NEED_REWORK, STATUS_APPROVED],
        STATUS_NEED_REWORK: [STATUS_TO_APPROVE, STATUS_APPROVED, STATUS_CANCELLED],
        STATUS_APPROVED: [STATUS_READY, STATUS_PUBLISHED, STATUS_PROJECT, STATUS_CANCELLED],
        STATUS_READY: [STATUS_APPROVED, STATUS_PUBLISHED, STATUS_PROJECT, STATUS_CANCELLED],
        STATUS_PUBLISHED: [STATUS_SUSPENDED, STATUS_FINISHED],
        STATUS_SUSPENDED: [STATUS_PUBLISHED, STATUS_FINISHED],
        STATUS_FINISHED: [],
        STATUS_CANCELLED: [STATUS_PROJECT],

}
TO_SAVE = 1
TO_APPROVE = 2
TO_CANCEL = 3
TO_PLAN = 4
TO_PUBLISH = 5
TO_PROJECT = 6
TO_SUSPEND = 7
TO_FINISH = 8

BUTTONS = {
        TO_SAVE: ('to-save','Сохранить'),
        TO_APPROVE: ('to-approve','Отправить на согласование'),
        TO_CANCEL: ('to-cancel','Отменить акцию'),
        TO_PLAN: ('to-plan','Запланировать старт'),
        TO_PUBLISH: ('to-publish','Стартовать немедленно'),
        TO_PROJECT: ('to-project','Вернуть на доработку'),
        TO_SUSPEND: ('to-suspend','Временно приостановить'),
        TO_FINISH: ('to-finish','Завершить окончательно'),
}


AVAILABLE_BUTTONS = {
        STATUS_NEW: [TO_SAVE, TO_APPROVE],
        STATUS_PROJECT: [TO_SAVE, TO_APPROVE, TO_CANCEL],
        STATUS_TO_APPROVE: [],
        STATUS_NEED_REWORK: [TO_SAVE, TO_APPROVE, TO_CANCEL],
        STATUS_APPROVED: [TO_SAVE, TO_PLAN, TO_PUBLISH, TO_PROJECT, TO_CANCEL],
        STATUS_READY: [TO_SAVE, TO_PUBLISH, TO_PROJECT, TO_CANCEL],
        STATUS_PUBLISHED: [TO_SAVE, TO_SUSPEND, TO_FINISH],
        STATUS_SUSPENDED: [TO_SAVE, TO_PUBLISH, TO_FINISH],
        STATUS_FINISHED: [],
        STATUS_CANCELLED: [TO_PROJECT],
}




SHOP_STATUS_PROJECT = 1
SHOP_STATUS_TO_APPROVE = 2
SHOP_STATUS_NEED_REWORK = 3
SHOP_STATUS_PUBLISHED = 4

SHOP_STATUSES = ((SHOP_STATUS_PROJECT, 'Проект'), (SHOP_STATUS_TO_APPROVE, 'На согласовании'),
                 (SHOP_STATUS_NEED_REWORK, 'На доработке'), (SHOP_STATUS_PUBLISHED, 'Опубликован'))

#CART_STATUS_PROJECT = 1
#CART_STATUS_FINISHED = 2
#CART_STATUS_DELETED = 3

#CART_STATUSES = ((CART_STATUS_PROJECT, 'Проект'), (CART_STATUS_FINISHED, 'Завершена'), (CART_STATUS_DELETED, 'Удалена'))

PTC_STATUS_CART = 1  # regular cart
PTC_STATUS_SUBSCRIBED = 2
PTC_STATUS_FINISHED_BY_SHOP = 3
PTC_STATUS_BOUGHT = 4
PTC_STATUS_CANCELLED = 5
PTC_STATUS_INSTANT = 6  # instant cart
PTC_STATUS_SUSPENDED = 7
PTC_STATUS_DELETED = 8

PTC_STATUSES = (
                (PTC_STATUS_CART, 'В корзине'), (PTC_STATUS_SUBSCRIBED, 'Код получен'),
                (PTC_STATUS_FINISHED_BY_SHOP, 'Завершена магазином'),
                (PTC_STATUS_BOUGHT, 'Купил(а)'), (PTC_STATUS_CANCELLED, 'Передумал(а)'),
                (PTC_STATUS_INSTANT, 'Для немедленного добавления'),
                (PTC_STATUS_SUSPENDED, 'Приостановлена магазином'),
                (PTC_STATUS_DELETED, 'Удалена'),
                )

ACTION_STATUS_PROJECT = 1
ACTION_STATUS_ACTIVE = 2
ACTION_STATUS_PLANNED = 3
ACTION_STATUS_PAUSED = 4
ACTION_STATUS_FINISHED = 5

ACTION_STATUSES = (
    (ACTION_STATUS_PROJECT, 'Проект'),
    (ACTION_STATUS_ACTIVE, 'Действует'),
    (ACTION_STATUS_PLANNED, 'Запланирована'),
    (ACTION_STATUS_PAUSED, 'Приостановлена'),
    (ACTION_STATUS_FINISHED, 'Завершена'),
)





FILTER_TYPE_COLOR = 1
FILTER_TYPE_SIZE_CHILDS = 2
FILTER_TYPE_SIZE_WOMAN = 3
FILTER_TYPE_SIZE_SHOES = 4
FILTER_TYPE_SIZE_MAN = 5


FILTER_TYPES = (
    (FILTER_TYPE_SIZE_MAN, 'Размер мужской одежды'),
    (FILTER_TYPE_SIZE_WOMAN, 'Размер женской одежды'),
    (FILTER_TYPE_SIZE_SHOES, 'Размер обуви'),
    (FILTER_TYPE_SIZE_CHILDS, 'Размер детской одежды'),
    (FILTER_TYPE_COLOR, 'Цвет'),

)

#TODO Сделать нормально
FILTER_PARAMS_FIELD_NAMES = {
    FILTER_TYPE_SIZE_MAN: ('sizes_man', 'Размеры'),
    FILTER_TYPE_SIZE_WOMAN: ('sizes_woman', 'Размеры'),
    FILTER_TYPE_SIZE_SHOES: ('sizes_shoes', 'Размеры'),
    FILTER_TYPE_SIZE_CHILDS: ('sizes_childs', 'Размеры'),
    FILTER_TYPE_COLOR: ('colors', 'Цвета'),
}

FILTER_PARAMS_BY_FIELD = {
    'sizes_man': FILTER_TYPE_SIZE_MAN,
    'sizes_woman': FILTER_TYPE_SIZE_WOMAN,
    'sizes_shoes': FILTER_TYPE_SIZE_SHOES,
    'sizes_childs': FILTER_TYPE_SIZE_CHILDS,
    'colors': FILTER_TYPE_COLOR,
}


ACTIVE_STATUSES = [STATUS_PUBLISHED]

if settings.SHOW_PREPARED_PRODUCTS:
    ACTIVE_STATUSES.append(STATUS_READY)


AVAILABLE_FOR_RELATED_PRODUCTS_STATUSES = (
        STATUS_TO_APPROVE,
        STATUS_NEED_REWORK,
        STATUS_APPROVED,
        STATUS_READY,
        STATUS_PUBLISHED,
        STATUS_SUSPENDED,
)


def get_title_by_num(tups, num):
    for tup in tups:
        n, txt = tup
        if n == num:
            return txt


def get_choice_by_num(tups, num):
    txt = get_title_by_num(tups, num)
    return (num, txt)


class AbstractHashMixin(models.Model):
    class Meta:
        abstract = True

    hashed = models.CharField(max_length=40, blank=True)


    @property
    def fieds_to_hash(self):
        return self._meta.get_all_field_names()

    def get_fields_hash(self):
        txt = type(self).__name__ + str(self.pk)
        if self.pk:
            txt += str(self.pk)
        for field_name in sorted(self.fieds_to_hash):
            try:
                val = str(getattr(self, field_name))
                txt += val
            except:
                pass
        return hashlib.sha1(txt.encode()).hexdigest()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        #self.hashed = self.get_fields_hash()
        type(self).objects.filter(pk=self.pk).update(hashed=self.get_fields_hash())

        #self.save(update_fields=["hashed"])


class AbstractStripTitleMixin(models.Model):
    class Meta:
        abstract = True

    

    def save(self, *args, **kwargs):
        self.title = self.title.strip()
        super().save(*args, **kwargs)



class AbstractModel(TatamoModelMixin, AbstractStripTitleMixin):
    class Meta:
        abstract = True
    title = models.CharField(max_length=500, blank=False, verbose_name='Название', default='')
    user = models.ForeignKey(User, null=True, blank=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title




class AbstractModelBodyMixin(TatamoModelMixin):
    class Meta:
        abstract = True

    body = models.TextField(null=True, blank=True, verbose_name='Описание')


class TatamoHistory(TatamoModelMixin):
    product = models.ForeignKey('Product', null=True, blank=True)
    product_type = models.ForeignKey('ProductType')
    created = models.DateTimeField(auto_now_add=True)


class AbstractProductStorage(TatamoModelMixin):
    class Meta:
        abstract = True

        # Для ускорения

    all_products_count = models.PositiveIntegerField(blank=True, default=0, db_index=True)
    available_products_count = models.PositiveIntegerField(blank=True, default=0, db_index=True)
    all_products_pks = models.TextField(blank=True, default='[]')
    available_products_pks = models.TextField(blank=True, default='[]')

    @property
    def all_products(self):
        return Product.objects.filter(pk__in=self.all_products_pks)

    @property
    def available_products(self):
        return Product.objects.filter(pk__in=self.available_products_pks)


    #def get_product_storage_elem_cache_key(self, param_name):
    #    key_prefix = 'product_storage_elem-{0}_{1}'.format(type(self).__name__, self.pk)
    #    key = '{0}_{1}'.format(key_prefix, param_name)
    #    return key

    def save_product_storage_elem(self):
        if isinstance(self, Brand):
            field_name = 'brand'
        elif isinstance(self, Shop):
            field_name = 'shop'
        elif isinstance(self, ProductType):
            field_name = 'product_type'

        if field_name == 'product_type':
            all_products_pks = Product.objects.filter(
                product_type__in=self.get_all_childs_with_self()).distinct().values_list('pk',flat=True)
        else:
            flt = {field_name: self}
            all_products_pks = Product.objects.filter(**flt).distinct().values_list('pk', flat=True)

        available_products_pks = Product.objects.filter(pk__in=all_products_pks).get_available_products().values_list('pk', flat=True)
        all_products_count = len(all_products_pks)
        available_products_count = len(available_products_pks)

        params = (('all_products_pks', all_products_pks), ('available_products_pks', available_products_pks),
                  ('all_products_count', all_products_count), ('available_products_count', available_products_count),)

        for param_name, param_value in params:
            if not isinstance(param_value, int):
                param_value = list(param_value)
            #cache.set(elem.get_product_storage_elem_cache_key(param_name), param_value, None)

        self.all_products_count = all_products_count
        self.all_products_pks = json.dumps(list(all_products_pks))
        self.available_products_pks = json.dumps(list(available_products_pks))
        self.all_products_count = all_products_count
        self.available_products_count = available_products_count
        if field_name == 'product_type':
            self.save(auto=True)
        else:
            self.save()



    def __getattribute__(self, item):
        try:
            pk = object.__getattribute__(self, 'id')
        except:
            pk = False
        if pk and item in ('all_products_count', 'available_products_count',
                           'all_products_pks', 'available_products_pks'):

            #key = self.get_product_storage_elem_cache_key(item)
            #result = cache.get(key)
            result = super().__getattribute__(item)
            if isinstance(result, str):
                result = json.loads(result)

            return result
        else:
            return super().__getattribute__(item)

    def save(self, *args, **kwargs):
        if self.id is None:
            self.all_products_count = 0
            self.available_products_count = 0
            self.all_products_pks = '[]'
            self.available_products_pks = '[]'
        super().save(*args, **kwargs)


class ProductType(AbstractModel, AbstractModelBodyMixin, AbstractProductStorage):
    class Meta:
        ordering = ['weight', 'title']
    parent = models.ForeignKey('self', null=True, blank=True, related_name='childs', db_index=True)
    level = models.IntegerField(blank=True, db_index=True)
    has_childs = models.BooleanField(default=False, blank=True, db_index=True)
    weight = models.PositiveIntegerField(blank=True, default=1000)
    alias = models.SlugField(null=True, blank=True, db_index=True)
    share_filter_params = models.BooleanField(default=False)
    #filter_values_available = models.ManyToManyField('FilterValueToProductType')
    #sizes_filter_available = models.BooleanField(default=True, blank=True, db_index=True)
    #colors_filter_available = models.BooleanField(default=True, blank=True, db_index=True)

    def get_nearest_parent_with_shared_filter_params(self):
        cur = self
        res = self
        while cur:
            if cur.share_filter_params:
                res = cur
            cur = cur.parent
        return res




    def filter_available(self, param_key):
        return self.filtervaluetoproducttype_set.filter(filter_type=param_key).exists()

    @property
    def available_filters(self):
        return FilterValueToProductType.objects.filter(product_type=self).values_list('filter_type', flat=True)


    #@property
    #def dress_sizes_filter_available(self):
    #    return self.filtervaluetoproducttype_set.filter(filter_param=FILTER_TYPE_DRESS_SIZE).exists()

    #@property
    #def colors_filter_available(self):
    #    return self.filtervaluetoproducttype_set.filter(filter_param=FILTER_TYPE_COLOR).exists()


    # objects = PublishedProductsManager()
    # all_objects = models.Manager()

    def product_create_pseudo_queryset(self):
        pks = self._product_create_pseudo_queryset()
        queryset = ProductType.objects.filter(pk__in=pks).order_by('parent')
        #clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(pks)])
        #ordering = 'CASE %s END' % clauses
        #queryset = ProductType.objects.filter(pk__in=pks).extra(
        #   select={'ordering': ordering}, order_by=('ordering',))
        return queryset


    def _product_create_pseudo_queryset(self):
        pseudo_queryset = []
        pts1 = ProductType.objects.filter(parent=self)
        for pt1 in pts1:
            if not pt1.has_childs:
                pseudo_queryset.append(pt1.pk)
            pseudo_queryset += pt1._product_create_pseudo_queryset()
        return pseudo_queryset


    @property
    def create_title(self):
        if self.level < 3:
            return self.title
        else:
            return '{0} -> {1}'.format(self.parent.title, self.title)


    def __str__(self):
        if self.level < 2:
            return self.title
        else:
            cur = self
            res = [cur.title]
            while cur.parent and cur.parent.level > 0:
                cur = cur.parent
                res.append(cur.title)

            return ' -> '.join(reversed(res))



    #@property
    #def left_menu_title(self):
    #    sep = '*'
    #    return (sep * (self.level - 1)) + self.title
        #if self.level < 3:
        #    return self.title
        #else:
        #    return '{0} -> {1}'.format(self.parent.title, self.title)


    def get_products_for_main_page(self):
        key = 'get_products_for_main_page_{0}'.format(self.pk)
        favourites = cache.get(key)
        if favourites is None:
            today = get_today()
            favourites = []
            from math import fabs

            today = get_today()

            max_number = settings.MAX_CATEGORY_COUNT
            available_products_pks = self.available_products_pks
            all_products_pks = self.all_products_pks


            #TODO переделать в продуктиве
            additional_products = Product.objects.filter(pk__in=available_products_pks)
            additional_products = list(additional_products)
            shuffle(additional_products)
            additional_products = additional_products[:max_number]
            #additional_products = filter_popular_products(additional_products, lack)
            for product in additional_products:
                favourites.append(product)


            cache.set(key, favourites, 60 * 30)
        shuffle(favourites)
        return favourites

    #def __str__(self):
    #    return self.title

        # if self.has_childs:
        #    return self.title
        # else:
        #    return '{0} - {1}'.format(self.title, self.parent.title)



        # separator = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
        # if self.level == 3:
        #    return format_html('{0}{1}'.format(separator * 2, self.title))
        # elif self.level == 2:
        #    return format_html('{0}{1}'.format(separator, self.title))
        # else:
        #    return self.title

    def get_level(self, obj=None, level=0):
        if obj == None:
            obj = self
        if not obj.parent:
            return level
        else:
            return self.get_level(obj.parent, level + 1)

    def get_all_childs_with_self(self):
        childs = [self]
        childs += self.get_all_childs()
        return childs

    def get_all_childs(self, item=None):
        if item is None:
            item = self
            self.all_childs = []
        for child in item.childs.all():
            self.all_childs.append(child)
            self.get_all_childs(item=child)
        return self.all_childs

    def get_all_elements_to_save(self):
        childs = self.get_all_childs()
        parents = self.get_all_parents()
        return childs + parents

    def get_all_parents(self, end_level=0):
        parents = []
        cur = self
        while cur.parent and cur.parent.level >= end_level:
            cur = cur.parent
            parents.append(cur)
        return parents

    def get_all_parents_with_self(self):
        parents = [self]
        parents += self.get_all_parents()
        return parents

    def save(self, *args, auto=False, **kwargs):
        self.level = self.get_level()
        self.has_childs = self.get_has_childs
        super().save(*args, **kwargs)
        top_parent = self.get_nearest_parent_with_shared_filter_params()
        if not top_parent.pk == self.pk:
            filter_types_parent = FilterValueToProductType.objects.filter(product_type=top_parent).values_list('filter_type', flat=True)
            filter_types_self = FilterValueToProductType.objects.filter(product_type=self).values_list('filter_type', flat=True)
            for f in filter_types_parent:
                if not f in filter_types_self:
                    FilterValueToProductType.objects.create(product_type=self, filter_type=f)
            for f in filter_types_self:
                if not f in filter_types_parent:
                    FilterValueToProductType.objects.filter(product_type=self, filter_type=f).delete()

        if not auto:
            to_save = self.get_all_elements_to_save()
            for elem in to_save:
                elem.save(auto=True)  # to change level

    @property
    def get_has_childs(self):
        if self.childs.exists():
            return True
        else:
            return False

    def get_absolute_url(self):
        if self.alias:
            return reverse('discount:product-list', kwargs={'alias': self.alias})
        else:
            return reverse('discount:product-list', kwargs={'alias': self.pk})

    def get_top_parent(self, level=1):
        if self.level <= level:
            return self
        else:
            return self.parent.get_top_parent()

    @classmethod
    def get_items_by_level(cls, level=0):
        return cls.objects.filter(level=level)

    """
    def get_available_products(self):
        queryset = self.products.filter(end_date__gte=timezone.now())
        queryset = queryset.filter(status=STATUS_PUBLISHED)
        return queryset
    """

    def get_all_products_with_hierarchy(self):
        # queryset = Product.objects.filter(product_type__in=self.get_all_childs_with_self()).distinct()
        product_pks = self.all_products_pks
        queryset = Product.objects.filter(pk__in=product_pks)
        return queryset

    def get_available_products_with_hierarchy(self):
        # queryset = Product.objects.filter(product_type__in=self.get_all_childs_with_self()).distinct()
        product_pks = self.available_products_pks
        queryset = Product.objects.filter(pk__in=product_pks)
        return queryset

    @staticmethod
    def append_perms(queryset, user):
        if user and user.is_shop_manager:
            queryset = queryset.exclude(~Q(status__in=ACTIVE_STATUSES) & ~Q(shop=user.get_shop)).distinct()
            # Если пользователь не админ и может редактировать магазины,
            #  то мы для него исключаем продукты, которые не в статусе опубликован и не
            # его магазина одновременно. То есть оставляем опубликованные и все его магазина.
        else:
            queryset = queryset.filter(end_date__gte=timezone.now())
            queryset = queryset.filter(status__in=ACTIVE_STATUSES)
        return queryset

    @cached_property
    def slug(self):
        if self.alias:
            return self.alias
        else:
            return self.pk


class ShopType(TatamoModelMixin):
    title = models.CharField(max_length=500, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    body = models.TextField(blank=True, default='')

    def __str__(self):
        return self.title


"""
fields_to_save = ['colors', 'product_type', 'sizes']
class ProductStorageMixin(TatamoModelMixin):
    #created = models.DateTimeField(auto_now_add=True)
    #model_type = models.CharField(max_length=256)
    #model = models.ForeignKey
    available_products_count = models.PositiveIntegerField(default=0)
    all_products_count = models.PositiveIntegerField(default=0)
    available_product_pks = models.TextField()
    all_product_pks = models.TextField()

    def apply_product_values(self):


        for field_name in fields_to_save:
            elems = getattr(self, field_name).all()
            for elem in elems:
                flt = {field_name: elem}
                all_products_pks = Product.objects.filter(**flt).distinct().values_list('pk', flat=True)
                available_products_pks = Product.objects.filter(pk__in=all_products_pks).get_available_products().values_list('pk', flat=True)
                all_products_count = len(all_products_pks)
                available_products_count = len(available_products_pks)
                ps = cls()
                ps.all_products_pks = json.dumps(all_products_pks)
                ps.available_products_pks = json.dumps(available_products_pks)
                ps.all_products_count = all_products_count
                ps.available_products_count = available_products_count
                ps.save()
"""


class ShopQueryset(models.QuerySet):
    def filter(self, *args, **kwargs):
        queryset = super().filter(*args, **kwargs)
        return queryset

    """
    def order_by_available_products_count(self):
        queryset = self.annotate(
        select={
            'available_products_count': 'SELECT COUNT(id) FROM discount_product WHERE discount_shop.id = discount_product.shop_id AND discount_product.status={0}'.format(STATUS_PUBLISHED)
        },
        ).extra(order_by=['-available_products_count'])
        queryset = self.annotate(available_products_count=Sum(
            Case(When(products__status=STATUS_PUBLISHED, then=1),
                 default=0,
                 output_field=IntegerField(),))).order_by('-available_products_count')
        return queryset
    """


class ShopManager(BaseManager.from_queryset(ShopQueryset)):
    use_for_related_fields = True

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class Shop(AbstractModel, AbstractModelBodyMixin, AbstractProductStorage, AbstractHashMixin):
    class Meta:
        ordering = ['title']

    # shop_type = models.ForeignKey(ShopType)
    users = models.ManyToManyField(User, through='ShopsToUsers', related_name='shops', blank=True)
    brands = models.ManyToManyField('Brand', through='ShopsToBrands', related_name='shops', blank=True)

    image = MyImageField(verbose_name='Логотип магазина', upload_to='discount_shop',
                         thumb_settings=settings.SHOP_THUMB_SETTINGS)
    status = models.IntegerField(choices=SHOP_STATUSES, default=SHOP_STATUS_PROJECT, verbose_name='Статус',
                                 db_index=True)
    site = models.CharField(max_length=300, verbose_name='Адрес сайта', blank=True, default='')
    work_time = models.TextField(verbose_name='Время работы', blank=True, default='')

    city = models.CharField(max_length=200, verbose_name='Город', blank=True, default='')
    region = models.CharField(max_length=200, verbose_name='Регион', blank=True, default='')
    area = models.CharField(max_length=200, verbose_name='Район', blank=True, default='')
    street = models.CharField(max_length=300, verbose_name='Улица', blank=True, default='')
    house = models.CharField(max_length=200, verbose_name='Дом', blank=True, default='')
    building = models.CharField(max_length=200, verbose_name='Корпус', blank=True, default='')
    flat = models.CharField(max_length=200, verbose_name='Квартира', blank=True, default='')
    index = models.CharField(max_length=200, verbose_name='Индекс', blank=True, default='')
    settlement = models.CharField(max_length=200, verbose_name='Населенный пункт', blank=True, default='')

    use_custom_adress = models.BooleanField(default=True)
    custom_adress = models.TextField(blank=True, verbose_name='Адрес', default='')

    shop_comment = models.TextField(blank=True, verbose_name='Комментарий магазина', default='')
    tatamo_comment = models.TextField(blank=True, verbose_name='Комментарий Tatamo', default='')
    add_brands = models.TextField(blank=True, verbose_name='Добавление брендов', default='')
    objects = ShopManager()

    @property
    def get_link(self):
        link = self.site
        if not link:
            ''
        else:
            return helper.get_link(link)

    @property
    def show_link(self):
        link = self.site.strip()
        if not link or ' ' in link or ',' in link or ';' in link:
            return False
        else:
            return True


    @property
    def fieds_to_hash(self):
        return ['title', 'user', 'created', 'add_brands', 'tatamo_comment', 'shop_comment', 'custom_adress',
                'use_custom_adress', 'settlement', 'index', 'flat', 'building', 'house', 'street', 'area', 'region',
                'city', 'work_time', 'site', 'status', 'image', 'brands', 'users', 'body']

    @property
    def status_text(self):
        if self.status == SHOP_STATUS_PROJECT:
            res = 'Проект'
        elif self.status == SHOP_STATUS_TO_APPROVE:
            res = 'На согласовании'
        elif self.status == SHOP_STATUS_NEED_REWORK:
            res = 'Необходима доработка'
        elif self.status == SHOP_STATUS_PUBLISHED:
            res = 'Опубликован'
        return res

    @property
    def is_project(self):
        return self.status == SHOP_STATUS_PROJECT

    @property
    def on_approve(self):
        return self.status == SHOP_STATUS_TO_APPROVE

    @property
    def is_published(self):
        return self.status == SHOP_STATUS_PUBLISHED

    @property
    def need_rework(self):
        return self.status == SHOP_STATUS_NEED_REWORK

    def get_absolute_url(self):
        return reverse('discount:shop-detail', kwargs={'pk': self.pk})

    def confirmed(self, user):
        return self.shopstousers_set.get(user=user).confirmed

    def managers_count(self):
        return self.shopstousers_set.filter(confirmed=True).count()

    def get_active_products(self, date=None, excluded_product=None):
        if date is None:
            date = get_today()
        ps = Product.objects.filter(shop=self, start_date__lte=date, end_date__gte=date,
                                    status__in=[STATUS_PUBLISHED, STATUS_READY])
        #print(date)
        if excluded_product is not None:
            ps = ps.exclude(pk=excluded_product.pk)

        return ps

    @property
    def emails(self):
        emails = []
        for stu in self.shopstousers_set.all():
            user = stu.user
            emails.append(user.email)
        emails = ', '.join(emails)
        return emails

    @property
    def total_products_count(self):
        return self.products.all().count()

    @property
    def projects_count(self):
        return self.products.filter(status=STATUS_PROJECT).count()


    def check_status(self):
        new_status = self.status
        if self.pk:
            status = self.saved_version.status
        else:
            status = STATUS_NEW

        if status == SHOP_STATUS_PUBLISHED and not new_status == SHOP_STATUS_PUBLISHED:
            raise ValidationError('Магазин уже опубликован')
        elif status in [SHOP_STATUS_TO_APPROVE, SHOP_STATUS_PUBLISHED, SHOP_STATUS_NEED_REWORK]:
            if new_status == SHOP_STATUS_PROJECT:
                raise ValidationError('Данные магазина были изменены и сохранение невозможно.')


    def clean(self):
        super().clean()

        if self.pk and self.status == SHOP_STATUS_PUBLISHED and self.brands.all().count() == 0:
            raise ValidationError('Для перевода магазина в статус Действующий необходимо добавить хотя бы один бренд')


    def save(self, *args, check_status=True, do_clean=True, **kwargs):
        self.site = self.site.strip()
        with transaction.atomic():
            if do_clean:
                self.full_clean()
            if check_status:
                self.check_status()
            super().save(*args, **kwargs)
            user_profiles = UserProfile.objects.filter(user__shop=self)
            for up in user_profiles:
                up.save()



class ShopPhone(TatamoModelMixin):
    shop = models.ForeignKey(Shop, related_name='phones')
    phone = models.CharField(verbose_name='Телефон', max_length=20)

    def __str__(self):
        return self.phone

class ProductCondition(TatamoModelMixin):
    product = models.ForeignKey('Product', related_name='conditions')
    condition = models.TextField(verbose_name='Условие')

    def __str__(self):
        return self.condition


class ProductChangerCondition(TatamoModelMixin):
    product_changer = models.ForeignKey('ProductChanger', related_name='conditions')
    condition = models.TextField(verbose_name='Условие')
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.condition


class ProductQueryset(models.QuerySet):
    def filter(self, *args, **kwargs):
        queryset = super().filter(*args, **kwargs)
        return queryset

    def get_available_products(self):
        queryset = self.filter(status__in=ACTIVE_STATUSES, ad=False).distinct()
        return queryset

    def get_ad_products_category(self):
        queryset = self.filter(ad=True, status=STATUS_PROJECT).distinct()
        return queryset

    def get_ad_products_popular(self):
        queryset = self.filter(~Q(productbanner__banner=None), ad=True, status=STATUS_PROJECT).distinct()
        return queryset

    def get_shop_products(self, user=None):
        if user.is_shop_manager:
            queryset = self.filter(shop=user.get_shop).distinct()
        else:
            queryset = self.none()

            # Если пользователь не имеет полномочий на редактирование продуктов
        return queryset

    def filter_has_code(self, user):
        queryset = self.filter(cart_products__status=PTC_STATUS_SUBSCRIBED, cart_products__user=user)
        return queryset

    def filter_finished_has_code(self, user):
        queryset = self.filter(
            cart_products__status__in=(PTC_STATUS_CANCELLED, PTC_STATUS_BOUGHT, PTC_STATUS_FINISHED_BY_SHOP),
            cart_products__user=user)
        return queryset


class ProductManager(BaseManager.from_queryset(ProductQueryset)):
    use_for_related_fields = True

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class ProductVersionMixin:
    def get_actual_field_value(self, field_name):
        try:
            actual_version_object = ModelHistory.get_version_by_date(self, timezone.now()).object
            value = getattr(actual_version_object, field_name, None)
        except:
            value = None
        return value
        # actual_version = model_to_dict(ModelHistory.get_version_by_date(self, timezone.now()).object)

    def get_subscribed_value(self, field_name, user):
        try:
            version = self.get_subscribed_version(user)
            value = getattr(version.object, field_name)
        except:
            value = None
        return value

    def get_last_sent_value(self, field_name, user):
        try:
            version = self.get_last_sent_version(user)
            value = getattr(version.object, field_name)
        except:
            value = None
        return value

    def get_m2m_version_values(self, field_name, user, subscribed_only=False):
        try:
            if subscribed_only:
                version = self.get_subscribed_version(user)
            else:
                version = self.get_last_sent_version(user)


            param_key = FILTER_PARAMS_BY_FIELD[field_name]
            version_values = FilterValue.objects.filter(pk__in=version.m2m_data['filter_values'], filter_type=param_key)
            #else:
            #    version_values = None
        except:
            version_values = None
        return version_values

    # def get_m2m_values_since_subscribe(self, field_name, uses):
    #    version =  self.get_subscribed_version(user)
    #    values = getattr(self, field_name)

    def get_last_sent_version(self, user):
        try:
            pm = ProductMail.objects.filter(user=user, product=self).latest('created')
            version = list(serializers.deserialize('json', pm.history.serialized))[0]
        except:
            version = None
        return version

    def get_subscribed_version(self, user):
        try:
            pm = ProductMail.objects.filter(user=user, product=self, subscribed=True).earliest('created')
            version = list(serializers.deserialize('json', pm.history.serialized))[0]
        except:
            version = None
        return version

    def get_changed_fields(self, user, subscribed_only=False, fields=None):
        # if end_date is None:
        #    end_date = timezone.now()
        if fields is None:
            fields = self._meta.get_all_field_names()
        changed_fields = {}
        try:
            if subscribed_only:
                # pm = ProductMail.objects.filter(product=self, user=user, subscribed=subscribed).latest('created')
                # start_version = list(serializers.deserialize('json', pm.history.serialized))[0]
                start_version = self.get_subscribed_version(user)
            else:
                start_version = self.get_last_sent_version(user)
        except:
            start_version = None
        try:
            actual_version = ModelHistory.get_version_by_date(self, timezone.now())
        except:
            raise Exception('Нет актуальной версии истории для данной акции')
        for field in fields:
            if field in actual_version.m2m_data:  # Если это related field
                start_value = sorted(start_version.m2m_data.get(field, None))
                actual_value = sorted(actual_version.m2m_data.get(field, None))
            else:
                start_value = getattr(start_version.object, field, None)
                actual_value = getattr(actual_version.object, field, None)
            if not start_value == actual_value:
                changed_fields[field] = (start_value, actual_value)
        return changed_fields

    def get_history_value(self, field_name, user):
        value = getattr(self, field_name)
        # version = self.get_subscribed_version(user)
        # version = product.get_last_sent_version(user)
        # if version is None:
        #    return {'value': value}
        version_value = self.get_subscribed_value(field_name, user)
        if field_name == 'status':
            value = get_title_by_num(PRODUCT_STATUSES, value)
            version_value = get_title_by_num(PRODUCT_STATUSES, version_value)
        if value == version_value or version_value is None:
            return {'value': value}
        else:
            return {'value': value, 'version_value': version_value}

    def get_history_m2m_values(self, field_name, user):
        # version = self.get_subscribed_version(user)
        # version = product.get_last_sent_version(user)
        version_values = self.get_m2m_version_values(field_name, user=user,
                                                     subscribed_only=True)  # Получаем данные на момент подписки
        values = getattr(self, field_name)
        if version_values is None:
            res = [[val, 'unchanged'] for val in list(values.all())]
            return res
        values_list = []
        for val in values.all():
            values_list.append(val)

        for val in version_values.all():
            if not val in values_list:
                values_list.append(val)
        result_list = []
        for val in values_list:
            if val in version_values.all() and val in values.all():
                result_list.append([val, 'unchanged'])
            elif val in version_values.all() and not val in values.all():
                result_list.append([val, 'removed'])
            elif val not in version_values.all() and val in values.all():
                result_list.append([val, 'added'])
        return result_list


class MoneyExeption(Exception):
    pass


"""
def get_sum_for_action_type(shop, action_type):
    if action_type == ACTION_TYPE_BASE:
        return settings.MONEY_PER_DAY
    elif action_type == ACTION_TYPE_POPULAR:
        return settings.MONEY_PER_DAY_ON_MAIN
    elif action_type == ACTION_TYPE_CATEGORY:
        return settings.MONEY_PER_DAY_CATEGORY
"""



class ProductChanger(TatamoModelMixin, AbstractHashMixin):
    title = models.CharField(max_length=500, blank=True, verbose_name='Название', default='')
    user = models.ForeignKey(User, null=True, blank=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    product = models.ForeignKey('Product')
    brand = models.ForeignKey('Brand', verbose_name='Бренд', db_index=True)
    body = models.TextField(null=False, blank=False, verbose_name='Описание')
    product_shop_code = models.CharField(max_length=30, blank=True, verbose_name='Артикул', default='')
    compound = models.TextField(max_length=1000, blank=True, verbose_name='Состав', default='')
    shop_comment = models.TextField(blank=True, verbose_name='Комментарий магазина', default='')
    tatamo_comment = models.TextField(blank=True, verbose_name='Комментарий Tatamo', default='')
    product_type = models.ForeignKey(ProductType, limit_choices_to={'has_childs': False}, related_name='changers',
                                     verbose_name='Тип товара', db_index=True)

    link = models.CharField(max_length=4000, blank=True, verbose_name='Ссылка на страницу товара на сайте магазина')
    status = models.IntegerField(choices=CHANGER_STATUSES, default=STATUS_PROJECT)

    normal_price = models.IntegerField(verbose_name='Цена до акции', db_index=True)
    stock_price = models.IntegerField(verbose_name='Цена по акции', db_index=True)

    @property
    def status_text(self):
        if self.status == STATUS_PROJECT:
            status_text = 'Проект'
        elif self.status == STATUS_TO_APPROVE:
            status_text = 'На согласовании'
        elif self.status == STATUS_NEED_REWORK:
            status_text = 'На уточнении'
        elif self.status == STATUS_APPROVED:
            status_text = 'Согласована'
        else:  # На всякий
            status_text = "Проект"
        return status_text


    def update_related_field(self, related_field_name, key_field_name, cls):
        product = self.product
        changer = self
        product_values = list(getattr(product, related_field_name).all().values_list(key_field_name, flat=True))
        changer_values = list(getattr(changer, related_field_name).all().values_list(key_field_name, flat=True))

        all_values = list(set(product_values + changer_values))

        to_add = []
        to_remove = []
        for value in all_values:
            if value in changer_values and not value in product_values:
                to_add.append(value)
            elif value not in changer_values and value in product_values:
                to_remove.append(value)

        flt = {'{0}__in'.format(key_field_name): to_remove}
        getattr(product, related_field_name).filter(**flt).delete()
        for value in to_add:
            elem = cls()
            elem.product = product
            setattr(elem, key_field_name, value)
            elem.save()


    def approve(self):
        #self.status = STATUS_APPROVED
        product = self.product
        product.title = self.title
        product.product_type = self.product_type
        product.brand = self.brand
        product.body = self.body
        product.link = self.link
        product.product_shop_code = self.product_shop_code
        product.compound = self.compound
        product.product_type = self.product_type
        product.normal_price = self.normal_price
        product.stock_price = self.stock_price
        product.save()

        self.update_related_field('images', 'image', ProductImage)
        self.update_related_field('conditions', 'condition', ProductCondition)

        """
        product_images = list(product.images.all().values_list('image', flat=True))
        changer_images = list(self.images.all().values_list('image', flat=True))

        all_images = list(set(product_images + changer_images))

        to_add = []
        to_remove = []
        for image in all_images:
            if image in changer_images and not image in product_images:
                to_add.append(image)
            elif image not in changer_images and image in product_images:
                to_remove.append(image)

        product.images.filter(image__in=to_remove).delete()
        for image in to_add:
            product_image = ProductImage()
            product_image.product = product
            product_image.image = image
            product_image.save()
        #self.save()
    """
    def save(self, *args, **kwargs):
        saved_version = self.saved_version
        with transaction.atomic():
            if self.status == STATUS_APPROVED and not saved_version.status == STATUS_APPROVED:
                self.approve()
            super().save(*args, **kwargs)




import string
# from django.forms.models import model_to_dict
class Product(TatamoModelMixin, ProductVersionMixin, AbstractHashMixin, AbstractStripTitleMixin):
    class Meta:
        index_together = [
            ["status", "ad"],
        ]

    title = models.CharField(max_length=500, blank=True, verbose_name='Название', default='')
    user = models.ForeignKey(User, null=True, blank=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    shop = models.ForeignKey(Shop, related_name='products', verbose_name='Магазин', db_index=True)
    normal_price = models.IntegerField(verbose_name='Цена до акции', db_index=True)
    stock_price = models.IntegerField(verbose_name='Цена по акции', db_index=True)
    product_type = models.ForeignKey(ProductType, limit_choices_to={'has_childs': False}, related_name='products',
                                     verbose_name='Тип товара', db_index=True)
    status = models.IntegerField(choices=PRODUCT_STATUSES, default=STATUS_PROJECT, verbose_name='Статус', db_index=True,
                                 blank=True)
    start_date = models.DateField(verbose_name='Дата начала акции', db_index=True)
    end_date = models.DateField(verbose_name='Дата окончания акции', db_index=True)
    brand = models.ForeignKey('Brand', related_name='products', verbose_name='Бренд', db_index=True)

    filter_values = models.ManyToManyField('FilterValue', db_index=True, blank=True, related_name='products')

    #sizes = models.ManyToManyField('Size', related_name='products', verbose_name='Размеры', db_index=True, blank=True)
    #colors = models.ManyToManyField('Color', related_name='products', verbose_name='Цвета', db_index=True, blank=True)
    code = models.CharField(max_length=200, blank=True, verbose_name='Код акции', default='', unique=True)
    body = models.TextField(blank=True, verbose_name='Описание')
    # short_description = models.TextField(null=True, blank=True, verbose_name='Краткое описание')
    product_shop_code = models.CharField(max_length=30, blank=True, verbose_name='Артикул', default='')
    compound = models.TextField(max_length=1000, blank=True, verbose_name='Состав', default='')
    cart_users = models.ManyToManyField(User, through='ProductToCart', related_name='products', blank=True)
    shop_comment = models.TextField(blank=True, verbose_name='Комментарий магазина', default='')
    tatamo_comment = models.TextField(blank=True, verbose_name='Комментарий Tatamo', default='')
    publish_time = models.DateTimeField(null=True, blank=True)
    link = models.CharField(max_length=4000, blank=True, verbose_name='Ссылка на страницу товара на сайте магазина')

    simple_code = models.CharField(max_length=100, verbose_name='Код акции', blank=True)
    use_simple_code = models.BooleanField(default=False, blank=True, verbose_name='Сгенерировать промокод вручную')
    use_code_postfix = models.BooleanField(default=True, blank=True, verbose_name='Использовать постфикс для промокода')
    no_code_required = models.BooleanField(default=False, blank=True, verbose_name='Для получения скидки не нужен промокод')

    percent = models.PositiveIntegerField(verbose_name='Скидка')
    price_category = models.IntegerField(choices=PRICE_CATEGORIES)
    discount_category = models.IntegerField(choices=DISCOUNT_CATEGORIES)

    ad = models.BooleanField(default=False, verbose_name='Рекламная акция', db_index=True)
    start_after_approve = models.BooleanField(default=True, verbose_name='Стартовать/запланировать акцию автоматически после согласования')

    objects = ProductManager()


    def __str__(self):
        if self.title:
            return "{0} - {1}".format(self.product_type.title, self.title)
        else:
            return self.product_type.title

    @property
    def title_with_pk(self):
        return '{0} - {1}'.format(str(self), self.pk)

    @property
    def get_link(self):
        return helper.get_link(self.link)


    @property
    def product_conditions(self):
        general_conditions = settings.GENERAL_CONDITIONS
        conditions = self.conditions.all().values_list('condition', flat=True)
        if not self.no_code_required:
            additional_conditions = [
                'Скидка предоставляется только на конкретную модель, указанную в купоне.',
                'Цены в магазине указаны без учета скидки, с помощью промокода у Вас есть возможность получить скидку.',
                'Скидка по купону не суммируется с другими спрецпредложениями магазина.',
                'Промокод не гарантирует наличия товара в магазине, предложение ограничено.',
            ]
            general_conditions += additional_conditions
        return list(conditions) + general_conditions

    @property
    def fieds_to_hash(self):
        return ['title', 'user','created', 'shop','normal_price', 'stock_price','product_type', 'status','start_date',
                'end_date','brand', 'filter_values','code', 'body','product_shop_code',
                'compound','shop_comment', 'tatamo_comment']


    @property
    def available_related_products(self):
        return self.related_products.filter(related_product__status__in=ACTIVE_STATUSES)


    @property
    def banner(self):
        try:
            banners = list(self.productbanner_set.filter(status=BANNER_STATUS_APPROVED))
            random.shuffle(banners)
            banner = banners[0].banner
        except:
            banner = None
        return banner


    @property
    def has_active_status(self):
        if self.status in [STATUS_PUBLISHED, STATUS_READY, STATUS_TO_APPROVE,
                           STATUS_NEED_REWORK, STATUS_APPROVED, STATUS_SUSPENDED]:
            return True
        else:
            return False

    @classmethod
    def generate_unique_code(cls):
        Products = Product.objects.select_for_update().all()
        while True:
            first_part = helper.generate_code(size=5, chars=string.ascii_uppercase)
            second_part = helper.generate_code(size=3, chars=string.digits)
            code = first_part + second_part
            count = cls.objects.filter(code=code).count()
            if count == 0:
                return code

    @property
    def saved_status(self):
        if not self.pk:
            return STATUS_NEW
        else:
            return self.saved_version.status


    def get_normal_carts_in_period(self, start_date=None, end_date=None):
        ptcs = self.cart_products.filter(status__in=[PTC_STATUS_CART])
        if start_date:
            ptcs = ptcs.filter(created__gte=start_date)
        if end_date:
            ptcs = ptcs.filter(created__lte=end_date + timezone.timedelta(days=1))
        return ptcs


    def get_instant_carts_in_period(self, start_date=None, end_date=None):
        ptcs = self.cart_products.filter(status__in=[PTC_STATUS_INSTANT])
        if start_date:
            ptcs = ptcs.filter(created__gte=start_date)
        if end_date:
            ptcs = ptcs.filter(created__lte=end_date + timezone.timedelta(days=1))
        return ptcs

    def get_subscriptions_in_period(self, start_date, end_date):
        ptcs = self.cart_products.filter(status=PTC_STATUS_SUBSCRIBED)
        if start_date:
            ptcs = ptcs.filter(created__gte=start_date)
        if end_date:
            ptcs = ptcs.filter(created__lt=end_date + timezone.timedelta(days=1))
        return ptcs

    def find_ptc_by_request(self, request):
        user = request.user
        if user.is_authenticated():
            ptc = self.find_ptc_by_user(user)
        else:
            try:
                ptc = ProductToCart.objects.get(product=self, session_key=request.session.session_key)
            except:
                ptc = None
        return ptc

    def get_ptc(self, user=None, request=None):
        if not user and request:
            user = request.user
        if user.is_authenticated():
            ptc, created = ProductToCart.objects.get_or_create(user=user, product=self)
        else:
            ptc, created = ProductToCart.objects.get_or_create(session_key=request.session.session_key, product=self)
        return ptc

    def find_ptc_by_user(self, user=None, request=None):
        if user is None or not user.is_authenticated():
            try:
                ptc = ProductToCart.objects.get(session_key=request.session.session_key, product=self)
            except:
                ptc = None
        else:
            try:
                ptc = ProductToCart.objects.get(user=user, product=self)
            except:
                ptc = None
        return ptc

    def get_code(self, user):
        if user.is_authenticated():# and self.is_available():
            try:
                ptc = ProductToCart.objects.get(product=self, user=user,
                                                status=PTC_STATUS_SUBSCRIBED)
                code = ptc.promocode
                return code
            except:
                code = ''
        else:
            code = ''
        return code

    def get_available_statuses(self):
        status = get_choice_by_num(PRODUCT_STATUSES, self.status)
        statuses = [status]
        if self.status == STATUS_PROJECT or self.status == STATUS_NEED_REWORK:
            statuses.append(get_choice_by_num(PRODUCT_STATUSES, STATUS_TO_APPROVE))
            statuses.append(get_choice_by_num(PRODUCT_STATUSES, STATUS_SUSPENDED))
        elif self.status == STATUS_SUSPENDED:
            statuses.append(get_choice_by_num(PRODUCT_STATUSES, STATUS_TO_APPROVE))
        elif self.status == STATUS_PUBLISHED:
            statuses.append(get_choice_by_num(PRODUCT_STATUSES, STATUS_SUSPENDED))
        return statuses



    def get_absolute_url(self):
        return reverse('discount:product-detail', kwargs={'pk': self.pk})

    def get_pdf_url(self):
        return reverse('discount:product-pdf-view', kwargs={'pk': self.pk})

    def get_coupon_url(self):
        return reverse('discount:coupon-view', kwargs={'pk': self.pk})

    def get_banners_url(self):
        return reverse('discount:product-banners', kwargs={'pk': self.pk})

    def get_coupon_qr_url(self, user):
        ptc = self.find_ptc_by_user(user)
        pin = ptc.code
        uid = user.pk
        return reverse('discount:qr-coupon-view', kwargs={'pk': self.pk, 'uid': uid, 'pin': pin})

    def get_class(self):
        if self.is_available():
            return 'enabled'
        else:
            return 'disabled'

    @cached_property
    def get_main_image(self):
        try:
            image = self.images.get(weight=1)
        except:
            image = self.images.first()

        if image is None:
            return None
        else:
            return image.image

    def is_available(self):
        today = get_today()
        if self.status != STATUS_PUBLISHED or self.end_date < today:
            return False
        else:
            return True

    @property
    def days_left(self):
        today = get_today()
        if today < self.start_date:
            start_date = self.start_date
        else:
            start_date = today
        delta = (self.end_date - start_date).days
        return delta

    @property
    def get_days_left(self):
        if self.status == STATUS_PUBLISHED:
            delta = self.days_left
            if delta > 1:
                return str(delta) + ' дней'
            elif delta == 0:
                return 'Акция заканчивается сегодня'
            elif delta == 1:
                return 'Акция заканчивается завтра'
            else:
                return 'Акция завершена'
        elif self.status in (STATUS_PROJECT, STATUS_TO_APPROVE, STATUS_NEED_REWORK, STATUS_APPROVED):
            return 'Акция в процессе согласования'
        elif self.status == STATUS_SUSPENDED:
            return 'Акция временно приостановлена'
        elif self.status == STATUS_READY:
            return 'Акция начнется {0}'.format(self.start_date)
        else:
            return 'Акция завершена'

    def get_manage_url(self):
        return reverse('discount:product-update', kwargs={'pk': self.pk})

    def is_active_on_day(self, period=None):
        if period is None:
            period = get_today()
        if period >= self.start_date and period <= self.end_date:
            return True
        else:
            return False


    def get_discount_category(self):
        if self.percent <= 30:
            discount_category = DISCOUNT_CATEGORY_1
        elif self.percent > 30 and self.percent <= 50:
            discount_category = DISCOUNT_CATEGORY_2
        elif self.percent > 50 and self.percent <= 80:
            discount_category = DISCOUNT_CATEGORY_3
        elif self.percent > 80:
            discount_category = DISCOUNT_CATEGORY_4
        return discount_category

    def get_price_category(self):
        if self.stock_price <= 3000:
            price_category = PRICE_CATEGORY_1
        elif self.stock_price > 3000 and self.stock_price <= 5000:
            price_category = PRICE_CATEGORY_2
        elif self.stock_price > 5000 and self.stock_price <= 10000:
            price_category = PRICE_CATEGORY_3
        elif self.stock_price > 10000 and self.stock_price <= 15000:
            price_category = PRICE_CATEGORY_4
        elif self.stock_price > 15000 and self.stock_price <= 30000:
            price_category = PRICE_CATEGORY_5
        elif self.stock_price > 30000 and self.stock_price <= 50000:
            price_category = PRICE_CATEGORY_6
        elif self.stock_price > 50000:
            price_category = PRICE_CATEGORY_7
        return price_category

    def get_percent(self):
        try:
            percent = round(((self.normal_price - self.stock_price) / self.normal_price) * 100)
            if percent == 100:
                percent = 99
            elif percent < 0:
                percent = 0
        except:
            percent = 0
        return percent


    def check_status(self):
        status = self.saved_status
        new_status = self.status

        available_statuses = AVAILABLE_STATUSES[status].append(status)
        if not new_status in AVAILABLE_STATUSES[status]:
            raise ValidationError('Недопустимое изменение статуса акции.')


    def clean(self, *args, **kwargs):
        super().clean()
        errors = ErrorDict()
        check_start_date = False
        today = get_today()
        if self.pk:
            old_instance = self.saved_version
        else:
            old_instance = self

        if self.status in [STATUS_FINISHED, STATUS_CANCELLED, STATUS_PROJECT, STATUS_NEED_REWORK]:
            return #Не будем ничего проверять

        if self.status == STATUS_READY:
            if self.end_date and self.end_date <= today:
                errors.append('end_date', 'Дата окончания акции не должна быть раньше, чем сегодня')
            if self.start_date and self.start_date <= today:
               errors.append('start_date', 'Дата начала запланированной акции должна быть в будующем.')

        if self.status == STATUS_PUBLISHED:
            if self.end_date and self.end_date < today:
                errors.append('end_date', 'Дата окончания акции не должна быть раньше, чем сегодня')
            if self.start_date and self.start_date > today:
               errors.append('start_date', 'Дата начала действующей акции не должна быть в будующем.')

            if not old_instance.status in [STATUS_PUBLISHED, STATUS_SUSPENDED]: #Публикация
                if self.start_date < today:
                    errors.append('start_date', 'Акция не может начаться раньше, чем сегодня')

        if self.status == STATUS_FINISHED:
            if not old_instance.status == STATUS_FINISHED: #Завершение
                self.end_date = today
                if self.start_date > today:
                    self.start_date = today

        if not self.shop.status == SHOP_STATUS_PUBLISHED:
            errors.append(NON_FIELD_ERRORS, 'Пожалуйста, дождитесь согласования информации о магазине')


        if self.start_date < settings.START_DATE:
            errors.append('start_date', 'Акция не может начаться раньше, чем {0}'.format(settings.START_DATE))

        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors.append(NON_FIELD_ERRORS, 'Акция не может закончиться раньше, чем начнется')

        if old_instance.status in [STATUS_PUBLISHED, STATUS_FINISHED, STATUS_SUSPENDED] and \
                not self.start_date == old_instance.start_date:
            errors.append('start_date', 'Дата начала действующей акции не может быть сдвинута')


        if self.stock_price and self.normal_price and self.stock_price >= self.normal_price:
            errors.append(NON_FIELD_ERRORS, 'Цена по акции должна быть ниже обычной цены')

        if errors.errors:
            raise ValidationError(errors.errors)

    def clear_cache(self):
        # Кеш
        fragments = ('product_list_inner_grid_1', 'product_list_inner_list_1',
                     'product_list_inner_list_2', 'product_info_main_1',
                     'main_page_product_1','product_detail_1', 'product_detail_2')
        for fragment in fragments:
            key = make_template_fragment_key(fragment, (self.pk,))
            cache.delete(key)

    def save(self, *args, do_clean=True, check_status=True, **kwargs):
        self.link = self.link.strip()
        saved_version = self.saved_version
        with transaction.atomic():
            today = get_today()
            if not self.code:
                self.code = self.generate_unique_code()

            self.percent = self.get_percent()
            self.price_category = self.get_price_category()
            self.discount_category = self.get_discount_category()
            if self.status == STATUS_FINISHED and self.end_date > today:
                self.end_date = today

            if self.status == STATUS_PUBLISHED and not self.publish_time:
                self.publish_time = timezone.now()

            if do_clean:
                self.full_clean()

            if check_status:
                self.check_status()

            old_instance = self.saved_version

            super().save(*args, **kwargs)
            self.apply_storage_params(saved_version) #TODO лучше сделать перед записью, сейчас много лишних сохранений


            # Запись истории
            pts = self.product_type.get_all_parents_with_self()
            for pt in pts:
                th = TatamoHistory()
                th.product_type = pt
                th.product = self
                th.save()

            self.clear_cache()

            #Приостановим действующие подписки
            if self.status == STATUS_SUSPENDED:
                ptcs = self.cart_products.filter(status=PTC_STATUS_SUBSCRIBED)
                for ptc in ptcs:
                    ptc.status = PTC_STATUS_SUSPENDED
                    ptc.save()

            #Завершим действующие подписки
            elif self.status == STATUS_FINISHED:
                ptcs = self.cart_products.filter(status=PTC_STATUS_SUBSCRIBED)
                for ptc in ptcs:
                    ptc.status = PTC_STATUS_FINISHED_BY_SHOP
                    ptc.save()

            #После возобновления акции вернуть все приостановленные подписки
            elif self.status == STATUS_PUBLISHED:
                ptcs = self.cart_products.filter(status=PTC_STATUS_SUSPENDED)
                for ptc in ptcs:
                    ptc.status = PTC_STATUS_SUBSCRIBED
                    ptc.save()

            #Удалим этот продукт из связанных
            if not self.status in AVAILABLE_FOR_RELATED_PRODUCTS_STATUSES:
                RelatedProduct.objects.filter(related_product=self).delete()


            fields, created = ProductFields.objects.get_or_create(product=self)

            #for action in self.actions.all():
            #    action.save()


    def apply_storage_params(self, saved_version):
        fields = ('brand', 'shop', 'product_type')

        for field in fields:
            # old_model = ModelHistory.get_version_by_date(self, timezone.now()).object
            elem = getattr(self, field)
            old_elem = getattr(saved_version, field, elem)
            # elem = getattr(self, field)
            elems = [elem]
            if not elem.pk == old_elem.pk:
                elems.append(old_elem)

            if field == 'product_type':
                final_elems = elems[:]
                for elem in elems:
                    pts = elem.get_all_elements_to_save() + [elem]
                    final_elems += pts
                elems = final_elems

            for elem in set(elems):
                elem.save_product_storage_elem()

    @property
    def status_text(self):
        if self.status == STATUS_PROJECT:
            status_text = 'Проект'
        elif self.status == STATUS_TO_APPROVE:
            status_text = 'На согласовании'
        elif self.status == STATUS_NEED_REWORK:
            status_text = 'На уточнении'
        elif self.status == STATUS_APPROVED:
            status_text = 'Согласована'
        elif self.status == STATUS_PUBLISHED:
            status_text = 'Действует'
        elif self.status == STATUS_SUSPENDED:
            status_text = 'Приостановлена'
        elif self.status == STATUS_READY:
            status_text = 'Старт запланирован {0}'.format(self.start_date.strftime("%d.%m.%Y"))
        elif self.status == STATUS_FINISHED:
            status_text = 'Завершена'
        elif self.status == STATUS_CANCELLED:
            status_text = 'Отменена'
        else:
            status_text = "Проект"
        return status_text

    @classmethod
    def get_all_filter_params(cls):
        params = []
        for field_name, label in FILTER_PARAMS_FIELD_NAMES.values():
            if hasattr(cls, field_name):
                params.append((field_name, label))
        return params

    #TODO криво всех пользователей 1 запросом
    def stat_all_in_period(self, start_date=None, end_date=None):
        stats = self.productstat_set.exclude(session_key='')
        shop = self.shop
        users = shop.users.all()
        stats = stats.exclude(user__in=users)

        users = User.objects.filter(profile__role=USER_ROLE_TATAMO_MANAGER)
        stats = stats.exclude(user__in=users)

        users = User.objects.filter(is_staff=True)
        stats = stats.exclude(user__in=users)

        if start_date:
            stats = stats.filter(created__gte=start_date)
        if end_date:
            stats = stats.filter(created__lt=end_date + timezone.timedelta(days=1))
        return stats

    def stat_users_in_period(self, start_date=None, end_date=None):
        stats = self.stat_all_in_period(start_date, end_date).filter(~Q(user=None))
        return stats

    def stat_guests_in_period(self, start_date=None, end_date=None):
        stats = self.stat_all_in_period(start_date, end_date).filter(user=None)
        return stats

    def stat_unique_all_in_period(self, start_date=None, end_date=None):
        stats = self.stat_all_in_period(start_date, end_date).distinct('session_key')
        return stats

    def stat_unique_users_in_period(self, start_date=None, end_date=None):
        stats = self.stat_users_in_period(start_date, end_date).distinct('user')
        return stats

    def stat_unique_guests_in_period(self, start_date=None, end_date=None):
        stats = self.stat_guests_in_period(start_date, end_date).distinct('session_key')
        return stats





for param_key, field_names in FILTER_PARAMS_FIELD_NAMES.items():
    field_name, field_label = field_names
    def get_filter_values(self, param_key=param_key):
        queryset = self.filter_values.filter(filter_type=param_key)
        return queryset

    setattr(Product, field_name, property(get_filter_values))




def start_or_plan_approved_action(sender, instance, created, **kwargs):
    today = get_today()
    if instance.status == STATUS_APPROVED and instance.start_after_approve:
        try:
            if instance.start_date > today:
                instance.status = STATUS_READY
                instance.save()
            elif instance.start_date <= today:
                instance.start_date = today
                instance.status = STATUS_PUBLISHED
                instance.save()
        except:
            pass



post_save.connect(start_or_plan_approved_action, sender=Product)



#def product_filter_values_dublicates_disabled(sender, instance, action, **kwargs):
#    if action in ['pre_add']:
#        pass

#m2m_changed.connect(product_filter_values_dublicates_disabled, sender=Product.filter_values.through)


def get_free_actions_for_main_count(day, action_type, product=None, category=None):
    if action_type == ACTION_TYPE_CATEGORY and not (product or category):
        raise ValidationError('Не указана категория и акция')


    product_actions = ProductAction.objects.filter(start_date__lte=day, end_date__gte=day, action_type=action_type, start=True)
    #products = Product.objects.filter(actions__in=product_actions)
    if product and product.pk:
        product_actions.exclude(product=product)
    if action_type == ACTION_TYPE_POPULAR:
        max = settings.MAX_POPULAR_COUNT

    elif action_type == ACTION_TYPE_CATEGORY:
        max = settings.MAX_CATEGORY_COUNT
        if not category:
            try:
                category = product.product_type.get_top_parent()
            except:
                return False  # Если форма еще вообще не заполнена, нечего и проверять

        if not category.level == 1:
            category = category.get_top_parent()
        product_pks = category.available_products_pks
        product_actions = product_actions.filter(product__in=product_pks)

    return max - product_actions.count()
        #products.filter(product_type__in=product_types)
        #if products.count() >= 6:
        #    return True


def get_actions_count_for_interval(action_type, start_date, end_date, product=None, category=None):
    today = get_today()
    days = OrderedDict()
    start_date = max(start_date, today)
    for day in range(0, (end_date - start_date).days + 1):
        date = start_date + timezone.timedelta(days=day)
        days_count = get_free_actions_for_main_count(date, action_type, product=product, category=category)
        days[date] = days_count
    return days


"""
class ProductActionAccount(TatamoModelMixin):
    product_action = models.OneToOneField('ProductAction', related_name='account')
    points_blocked = models.IntegerField(default=0, blank=True)

    def save(self, *args, **kwargs):
        self.points_blocked = self.product_action.points_required
        super().save(*args, **kwargs)
"""

class RelatedProduct(TatamoModelMixin):
    product = models.ForeignKey('Product', verbose_name='Акция', related_name='related_products')
    related_product = models.ForeignKey('Product', verbose_name='Связанная акция', related_name='products')



class ShopsToUsers(TatamoModelMixin):
    shop = models.ForeignKey(Shop, db_index=True)
    user = models.ForeignKey(User, db_index=True, verbose_name='Имя пользователя')
    confirmed = models.BooleanField(default=False, verbose_name='Подтверждено')

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        """
        user = getattr(self, 'user', None)
        shop = self.shop
        try:
            user_shop = user.get_shop()
        except:
            user_shop = None
        if user_shop is not None and not user_shop == shop:
            raise ValidationError('Пользователь уже является менеджером другого магазина')
        """


class ShopsToBrands(TatamoModelMixin):
    brand = models.ForeignKey('Brand', db_index=True)
    shop = models.ForeignKey('Shop', db_index=True)


class ProductImage(TatamoModelMixin):  # AbstractImageDeleteMixin Убрал для history
    class Meta:
        ordering = ['weight']
        index_together = [
            ["product", "weight"],
        ]

    image = MyImageField(verbose_name='Изображение', upload_to='discount_product', db_index=True,
                         thumb_settings=settings.PRODUCT_THUMB_SETTINGS)
    product = models.ForeignKey(Product, related_name='images', db_index=True)
    # title = models.CharField(max_length=500, blank=True, verbose_name='Название изображения', default='')
    # body = models.TextField(blank=True, verbose_name='Описание', default='')
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    # main = models.BooleanField(default=False, verbose_name='Основное изображение', db_index=True)
    weight = models.IntegerField(default=1, verbose_name='Порядок показа', db_index=True)

    # def __str__(self):
    #    return self.title





class ProductChangerImage(TatamoModelMixin):  # AbstractImageDeleteMixin Убрал для history
    image = MyImageField(verbose_name='Изображение', upload_to='discount_product', db_index=True,
                         thumb_settings=settings.PRODUCT_THUMB_SETTINGS)
    #product = models.ForeignKey(Product, db_index=True, related_name='product_changer_images')
    product_changer = models.ForeignKey(ProductChanger, related_name='images', db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)


class Brand(AbstractModel, AbstractModelBodyMixin, AbstractProductStorage):  # AbstractImageDeleteMixin removed
    class Meta:
        ordering = ['title']

    image = MyImageField(verbose_name='Изображение', upload_to='discount_brand', null=True, blank=True)

    def clean(self):
        brands = type(self).objects.filter(title__iexact=self.title)
        if self.pk:
            brands = brands.exclude(pk=self.pk)
        if brands.exists():
            raise ValidationError('Бренд с таким названием уже существует')

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)
#class Size(AbstractModel, AbstractModelBodyMixin):  # AbstractImageDeleteMixin removed
#    pass





class FilterValueToProductType(TatamoModelMixin):
    product_type = models.ForeignKey('ProductType', db_index=True)
    filter_type = models.IntegerField(choices=FILTER_TYPES, db_index=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product_type.save()



"""
SIZE_PARAMS = ('sizes_man','sizes_woman','sizes_shoes','sizes_childs')



class FilterValueQueryset(models.QuerySet):
    def filter(self, *args, **kwargs):
        queryset = super().filter(*args, **kwargs)
        return queryset

    def order_by(self, *field_names):
        for size_param in SIZE_PARAMS:
            if size_param in field_names:
                field_names[size_param] = int(field_names[size_param])



class FiltervalueManager(BaseManager.from_queryset(FilterValueQueryset)):
    use_for_related_fields = True

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset
"""



class FilterValue(TatamoModelMixin, AbstractStripTitleMixin):
    class Meta:
        ordering = ['title_int', 'title']
        index_together = [
            ["title_int", "title"]
        ]
    title = models.CharField(max_length=500, blank=False, verbose_name='Название', default='')
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    filter_type = models.IntegerField(choices=FILTER_TYPES, db_index=True)
    title_int = models.FloatField(blank=True, default=0, db_index=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        try:
            pos = self.title.find('-')
            if pos > 0:
                title = self.title[:pos]
            else:
                title = self.title
            self.title_int = float(title)
            if pos > 0:
                self.title_int += 0.5
        except:
            self.title_int = 0

        super().save(*args, **kwargs)

#class FilterValueToProduct(TatamoModelMixin):
#    product = models.ForeignKey('Product', db_index=True)
#    filter_value = models.ForeignKey('FilterValue', db_index=True)





#class Color(AbstractModel, AbstractModelBodyMixin):  # AbstractImageDeleteMixin removed
#    image = MyImageField(verbose_name='Изображение', upload_to='discount_color', null=True, blank=True, db_index=True)


class Comment(AbstractModel):
    name = models.CharField(max_length=256, verbose_name='Имя')
    email = models.EmailField(max_length=256, verbose_name='E-MAIL')
    product = models.ForeignKey(Product, related_name='comments', db_index=True)
    body = models.TextField(blank=False, verbose_name='Комментарий', default='')

    def __str__(self):
        return self.body[0:50]


#BANNER_STATUS_PROJECT = 1
BANNER_STATUS_ON_APPROVE = 1
BANNER_STATUS_NEED_REWORK = 2
BANNER_STATUS_APPROVED = 3

BANNER_STATUSES = (
    #(BANNER_STATUS_PROJECT, 'Проект'),
    (BANNER_STATUS_ON_APPROVE, 'На согласовании'),
    (BANNER_STATUS_NEED_REWORK, 'На доработке'),
    (BANNER_STATUS_APPROVED, 'Согласован'),

)


class ProductBanner(TatamoModelMixin, AbstractHashMixin):
    created = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey('Product', db_index=True)
    status = models.IntegerField(choices=BANNER_STATUSES, default=BANNER_STATUS_ON_APPROVE, blank=True,
                                 verbose_name='Статус', db_index=True)
    tatamo_comment = models.TextField(blank=True, verbose_name='Комментарий Татамо')
    shop_comment = models.TextField(blank=True, verbose_name='Комментарий магазина')
    banner = MyImageField(verbose_name='Изображение', upload_to='discount_product_banner',
                          thumb_settings=settings.PRODUCT_BANNER_THUMB_SETTINGS)
    number = models.PositiveIntegerField(null=False, blank=True, default=1)



    def save(self, *args, **kwargs):
        try:
            max_number = type(self).objects.filter(product=self.product).aggregate(Max('number'))['number_max']
        except:
            max_number = 0
        self.number = max_number + 1
        super().save(*args, **kwargs)


    def __str__(self):
        text = 'Баннер {0}. Статус: {1}'.format(self.number, self.status_text)
        return text

    @property
    def status_text(self):
        if self.pk:
            if self.status == BANNER_STATUS_APPROVED:
                text = 'Согласован'
            elif self.status == BANNER_STATUS_ON_APPROVE:
                text = 'На согласовании'
            elif self.status == BANNER_STATUS_NEED_REWORK:
                text = 'На доработке'
            else:
                text = 'Проект'
        else:
            text = 'Проект'
        return text

    def form_status_cls(self):
        if self.pk:
            if self.status == BANNER_STATUS_APPROVED:
                status_cls = 'form-status-approved'
            elif self.status == BANNER_STATUS_ON_APPROVE:
                status_cls = 'form-status-on-approve'
            elif self.status == BANNER_STATUS_NEED_REWORK:
                status_cls = 'form-status-need-rework'
            else:
                status_cls = 'form-status-project'
        else:
            status_cls = 'form-status-project'
        return status_cls



# from django.db.models import Max
class ProductToCart(TatamoModelMixin):
    class Meta:
        index_together = [
            ["product", "user"], ["user", "status"],
        ]

    product = models.ForeignKey('Product', db_index=True, related_name='cart_products')
    # cart = models.ForeignKey('Cart', db_index=True, blank=True, null=True)
    code = models.PositiveIntegerField(null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, related_name='cart_products', db_index=True)
    status = models.IntegerField(choices=PTC_STATUSES, default=PTC_STATUS_CART, db_index=True)
    comment = models.TextField(blank=True, default='')
    session_key = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    subscription_time =  models.DateTimeField(null=True, blank=True)


    @staticmethod
    def get_subscribed_count_text(user):
        if user.is_authenticated():
            ptcs = ProductToCart.get_subscribed_queryset(user)
            count = Product.objects.get_available_products().filter(cart_products__in=ptcs).count()
            return 'Мои действующие подписки({0})'.format(count)
        else:
            return ""

    @staticmethod
    def get_finished_count_text(user):
        if user.is_authenticated():
            count = ProductToCart.get_finished_queryset(user).count()
            return 'Мои завершенные подписки({0})'.format(count)
        else:
            return ""

    @staticmethod
    def get_expired_cart_queryset(request):
        queryset = ProductToCart.get_cart_queryset(request).filter(
            Q(product__end_date__lt=timezone.now()) | ~Q(product__status=STATUS_PUBLISHED))
        return queryset

    def clean(self):
        if not self.user and not self.session_key:
            raise ValidationError('Пользователь или ключ сессии не заполнен')

        #Подписаться можно только на действующую акцию
        if not self.pk and not self.product.status == STATUS_PUBLISHED:
            raise ValidationError('Подписаться можно только на действующую акцию')


    #def generate_code(self):
    #    product = self.product
    #    try:
    #        max_code = type(self).objects.select_for_update().filter(~Q(pk=self.pk), product=product).aggregate(Max('code'))['code__max']
    #        if max_code is None:
    #            max_code = '00000'
    #    except:
    #        max_code = '00000'
    #    code = int(max_code)
    #    code += 1
    #    code = str(code)
    #    code = '00000' + code
    #    code = code[-5:]
    #    self.code = code

    def save(self, *args, **kwargs):
        if self.user and not self.user.is_simple_user:
            return
        if self.status == PTC_STATUS_SUBSCRIBED and not self.subscription_time:
            self.subscription_time = timezone.now()

        super().save()  #Чтобы конкуренту было что блокировать
        if self.status == PTC_STATUS_SUBSCRIBED and not self.code:
            with transaction.atomic():
                product = self.product
                if not self.code:
                    all_ptcs = type(self).objects.select_for_update().filter(product=product)
                    try:
                        max_code = all_ptcs.aggregate(Max('code'))['code__max']
                        if max_code is None:
                            max_code = 0
                    except:
                        max_code = 0
                    code = max_code + 1
                    self.code = code
                    self.save()


            if self.user:
                ptcs = all_ptcs.filter(user=self.user, product=self.product).filter(~Q(pk=self.pk))
            else:
                ptcs = all_ptcs.filter(session_key=self.session_key, product=self.product).filter(
                        ~Q(pk=self.pk))
            ptcs.delete()




    """
    @classmethod
    def get_ptc(cls, request, product, save=True):
        user = request.user
        session_key = request.session.session_key
        if user.is_authenticated():
            ptc, created = cls.objects.get_or_create(user=user, product=product)
        else:
            ptc, created = cls.objects.get_or_create(session_key=session_key, product=product)
        if created and save:
                ptc.save()

        return ptc
    """

    @classmethod
    def get_instant_ptc(cls, request):
        user = request.user
        try:
            if user.is_authenticated():
                return cls.objects.get(user=user, status=PTC_STATUS_INSTANT)
            else:
                return cls.objects.get(session_key=request.session.session_key, status=PTC_STATUS_INSTANT)
        except:
            return None

    @classmethod
    def get_full_cart_queryset(cls, request):
        user = request.user
        if user.is_authenticated():
            return cls.objects.filter(user=user)
        else:
            return cls.objects.filter(session_key=request.session.session_key)

    @classmethod
    def get_cart_queryset(cls, request):
        user = request.user
        if user.is_authenticated():
            return cls.objects.filter(user=user,
                                      status__in=[PTC_STATUS_CART, PTC_STATUS_INSTANT])
        else:
            return cls.objects.filter(session_key=request.session.session_key,
                                      status__in=[PTC_STATUS_CART, PTC_STATUS_INSTANT])

    @classmethod
    def get_guest_cart_queryset(cls, request):
        user = request.user
        if user.is_authenticated():
            return cls.objects.filter(user=user, status__in=[PTC_STATUS_INSTANT])
        else:
            return cls.objects.filter(session_key=request.session.session_key,
                                      status__in=[PTC_STATUS_INSTANT])

    @classmethod
    def get_subscribed_queryset(cls, user):
        return cls.objects.filter(user=user, status=PTC_STATUS_SUBSCRIBED)

    @classmethod
    def get_finished_queryset(cls, user):
        return cls.objects.filter(user=user,
                                  status__in=[PTC_STATUS_CANCELLED, PTC_STATUS_BOUGHT, PTC_STATUS_FINISHED_BY_SHOP])

    @classmethod
    def request_has_cart(cls, request):
        user = getattr(request, 'user', None)
        if user is None:
            return False
        else:
            if user.is_authenticated():
                result = cls.objects.filter(user=user).exists()
            else:
                result = cls.objects.filter(session_key=request.session.session_key).exists()
        return result


    @property
    def promocode(self):
        if self.status == PTC_STATUS_SUBSCRIBED:
            if self.product.use_simple_code:
                product_code = self.product.simple_code
            else:
                product_code = self.product.code
            if self.product.use_code_postfix:
                postfix = '00000' + str(self.code)
                postfix = postfix[:6]
                code = "{0}-{1}".format(product_code, postfix)
            else:
                code = product_code
            return code
        else:
            return None

CHECK_FIELDS = ('filter_values', 'status', 'end_date')


class ProductMail(TatamoModelMixin):
    user = models.ForeignKey(User, blank=True, null=True)
    email = models.EmailField(max_length=256)
    created = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, related_name='mails')
    history = models.ForeignKey('ModelHistory')
    subscribed = models.BooleanField(default=False)

    text_template_name = 'discount/cart/cart_text_email_view.txt'
    html_template_name = 'discount/cart/cart_html_email_view.html'

    def __str__(self):
        return '{0}/{1}/{2}/{3}'.format(self.user, self.product, self.created, self.subscribed)

    @classmethod
    def send_products_messages(cls, products=None, user=None, subscribed=False, moment=None):
        if moment is None:
            moment = timezone.now()
        html = render_to_string(cls.html_template_name, {'products': products, 'user': user, 'subscribed': subscribed,
                                                         'site_url': settings.SITE_URL})
        text = render_to_string(cls.text_template_name, {'products': products, 'subscribed': subscribed})
        if subscribed:
            subject = 'Вы подписались на акции на Tatamo.ru'
        else:
            subject = 'Условия акций, на которые Вы подписаны, изменились'
        from_email = settings.DEFAULT_FROM_EMAIL
        to = user.email
        try:
            msg = EmailMultiAlternatives(subject, text, from_email, [to])
            msg.attach_alternative(html, "text/html")
            msg.send()
            for product in products:
                pm = cls(user=user, product=product, email=to)
                pm.created = moment
                pm.subscribed = subscribed
                pm.history = ModelHistory.get_history_by_date(product, moment)
                pm.save()
        except:
            pass

    @classmethod
    def get_send_products_dict(cls, moment):
        to_send = {}
        cart_products = ProductToCart.objects.filter(status__in=[PTC_STATUS_SUBSCRIBED, PTC_STATUS_FINISHED_BY_SHOP, PTC_STATUS_SUSPENDED])
        users = User.objects.filter(cart_products__in=cart_products,
                                    profile__get_product_changed_messages=True).distinct()
        for user in users:
            try:
                last_pm = ProductMail.objects.filter(user=user).latest('created')
            except:
                last_pm = None
            if not settings.DEBUG and last_pm is not None and (
                        moment - last_pm.created).seconds < settings.REPEATED_LETTER_INTERVAL:  # If user has got mail recently, dont repeat
                continue
            user_cart_products = cart_products.filter(user=user)
            for cp in user_cart_products:
                product = cp.product
                send_flag = False
                changed_fields = []
                try:
                    if cp.status in [PTC_STATUS_SUSPENDED, PTC_STATUS_FINISHED_BY_SHOP]: #Для приостановленной акции нам не интересно внутреннее изменение полей,
                        #мы получим его совокупно, когда акция вернется в действующую
                        changed_fields = product.get_changed_fields(user, fields=['status'], subscribed_only=False)

                    else:
                        changed_fields = product.get_changed_fields(user, fields=CHECK_FIELDS, subscribed_only=False)
                except:
                    send_flag = True
                if not send_flag:
                    if len(changed_fields) > 0:
                        send_flag = True
                if send_flag:
                    if user not in to_send:
                        to_send[user] = {}
                    to_send[user][product] = changed_fields
        return to_send

    @classmethod
    def send_message_for_all_changed_products(cls):
        moment = timezone.now()  # Фиксируем момент до отправки. Если изменения произойдут после него, мы их учтем в
        # следующей рассылке
        to_send = cls.get_send_products_dict(moment)
        users_count = len(to_send)
        products_count = 0
        for user in to_send:
            # if user.get_product_changed_messages: #reassurance
            products = list(to_send[user].keys())
            products_count += len(products)
            cls.send_products_messages(products, user=user, moment=moment)
        return users_count, products_count


# TODO move from helper, replace in code
# def generate_unique_code(size=16, model, fieldname)


USER_ROLE_DEFAULT = 1
USER_ROLE_SHOP_MANAGER = 2
USER_ROLE_TATAMO_MANAGER = 3

USER_ROLES = (
    (USER_ROLE_DEFAULT, 'Пользователь'),
    (USER_ROLE_SHOP_MANAGER, 'Менеджер магазина'),
    (USER_ROLE_TATAMO_MANAGER, 'Менеджер Татамо'),

)


class UserProfile(TatamoModelMixin):
    # required by the auth model
    user = models.OneToOneField(User, related_name='profile')  # reverse returns single object, not queryset
    phone = models.CharField(max_length=100, blank=True, verbose_name='Телефон', default='')
    get_product_changed_messages = models.BooleanField(default=True,
                                                       verbose_name='Получать уведомления об изменении условий акций')
    active_shop = models.ForeignKey(Shop, null=True, blank=True, verbose_name='Активный магазин')
    role = models.PositiveIntegerField(choices=USER_ROLES, default=USER_ROLE_DEFAULT, blank=True)

    #@staticmethod
    #def cache_key(user):
    #    key = 'user_profile_{0}'.format(user.pk)
    #    return key

    def __str__(self):
        return 'Профиль пользователя {0}, pk={1}'.format(self.user.username, self.user.pk)

    @classmethod
    def get_profile(cls, user):

        user_profile, created = cls.objects.get_or_create(user=user)
        if created:
            user_profile.save()
        return user_profile

    def save(self, *args, **kwargs):
        #if self.pk is None:
        #    try:
        #        up = UserProfile.objects.get(pk=self.user)
        #    except:
        #        up = None
        if not self.role == USER_ROLE_TATAMO_MANAGER:
            if (not self.active_shop or not self.active_shop in self.user.get_confirmed_shops()) \
                    and self.user.get_confirmed_shops().exists():
                self.active_shop = self.user.get_confirmed_shops().latest('created')

            if not self.user.get_confirmed_shops().exists():
                self.active_shop = None
                self.role = USER_ROLE_DEFAULT
            elif self.role == USER_ROLE_DEFAULT:
                self.role = USER_ROLE_SHOP_MANAGER
        super().save(*args, **kwargs)
        if not self.role == USER_ROLE_DEFAULT:
            ProductToCart.objects.filter(user=self.user).delete()

    def delete(self, *args, **kwargs):
        if self.code:
            self.status = PTC_STATUS_DELETED
            self.save()
        else:
            super().delete(*args, **kwargs)

def create_user_profile(sender, instance, created, **kwargs):
    profile, created = UserProfile.objects.get_or_create(user=instance)
    if created:
        profile.save()


post_save.connect(create_user_profile, sender=User)


class Breadcrumb:
    def __init__(self, title, type, href=''):
        self.href = href
        self.title = title
        self.type = type

# ModelHistory ************************************



class ModelHistory(TatamoModelMixin):
    cls = models.CharField(max_length=100, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    serialized = models.TextField()
    key = models.PositiveIntegerField(db_index=True)
    is_new = models.BooleanField(default=False)

    @classmethod
    def get_history_by_date(cls, instance, created):
        try:
            hist = cls.objects.filter(key=instance.pk, cls=type(instance).__name__, created__lte=created).latest(
                'created')
        except:
            hist = None
        return hist

    @classmethod
    def get_version_by_date(cls, instance, created):
        hist = cls.get_history_by_date(instance, created)
        if hist:
            try:
                version = list(serializers.deserialize('json', hist.serialized))[0]
            except:
                version = None

        else:
            version = None
        return version


def model_history_writer(sender, instance, created, **kwargs):
    # if not hasattr(loc, 'model_history_hists'):
    #    loc.model_history_hists = {}
    serialized = serializers.serialize('json', [instance])
    # if not instance in loc.model_history_hists:
    save_model_history(instance, serialized, created)


def model_history_m2m_writer(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove']:
        serialized = serializers.serialize('json', [instance])
        save_model_history(instance, serialized)


def save_model_history(instance, serialized, created=False):
    try:
        recent_history = ModelHistory.objects.filter(cls=type(instance).__name__, key=instance.pk).latest('created')
    except:
        recent_history = None

    if not recent_history or not serialized == recent_history.serialized:
        model_history = ModelHistory()
        model_history.cls = type(instance).__name__
        model_history.key = instance.pk
        model_history.is_new = False
        model_history.serialized = serialized
        model_history.save()


post_save.connect(model_history_writer, sender=Product)
post_save.connect(model_history_writer, sender=ProductImage)
#post_save.connect(model_history_writer, sender=Product.filter_values.through)
m2m_changed.connect(model_history_m2m_writer, sender=Product.filter_values.through)

post_save.connect(model_history_writer, sender=ProductType)





# ************************** ModelHistory>>>>
def get_unconfirmed_shops(self):
    try:
        shops = Shop.objects.filter(shopstousers__in=self.shopstousers_set.filter(confirmed=False))
    except:
        shops = None
    return shops


def get_all_shops(self):
    try:
        shops = Shop.objects.filter(shopstousers__in=self.shopstousers_set.all())
    except:
        shops = None
    return shops


def get_confirmed_shops(self):
    try:
        shops = Shop.objects.filter(shopstousers__in=self.shopstousers_set.filter(confirmed=True))
    except:
        shops = None
    return shops


def get_shop(self):
    # count = self.shopstousers_set.filter(user=self, confirmed=True).count()
    profile = self.profile
    active_shop = getattr(profile, 'active_shop', None)
    if active_shop is None:
        try:
            active_shop = self.get_confirmed_shops().latest('created')
        except:
            active_shop = None

    return active_shop


def has_perm_for_shop(self, shop):
    if not self.is_authenticated():
        return False

    user_shops = self.get_confirmed_shops()
    if shop in user_shops:
        return True

    return False


def has_perm_for_product(self, product):
    if self.is_staff or self.is_tatamo_manager:
        return True
    if not self.is_authenticated():
        return False
    elif not product or not product.pk:
        return True
    else:
        return self.get_shop == product.shop
    #user_shops = self.get_confirmed_shops()
    #if user_shops is None:
    #    return False

    #if product is None or product.shop in user_shops:
    #    return True



def get_user_profile(self):
    user_profile = UserProfile.get_profile(self)
    return user_profile




def active_subscription(self):
    return self.get_shop.active_subscription


def is_tatamo_manager(self):
    if self.profile.role == USER_ROLE_TATAMO_MANAGER or self.is_staff:
        return True
    else:
        return False

def planned_subscription(self):
    return self.get_shop.planned_subscription


def is_simple_user(self):
    if self.profile.role == USER_ROLE_DEFAULT:
        return True
    else:
        return False

# TODO Сделал заплатку. Правильно хранить эту функцию в backends, но тогда нужно добавлять полномочия
User.is_shop_manager = property(lambda self: self.get_shop is not None)
User.is_tatamo_manager = property(is_tatamo_manager)
User.has_perm_for_product = has_perm_for_product
User.has_perm_for_shop = has_perm_for_shop
User.get_admin = lambda: User.objects.get(pk=1)
# User.get_active_shop = get_active_shop
User.get_shop = property(get_shop)
User.get_all_shops = get_all_shops
User.get_confirmed_shops = get_confirmed_shops
User.active_subscription = property(active_subscription)
User.planned_subscription = property(planned_subscription)
User.is_simple_user = property(is_simple_user)

User.get_unconfirmed_shops = get_unconfirmed_shops
User.profile = property(get_user_profile)

AnonymousUser.is_shop_manager = False
AnonymousUser.has_perm_for_product = lambda self, product: False
AnonymousUser.has_perm_for_shop = lambda self, shop: False
# has_perm_for_shop.get_shop = lambda self: False
AnonymousUser.get_shop = None
AnonymousUser.profile = property(lambda self: None)
AnonymousUser.get_all_shops = lambda self: None
AnonymousUser.get_unconfirmed_shops = lambda self: None
AnonymousUser.get_confirmed_shops = lambda self: None
AnonymousUser.active_subscription = lambda self: None
AnonymousUser.is_staff = False
AnonymousUser.is_tatamo_manager = False
AnonymousUser.is_simple_user = True


# AnonymousUser.get_active_shop = lambda self: None


class MenuItem:
    def __init__(self, cls=None, id=None, href=None, title=None, url_name=None):
        self.cls = cls
        self.href = href
        self.title = title
        self.url_name = url_name

    @classmethod
    def get_partial_menu_list(cls, category, *args, **kwargs):
        cache_key = 'partial-menu-list-' + str(category.pk)
        partial_menu_list = cache.get(cache_key)
        if partial_menu_list is None:
            partial_menu_list = cls.get_partial_menu_list_uncached(category, *args, **kwargs)
            cache.set(cache_key, partial_menu_list, timeout=60 * 60)
        return partial_menu_list

    def set_class(self, level, active=False):
        if active:
            self.cls = 'menu-item-level-{0} {1}'.format(str(level), 'active')
        else:
            self.cls = 'menu-item-level-{0}'.format(str(level))

    @classmethod
    def get_partial_menu_list_uncached(cls, category, pts=None, end_level=3):
        menu_list = []
        if pts is None:
            pts = ProductType.objects.filter(level=1)
            end_level = category.level + 1
        for pt in pts:
            item = cls(title=pt.title, href=pt.get_absolute_url())
            if not settings.SHOW_EMPTY_CATEGORIES and pt.available_products_count == 0:
                continue
            if pt == category:
                item.set_class(level=pt.level, active=True)
            else:
                item.set_class(level=pt.level, active=False)

            if pt.level == 3 and not pt.parent == category:
                continue
            menu_list.append(item)
            if ((category.get_top_parent() == pt.get_top_parent()) and (pt.level < end_level)):
                menu_list += cls.get_partial_menu_list_uncached(category, pts=pt.childs.all(), end_level=end_level)

        return menu_list

    @classmethod
    def get_full_menu(cls):
        cache_key = 'full-menu-list'
        full_menu_list = cache.get(cache_key)
        if full_menu_list is None:
            full_menu_list = cls.get_full_menu_list_uncached()
            cache.set(cache_key, full_menu_list, timeout=60 * 10)
        return full_menu_list

    @classmethod
    def get_full_menu_list_uncached(cls):
        full_menu = OrderedDict()
        pts = ProductType.objects.filter(level=1)
        for pt in pts:
            item = cls(title=pt.title, href=pt.get_absolute_url())
            if not settings.SHOW_EMPTY_CATEGORIES and pt.available_products_count == 0:
                continue
            item.set_class(level=pt.level, active=False)
            item.id = 'menu-item-li-{0}'.format(pt.id)
            full_menu[item] = OrderedDict()
            childs = pt.childs.all()
            for child in childs:
                if not settings.SHOW_EMPTY_CATEGORIES and child.available_products_count == 0:
                    continue
                child_item = cls(title=child.title, href=child.get_absolute_url())
                child_item.set_class(level=child.level, active=False)
                child_item.id = 'menu-item-li-{0}'.format(child.id)
                full_menu[item][child_item] = []
                childs2 = child.childs.all()
                for child2 in childs2:
                    if not settings.SHOW_EMPTY_CATEGORIES and child2.available_products_count == 0:
                        continue
                    child2_item = cls(title=child2.title, href=child2.get_absolute_url())
                    child2_item.set_class(level=child2.level, active=False)
                    child2_item.id = 'menu-item-li-{0}'.format(child2.id)
                    full_menu[item][child_item].append(child2_item)

        return full_menu

    def is_active(self, url_name):
        if url_name == self.url_name:
            return True
        else:
            return False

# reversion, not used for models now
#import reversion

#reversion.register(Product, follow=["images"])
#reversion.register(Comment)
#reversion.register(Shop)
#reversion.register(ProductImage)


# reversion



# <<<<<<<<<<<<<Money


# Actions>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def filter_popular_products(queryset, limit=10):
    queryset = queryset.annotate(cart_count=Count('cart_products')).order_by('-cart_count')[:limit]
    """
    queryset = queryset.extra(
    select={
        'cart_count': 'SELECT COUNT(*) FROM discount_producttocart WHERE discount_producttocart.product_id = discount_product.id'
    },
).extra(order_by = ['-cart_count'])[:limit]
    """
    return queryset




class AdminMonitorMail(models.Model):
    keys = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_products_queryset():
        return Product.objects.filter(status=SHOP_STATUS_TO_APPROVE)

    @staticmethod
    def get_banners_queryset():
        return ProductBanner.objects.filter(status=BANNER_STATUS_ON_APPROVE)

    @staticmethod
    def get_shops_queryset():
        return Shop.objects.filter(Q(status=SHOP_STATUS_TO_APPROVE) |
                                           Q(~Q(add_brands=''), status=SHOP_STATUS_PUBLISHED))

    @staticmethod
    def get_changers_queryset():
        return ProductChanger.objects.filter(status=SHOP_STATUS_TO_APPROVE).all()

    @staticmethod
    def get_contact_forms_queryset():
        return ContactForm.objects.filter(status=STATUS_CREATED).all()

    @classmethod
    def get_querysets(cls):
        querysets = []
        querysets.append(cls.get_products_queryset().all())
        querysets.append(cls.get_banners_queryset().all())
        querysets.append(cls.get_shops_queryset().all())
        querysets.append(cls.get_changers_queryset().all())
        querysets.append(cls.get_contact_forms_queryset().all())
        return querysets

    @classmethod
    def get_keys(cls):
        keys = []
        qs = cls.get_querysets()
        for q in qs:
            for ob in q:
                if hasattr(ob, 'hashed'):
                    keys.append(ob.hashed)
                else:
                    key = type(ob).__name__ + str(ob.pk)
                    keys.append(key)
        return json.dumps(keys)

    @classmethod
    def create_mail(cls):
        keys = json.loads(cls.get_keys())
        try:
            prev_mail = cls.objects.all().latest('created')
        except:
            prev_mail = None
        if prev_mail:
            send = False
            prev_keys = json.loads(prev_mail.keys)
            if not len(prev_keys) == len(keys):
                send = True
            else:
                for key in keys:
                    if not key in prev_keys:
                        send = True
                        break
        else:
            send = True

        if send:
            mail = cls.objects.create(keys=json.dumps(keys))
        else:
            mail = None
        return mail

class ProductFields(TatamoModelMixin):
    product = models.OneToOneField(Product, related_name='product_fields')
    weight = models.PositiveIntegerField(default=0, db_index=True)


class ProductStat(TatamoModelMixin):
    created = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey('Product')
    user = models.ForeignKey(User, null=True, blank=True)
    session_key = models.TextField(blank=True)
    ip = models.CharField(max_length=15)

