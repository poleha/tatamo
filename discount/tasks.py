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
                product.prepare_product_account()


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
                product.prepare_product_account()

        elif product.stock_price <= 0:
            product.tatamo_comment = 'Автоматически сгенерированное сообщение: Некорректная цена'
            product.status = models.STATUS_NEED_REWORK
            with transaction.atomic():
                product.save()
                product.prepare_product_account()

    message = '_suspend_empty_products: need_rework %s' % (need_rework,)
    return message

def _start_ready_products():
    today = get_today()
    products = models.Product.objects.filter(status=models.STATUS_READY, start_date__lte=timezone.now())
    count = products.count()


    for product in products:
        shop_active_products = product.shop.get_active_products(date=today, excluded_product=product)
        active_subscription = product.shop.subscription_by_date(today)
        if active_subscription.subscription_type.max_products > shop_active_products.count():
            product.status = models.STATUS_PUBLISHED
            if product.start_date < today:
                product.start_date = today
            with transaction.atomic():
                product.save()
                product.pay()
                product.prepare_product_account()
        else:
            product.tatamo_comment = 'Автоматически сгенерированное сообщение: Превышено допустимое количество акций.'
            product.status = models.STATUS_SUSPENDED
            with transaction.atomic():
                product.save()
                product.prepare_product_account()

    message = '_start_ready_products: started %s' % (count,)
    return message


def _send_message_for_all_changed_products():
    users_count, products_count = models.ProductMail.send_message_for_all_changed_products()

    message = '_send_message_for_all_changed_products: users_count %s products_count %s'  % (users_count, products_count)
    mail_admins('_send_message_for_all_changed_products procedure is completed', message)

#TODO send letters to unapproved mails

def _start_stop_subscriptions():
    today = get_today()
    stopped = 0
    started_continue = 0
    started_planned = 0
    total = 0

    subscriptions_to_stop = models.Subscription.objects.filter(end_date__lt=today, status=models.SUBSCRIPTION_STATUS_ACTIVE)
    for s in subscriptions_to_stop:
        total += 1
        s.status = models.SUBSCRIPTION_STATUS_INACTIVE
        s.save()
        stopped += 1
        if s.auto_pay:
            new_s = copy(s)
            new_s.pk = None
            new_s.start_date = today
            new_s.set_end_date()
            points_free = new_s.shop.points_free
            if points_free >= new_s.subscription_type.price:
                with transaction.atomic():
                    new_s.status = models.SUBSCRIPTION_STATUS_ACTIVE
                    new_s.save()
                    models.Payment.subscription_type_pay(new_s.shop, new_s.user, new_s.subscription_type.price, new_s)
                    models.Subscription.objects.filter(shop=s.shop, status=models.SUBSCRIPTION_STATUS_PLANNED).delete()
                    started_continue += 1

        else:
            try:
                planned = models.Subscription.objects.get(shop=s.shop, status=models.SUBSCRIPTION_STATUS_PLANNED)
            except:
                planned = None

            if planned is not None:
                if planned.shop.points_free >= planned.subscription_type.price:
                    with transaction.atomic():
                        planned.status = models.SUBSCRIPTION_STATUS_ACTIVE
                        models.Payment.subscription_type_pay(planned.shop, planned.user, planned.subscription_type.price, planned)
                        planned.save()
                        started_planned += 1

    message = '_start_stop_actions total:{0}, planned:{1}, continue: {2}, stopped: {3}'.\
        format(total, started_planned, started_continue, stopped)
    return message


#@celery.decorators.periodic_task(run_every=crontab(minute=10, hour=[0]))
def _payday():
    today = get_today()
    products = models.Product.objects.filter(
                                            ~Q(actions__payment__period=today),
                                             actions__start_date__lte=today,
                                             actions__end_date__gte=today,
                                             status=models.STATUS_PUBLISHED,
                                             end_date__gte=today,
                                             start_date__lte=today
                                            )

    #actions = models.ProductAction.objects.filter(~Q(transaction__period=today), product__status=models.STATUS_PUBLISHED,
    #                                         end_date__gte=today)

    count = 0
    for product in products:
        actions = product.actions.filter(~Q(payment__period=today), start_date__lte=today, end_date__gte=today)
        if actions:
            with transaction.atomic():
                product.pay()
                product.prepare_product_account()
                count += 1
    message = '_payday count %s' % (count,)
    return message


#TODO вернуть
def _main_procedure():
    m0 = _suspend_expired_products()
    m1 = ''#_suspend_empty_products()
    m2 = ''#_start_stop_subscriptions()
    m3 = _start_ready_products()
    m4 = ''#_payday()
    message = '%s \n %s \n %s \n %s \n %s' % (m0, m1, m2, m3, m4)
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


"""
@celery.decorators.periodic_task(run_every=crontab(day_of_month=1, hour=[0], minute=45))
def add_days_monthly():
    _add_days_monthly()
"""

#@celery.task
#def test_task():
#    print('finished')


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



