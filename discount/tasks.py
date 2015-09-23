from __future__ import absolute_import
from . import models
from django.utils import timezone
import celery
from django.core.cache import cache
from django.conf import settings
from .helper import get_today
from django.core.mail import mail_admins
from django.db.models import Q
from django.db import transaction
from copy import copy
from celery.task import periodic_task
from contact_form.models import ContactForm, STATUS_CREATED
import datetime
from celery.schedules import crontab
#celery.decorators.periodic_task(run_every=datetime.timedelta(hours=1))

#@celery.decorators.periodic_task(run_every=crontab(minute=0, hour=list(range(24))))
def _suspend_expired_products():
    suspended = 0
    need_rework = 0
    today = get_today()
    products = models.Product.objects.filter(status__in=[models.STATUS_PUBLISHED,
                                                         models.STATUS_READY],
                                             end_date__lt=today)
    #count = products.count()

    for product in products:
        if product.status == models.STATUS_PUBLISHED:
            product.status = models.STATUS_SUSPENDED
            product.tatamo_comment = 'Автоматически сгенерированное сообщение: Дата окончания акции прошла'
            suspended += 1
        elif product.status == models.STATUS_READY:
            product.status = models.STATUS_NEED_REWORK
            product.tatamo_comment = 'Автоматически сгенерированное сообщение: Дата окончания акции прошла'
            need_rework += 1
        with transaction.atomic():
                product.save(do_clean=False, check_status=False)


    message = '_suspend_expired_products: need_rework %s suspended %s' % (need_rework, suspended)
    return message

#TODO доделать цену, может еще что-то. И сделать правильно, на запросах
def _suspend_empty_products():
    need_rework = 0
    products = models.Product.objects.filter(~Q(status=models.STATUS_NEED_REWORK))
    for product in products:
        if not product.images.exists():
            product.tatamo_comment = 'Автоматически сгенерированное сообщение: Для акции нет изображений'
            product.status = models.STATUS_NEED_REWORK
            with transaction.atomic():
                product.save()

        elif product.stock_price <= 0:
            product.tatamo_comment = 'Автоматически сгенерированное сообщение: Некорректная цена'
            product.status = models.STATUS_NEED_REWORK
            with transaction.atomic():
                product.save()

    message = '_suspend_empty_products: need_rework %s' % (need_rework,)
    return message

def _start_ready_products():
    today = get_today()
    products = models.Product.objects.filter(status=models.STATUS_READY, start_date__lte=timezone.now())
    count = products.count()


    for product in products:
        #shop_active_products = product.shop.get_active_products(date=today, excluded_product=product)
        product.status = models.STATUS_PUBLISHED
        if product.start_date < today:
            product.start_date = today
        with transaction.atomic():
            product.save()

    message = '_start_ready_products: started %s' % (count,)
    return message


def _send_message_for_all_changed_products():
    users_count, products_count = models.ProductMail.send_message_for_all_changed_products()

    message = '_send_message_for_all_changed_products: users_count %s products_count %s'  % (users_count, products_count)
    mail_admins('_send_message_for_all_changed_products procedure is completed', message)

#TODO send letters to unapproved mails


#TODO вернуть
def _main_procedure():
    m0 = _suspend_expired_products()
    m1 = _start_ready_products()
    message = '%s \n %s' % (m0, m1)
    mail_admins('_main_procedure procedure is completed on Tatamo productive', message)




#@celery.decorators.periodic_task(run_every=crontab(minute=1, hour=[0, 3]))

#@celery.decorators.periodic_task(run_every=datetime.timedelta(minutes=2))
@periodic_task(run_every=crontab(minute=1, hour='0, 3'))
def main_procedure():
    return _main_procedure()

#TODO включить в продуктиве, перепроверив
@celery.decorators.periodic_task(run_every=crontab(minute=0, hour=[4, 16]))
################@celery.decorators.periodic_task(run_every=datetime.timedelta(minutes=3))
def send_message_for_all_changed_products():
    _send_message_for_all_changed_products()





def _admin_monitor():
    mail = models.AdminMonitorMail.create_mail()
    message = None
    if mail:
        products_count = models.AdminMonitorMail.get_products_queryset().count()
        banners_count = models.AdminMonitorMail.get_banners_queryset().count()
        shops_count = models.AdminMonitorMail.get_shops_queryset().count()
        changers_count = models.AdminMonitorMail.get_changers_queryset().count()
        contact_forms_count = models.AdminMonitorMail.get_contact_forms_queryset().count()

        sum = products_count + banners_count + shops_count + changers_count + contact_forms_count
        if sum > 0:
            message = 'Акций: {0}\n Баннеров: {1}\n Магазинов: {2}\n Заявок: {3}\n Контактных форм: {4}'.format(
                products_count, banners_count, shops_count, changers_count, contact_forms_count
            )
            mail_admins('Есть {0} необработанных событий'.format(sum), message)
    return message

import random
@periodic_task(run_every=datetime.timedelta(minutes=10))
def admin_monitor():
    return _admin_monitor()


def _recalc_product_weights():
    ps = models.Product.objects.filter(ad=False)
    for p in ps:
        fields, created = models.ProductFields.objects.get_or_create(product=p)

        if p.status in [models.STATUS_CANCELLED, models.STATUS_FINISHED]:
            if not fields.weight == 1000:
                fields.weight = 1000
                fields.save()
        else:
            fields, created = models.ProductFields.objects.get_or_create(product=p)
            fields.weight = random.random() * 100
            fields.save()


@periodic_task(run_every=datetime.timedelta(minutes=70))
def recalc_product_weights():
    _recalc_product_weights()



#TODO переделатьнормально, чтобы это был метод модели
def _save_product_storages():
    pts = models.ProductType.objects.all()
    for pt in pts:
        pt.save_product_storage_elem()
        pt.save()

    shops = models.Shop.objects.all()
    for s in shops:
        s.save_product_storage_elem()


    brands = models.Brand.objects.all()
    for b in brands:
        b.save_product_storage_elem()


@periodic_task(run_every=crontab(minute=1, hour='1, 4, 6, 16, 21'))
def save_product_storages():
    _save_product_storages()



