from django.conf import settings
from django.test import TestCase
from django_webtest import WebTest
from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory
from django.forms import ValidationError
from django.test.utils import setup_test_environment
setup_test_environment()
from django.test import Client
client = Client()
from django.core.urlresolvers import reverse
# Create your tests here.
from discount import views
from webtest import Upload
from PIL import Image
from io import StringIO, BytesIO
import os
import datetime
#from discount.urls import urlpatterns
from polls.models import  Poll, Answer
from django.contrib.auth.models import User, AnonymousUser
from contact_form.models import ContactForm, STATUS_CREATED, STATUS_CHECKED
from discount import tasks
from django.core.files.storage import FileSystemStorage
from discount import helper

from django.utils import timezone
from discount import models
from .models import Product, ProductAction, ProductToCart, ProductType
from discount.templatetags import discount_tags

TEST_IMAGE_PATH = os.path.join(settings.BASE_DIR, 'discount', 'test_images', 'test.jpg')

class BaseTest(WebTest):
    def setUp(self):
        today = models.get_today()
        self.start_date = settings.START_DATE
        settings.START_DATE = today
        self.discount_cache_enabled = settings.DISCOUNT_CACHE_ENABLED
        settings.DISCOUNT_CACHE_ENABLED = False


        self.today = today
        self.user_password = 'top_secret'
        self.user = User.objects.create_user(
                username='alex', email='alex@alex.ru', password=self.user_password)


        self.brand = models.Brand.objects.create(title='Бренд1')
        self.shop = models.Shop.objects.create(title='Магазин1', status=models.SHOP_STATUS_PROJECT, image=models.Product.generate_unique_code())
        models.ShopsToBrands.objects.create(shop=self.shop, brand=self.brand)
        self.shop.status = models.SHOP_STATUS_PUBLISHED
        self.shop.save()



        self.pt0 = ProductType.objects.create(title='level0')
        self.pt1 = ProductType.objects.create(title='level1', parent=self.pt0, alias='test_alias_1', share_filter_params=True)
        self.pt2 = ProductType.objects.create(title='level2', parent=self.pt1, alias='test_alias_2')
        self.pt3 = ProductType.objects.create(title='level3', parent=self.pt2, alias='test_alias_3')



        self.product = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                     start_date=today,
                                     end_date=today + timezone.timedelta(days=5),
                                     code=models.Product.generate_unique_code(), product_type=self.pt3, shop=self.shop, brand=self.brand,
                                     start_after_approve=False,
                                     )

        self.product1 = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                     start_date=today,
                                     end_date=today + timezone.timedelta(days=5),
                                     code=models.Product.generate_unique_code(), product_type=self.pt3, shop=self.shop, brand=self.brand,
                                     start_after_approve=False,
                                     )


        self.product2 = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                     start_date=today,
                                     end_date=today + timezone.timedelta(days=5),
                                     code=models.Product.generate_unique_code(), product_type=self.pt3, shop=self.shop, brand=self.brand,
                                     start_after_approve=False,
                                     )

        self.product3 = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                     start_date=today,
                                     end_date=today + timezone.timedelta(days=5),
                                     code=models.Product.generate_unique_code(), product_type=self.pt3, shop=self.shop, brand=self.brand,
                                     start_after_approve=False,
                                     )

        self.product4 = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                     start_date=today,
                                     end_date=today + timezone.timedelta(days=5),
                                     code=models.Product.generate_unique_code(), product_type=self.pt3, shop=self.shop, brand=self.brand,
                                     status=models.STATUS_PROJECT,
                                     start_after_approve=False,
                                     )

        self.product5 = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                     start_date=today,
                                     end_date=today + timezone.timedelta(days=5),
                                     code=models.Product.generate_unique_code(), product_type=self.pt3, shop=self.shop, brand=self.brand,
                                     status=models.STATUS_PROJECT,
                                     start_after_approve=False,
                                     )


        models.ShopsToUsers.objects.create(shop=self.shop, user=self.user, confirmed=True)

        user_profile = self.user.profile
        user_profile.active_shop = self.shop
        user_profile.save()

        self.subscription_type = models.SubscriptionType.objects.create(title='Subscription type', period_points=1,
                                                                        max_products=1,
                                                                        price=100,
                                                                        period_type=models.SUBSCRIPTION_PERIOD_TYPE_MONTH,
                                                                        )

        #models.ShopsToBrands.objects.create(shop=self.shop, brand=self.brand)

        self.simple_user_password = 'top_secret1'
        self.simple_user = User.objects.create_user(
                username='alex1', email='ale1x@alex.ru', password=self.simple_user_password)

        self.color_red = models.FilterValue.objects.create(title='Красный', filter_type=models.FILTER_TYPE_COLOR)
        self.color_green = models.FilterValue.objects.create(title='Зеленый', filter_type=models.FILTER_TYPE_COLOR)

        self.dress_size_42 = models.FilterValue.objects.create(title='42', filter_type=models.FILTER_TYPE_SIZE_WOMAN)
        self.dress_size_44 = models.FilterValue.objects.create(title='44', filter_type=models.FILTER_TYPE_SIZE_WOMAN)

        self.product1.filter_values.add(self.color_green)
        models.FilterValueToProductType.objects.create(product_type=self.pt1, filter_type=models.FILTER_TYPE_COLOR)
        models.FilterValueToProductType.objects.create(product_type=self.pt2, filter_type=models.FILTER_TYPE_COLOR)
        models.FilterValueToProductType.objects.create(product_type=self.pt3, filter_type=models.FILTER_TYPE_COLOR)


    def tearDown(self):
        settings.START_DATE = self.start_date
        settings.DISCOUNT_CACHE_ENABLED = self.discount_cache_enabled

class ProductTypeTests(BaseTest):
    def test_top_parent_attrs_applied_to_childs(self):
        pt0 = ProductType.objects.create(title='level0')
        pt1 = ProductType.objects.create(title='level1', parent=pt0)
        models.FilterValueToProductType.objects.create(product_type=pt1, filter_type=models.FILTER_TYPE_COLOR)
        pt1.share_filter_params = True
        pt1.save()

        pt2 = ProductType.objects.create(title='level2', parent=pt1)
        pt3 = ProductType.objects.create(title='level3', parent=pt2)


        pt0 = pt0.saved_version
        pt1 = pt1.saved_version
        pt2 = pt2.saved_version
        pt3 = pt3.saved_version

        self.assertEquals(pt3.level, 3)
        self.assertEquals(pt2.level, 2)
        self.assertEquals(pt1.level, 1)
        self.assertEquals(pt0.level, 0)

        self.assertEquals(pt3.has_childs, False)
        self.assertEquals(pt2.has_childs, True)
        self.assertEquals(pt1.has_childs, True)
        self.assertEquals(pt0.has_childs, True)

        self.assertEquals(pt0.filtervaluetoproducttype_set.all().count(), 0)
        self.assertEquals(pt1.filtervaluetoproducttype_set.all().count(), 1)
        self.assertEquals(pt2.filtervaluetoproducttype_set.all().count(), 1)
        self.assertEquals(pt3.filtervaluetoproducttype_set.all().count(), 1)

    def test_new_created_product_type_taked_right_parents_params(self):
        pt0 = ProductType.objects.create(title='level0')
        pt1 = ProductType.objects.create(title='level1', parent=pt0)
        models.FilterValueToProductType.objects.create(product_type=pt1, filter_type=models.FILTER_TYPE_COLOR)
        pt1.share_filter_params = True
        pt1.save()

        pt2 = ProductType.objects.create(title='level2', parent=pt1)
        pt3 = ProductType.objects.create(title='level3', parent=pt2)

        self.assertEqual(pt2.filtervaluetoproducttype_set.all().count(), 1)
        self.assertEqual(pt3.filtervaluetoproducttype_set.all().count(), 1)

        pt1.share_filter_params = False
        pt1.save()


    def test_title_int_works_fine_with_str_int_hyphen(self):
        fv = models.FilterValue.objects.create(title='1', filter_type=models.FILTER_TYPE_SIZE_MAN)
        self.assertEqual(fv.title_int, 1)

        fv = models.FilterValue.objects.create(title='114-234423', filter_type=models.FILTER_TYPE_SIZE_MAN)
        self.assertEqual(fv.title_int, 114.5)

        fv = models.FilterValue.objects.create(title='114-fdsfsd', filter_type=models.FILTER_TYPE_SIZE_MAN)
        self.assertEqual(fv.title_int, 114.5)

        fv = models.FilterValue.objects.create(title='fsddsfsd', filter_type=models.FILTER_TYPE_SIZE_MAN)
        self.assertEqual(fv.title_int, 0)

        fv = models.FilterValue.objects.create(title='fsdd-sfsd', filter_type=models.FILTER_TYPE_SIZE_MAN)
        self.assertEqual(fv.title_int, 0)


class ProductFirstTest(BaseTest):
    def test_get_actions_count_for_interval_popular(self):
        max_polular = settings.MAX_POPULAR_COUNT
        today = self.today
        tomorrow = self.today + timezone.timedelta(days=1)
        yesterday = self.today + timezone.timedelta(days=-1)
        after_tomorrow = self.today + timezone.timedelta(days=2)
        md = models.get_actions_count_for_interval(models.ACTION_TYPE_POPULAR, yesterday, after_tomorrow)
        self.assertNotIn(yesterday, md)
        self.assertEquals(md[today], max_polular)
        self.assertEquals(md[tomorrow], max_polular)
        self.assertEquals(md[after_tomorrow], max_polular)


        user = User.objects.create_user(
        username='alex121', email='alexpfdfsdf@alex.ru', password='top_secret')
        shop = models.Shop.objects.create(title='Магазин1', status=models.SHOP_STATUS_PUBLISHED, image=models.Product.generate_unique_code())
        models.ShopsToBrands.objects.create(shop=shop, brand=self.brand)
        models.Payment.increase(shop, user, 500000)
        models.Subscription.objects.create(start_date=self.today,
                                                           end_date=self.today + timezone.timedelta(days=30),
                                                           user=user,
                                                           shop=shop,
                                                           subscription_type=self.subscription_type,
                                                           )


        product = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                 start_date=self.today,
                                 end_date=self.today + timezone.timedelta(days=1),
                                 code=models.Product.generate_unique_code(), product_type=self.pt3, shop=shop, brand=self.brand,
                                         status=models.STATUS_TO_APPROVE,
                                 )

        product.status = models.STATUS_APPROVED
        product.save()

        product.status = models.STATUS_PUBLISHED
        product.save()


        banner = models.ProductBanner.objects.create(product=product, banner='/path/to/banner', status=models.BANNER_STATUS_APPROVED)
        action_popular = models.ProductAction.objects.create(start=True, start_date=self.product.start_date,
                                                                   end_date=self.product.end_date,
                                                                   action_type=models.ACTION_TYPE_POPULAR,
                                                                   product=product, banner=banner,
                                                                   )

        md = models.get_actions_count_for_interval(models.ACTION_TYPE_POPULAR, yesterday, after_tomorrow)
        self.assertNotIn(yesterday,md)
        self.assertEquals(md[today], max_polular - 1)
        self.assertEquals(md[tomorrow], max_polular - 1)
        self.assertEquals(md[after_tomorrow], max_polular)




    def test_get_actions_count_for_interval_category(self):
        max_category = settings.MAX_CATEGORY_COUNT
        today = self.today
        tomorrow = self.today + timezone.timedelta(days=1)
        yesterday = self.today + timezone.timedelta(days=-1)
        after_tomorrow = self.today + timezone.timedelta(days=2)
        md = models.get_actions_count_for_interval(models.ACTION_TYPE_CATEGORY, yesterday, after_tomorrow, category=self.pt3)
        self.assertNotIn(yesterday, md)
        self.assertEquals(md[today], max_category)
        self.assertEquals(md[tomorrow], max_category)
        self.assertEquals(md[after_tomorrow], max_category)


        user = User.objects.create_user(
        username='alex121', email='alexpfdfsdf@alex.ru', password='top_secret')
        shop = models.Shop.objects.create(title='Магазин1', status=models.SHOP_STATUS_PUBLISHED, image=models.Product.generate_unique_code())
        models.ShopsToBrands.objects.create(shop=shop, brand=self.brand)
        models.Payment.increase(shop, user, 500000)
        models.Subscription.objects.create(start_date=self.today,
                                                           end_date=self.today + timezone.timedelta(days=30),
                                                           user=user,
                                                           shop=shop,
                                                           subscription_type=self.subscription_type,
                                                           )


        product = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                 start_date=self.today,
                                 end_date=self.today + timezone.timedelta(days=1),
                                 code=models.Product.generate_unique_code(), product_type=self.pt3, shop=shop, brand=self.brand,
                                         status=models.STATUS_TO_APPROVE,
                                 )

        product.status = models.STATUS_APPROVED
        product.save()

        product.status = models.STATUS_PUBLISHED
        product.save()


        banner = models.ProductBanner.objects.create(product=product, banner='/path/to/banner', status=models.BANNER_STATUS_APPROVED)
        action_category = models.ProductAction.objects.create(start=True, start_date=self.product.start_date,
                                                                   end_date=self.product.end_date,
                                                                   action_type=models.ACTION_TYPE_CATEGORY,
                                                                   product=product, banner=banner,
                                                                   )

        md = models.get_actions_count_for_interval(models.ACTION_TYPE_CATEGORY, yesterday, after_tomorrow, category=self.pt3)
        self.assertNotIn(yesterday,md)
        self.assertEquals(md[today], max_category - 1)
        self.assertEquals(md[tomorrow], max_category - 1)
        self.assertEquals(md[after_tomorrow], max_category)

        md1 = models.get_actions_count_for_interval(models.ACTION_TYPE_CATEGORY, yesterday, after_tomorrow, product=product)
        md2 = models.get_actions_count_for_interval(models.ACTION_TYPE_CATEGORY, yesterday, after_tomorrow, category=self.pt3.get_top_parent())
        self.assertEquals(md, md1)
        self.assertEquals(md1, md2)


    def test_can_start_allowed_actions_in_one_day_than_enabled_easy_check_without_forms(self):


        max_polular = settings.MAX_POPULAR_COUNT
        max_cat = settings.MAX_CATEGORY_COUNT

        for i in range(max_polular):
            user = User.objects.create_user(
            username='alexp{0}'.format(i), email='alexp{0}@alex.ru'.format(i), password='top_secret')
            shop = models.Shop.objects.create(title='Магазин1', image='sdfsdaf')
            shop.status = models.SHOP_STATUS_PUBLISHED
            shop.save(check_status=False, do_clean=False)
            models.ShopsToBrands.objects.create(shop=shop, brand=self.brand)
            models.Payment.increase(shop, user, 500000)
            models.Subscription.objects.create(start_date=self.today,
                                                               end_date=self.today + timezone.timedelta(days=30),
                                                               user=user,
                                                               shop=shop,
                                                               subscription_type=self.subscription_type,
                                                               )


            product = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                     start_date=self.today,
                                     end_date=self.today + timezone.timedelta(days=5),
                                     code=models.Product.generate_unique_code(), product_type=self.pt3, shop=shop, brand=self.brand,
                                             status=models.STATUS_TO_APPROVE,
                                     )

            product.status = models.STATUS_APPROVED
            product.save()

            product.status = models.STATUS_PUBLISHED
            product.save()



            banner = models.ProductBanner.objects.create(product=product, banner='/path/to/banner', status=models.BANNER_STATUS_APPROVED)
            action_popular = models.ProductAction.objects.create(start=True, start_date=self.product.start_date,
                                                                       end_date=self.product.end_date,
                                                                       action_type=models.ACTION_TYPE_POPULAR,
                                                                       product=product, banner=banner,
                                                                       )

        for i in range(max_cat):
            user = User.objects.create_user(
            username='alexc{0}'.format(i), email='alexc{0}@alex.ru'.format(i), password='top_secret')
            shop = models.Shop.objects.create(title='Магазин1', image='dsfgdsfg')
            shop.status = models.SHOP_STATUS_PUBLISHED
            shop.save(check_status=False, do_clean=False)
            models.ShopsToBrands.objects.create(shop=shop, brand=self.brand)
            models.Payment.increase(shop, user, 500000)
            models.Subscription.objects.create(start_date=self.today,
                                                               end_date=self.today + timezone.timedelta(days=30),
                                                               user=user,
                                                               shop=shop,
                                                               subscription_type=self.subscription_type,
                                                               )


            product = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                     start_date=self.today,
                                     end_date=self.today + timezone.timedelta(days=5),
                                     code=models.Product.generate_unique_code(), product_type=self.pt3, shop=shop, brand=self.brand,
                                             status=models.STATUS_TO_APPROVE,
                                     )


            product.status = models.STATUS_APPROVED
            product.save()

            product.status = models.STATUS_PUBLISHED
            product.save()

            action_categ = models.ProductAction.objects.create(start=True, start_date=self.product.start_date,
                                                                       end_date=self.product.end_date,
                                                                       action_type=models.ACTION_TYPE_CATEGORY,
                                                                       product=product,
                                                                       )



    def test_cant_start_more_actions_in_one_day_than_enabled_easy_check_without_forms(self):


        max_polular = settings.MAX_POPULAR_COUNT
        max_cat = settings.MAX_CATEGORY_COUNT

        with self.assertRaises(ValidationError):
            for i in range(max_polular+1):
                user = User.objects.create_user(
                username='alexp{0}'.format(i), email='alexp{0}@alex.ru'.format(i), password='top_secret')
                shop = models.Shop.objects.create(title='Магазин1')
                shop.status = models.SHOP_STATUS_PUBLISHED
                shop.save(check_status=False, do_clean=False)
                models.ShopsToBrands.objects.create(shop=shop, brand=self.brand)
                models.Payment.increase(shop, user, 500000)
                models.Subscription.objects.create(start_date=self.today,
                                                                   end_date=self.today + timezone.timedelta(days=30),
                                                                   user=user,
                                                                   shop=shop,
                                                                   subscription_type=self.subscription_type,
                                                                   )


                product = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                         start_date=self.today,
                                         end_date=self.today + timezone.timedelta(days=5),
                                         code=models.Product.generate_unique_code(), product_type=self.pt3, shop=shop, brand=self.brand,
                                                 status=models.STATUS_TO_APPROVE,
                                         )

                product.status = models.STATUS_APPROVED
                product.save()

                product.status = models.STATUS_PUBLISHED
                product.save()

                banner = models.ProductBanner.objects.create(product=product, banner='/path/to/banner', status=models.BANNER_STATUS_APPROVED)
                action_popular = models.ProductAction.objects.create(start=True, start_date=self.product.start_date,
                                                                           end_date=self.product.end_date,
                                                                           action_type=models.ACTION_TYPE_POPULAR,
                                                                           product=product, banner=banner,
                                                                           )

        with self.assertRaises(ValidationError):
            for i in range(max_cat + 1):
                user = User.objects.create_user(
                username='alexc{0}'.format(i), email='alexc{0}@alex.ru'.format(i), password='top_secret')
                shop = models.Shop.objects.create(title='Магазин1')
                shop.status = models.SHOP_STATUS_PUBLISHED
                shop.save(check_status=False, do_clean=False)
                models.ShopsToBrands.objects.create(shop=shop, brand=self.brand)
                models.Payment.increase(shop, user, 500000)
                models.Subscription.objects.create(start_date=self.today,
                                                                   end_date=self.today + timezone.timedelta(days=30),
                                                                   user=user,
                                                                   shop=shop,
                                                                   subscription_type=self.subscription_type,
                                                                   )


                product = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                         start_date=self.today,
                                         end_date=self.today + timezone.timedelta(days=5),
                                         code=models.Product.generate_unique_code(), product_type=self.pt3, shop=shop, brand=self.brand,
                                                 status=models.STATUS_TO_APPROVE,
                                         )
                product.status = models.STATUS_APPROVED
                product.save()

                product.status = models.STATUS_PUBLISHED
                product.save()

                action_categ = models.ProductAction.objects.create(start=True, start_date=self.product.start_date,
                                                                           end_date=self.product.end_date,
                                                                           action_type=models.ACTION_TYPE_CATEGORY,
                                                                           product=product,
                                                                           )


    def test_product_without_active_subscription_cannot_start(self):
        self.product.status = models.STATUS_PUBLISHED
        try:
            self.product.save()
        except ValidationError:
            pass
        product = self.product.saved_version
        self.assertEquals(product.status, models.STATUS_PROJECT)


    def test_product_with_active_but_not_available_subscription_can_start(self):
        self.subscription_type.available = False
        self.subscription_type.save()
        models.Subscription.objects.create(start_date=self.today,
                                                                   end_date=self.today + timezone.timedelta(days=30),
                                                                   user=self.user,
                                                                   shop=self.shop,
                                                                   subscription_type=self.subscription_type,
                                                                   )

        self.product.status = models.STATUS_TO_APPROVE
        self.product.save()
        self.product.status = models.STATUS_APPROVED
        self.product.save()
        self.product.status = models.STATUS_PUBLISHED
        self.product.save()
        self.assertEquals(self.product.status, models.STATUS_PUBLISHED)



    def test_with_active_subscription_starts(self):
        models.Subscription.objects.create(start_date=self.today,
                                                               end_date=self.today + timezone.timedelta(days=30),
                                                               user=self.user,
                                                               shop=self.shop,
                                                               subscription_type=self.subscription_type,
                                                               )

        self.product.status = models.STATUS_TO_APPROVE
        self.product.save()

        self.product.status = models.STATUS_APPROVED
        self.product.save()


        self.product.status = models.STATUS_PUBLISHED
        self.product.save()
        self.assertEquals(self.product.status, models.STATUS_PUBLISHED)


    def test_action_without_money_cannot_start(self):
        models.Subscription.objects.create(start_date=self.today,
                                                               end_date=self.today + timezone.timedelta(days=30),
                                                               user=self.user,
                                                               shop=self.shop,
                                                               subscription_type=self.subscription_type,
                                                               )

        self.assertEquals(self.product.status, models.STATUS_PROJECT)


        self.product.status = models.STATUS_TO_APPROVE
        self.product.save()

        self.product.status = models.STATUS_APPROVED
        self.product.save()

        self.product.status = models.STATUS_PUBLISHED
        self.product.save()
        self.assertEquals(self.product.status, models.STATUS_PUBLISHED)
        action_category = models.ProductAction.objects.create(start=False, start_date=self.product.start_date,
                                                                       end_date=self.product.end_date,
                                                                       action_type=models.ACTION_TYPE_CATEGORY,
                                                                       product=self.product,
                                                                       )
        try:
            action_category.start = True
            action_category.save()

            caught_except = False
        except models.MoneyExeption:
            caught_except = True
        self.assertTrue(caught_except)


        self.product.pay()


        self.assertEquals(self.product.status, models.STATUS_PUBLISHED)
        self.assertEquals(self.product.shop.points_spent, 0)
        self.assertEquals(self.product.shop.points_blocked, 0)
        self.assertEquals(self.product.shop.points_total, 0)

        action_category = models.ProductAction.objects.get(pk=action_category.pk)
        self.assertEquals(action_category.status, models.ACTION_STATUS_PROJECT)


    def test_action_with_money_starts_and_dates_move_test(self):
        with self.settings(PAYMENT_USER_ID=self.user.pk):
            models.Subscription.objects.create(start_date=self.today,
                                                                   end_date=self.today + timezone.timedelta(days=30),
                                                                   user=self.user,
                                                                   shop=self.shop,
                                                                   subscription_type=self.subscription_type,
                                                                   )

            models.Payment.increase(self.shop, self.user, 5000)
            action_category = models.ProductAction.objects.create(start=True, start_date=self.product.start_date,
                                                                           end_date=self.product.end_date,
                                                                           action_type=models.ACTION_TYPE_CATEGORY,
                                                                           product=self.product,
                                                                           )
            self.product.status = models.STATUS_TO_APPROVE
            self.product.save()

            self.product.status = models.STATUS_APPROVED
            self.product.save()

            self.product.status = models.STATUS_PUBLISHED
            self.product.save()
            self.product.pay()
            action_category = models.ProductAction.objects.get(pk=action_category.pk)
            self.assertEquals(action_category.status, models.ACTION_STATUS_ACTIVE)
            self.assertEquals(action_category.points_spent, settings.ACTION_TYPE_CATEGORY_COST)
            start_date = action_category.start_date
            action_category.start_date += timezone.timedelta(days=1)
            try:
                action_category.save()
                caught_except = False
            except ValidationError:
                caught_except = True
            self.assertTrue(caught_except)
            action_category = action_category.saved_version
            self.assertEquals(start_date, action_category.start_date)
            self.assertEquals(action_category.status, models.ACTION_STATUS_ACTIVE)
            self.assertEquals(action_category.points_spent, settings.ACTION_TYPE_CATEGORY_COST)

            end_date = action_category.end_date
            action_category.end_date -= timezone.timedelta(days=1)
            action_category.save()
            action_category = action_category.saved_version
            self.assertNotEquals(end_date, action_category.end_date)
            self.assertEquals(action_category.status, models.ACTION_STATUS_ACTIVE)
            self.assertEquals(action_category.points_spent, settings.ACTION_TYPE_CATEGORY_COST)

            end_date = self.product.end_date
            new_end_date = self.product.end_date + timezone.timedelta(days=1)
            action_category.end_date = new_end_date
            action_category.save()
            action_category = action_category.saved_version
            self.assertEquals(end_date, action_category.end_date)
            self.assertEquals(action_category.status, models.ACTION_STATUS_ACTIVE)
            self.assertEquals(action_category.points_spent, settings.ACTION_TYPE_CATEGORY_COST)



    def test_cant_move_action_end_date_earlier_than_last_paid_day(self):
        with self.settings(PAYMENT_USER_ID=self.user.pk):
            models.Subscription.objects.create(start_date=self.today,
                                                                   end_date=self.today + timezone.timedelta(days=30),
                                                                   user=self.user,
                                                                   shop=self.shop,
                                                                   subscription_type=self.subscription_type,
                                                                   )

            models.Payment.increase(self.shop, self.user, 5000)
            action_category = models.ProductAction.objects.create(start=True, start_date=self.product.start_date,
                                                                           end_date=self.product.end_date,
                                                                           action_type=models.ACTION_TYPE_CATEGORY,
                                                                           product=self.product,
                                                                           )

            self.product.status = models.STATUS_TO_APPROVE
            self.product.save()

            self.product.status = models.STATUS_APPROVED
            self.product.save()

            self.product.status = models.STATUS_PUBLISHED
            self.product.save()
            self.product.pay()
            points_total1 = self.product.shop.points_total
            self.assertLess(points_total1, 5000)
            t = models.Payment.objects.all().latest('created')
            t.period += timezone.timedelta(days=5)
            t.save()
            action_category = models.ProductAction.objects.get(pk=action_category.pk)
            #action_category.start_date = self.today + timezone.timedelta(days=-1)
            action_category.end_date = self.today
            try:
                action_category.save()
                caught_except = False
            except:
                caught_except = True
            self.assertTrue(caught_except)



    def test_actions_takes_status_paused_on_suspend_and_returns_back(self):
        product = self.product
        models.Subscription.objects.create(start_date=self.today,
                                                                   end_date=self.today + timezone.timedelta(days=30),
                                                                   user=self.user,
                                                                   shop=self.shop,
                                                                   subscription_type=self.subscription_type,
                                                                   )
        start_active_count = product.actions.filter(status=models.ACTION_STATUS_ACTIVE).count()

        product.status = models.STATUS_TO_APPROVE
        product.save()

        product.status = models.STATUS_APPROVED
        product.save()

        product.status = models.STATUS_PUBLISHED
        product.save()

        product.status = models.STATUS_SUSPENDED
        product.save()


        suspended_active_count = product.actions.filter(status=models.ACTION_STATUS_ACTIVE).count()
        suspended_paused_count = product.actions.filter(status=models.ACTION_STATUS_PAUSED).count()

        #product.status = models.STATUS_TO_APPROVE
        #product.save()

        #product.status = models.STATUS_APPROVED
        #product.save()

        product.status = models.STATUS_PUBLISHED
        product.save()

        published_active_count = product.actions.filter(status=models.ACTION_STATUS_ACTIVE).count()
        published_paused_count = product.actions.filter(status=models.ACTION_STATUS_PAUSED).count()

        self.assertEqual(start_active_count, suspended_paused_count)
        self.assertEqual(suspended_active_count, 0)
        self.assertEqual(start_active_count, published_active_count)
        self.assertEqual(published_paused_count, 0)

    def test_cannot_start_popular_action_without_approved_banner(self):
        models.Payment.increase(self.shop, self.user, 5000)
        banner = models.ProductBanner.objects.create(product=self.product, banner='/path/to/banner')
        action_popular = models.ProductAction.objects.create(start=True, start_date=self.product.start_date,
                                                                       end_date=self.product.end_date,
                                                                       action_type=models.ACTION_TYPE_POPULAR,
                                                                       product=self.product, banner=banner,
                                                                       )
        self.product.pay()
        self.assertEqual(action_popular.status, models.ACTION_STATUS_PLANNED)



    def test_new_banner_is_saved_on_approve(self):
        banner = models.ProductBanner.objects.create(product=self.product, banner='/path/to/banner')
        self.assertEquals(banner.status, models.BANNER_STATUS_ON_APPROVE)


    def test_popular_action_doenst_start_with_banner_when_product_project(self):
        with self.settings(PAYMENT_USER_ID=self.user.pk):
            models.Subscription.objects.create(start_date=self.today,
                                                                   end_date=self.today + timezone.timedelta(days=30),
                                                                   user=self.user,
                                                                   shop=self.shop,
                                                                   subscription_type=self.subscription_type,
                                                                   )

            models.Payment.increase(self.shop, self.user, 5000)
            banner = models.ProductBanner.objects.create(product=self.product, banner='/path/to/banner',
                                                         status=models.BANNER_STATUS_APPROVED)

            action_popular = models.ProductAction.objects.create(start=True, start_date=self.product.start_date,
                                                                           end_date=self.product.end_date,
                                                                           action_type=models.ACTION_TYPE_POPULAR,
                                                                           product=self.product, banner=banner,
                                                                           )

            #self.product.status = models.STATUS_PUBLISHED
            self.product.pay()

            action_popular = action_popular.saved_version
            self.assertEqual(self.product.status, models.STATUS_PROJECT)
            self.assertEqual(action_popular.status, models.ACTION_STATUS_PLANNED)










class ProductSubscriptionAccuracyTest(BaseTest):
    def setUp(self):
        super().setUp()
        today = models.get_today()
        self.today = today
        #self.user = User.objects.create_user(
        #        username='alex', email='alex@alex.ru', password='top_secret')


        #self.simple_user = User.objects.create_user(
        #        username='alex1', email='ale1x@alex.ru', password='top_secret1')


        self.subscription_type = models.SubscriptionType.objects.create(title='Subscription type', period_points=1,
                                                                        max_products=2,
                                                                        price=100,
                                                                        period_type=models.SUBSCRIPTION_PERIOD_TYPE_MONTH,
                                                                        )

        self.subscription = models.Subscription.objects.create(start_date=self.today,
                                                                   end_date=self.today + timezone.timedelta(days=30),
                                                                   user=self.user,
                                                                   shop=self.shop,
                                                                   subscription_type=self.subscription_type,
                                                                   )



        self.product1.status = models.STATUS_TO_APPROVE
        self.product1.save()

        self.product2.status = models.STATUS_TO_APPROVE
        self.product2.save()

        self.product1.status = models.STATUS_APPROVED
        self.product1.save()

        self.product2.status = models.STATUS_APPROVED
        self.product2.save()



        self.product1.status = models.STATUS_PUBLISHED
        self.product1.save()


        self.product2.status = models.STATUS_PUBLISHED
        self.product2.save()

        #self.product3.status = models.STATUS_PUBLISHED
        #self.product3.save()



        self.color_red = models.FilterValue.objects.create(title='Красный', filter_type=models.FILTER_TYPE_COLOR)
        self.color_green = models.FilterValue.objects.create(title='Зеленый', filter_type=models.FILTER_TYPE_COLOR)

        self.dress_size_42 = models.FilterValue.objects.create(title='42', filter_type=models.FILTER_TYPE_SIZE_WOMAN)
        self.dress_size_44 = models.FilterValue.objects.create(title='44', filter_type=models.FILTER_TYPE_SIZE_WOMAN)

        self.product1.filter_values.add(self.color_green)
        models.FilterValueToProductType.objects.create(product_type=self.pt3, filter_type=models.FILTER_TYPE_COLOR)

        #models.FilterValueToProduct.objects.create(product=self.product1, filter_value=self.color_green)


    def test_product_with_start_date_in_past_moved_to_present(self):
        self.assertEqual(self.product2.start_date, self.today)


    def test_cannot_start_more_actions_than_subscribed(self):
        self.product3.status = models.STATUS_PUBLISHED
        try:
            self.product3.save()
            caught_except = False
        except ValidationError:
            caught_except = True
        self.assertTrue(caught_except)



    def test_can_plan_action_after_subscription_ends_within_a_limit(self):
        self.subscription.auto_pay = True
        self.subscription.save()
        self.product3.start_date = self.subscription.end_date + timezone.timedelta(days=1)
        self.product3.end_date = max(self.product2.start_date, self.subscription.end_date) + timezone.timedelta(days=30)

        self.product3.status = models.STATUS_TO_APPROVE
        self.product3.save()

        self.product3.status = models.STATUS_APPROVED
        self.product3.save()


        self.product3.status = models.STATUS_READY
        self.product3.save()
        self.assertEquals(self.product3.status, models.STATUS_READY)




    def test_cannot_plan_actions_after_subscription_ends_not_within_a_limit(self):
        self.subscription.auto_pay = True
        self.subscription.save()
        start_date = max(self.product2.end_date, self.subscription.end_date) + timezone.timedelta(days=3)
        end_date = max(self.product2.end_date, self.subscription.end_date) + timezone.timedelta(days=20)
        self.product3.status = models.STATUS_TO_APPROVE
        self.product3.save()

        self.product3.status = models.STATUS_APPROVED
        self.product3.save()


        self.product3.start_date = start_date
        self.product3.end_date = end_date



        self.product3.status = models.STATUS_READY
        self.product3.save()

        self.product4.start_date = start_date
        self.product4.end_date = end_date
        self.product4.status = models.STATUS_READY
        self.product4.save(check_status=False)

        try:
            self.product5.start_date = start_date
            self.product5.end_date = end_date
            self.product5.status = models.STATUS_READY
            self.product5.save()
        except:
            pass


        self.assertEqual(self.product3.start_date, self.product4.start_date, self.product5.start_date)
        self.assertGreater(self.product3.start_date, self.subscription.end_date)
        self.product4 = self.product4.saved_version
        self.product5 = self.product5.saved_version
        self.assertEqual(self.product4.status, models.STATUS_READY)
        self.assertEqual(self.product5.status, models.STATUS_PROJECT)


    def test_shop_get_active_products_works_fine_with_one_active_and_one_planned(self):
        tomorrow = self.product3.start_date + timezone.timedelta(days=1)
        self.product3.start_date = tomorrow
        try:
            self.product3.status = models.STATUS_READY
            self.product3.save(check_status=False)
        except ValidationError:
            pass
        count = self.shop.get_active_products(tomorrow).count()
        self.assertEqual(count, 2)


    def test_shop_get_active_products_works_fine_with_three_planned_after_subs_end_one_of_them_suspended(self):
        self.subscription.auto_pay = True
        self.subscription.save()
        start_date = max(self.product2.end_date, self.subscription.end_date) + timezone.timedelta(days=3)
        end_date = max(self.product2.end_date, self.subscription.end_date) + timezone.timedelta(days=20)
        self.product3.start_date = start_date
        self.product3.end_date = end_date
        self.product3.status = models.STATUS_READY
        self.product3.save(check_status=False)
        self.product4.start_date = start_date
        self.product4.end_date = end_date
        self.product4.status = models.STATUS_READY
        self.product4.save(check_status=False)

        self.product5.start_date = start_date
        self.product5.end_date = end_date
        self.product5.status = models.STATUS_SUSPENDED
        self.product5.save(check_status=False)

        count = self.shop.get_active_products(start_date).count()
        self.assertEqual(self.product3.start_date, start_date)
        self.assertEqual(count, 2)


    def test_shop_cant_start_product_after_subs_ends_but_can_with_autopay(self):

        start_date = max(self.product2.end_date, self.subscription.end_date) + timezone.timedelta(days=3)
        end_date = max(self.product2.end_date, self.subscription.end_date) + timezone.timedelta(days=20)
        self.product3.start_date = start_date
        self.product3.end_date = end_date
        self.product3.status = models.STATUS_READY
        try:
            self.product3.save(check_status=False)
        except:
            pass
        self.product3 = self.product3.saved_version
        self.assertEquals(self.product3.status, models.STATUS_PROJECT)


        self.subscription.auto_pay = True
        self.subscription.save()

        self.product3.start_date = start_date
        self.product3.end_date = end_date
        self.product3.status = models.STATUS_READY
        self.product3.save(check_status=False)
        self.product3 = self.product3.saved_version
        self.assertEquals(self.product3.status, models.STATUS_READY)


    def test_cannot_save_product_with_end_date_lte_start_date(self):
        start_date = self.today
        end_date = start_date + timezone.timedelta(days=-1)
        self.product3.start_date = start_date
        self.product3.end_date = end_date
        self.product3.save()

        with self.assertRaises(ValidationError):
            self.product3.status = models.STATUS_TO_APPROVE
            self.product3.save()



    def test_cancelled_subscriptions_stay_unchanged_after_product_pause_and_back(self):
        product = self.product1

        ptc = models.ProductToCart.objects.create(product=product, user=self.simple_user, status=models.PTC_STATUS_CANCELLED)
        product.status = models.STATUS_SUSPENDED
        product.save()
        ptc = ptc.saved_version
        self.assertEquals(ptc.status, models.PTC_STATUS_CANCELLED)
        self.assertEquals(product.status, models.STATUS_SUSPENDED)
        product.status = models.STATUS_PUBLISHED
        product.save()
        ptc = ptc.saved_version
        self.assertEquals(product.status, models.STATUS_PUBLISHED)
        self.assertEquals(ptc.status, models.PTC_STATUS_CANCELLED)


    def test_subscriptions_takes_status_paused_on_suspend_and_returns_back(self):
        product = self.product1
        ptc = models.ProductToCart.objects.create(product=product, user=self.simple_user, status=models.PTC_STATUS_SUBSCRIBED)
        product.status = models.STATUS_SUSPENDED
        product.save()
        ptc = ptc.saved_version
        self.assertEquals(ptc.status, models.PTC_STATUS_SUSPENDED)
        self.assertEquals(product.status, models.STATUS_SUSPENDED)
        product.status = models.STATUS_PUBLISHED
        product.save()
        ptc = ptc.saved_version
        self.assertEquals(product.status, models.STATUS_PUBLISHED)
        self.assertEquals(ptc.status, models.PTC_STATUS_SUBSCRIBED)

    def test_product_mail_is_created_on_status_change_from_active_to_suspended_and_no_mails_in_suspended(self):
        with self.settings(REPEATED_LETTER_INTERVAL=0):
            product = self.product1
            count0 = product.mails.count()
            self.assertEquals(count0, 0)
            ptc = models.ProductToCart.objects.create(product=product, user=self.simple_user, status=models.PTC_STATUS_SUBSCRIBED)
            models.ProductMail.send_products_messages([product], self.simple_user, subscribed=True)
            models.ProductMail.send_message_for_all_changed_products()
            count1 = product.mails.count()
            self.assertEquals(count1, 1)
            models.ProductMail.send_message_for_all_changed_products()
            models.ProductMail.send_message_for_all_changed_products()
            count2 = product.mails.count()
            self.assertEquals(count2, 1)
            product.status = models.STATUS_SUSPENDED
            product.save()
            models.ProductMail.send_message_for_all_changed_products()
            models.ProductMail.send_message_for_all_changed_products()
            count3 = product.mails.count()
            self.assertEquals(count3, 2)
            self.product1.filter_values.add(self.color_red)
            models.ProductMail.send_message_for_all_changed_products()
            models.ProductMail.send_message_for_all_changed_products()
            count4 = product.mails.count()
            self.assertEquals(count4, 2)
            product.status = models.STATUS_PUBLISHED
            product.save()

            changed_fields = product.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=False)
            self.assertIn('status', changed_fields)
            self.assertIn('filter_values', changed_fields)

            models.ProductMail.send_message_for_all_changed_products()
            models.ProductMail.send_message_for_all_changed_products()
            count5 = product.mails.count()
            self.assertEquals(count5, 3)
            product.status = models.STATUS_FINISHED
            product.save()
            changed_fields = product.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=False)
            self.assertIn('status', changed_fields)
            self.assertNotIn('filter_values', changed_fields)
            models.ProductMail.send_message_for_all_changed_products()
            models.ProductMail.send_message_for_all_changed_products()
            count6 = product.mails.count()
            self.assertEquals(count6, 4)
            ptc = ptc.saved_version
            self.assertEquals(ptc.status, models.PTC_STATUS_FINISHED_BY_SHOP)


    def test_action_doensnt_start_after_save_but_start_after_pay(self):
        with self.settings(PAYMENT_USER_ID=self.user.pk):
            sum = settings.ACTION_TYPE_POPULAR_COST * 2 + settings.ACTION_TYPE_CATEGORY_COST * 3
            models.Payment.increase(self.shop, self.user, sum)
            action_category = models.ProductAction.objects.create(start=True, start_date=self.product1.start_date,
                                                                           end_date=self.product1.start_date + timezone.timedelta(days=2),
                                                                           action_type=models.ACTION_TYPE_CATEGORY,
                                                                           product=self.product1,
                                                                           )

            banner = models.ProductBanner.objects.create(product=self.product1, banner='/path/to/banner', status=models.BANNER_STATUS_APPROVED)
            action_popular = models.ProductAction.objects.create(start=True, start_date=self.product1.start_date,
                                                                           end_date=self.product1.start_date + timezone.timedelta(days=1),
                                                                           action_type=models.ACTION_TYPE_POPULAR,
                                                                           product=self.product1, banner=banner,
                                                                           )

            self.assertEquals(self.product1.status, models.STATUS_PUBLISHED)
            self.assertEquals(action_popular.status, models.ACTION_STATUS_PLANNED)
            self.assertEquals(action_category.status, models.ACTION_STATUS_PLANNED)
            self.product1.pay()
            action_category = action_category.saved_version
            action_popular = action_popular.saved_version
            self.assertEquals(action_popular.status, models.ACTION_STATUS_ACTIVE)
            self.assertEquals(action_category.status, models.ACTION_STATUS_ACTIVE)
            cdc = settings.ACTION_TYPE_CATEGORY_COST
            pdc = settings.ACTION_TYPE_POPULAR_COST


            self.assertEquals(self.product1.points_blocked, cdc * 2 + pdc * 1)
            self.assertEquals(self.product1.shop.points_blocked, cdc * 2 + pdc * 1)
            self.assertEquals(self.product1.points_spent, cdc + pdc)
            self.assertEquals(self.product1.shop.points_free, sum - (cdc * 2 + pdc * 1) - cdc - pdc)



    def test_action_with_no_money_to_block_cannot_start(self):
        with self.settings(PAYMENT_USER_ID=self.user.pk):
            sum = (settings.ACTION_TYPE_CATEGORY_COST * 3 + settings.ACTION_TYPE_POPULAR_COST * 3) - 1
            models.Payment.increase(self.shop, self.user, sum)
            action_category = models.ProductAction.objects.create(start=False, start_date=self.product1.start_date,
                                                                           end_date=self.product1.start_date + timezone.timedelta(days=2),
                                                                           action_type=models.ACTION_TYPE_CATEGORY,
                                                                           product=self.product1,
                                                                           )

            banner = models.ProductBanner.objects.create(product=self.product1, banner='/path/to/banner', status=models.BANNER_STATUS_APPROVED)
            action_popular = models.ProductAction.objects.create(start=False, start_date=self.product1.start_date,
                                                                           end_date=self.product1.start_date + timezone.timedelta(days=2),
                                                                           action_type=models.ACTION_TYPE_POPULAR,
                                                                           product=self.product1, banner=banner,
                                                                           )

            action_category.start = True
            action_category.save()


            try:
                action_popular.start = True
                action_popular.save()
                caught_except = False
            except models.MoneyExeption:
                caught_except = True
            self.assertTrue(caught_except)
            action_category = action_category.saved_version
            action_popular = action_popular.saved_version

            self.assertEquals(self.product1.status, models.STATUS_PUBLISHED)
            self.assertEquals(action_category.status, models.ACTION_STATUS_PLANNED)
            self.assertEquals(action_popular.status, models.ACTION_STATUS_PROJECT)
            self.product1.pay()

            action_category = action_category.saved_version
            action_popular = action_popular.saved_version
            self.assertEquals(action_popular.status, models.ACTION_STATUS_PROJECT)
            self.assertEquals(action_category.status, models.ACTION_STATUS_ACTIVE)

            models.Payment.increase(self.shop, self.user, 1)
            action_popular.start = True
            action_popular.save()

            try:
                #self.product1.prepare_product_account()
                self.product1.pay()
            except models.MoneyExeption:
                pass

            action_category = action_category.saved_version
            action_popular = action_popular.saved_version
            self.assertEquals(action_popular.status, models.ACTION_STATUS_ACTIVE)
            self.assertEquals(action_category.status, models.ACTION_STATUS_ACTIVE)

    def test_shop_get_busy_days_within_a_subscription(self):
        shop = self.shop
        days_count = (self.product1.end_date - self.product1.start_date).days + 1
        busy_days1 = shop.get_busy_days(self.product1.start_date, self.product1.end_date)
        len1 = len(busy_days1)
        self.assertEquals(len1, days_count)

        self.product1.status = models.STATUS_NEED_REWORK
        self.product1.save(check_status=False)
        busy_days2 = shop.get_busy_days(self.product1.start_date, self.product1.end_date)
        self.assertEquals(busy_days2, None)



        self.product1.status = models.STATUS_PUBLISHED
        self.product1.save(check_status=False)
        busy_days3 = shop.get_busy_days(self.product1.start_date, self.product1.end_date)
        len3 = len(busy_days3)
        self.assertEquals(len3, days_count)

        busy_days4 = shop.get_busy_days(self.product1.end_date, self.product1.end_date + timezone.timedelta(days=5))
        len4 = len(busy_days4)
        self.assertEquals(len4, 1)

        busy_days5 = shop.get_busy_days(self.product1.start_date, self.product1.end_date, excluded_product=self.product1)
        self.assertEquals(busy_days5, None)

        busy_days6 = shop.get_busy_days(self.product1.start_date, self.product1.end_date, excluded_product=self.product3)
        len6 = len(busy_days6)
        self.assertEquals(len6, days_count)

        start = self.subscription.end_date + datetime.timedelta(days=1)
        end = self.subscription.end_date + datetime.timedelta(days=30)
        busy_days7 = shop.get_busy_days(start, end)
        self.assertEquals(len(busy_days7), (end - start).days + 1)

    def test_shop_get_busy_days_within_planned_subscription(self):
        subscription_type1 = models.SubscriptionType.objects.create(title='Subscription type1', period_points=1,
                                                                        max_products=1,
                                                                        price=100,
                                                                        period_type=models.SUBSCRIPTION_PERIOD_TYPE_MONTH,
                                                                        )


        planned_start_date = self.subscription.end_date + timezone.timedelta(days=1)
        planned_end_date = self.subscription.end_date + timezone.timedelta(days=30)
        days_count = (planned_end_date - planned_start_date).days + 1
        planned_subscription = models.Subscription.objects.create(start_date=planned_start_date,
                                                                   end_date=planned_end_date,
                                                                   user=self.user,
                                                                   shop=self.shop,
                                                                   subscription_type=subscription_type1,
                                                                   status=models.SUBSCRIPTION_STATUS_PLANNED,
                                                                   )

        busy_days = self.shop.get_busy_days(planned_start_date, planned_end_date)
        self.assertEquals(busy_days, None)


    def test_shop_get_busy_days_within_autopay_subscription(self):
        planned_start_date = self.subscription.end_date + timezone.timedelta(days=1)
        planned_end_date = self.subscription.end_date + timezone.timedelta(days=30)
        days_count = (planned_end_date - planned_start_date).days + 1

        busy_days = self.shop.get_busy_days(planned_start_date, planned_end_date)
        self.assertEquals(len(busy_days), days_count)

        self.subscription.auto_pay = True
        self.subscription.save()

        busy_days = self.shop.get_busy_days(planned_start_date, planned_end_date)
        self.assertEquals(busy_days, None)


    def test_repeated_pay_doesnt_take_money(self):
        with self.settings(PAYMENT_USER_ID=self.user.pk):
            models.Payment.increase(self.shop, self.user, 5000)
            action_category = models.ProductAction.objects.create(start=True, start_date=self.product1.start_date,
                                                                               end_date=self.product1.start_date + timezone.timedelta(days=2),
                                                                               action_type=models.ACTION_TYPE_CATEGORY,
                                                                               product=self.product1,
                                                                               )

            banner = models.ProductBanner.objects.create(product=self.product1, banner='/path/to/banner', status=models.BANNER_STATUS_APPROVED)
            action_popular = models.ProductAction.objects.create(start=True, start_date=self.product1.start_date,
                                                                               end_date=self.product1.start_date + timezone.timedelta(days=2),
                                                                               action_type=models.ACTION_TYPE_POPULAR,
                                                                               product=self.product1, banner=banner,
                                                                               )
            self.assertLess(self.shop.points_free, 5000)
            self.assertEquals(self.shop.points_total, 5000)

            self.product1.pay()
            free = self.shop.points_free
            total = self.shop.points_total

            self.assertLess(self.shop.points_free, 5000)
            self.assertLess(self.shop.points_total, 5000)
            self.product1.pay()
            self.product1.prepare_product_account()
            self.product1.pay()
            self.product1.prepare_product_account()
            self.assertEquals(self.shop.points_free, free)
            self.assertEquals(self.shop.points_total, total)



    def test_multiple_actions_of_one_kind_cannot_start(self):
        with self.settings(PAYMENT_USER_ID=self.user.pk):
            models.Payment.increase(self.shop, self.user, 5000)
            self.assertEquals(self.shop.points_free, 5000)
            self.assertEquals(self.shop.points_blocked, 0)

            action_category1 = models.ProductAction.objects.create(start=True, start_date=self.product1.start_date,
                                                                           end_date=self.product1.start_date + timezone.timedelta(days=2),
                                                                           action_type=models.ACTION_TYPE_CATEGORY,
                                                                           product=self.product1,
                                                                           )



            try:
                action_category2 = models.ProductAction.objects.create(start=True, start_date=self.product1.start_date,
                                                                           end_date=self.product1.start_date + timezone.timedelta(days=2),
                                                                           action_type=models.ACTION_TYPE_CATEGORY,
                                                                           product=self.product1,
                                                                            )
                caught_except = False
            except ValidationError:
                caught_except = True
            self.assertTrue(caught_except)




            banner = models.ProductBanner.objects.create(product=self.product1, banner='/path/to/banner', status=models.BANNER_STATUS_APPROVED)
            action_popular = models.ProductAction.objects.create(start=True, start_date=self.product1.start_date,
                                                                           end_date=self.product1.start_date + timezone.timedelta(days=2),
                                                                           action_type=models.ACTION_TYPE_POPULAR,
                                                                           product=self.product1, banner=banner,
                                                                           )

            try:
                action_popular2 = models.ProductAction.objects.create(start=True, start_date=self.product1.start_date,
                                                                           end_date=self.product1.start_date,
                                                                           action_type=models.ACTION_TYPE_POPULAR,
                                                                           product=self.product1,
                                                                            )
                caught_except = False

            except ValidationError:
                caught_except = True

            self.assertTrue(caught_except)

            try:
                #self.product1.prepare_product_account()
                self.product1.pay()

            except models.ValidationError:
                self.assertTrue(False)


            try:
                #self.product1.prepare_product_account()
                action_category1.pay()

            except models.ValidationError:
                self.assertTrue(False)




            try:
                #self.product1.prepare_product_account()
                action_popular.pay()

            except models.ValidationError:
                self.assertTrue(False)

            self.assertEquals(action_category1.status, models.ACTION_STATUS_ACTIVE)
            #self.assertEquals(action_category2.status, models.ACTION_STATUS_PLANNED)
            self.assertEquals(action_popular.status, models.ACTION_STATUS_ACTIVE)
            self.assertEquals(self.shop.points_free + self.shop.points_blocked + action_category1.points_spent + action_popular.points_spent, 5000)
            self.assertGreater(self.shop.points_free, 0)
            self.assertGreater(self.shop.points_blocked, 0)
            self.assertGreater(action_category1.points_spent, 0)
            self.assertGreater(action_popular.points_spent, 0)

    def test_to_pay_warning_is_shown_on_product_update_detail(self):
        models.Payment.increase(self.shop, self.user, 5000)
        self.product3.status = models.STATUS_APPROVED
        self.product3.save(check_status=False)
        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': self.product3.pk}), user=self.user)
        self.assertEquals(self.product3.to_pay_in_day(), 0)
        self.assertNotIn('Со счета будет списано', page)

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': self.product3.pk}), user=self.user)
        self.assertNotIn('Со счета будет списано', page)


        action_category1 = models.ProductAction.objects.create(start=True, start_date=self.product3.start_date,
                                                                           end_date=self.product3.start_date + timezone.timedelta(days=2),
                                                                           action_type=models.ACTION_TYPE_CATEGORY,
                                                                           product=self.product3,
                                                                           )


        banner = models.ProductBanner.objects.create(product=self.product3, banner='/path/to/banner', status=models.BANNER_STATUS_APPROVED)
        action_popular = models.ProductAction.objects.create(start=False, start_date=self.product3.start_date,
                                                                           end_date=self.product3.start_date + timezone.timedelta(days=2),
                                                                           action_type=models.ACTION_TYPE_POPULAR,
                                                                           product=self.product3, banner=banner,
                                                                           )


        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': self.product3.pk}), user=self.user)
        self.assertEquals(self.product3.to_pay_in_day(), settings.ACTION_TYPE_CATEGORY_COST)
        self.assertIn('Со счета будет списано', page)
        self.assertEquals(self.product3.status, models.STATUS_APPROVED)
        self.assertEquals(action_category1.status, models.ACTION_STATUS_PLANNED)

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': self.product3.pk}), user=self.user)
        self.assertIn('со счета будет списано {0}'.format(self.product3.to_pay_in_day()), page)






class ProductCreateViewTests(BaseTest):
    def setUp(self):
        super().setUp()
        #response = self.client.post(reverse('discount:signup'), {'username': 'kulik', 'email': '1191@bk.ru',
        #                                             'password1':'1234567',
        #                                             'password2':'1234567',
        #                                             }
        #                         )

        self.factory = RequestFactory()
        #models.ShopsToUsers.objects.create(shop=self.shop, user=self.client.request.user, confirmed=True)

    def test_product_create_page_is_available(self):
        request = self.factory.get(reverse('discount:product-create'))
        request.user = self.user
        response = views.ProductCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def get_form(self, page):
        form = page.forms['product-create-form']
        title = 'Тестовое название, не повторять 23423465347'
        form['title'] = title
        form['normal_price'] = '500'
        form['stock_price'] = '300'
        form['product_type'] = str(self.pt3.pk)
        form['category'] = str(self.pt3.get_top_parent().pk)
        form['end_date'] = str(self.today)
        form['brand'] = str(self.brand.pk)
        form['body'] = 'описание описание описание'
        return form

    def test_user_can_create_product_and_filter_value_is_required(self):
        u = models.User.objects.get(username='alex')
        product = self.product1


        page = self.app.get(reverse('discount:product-create'), user=u)
        form = self.get_form(page)
        title = 'Тестовое название, не повторять 23423465347'
        path = TEST_IMAGE_PATH
        f = open(path, 'rb')
        form['images-0-image'] = ('images-0-image', f.read())
        models.FilterValueToProductType.objects.create(product_type=self.pt1, filter_type=models.FILTER_TYPE_COLOR)
        page = form.submit(name='to-approve')
        self.assertEquals(page.status_code, 200) #"Неудачно"


        models.FilterValueToProductType.objects.filter(product_type=self.pt1, filter_type=models.FILTER_TYPE_COLOR).delete()

        page = form.submit(name='to-approve')
        self.assertEquals(page.status_code, 302)
        p = models.Product.objects.latest('created')
        self.assertEquals(p.title, title)
        self.assertEquals(p.images.count(), 1)


    def test_image_is_required(self):
        u = models.User.objects.get(username='alex')
        page = self.app.get(reverse('discount:product-create'), user=u)

        form = self.get_form(page)

        #('avatar', file(os.path.join(settings.project_path, '....', 'avatar.png')).read())

        page = form.submit()
        self.assertEquals(page.status_code, 200) #"Неудачно"


    def test_can_send_new_product_to_approve_with_code_and_further_full_cycle(self):
        u = models.User.objects.get(username='alex')
        page = self.app.get(reverse('discount:product-create'), user=u)
        form = self.get_form(page)
        title = 'Тестовое название, не повторять 23423465347'
        path = TEST_IMAGE_PATH
        f = open(path, 'rb')
        form['images-0-image'] = ('images-0-image', f.read())
        models.FilterValueToProductType.objects.create(product_type=self.pt1, filter_type=models.FILTER_TYPE_COLOR)
        page = form.submit(name='to-approve')
        self.assertEquals(page.status_code, 200) #"Неудачно"


        #models.FilterValueToProductType.objects.filter(product_type=self.pt1, filter_param=models.FILTER_TYPE_COLOR).delete()

        form['colors'] = [str(self.color_green.pk)]
        page = form.submit(name='to-approve')
        self.assertEquals(page.status_code, 302)
        p = models.Product.objects.latest('created')
        p.start_after_approve = False
        self.assertEquals(p.title, title)
        self.assertEquals(p.images.count(), 1)
        self.assertNotEquals(p.code, '')
        self.assertEquals(p.status, models.STATUS_TO_APPROVE)
        code = p.code

        p.status = models.STATUS_NEED_REWORK
        p.save()

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']
        f = open(path, 'rb')
        form['images-1-image'] = ('images-1-image', f.read())
        page = form.submit(name='to-approve')
        self.assertEquals(page.status_code, 302)
        p = p.saved_version
        self.assertEquals(p.title, title)
        self.assertEquals(p.images.count(), 2)
        self.assertNotEquals(p.code, code)
        self.assertEquals(p.status, models.STATUS_TO_APPROVE)

        p.status = models.STATUS_APPROVED
        p.save()

        try: #Там ошибка неуловимая(похоже что jquery) но факт, что нет акт подписки и не должно разрешать
            page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
            form = page.forms['product-create-form']
            page = form.submit(name='to-publish')
        except:
            pass

        p = p.saved_version
        self.assertEquals(p.status, models.STATUS_APPROVED)


        models.Subscription.objects.create(start_date=self.today,
                                                               end_date=self.today + timezone.timedelta(days=30),
                                                               user=self.user,
                                                               shop=self.shop,
                                                               subscription_type=self.subscription_type,
                                                               )

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']
        page = form.submit(name='to-publish')
        self.assertEquals(page.status_code, 302)
        p = p.saved_version
        self.assertEquals(p.status, models.STATUS_PUBLISHED)

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']
        page = form.submit(name='to-suspend')
        self.assertEquals(page.status_code, 302)
        p = p.saved_version
        self.assertEquals(p.status, models.STATUS_SUSPENDED)

        p.status = models.STATUS_NEED_REWORK
        p.save(check_status=False)


        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']
        page = form.submit(name='to-approve')
        self.assertEquals(page.status_code, 302)
        p = p.saved_version
        self.assertEquals(p.status, models.STATUS_TO_APPROVE)

        p.status = models.STATUS_APPROVED
        p.save()

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']
        form['start_date'] = str(self.today + timezone.timedelta(days=1))
        page = form.submit(name='to-publish')
        self.assertEquals(page.status_code, 200)
        p = p.saved_version
        self.assertEquals(p.status, models.STATUS_APPROVED)

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']
        form['start_date'] = str(self.today + timezone.timedelta(days=1))
        form['end_date'] = str(self.today + timezone.timedelta(days=2))
        page = form.submit(name='to-plan')
        self.assertEquals(page.status_code, 302)
        p = p.saved_version
        self.assertEquals(p.status, models.STATUS_READY)


        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']
        page = form.submit(name='to-project')
        self.assertEquals(page.status_code, 302)
        p = p.saved_version
        self.assertEquals(p.status, models.STATUS_PROJECT)


        #Возврат в проект с ошибками
        p.status = models.STATUS_APPROVED
        p.start_date = self.today + timezone.timedelta(days=-1)
        p.end_date = self.today + timezone.timedelta(days=-2)
        p.save(check_status=False, do_clean=False)
        self.assertEquals(p.status, models.STATUS_APPROVED)

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']
        page = form.submit(name='to-project')
        self.assertEquals(page.status_code, 302)
        p = p.saved_version
        self.assertEquals(p.status, models.STATUS_PROJECT)


         #Из действующей нельзя
        p.status = models.STATUS_PUBLISHED
        p.start_date = self.today
        p.end_date = self.today
        p.save(check_status=False, do_clean=False)
        self.assertEquals(p.status, models.STATUS_PUBLISHED)

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']
        page = form.submit(name='to-project')
        p = p.saved_version
        self.assertEquals(p.status, models.STATUS_PUBLISHED)

        #авто-старт работает
        p.status = models.STATUS_TO_APPROVE
        p.start_after_approve = True
        p.start_date = self.today
        p.end_date = self.today
        p.save(check_status=False, do_clean=False)
        self.assertEquals(p.status, models.STATUS_TO_APPROVE)

        p.status = models.STATUS_APPROVED
        p.save()
        self.assertEquals(p.status, models.STATUS_PUBLISHED)


        p.status = models.STATUS_TO_APPROVE
        p.start_after_approve = True
        p.start_date = self.today + timezone.timedelta(days=1)
        p.end_date = p.start_date
        p.save(check_status=False, do_clean=False)
        self.assertEquals(p.status, models.STATUS_TO_APPROVE)

        p.status = models.STATUS_APPROVED
        p.save()
        self.assertEquals(p.status, models.STATUS_READY)


    def test_hash_field_works_fine(self):
        u = self.user
        s = self.shop
        p = self.product
        p.filter_values.add(self.color_green)
        models.ProductImage.objects.create(image='image', product=p)
        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        self.assertEquals(page.status_code, 200)

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']
        page = form.submit()
        self.assertEquals(page.status_code, 302)

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']
        p.body += '1'
        p.save()
        page = form.submit()
        self.assertEquals(page.status_code, 200)


        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']
        p.save()
        page = form.submit()
        self.assertEquals(page.status_code, 302)

        p.status = models.STATUS_TO_APPROVE
        p.save()

        p.status = models.STATUS_APPROVED
        p.save()

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']
        p.save()
        page = form.submit()
        self.assertEquals(page.status_code, 302)

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']
        p.body += '1'
        p.save()
        page = form.submit()
        self.assertEquals(page.status_code, 200)



    def test_related_products_field_works_fine(self):
        self.product1.status = models.STATUS_APPROVED
        self.product1.save(check_status=False, do_clean=False)
        self.product2.status = models.STATUS_APPROVED
        self.product2.save(check_status=False, do_clean=False)
        self.product3.status = models.STATUS_APPROVED
        self.product3.save(check_status=False, do_clean=False)

        u = models.User.objects.get(username='alex')
        page = self.app.get(reverse('discount:product-create'), user=u)
        form = self.get_form(page)
        path = TEST_IMAGE_PATH
        f = open(path, 'rb')
        form['images-0-image'] = ('images-0-image', f.read())
        models.FilterValueToProductType.objects.create(product_type=self.pt1, filter_type=models.FILTER_TYPE_COLOR)

        form['related_products-0-related_product'] = str(self.product1.pk)
        form['related_products-1-related_product'] = str(self.product2.pk)

        page = form.submit()
        self.assertEquals(page.status_code, 302)

        p = models.Product.objects.latest('created')

        self.assertEquals(p.related_products.all().count(), 2)

        self.product1.status = models.STATUS_FINISHED
        self.product1.save(check_status=False, do_clean=False)

        self.assertEquals(p.related_products.all().count(), 1)

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']

        form['related_products-0-related_product'] = ''

        page = form.submit()
        self.assertEquals(page.status_code, 302)

        p = p.saved_version

        self.assertEquals(p.related_products.all().count(), 0)


        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']

        form['related_products-0-related_product'] = str(self.product3.pk)

        page = form.submit()
        self.assertEquals(page.status_code, 302)

        p = p.saved_version

        self.assertEquals(p.related_products.all().count(), 1)

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = page.forms['product-create-form']

        with self.assertRaises(ValueError):
            form['related_products-0-related_product'] = str(self.product1.pk)
            page = form.submit()

        p = p.saved_version

        self.assertEquals(p.related_products.all().count(), 1)


    def test_related_products_field_is_available_for_various_statuses(self):

        subscription = models.Subscription.objects.create(start_date=self.today,
                                                                   end_date=self.today + timezone.timedelta(days=30),
                                                                   user=self.user,
                                                                   shop=self.shop,
                                                                   subscription_type=self.subscription_type,
                                                                   )

        models.FilterValueToProductType.objects.all().delete()
        u = self.user
        page = self.app.get(reverse('discount:product-create'), user=u)
        form = self.get_form(page)
        path = TEST_IMAGE_PATH
        f = open(path, 'rb')
        form['images-0-image'] = ('images-0-image', f.read())
        page = form.submit()
        self.assertEquals(page.status_code, 302)

        p = models.Product.objects.latest('created')

        self.assertEquals(p.related_products.all().count(), 0)
        p.status = models.STATUS_APPROVED
        p.save(check_status=False, do_clean=False)

        statuses = [models.STATUS_PROJECT, models.STATUS_APPROVED, models.STATUS_PUBLISHED, models.STATUS_SUSPENDED]

        self.product2.status = models.STATUS_APPROVED
        self.product2.save(check_status=False, do_clean=False)

        for status in statuses:
            p.status = status
            p.save(check_status=False, do_clean=False)
            self.renew_app()
            page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
            form = page.forms['product-create-form']
            form['related_products-0-related_product'] = str(self.product2.pk)
            page = form.submit()
            self.assertEquals(page.status_code, 302)
            self.assertEquals(p.related_products.all().count(), 1)
            page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
            form = page.forms['product-create-form']
            form['related_products-0-related_product'] = ''
            page = form.submit()
            self.assertEquals(page.status_code, 302)
            self.assertEquals(p.related_products.all().count(), 0)



    def test_conditions_field_works_fine(self):
        u = models.User.objects.get(username='alex')
        page = self.app.get(reverse('discount:product-create'), user=u)
        form = self.get_form(page)
        path = TEST_IMAGE_PATH
        f = open(path, 'rb')
        form['images-0-image'] = ('images-0-image', f.read())
        models.FilterValueToProductType.objects.create(product_type=self.pt1, filter_type=models.FILTER_TYPE_COLOR)

        c1 = 'sdfhjsdfsdgfsdf'
        c2 = 'gr544heuigrtg'

        form['conditions-0-condition'] = c1
        form['conditions-1-condition'] = c2

        page = form.submit()
        self.assertEquals(page.status_code, 302)

        p = models.Product.objects.latest('created')

        self.assertEquals(p.conditions.all().count(), 2)

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': p.pk}), user=u)
        form = self.get_form(page)

        form['conditions-1-condition'] = ''

        page = form.submit()
        self.assertEquals(page.status_code, 302)

        p = p.saved_version

        self.assertEquals(p.conditions.all().count(), 1)





class ShopCreateAndSendToApproveTest(BaseTest):
    def test_can_signup_and_create_shop_and_manager_added_and_sends_to_approve(self):
        #response = self.client.post(reverse('discount:signup'), {'username': 'alex2', 'email': '119fsd1@bsdfk.ru',
        #                                             'password1':'1234567',
        #                                             'password2':'1234567',
        #                                             }
        page = self.app.get(reverse('discount:signup'))
        form = page.forms['signup-form']
        form['username'] = 'tester'
        form['password1'] = '1234567'
        form['password2'] = '1234567'
        form['email'] = 'tester@testerdsads.ru'
        page = form.submit()
        u = models.User.objects.latest('date_joined')
        self.assertEquals(u.username, 'tester')

        f = open(TEST_IMAGE_PATH, 'rb')

        page = self.app.get(reverse('discount:shop-create'), user=u)
        form = page.forms['shop-create-form']
        form['image'] = ('image', f.read())
        form['add_brands'] = 'sdfsdf, sdfsdf, sdffsd'
        form['custom_adress'] = 'dfsgdfgsdgsdfgs'
        form['phones-0-phone'] = '123435345'
        form['title'] = 'Магазинчик12313443'
        #form['to-approve'] = ''
        page = form.submit(name='to-approve')

        self.assertEquals(page.status_code, 302)
        shop = models.Shop.objects.latest('created')
        self.assertEquals(shop.title, 'Магазинчик12313443')

        self.assertEquals(shop.users.all()[0], u)
        self.assertEquals(shop.status, models.SHOP_STATUS_TO_APPROVE)

    def test_checking_adiing_and_deleting_users(self):
        additional_user = User.objects.create_user(
            username='additionaldsf', email='addtiono@fdsfsd.ru', password='top_secret')
        user = User.objects.create_user(
            username='addisdftionaldsf', email='sdfno@fdsfsd.ru', password='top_secresdft')
        f = open(TEST_IMAGE_PATH, 'rb')
        page = self.app.get(reverse('discount:shop-create'), user=user)
        form = page.forms['shop-create-form']
        form['image'] = ('image', f.read())
        form['add_brands'] = 'sdfsdf, sdfsdf, sdffsd'
        form['custom_adress'] = 'dfsgdfgsdgsdfgs'
        form['phones-0-phone'] = '123435345'
        form['title'] = 'Магазинчик12313443'
        #form['to-approve'] = ''
        page = form.submit()
        self.assertEquals(page.status_code, 302)
        shop = user.get_shop
        self.assertEquals(shop.title, 'Магазинчик12313443')
        self.assertEquals(shop.users.all()[0], user)
        self.assertEquals(shop.users.all().count(), 1)

        #self.renew_app()
        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=user)
        form = page.forms['shop-create-form']
        form['shopstousers_set-0-user'] = ''
        page = form.submit()
        self.assertEquals(page.status_code, 302)
        self.assertEquals(shop.users.all()[0], user)
        self.assertEquals(shop.users.all().count(), 1)

        #self.renew_app()
        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=user)
        form = page.forms['shop-create-form']
        form['shopstousers_set-0-user'] = ''
        form['shopstousers_set-1-user'] = additional_user.username
        page = form.submit()
        self.assertEquals(page.status_code, 302)
        self.assertEquals(shop.users.all().count(), 2)
        users_list = list(shop.users.all())
        self.assertIn(user, users_list)
        self.assertIn(additional_user, users_list)


           #self.renew_app()
        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=user)
        form = page.forms['shop-create-form']
        form['shopstousers_set-0-user'] = ''
        form['shopstousers_set-1-user'] = 'sdsfsdfsdfsdfsd'
        form['shopstousers_set-2-user'] = ''
        page = form.submit()
        self.assertEquals(page.status_code, 200)
        self.assertEquals(shop.users.all().count(), 2)
        users_list = list(shop.users.all())
        self.assertIn(user, users_list)
        self.assertIn(additional_user, users_list)


        #self.renew_app()
        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=user)
        form = page.forms['shop-create-form']
        form['shopstousers_set-0-user'] = ''
        form['shopstousers_set-1-user'] = ''
        form['shopstousers_set-2-user'] = ''
        page = form.submit()
        self.assertEquals(page.status_code, 302)
        self.assertEquals(shop.users.all().count(), 1)
        users_list = list(shop.users.all())
        self.assertIn(user, users_list)
        self.assertNotIn(additional_user, users_list)

        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=user)
        form = page.forms['shop-create-form']
        form['shopstousers_set-0-user'] = ''
        form['shopstousers_set-1-user'] = user.username
        form['shopstousers_set-2-user'] = ''
        page = form.submit()
        self.assertEquals(page.status_code, 302)
        self.assertEquals(shop.users.all().count(), 1)
        users_list = list(shop.users.all())
        self.assertIn(user, users_list)
        self.assertNotIn(additional_user, users_list)


        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=user)
        form = page.forms['shop-create-form']
        form['shopstousers_set-0-user'] = 'sdfsdfsgdfgdf'
        form['shopstousers_set-1-user'] = ''
        form['shopstousers_set-2-user'] = ''
        page = form.submit()
        self.assertEquals(page.status_code, 200)
        self.assertEquals(shop.users.all().count(), 1)
        users_list = list(shop.users.all())
        self.assertIn(user, users_list)
        self.assertNotIn(additional_user, users_list)

    def test_checking_adiing_and_deleting_phones(self):
        user = User.objects.create_user(
            username='addisdftionaldsf', email='sdfno@fdsfsd.ru', password='top_secresdft')
        f = open(TEST_IMAGE_PATH, 'rb')
        page = self.app.get(reverse('discount:shop-create'), user=user)
        form = page.forms['shop-create-form']
        form['image'] = ('image', f.read())
        form['add_brands'] = 'sdfsdf, sdfsdf, sdffsd'
        form['custom_adress'] = 'dfsgdfgsdgsdfgs'
        form['phones-0-phone'] = '+ 7 (123'
        form['phones-1-phone'] = '456'
        form['title'] = 'Магазинчик12313443'
        #form['to-approve'] = ''
        page = form.submit()
        self.assertEquals(page.status_code, 302)
        shop = user.get_shop
        self.assertEquals(shop.title, 'Магазинчик12313443')
        phones_count = shop.phones.all().count()
        self.assertEquals(phones_count, 2)
        phones = shop.phones.all().values_list('phone', flat=True)
        self.assertIn('+ 7 (123', phones)
        self.assertIn('456', phones)


        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=user)
        form = page.forms['shop-create-form']
        form['phones-0-phone'] = ''
        page = form.submit()
        phones_count = shop.phones.all().count()
        self.assertEquals(phones_count, 1)
        phones = shop.phones.all().values_list('phone', flat=True)
        self.assertNotIn('+ 7 (123', phones)
        self.assertIn('456', phones)

        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=user)
        form = page.forms['shop-create-form']
        form['phones-0-phone'] = ''
        form['phones-1-phone'] = ''
        form['phones-2-phone'] = '   '
        page = form.submit()
        phones_count = shop.phones.all().count()
        self.assertEquals(phones_count, 0)
        phones = shop.phones.all().values_list('phone', flat=True)

    def test_hashed_shop_field(self):
        page = self.app.get(reverse('discount:signup'))
        form = page.forms['signup-form']
        form['username'] = 'tester'
        form['password1'] = '1234567'
        form['password2'] = '1234567'
        form['email'] = 'tester@testerdsads.ru'
        page = form.submit()
        u = models.User.objects.latest('date_joined')
        self.assertEquals(u.username, 'tester')

        f = open(TEST_IMAGE_PATH, 'rb')

        page = self.app.get(reverse('discount:shop-create'), user=u)
        form = page.forms['shop-create-form']
        form['image'] = ('image', f.read())
        form['add_brands'] = 'sdfsdf, sdfsdf, sdffsd'
        form['custom_adress'] = 'dfsgdfgsdgsdfgs'
        form['phones-0-phone'] = '123435345'
        form['title'] = 'Магазинчик12313443'
        #form['to-approve'] = ''
        page = form.submit()

        self.assertEquals(page.status_code, 302)
        shop = models.Shop.objects.latest('created')
        self.assertEquals(shop.title, 'Магазинчик12313443')
        self.assertEquals(shop.users.all()[0], u)

        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=u)
        form = page.forms['shop-create-form']
        page = form.submit()
        self.assertEquals(page.status_code, 302)

        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=u)
        shop.body += '1'
        shop.save()
        form = page.forms['shop-create-form']
        page = form.submit()
        self.assertEquals(page.status_code, 200)

        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=u)
        form = page.forms['shop-create-form']
        page = form.submit()
        self.assertEquals(page.status_code, 302)

        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=u)
        form = page.forms['shop-create-form']
        shop.save()
        page = form.submit(name='to-approve')
        self.assertEquals(page.status_code, 302)

        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=u)
        form = page.forms['shop-create-form']
        page = form.submit()
        self.assertEquals(page.status_code, 200)



        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=u)
        shop.status = models.SHOP_STATUS_PUBLISHED
        models.ShopsToBrands.objects.create(shop=shop, brand=self.brand)
        shop.save()
        form = page.forms['shop-create-form']
        page = form.submit()
        self.assertEquals(page.status_code, 200)


        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=u)
        #shop.status = models.SHOP_STATUS_PUBLISHED
        shop.save()
        form = page.forms['shop-create-form']
        page = form.submit()
        self.assertEquals(page.status_code, 302)















class SubscriptionsTests(BaseTest):
    def setUp(self):
        super().setUp()
        self.subscription_type1 = models.SubscriptionType.objects.create(title='Subscription type', period_points=1,
                                                                        max_products=2,
                                                                        price=200,
                                                                        period_type=models.SUBSCRIPTION_PERIOD_TYPE_MONTH,
                                                                        )

        self.subscription_type2 = models.SubscriptionType.objects.create(title='Subscription type', period_points=1,
                                                                        max_products=2,
                                                                        price=300,
                                                                        period_type=models.SUBSCRIPTION_PERIOD_TYPE_MONTH,
                                                                        )

        self.subscription_type0 = models.SubscriptionType.objects.create(title='Subscription type', period_points=1,
                                                                        max_products=2,
                                                                        price=0,
                                                                        period_type=models.SUBSCRIPTION_PERIOD_TYPE_MONTH,
                                                                        )


        models.Subscription.objects.all().delete()
        response = self.client.post(reverse('discount:login'), {'login': 'alex', 'password':'top_secret'})
        #self.factory = RequestFactory()


        #self.subscription = models.Subscription.objects.create(start_date=self.today,
        #                                                           end_date=self.today + timezone.timedelta(days=30),
        #                                                           user=self.user,
        #                                                           shop=self.shop,
        #                                                           subscription_type=self.self.subscription_type0,
        #                                                           )

    def test_can_activate_free_subscription_without_money(self):
        subs = self.user.active_subscription
        self.assertEquals(subs, None)

        response = self.client.post(reverse('discount:subscription-confirm'), data={
            'subscription-pk': self.subscription_type0.pk,
            'action-type': 'confirm-now',

                                                                                    },)
                                    #follow=True)

        self.assertEqual(response.status_code, 302)

        subs = self.user.active_subscription
        self.assertEquals(subs.subscription_type.pk, self.subscription_type0.pk)

    def test_cant_activate_payed_subscription_without_money(self):
        subs = self.user.active_subscription
        self.assertEquals(subs, None)

        try:
            response = self.client.post(reverse('discount:subscription-confirm'), data={
                'subscription-pk': self.subscription_type1.pk,
                'action-type': 'confirm-now',

                                                                                },)

        except models.MoneyExeption:
            pass

        subs = self.user.active_subscription
        self.assertEquals(subs, None)

    def test_can_activate_payed_subscription_with_money(self):
        with self.settings(PAYMENT_USER_ID=self.user.pk):
            self.assertEquals(self.shop.points_free, 0)
            self.assertEquals(self.shop.points_total, 0)
            models.Payment.increase(self.shop, self.user, self.subscription_type1.price)
            self.assertEquals(self.shop.points_free, self.subscription_type1.price)
            self.assertEquals(self.shop.points_total, self.subscription_type1.price)

            subs = self.user.active_subscription
            self.assertEquals(subs, None)

            response = self.client.get(reverse('discount:subscription-confirm-now', kwargs={'pk': self.subscription_type1.pk}))

            to_pay_confirmed = response.context_data['to_pay']


            try:
                response = self.client.post(reverse('discount:subscription-confirm'), data={
                    'subscription-pk': self.subscription_type1.pk,
                    'action-type': 'confirm-now',
                    'to-pay': to_pay_confirmed,

                                                                                    },)

            except models.MoneyExeption:
                self.assertTrue(False)

            subs = self.user.active_subscription
            self.assertEquals(subs.subscription_type.pk, self.subscription_type1.pk)

            self.assertEquals(self.shop.points_free, 0)
            self.assertEquals(self.shop.points_total, 0)


    def test_cant_activate_payed_subscription_with_money_but_blocked(self):
        with self.settings(PAYMENT_USER_ID=self.user.pk):
            self.assertEquals(self.shop.points_free, 0)
            self.assertEquals(self.shop.points_total, 0)
            sum = max(self.subscription_type1.price, settings.ACTION_TYPE_CATEGORY_COST * 2)
            models.Payment.increase(self.shop, self.user, sum)
            self.assertEquals(self.shop.points_free, sum)
            self.assertEquals(self.shop.points_total, sum)
            subs = self.user.active_subscription
            self.assertEquals(subs, None)


            action_category = models.ProductAction.objects.create(start=True, start_date=self.product1.start_date + timezone.timedelta(days=2),
                                                                           end_date=self.product1.start_date + timezone.timedelta(days=3),
                                                                           action_type=models.ACTION_TYPE_CATEGORY,
                                                                           product=self.product1,
                                                                           )
            #self.product1.status = models.STATUS_PUBLISHED
            #self.product1.save()
            self.assertEquals(self.shop.points_free, 0)
            self.assertEquals(self.shop.points_total, sum)

            response = self.client.get(reverse('discount:subscription-confirm-now', kwargs={'pk': self.subscription_type1.pk}))

            to_pay_confirmed = response.context_data['to_pay']


            try:
                response = self.client.post(reverse('discount:subscription-confirm'), data={
                    'subscription-pk': self.subscription_type1.pk,
                    'action-type': 'confirm-now',
                    'to-pay': to_pay_confirmed,

                                                                                    },)

            except models.MoneyExeption:
                pass

            subs = self.user.active_subscription
            self.assertEquals(subs, None)

            self.assertEquals(self.shop.points_free, 0)
            self.assertEquals(self.shop.points_total, sum)

    def test_can_change_from_cheap_subscription_to_expensive_with_money_and_inactive_product(self):
        with self.settings(PAYMENT_USER_ID=self.user.pk):
            self.assertEquals(self.shop.points_free, 0)
            self.assertEquals(self.shop.points_total, 0)
            models.Payment.increase(self.shop, self.user, self.subscription_type1.price)
            self.assertEquals(self.shop.points_free, self.subscription_type1.price)
            self.assertEquals(self.shop.points_total, self.subscription_type1.price)
            subs = self.user.active_subscription
            self.assertEquals(subs, None)


            action_category = models.ProductAction.objects.create(start=False, start_date=self.product1.start_date,
                                                                           end_date=self.product1.start_date + timezone.timedelta(days=3),
                                                                           action_type=models.ACTION_TYPE_CATEGORY,
                                                                           product=self.product1,
                                                                           )
            self.assertEquals(self.shop.points_free, self.subscription_type1.price)
            self.assertEquals(self.shop.points_total, self.subscription_type1.price)

            response = self.client.get(reverse('discount:subscription-confirm-now', kwargs={'pk': self.subscription_type1.pk}))

            to_pay_confirmed = response.context_data['to_pay']


            try:
                response = self.client.post(reverse('discount:subscription-confirm'), data={
                    'subscription-pk': self.subscription_type1.pk,
                    'action-type': 'confirm-now',
                    'to-pay': to_pay_confirmed,

                                                                                    },)

            except models.MoneyExeption:
                self.assertTrue(False)

            subs = self.user.active_subscription
            self.assertEquals(subs.subscription_type, self.subscription_type1)

            self.assertEquals(self.shop.points_free, 0)
            self.assertEquals(self.shop.points_total, 0)

            subs.start_date = self.today + timezone.timedelta(days=-1)
            subs.save()
            models.Payment.increase(self.shop, self.user, 1.1 * self.subscription_type2.price - self.subscription_type1.price)

            response = self.client.get(reverse('discount:subscription-confirm-now', kwargs={'pk': self.subscription_type2.pk}))

            to_pay_confirmed = response.context_data['to_pay']
            self.assertGreater(int(to_pay_confirmed), self.subscription_type2.price - self.subscription_type1.price)
            self.assertLess(0, int(to_pay_confirmed))
            try:
                response = self.client.post(reverse('discount:subscription-confirm'), data={
                    'subscription-pk': self.subscription_type2.pk,
                    'action-type': 'confirm-now',
                    'to-pay': to_pay_confirmed,

                                                                                    },)

            except models.MoneyExeption:
                self.assertTrue(False)


            subs = self.user.active_subscription
            self.assertEquals(subs.subscription_type, self.subscription_type2)

            self.assertEquals(self.shop.points_free, self.shop.points_total)
            self.assertLess(self.shop.points_total, self.subscription_type2.price)
            self.assertLess(0, self.shop.points_total)

    def test_cant_change_from_cheap_subscription_to_expensive_without_money(self):
        with self.settings(PAYMENT_USER_ID=self.user.pk):
            self.assertEquals(self.shop.points_free, 0)
            self.assertEquals(self.shop.points_total, 0)
            models.Payment.increase(self.shop, self.user, self.subscription_type1.price)
            self.assertEquals(self.shop.points_free, self.subscription_type1.price)
            self.assertEquals(self.shop.points_total, self.subscription_type1.price)
            subs = self.user.active_subscription
            self.assertEquals(subs, None)



            self.assertEquals(self.shop.points_free, self.subscription_type1.price)
            self.assertEquals(self.shop.points_total, self.subscription_type1.price)

            response = self.client.get(reverse('discount:subscription-confirm-now', kwargs={'pk': self.subscription_type1.pk}))

            to_pay_confirmed = response.context_data['to_pay']


            try:
                response = self.client.post(reverse('discount:subscription-confirm'), data={
                    'subscription-pk': self.subscription_type1.pk,
                    'action-type': 'confirm-now',
                    'to-pay': to_pay_confirmed,

                                                                                    },)

            except models.MoneyExeption:
                self.assertTrue(False)

            subs = self.user.active_subscription
            self.assertEquals(subs.subscription_type, self.subscription_type1)

            self.assertEquals(self.shop.points_free, 0)
            self.assertEquals(self.shop.points_total, 0)

            subs.start_date = self.today + timezone.timedelta(days=-1)
            subs.save()
            models.Payment.increase(self.shop, self.user, self.subscription_type2.price - self.subscription_type1.price)

            response = self.client.get(reverse('discount:subscription-confirm-now', kwargs={'pk': self.subscription_type2.pk}))

            to_pay_confirmed = response.context_data['to_pay']
            self.assertGreater(int(to_pay_confirmed), self.subscription_type2.price - self.subscription_type1.price)
            self.assertLess(0, int(to_pay_confirmed))
            try:
                response = self.client.post(reverse('discount:subscription-confirm'), data={
                    'subscription-pk': self.subscription_type2.pk,
                    'action-type': 'confirm-now',
                    'to-pay': to_pay_confirmed,

                                                                                    },)

                caught_except = False
            except models.MoneyExeption:
                caught_except = True
            self.assertTrue(caught_except)

            subs = self.user.active_subscription
            self.assertEquals(self.subscription_type2.price - self.subscription_type1.price, self.shop.points_free)

            self.assertEquals(self.shop.points_free, self.shop.points_total)
            self.assertEquals(subs.subscription_type, self.subscription_type1)






    def test_cant_change_from_subscription_to_same(self):
        with self.settings(PAYMENT_USER_ID=self.user.pk):
            self.assertEquals(self.shop.points_free, 0)
            self.assertEquals(self.shop.points_total, 0)
            models.Payment.increase(self.shop, self.user, self.subscription_type1.price)
            self.assertEquals(self.shop.points_free, self.subscription_type1.price)
            self.assertEquals(self.shop.points_total, self.subscription_type1.price)
            subs = self.user.active_subscription
            self.assertEquals(subs, None)



            self.assertEquals(self.shop.points_free, self.subscription_type1.price)
            self.assertEquals(self.shop.points_total, self.subscription_type1.price)

            response = self.client.get(reverse('discount:subscription-confirm-now', kwargs={'pk': self.subscription_type1.pk}))

            to_pay_confirmed = response.context_data['to_pay']


            try:
                response = self.client.post(reverse('discount:subscription-confirm'), data={
                    'subscription-pk': self.subscription_type1.pk,
                    'action-type': 'confirm-now',
                    'to-pay': to_pay_confirmed,

                                                                                    },)

            except models.MoneyExeption:
                self.assertTrue(False)

            subs = self.user.active_subscription
            self.assertEquals(subs.subscription_type, self.subscription_type1)

            self.assertEquals(self.shop.points_free, 0)
            self.assertEquals(self.shop.points_total, 0)

            subs.start_date = self.today + timezone.timedelta(days=-1)
            subs.save()
            models.Payment.increase(self.shop, self.user, self.subscription_type1.price)

            response = self.client.get(reverse('discount:subscription-confirm-now', kwargs={'pk': self.subscription_type1.pk}))

            to_pay_confirmed = response.context_data['to_pay']

            try:
                response = self.client.post(reverse('discount:subscription-confirm'), data={
                    'subscription-pk': self.subscription_type1.pk,
                    'action-type': 'confirm-now',
                    'to-pay': to_pay_confirmed,

                                                                                    },)


            except:
                self.assertTrue(False)

            subs = self.user.active_subscription
            self.assertEquals(self.subscription_type1.price, self.shop.points_free)

            self.assertEquals(self.shop.points_free, self.shop.points_total)
            self.assertEquals(subs.subscription_type, self.subscription_type1)

    def test_cant_activate_free_subscription_often_and_can_in_time(self):
        subs = self.user.active_subscription
        self.assertEquals(subs, None)

        response = self.client.post(reverse('discount:subscription-confirm'), data={
            'subscription-pk': self.subscription_type0.pk,
            'action-type': 'confirm-now',

                                                                                    },)
                                    #follow=True)

        self.assertEqual(response.status_code, 302)

        subs = self.user.active_subscription
        self.assertEquals(subs.subscription_type.pk, self.subscription_type0.pk)

        subs.start_date = self.today + timezone.timedelta(days=-settings.REPEATED_FREE_SUBSCRIPTION_INTERVAL)
        subs.end_date = subs.start_date + timezone.timedelta(days=5)

        subs.save()
        subs = self.user.active_subscription
        self.assertEquals(subs, None)
        response = self.client.post(reverse('discount:subscription-confirm'), data={
            'subscription-pk': self.subscription_type0.pk,
            'action-type': 'confirm-now',

                                                                                    },)


        subs = self.user.active_subscription
        self.assertEquals(subs.subscription_type, self.subscription_type0)


        subs.start_date = self.today + timezone.timedelta(days=-settings.REPEATED_FREE_SUBSCRIPTION_INTERVAL+1)
        subs.end_date = subs.start_date + timezone.timedelta(days=5)

        subs.save()
        subs = self.user.active_subscription
        self.assertEquals(subs, None)
        response = self.client.post(reverse('discount:subscription-confirm'), data={
            'subscription-pk': self.subscription_type0.pk,
            'action-type': 'confirm-now',

                                                                                    },)


        subs = self.user.active_subscription
        self.assertEquals(subs, None)





class MoveCartTest(BaseTest):
    def setUp(self):
        super().setUp()
        s = self.client.session
        s["expire_date"] = '2050-12-05'
        s["session_key"] = 'test_session_key'
        s.save()



        self.subscription_type = models.SubscriptionType.objects.create(title='Subscription type', period_points=1,
                                                                        max_products=3,
                                                                        price=100,
                                                                        period_type=models.SUBSCRIPTION_PERIOD_TYPE_MONTH,
                                                                        )


        models.Subscription.objects.create(start_date=self.today,
                                                               end_date=self.today + timezone.timedelta(days=30),
                                                               user=self.user,
                                                               shop=self.shop,
                                                               subscription_type=self.subscription_type,
                                                               )

        self.product1.status = models.STATUS_TO_APPROVE
        self.product2.status = models.STATUS_TO_APPROVE
        self.product3.status = models.STATUS_TO_APPROVE
        self.product1.save()
        self.product2.save()
        self.product3.save()


        self.product1.status = models.STATUS_APPROVED
        self.product2.status = models.STATUS_APPROVED
        self.product3.status = models.STATUS_APPROVED
        self.product1.save()
        self.product2.save()
        self.product3.save()


        self.product1.status = models.STATUS_PUBLISHED
        self.product2.status = models.STATUS_PUBLISHED
        self.product3.status = models.STATUS_PUBLISHED
        self.product1.save()
        self.product2.save()
        self.product3.save()



    def test_guest_can_add_published_products_to_cart_and_can_move_it_to_user_on_simple_signup(self):
        #self.client.post(reverse('discount:login'), {'login': 'alex', 'password':'top_secret'})
        self.assertEquals(self.product1.status, models.STATUS_PUBLISHED)
        response = self.client.post(reverse('discount:ptc-add', kwargs={'pk': self.product1.pk}), {'submit-type': 'add'})
        ptc1 = self.product1.find_ptc_by_request(response.wsgi_request)
        response = self.client.post(reverse('discount:ptc-add', kwargs={'pk': self.product2.pk}), {'submit-type': 'add'})
        ptc2 = self.product1.find_ptc_by_request(response.wsgi_request)
        all_ptc = models.ProductToCart.objects.all()
        self.assertEquals(all_ptc.count(), 2)
        self.assertEquals(ptc1.status, models.PTC_STATUS_CART)
        self.assertEquals(ptc2.status, models.PTC_STATUS_CART)



        response = self.client.post(reverse('discount:signup'), {'username': 'tester', 'email': 'tester@tester.ru',
                                                     'password1':'1234567',
                                                     'password2':'1234567',
                                                     }
                                 )
        ptc1 = ptc1.saved_version
        ptc2 = ptc1.saved_version

        self.assertEquals(ptc1.user, response.wsgi_request.user)
        self.assertEquals(ptc2.user, response.wsgi_request.user)
        self.assertEquals(all_ptc.count(), 2)
        self.assertEquals(ptc1.status, models.PTC_STATUS_CART)
        self.assertEquals(ptc2.status, models.PTC_STATUS_CART)


    def test_guest_can_add_published_products_to_cart_and_can_move_it_to_user_on_cart_signup_than_logout_and_add_another(self):
        #self.client.post(reverse('discount:login'), {'login': 'alex', 'password':'top_secret'})
        self.assertEquals(self.product1.status, models.STATUS_PUBLISHED)
        response = self.client.post(reverse('discount:ptc-add', kwargs={'pk': self.product1.pk}), {'submit-type': 'add'})
        ptc1 = self.product1.find_ptc_by_request(response.wsgi_request)
        response = self.client.post(reverse('discount:ptc-add', kwargs={'pk': self.product2.pk}), {'submit-type': 'add'})
        ptc2 = self.product1.find_ptc_by_request(response.wsgi_request)
        all_ptc = models.ProductToCart.objects.all()
        self.assertEquals(all_ptc.count(), 2)
        self.assertEquals(ptc1.status, models.PTC_STATUS_CART)
        self.assertEquals(ptc2.status, models.PTC_STATUS_CART)



        response = self.client.post(reverse('discount:cart-signup'), {'username': 'tester', 'email': 'tester@tester.ru',
                                                     'password1':'1234567',
                                                     'password2':'1234567',
                                                     }
                                 )
        user = models.User.objects.get(username='tester')
        ptc1 = ptc1.saved_version
        ptc2 = ptc1.saved_version
        mails = models.ProductMail.objects.filter(user=user)
        self.assertEqual(mails.count(),2)
        self.assertEquals(ptc1.user, response.wsgi_request.user)
        self.assertEquals(ptc2.user, response.wsgi_request.user)
        self.assertEquals(all_ptc.count(), 2)
        self.assertEquals(ptc1.status, models.PTC_STATUS_SUBSCRIBED)
        self.assertEquals(ptc2.status, models.PTC_STATUS_SUBSCRIBED)

        response = self.client.get(reverse('account_logout'))
        ptc1 = self.product1.find_ptc_by_request(response.wsgi_request)
        ptc2 = self.product2.find_ptc_by_request(response.wsgi_request)
        self.assertEquals(ptc1, None)
        self.assertEquals(ptc2, None)

        response2 = self.client.post(reverse('discount:ptc-add', kwargs={'pk': self.product2.pk}), {'submit-type': 'add'})
        ptc2 = self.product2.find_ptc_by_request(response2.wsgi_request)
        response3 = self.client.post(reverse('discount:ptc-add', kwargs={'pk': self.product3.pk}), {'submit-type': 'add'})
        ptc3 = self.product3.find_ptc_by_request(response3.wsgi_request)
        self.assertEquals(ptc2.status, models.PTC_STATUS_CART)
        self.assertEquals(ptc3.status, models.PTC_STATUS_CART)
        all_ptc = models.ProductToCart.objects.all()
        self.assertEquals(all_ptc.count(), 4)

        response = self.client.post(reverse('discount:login'), {'login': 'tester', 'password': '1234567'})
        user = response.wsgi_request.user
        self.assertEquals(user.is_authenticated(), True)
        all_ptc = models.ProductToCart.objects.all()
        self.assertEquals(all_ptc.count(), 3)
        mails = models.ProductMail.objects.filter(user=user)
        self.assertEqual(mails.count(),2)
        subscribed_ptc = models.ProductToCart.objects.filter(status=models.PTC_STATUS_SUBSCRIBED)
        self.assertEquals(subscribed_ptc.count(), 2)
        cart_ptc = models.ProductToCart.objects.filter(status=models.PTC_STATUS_CART)
        self.assertEquals(cart_ptc.count(), 1)
        user_ptc = models.ProductToCart.objects.filter(user=user)
        self.assertEquals(user_ptc.count(), 3)



    def test_user_can_make_instant_subscribe_and_mails_are_sent(self):
        with self.settings(REPEATED_LETTER_INTERVAL=0):
            response = self.client.post(reverse('discount:signup'), {'username': 'tester', 'email': 'tester@tester.ru',
                                                         'password1':'1234567',
                                                         'password2':'1234567',
                                                         })
            self.assertEquals(self.product1.status, models.STATUS_PUBLISHED)
            self.assertEquals(self.product2.status, models.STATUS_PUBLISHED)
            response = self.client.post(reverse('discount:ptc-subscribe', kwargs={'pk': self.product1.pk}), {'submit-type': 'subscribe'})
            ptc1 = self.product1.find_ptc_by_request(response.wsgi_request)
            response = self.client.post(reverse('discount:ptc-subscribe', kwargs={'pk': self.product2.pk}), {'submit-type': 'subscribe'})
            ptc2 = self.product1.find_ptc_by_request(response.wsgi_request)
            all_ptc = models.ProductToCart.objects.all()
            self.assertEquals(all_ptc.count(), 2)
            self.assertEquals(ptc1.status, models.PTC_STATUS_SUBSCRIBED)
            self.assertEquals(ptc2.status, models.PTC_STATUS_SUBSCRIBED)
            user = response.wsgi_request.user
            user_ptc = models.ProductToCart.objects.filter(user=user)
            self.assertEquals(user_ptc.count(), 2)
            mails = models.ProductMail.objects.filter(user=user)
            self.assertEquals(mails.count(), 2)
            models.ProductMail.send_message_for_all_changed_products()
            mails = models.ProductMail.objects.filter(user=user)
            self.assertEquals(mails.count(), 2)
            self.product1.status = models.STATUS_FINISHED
            self.product1.save()
            models.ProductMail.send_message_for_all_changed_products()
            mails = models.ProductMail.objects.filter(user=user)
            self.assertEquals(mails.count(), 3)
            mails = models.ProductMail.objects.filter(user=user)
            self.assertEquals(mails.count(), 3)

    def test_user_bought_or_cancelled_ptc_and_added_it_again_as_guest_status_doesnt_change(self):
        response = self.client.post(reverse('discount:signup'), {'username': 'tester', 'email': 'tester@tester.ru',
                                                         'password1':'1234567',
                                                         'password2':'1234567',
                                                         })
        self.assertEquals(self.product1.status, models.STATUS_PUBLISHED)
        self.assertEquals(self.product2.status, models.STATUS_PUBLISHED)
        response = self.client.post(reverse('discount:ptc-subscribe', kwargs={'pk': self.product1.pk}), {'submit-type': 'subscribe'})
        ptc1 = self.product1.find_ptc_by_request(response.wsgi_request)
        response = self.client.post(reverse('discount:ptc-subscribe', kwargs={'pk': self.product2.pk}), {'submit-type': 'subscribe'})
        ptc2 = self.product1.find_ptc_by_request(response.wsgi_request)
        all_ptc = models.ProductToCart.objects.all()
        self.assertEquals(all_ptc.count(), 2)

        response1 = self.client.post(reverse('discount:ptc-subscribe', kwargs={'pk': self.product1.pk}), {'submit-type': 'unsubscribe', 'reason': 1, 'comment': 'sample comment'})
        ptc1 = self.product1.find_ptc_by_request(response1.wsgi_request)
        response2 = self.client.post(reverse('discount:ptc-subscribe', kwargs={'pk': self.product2.pk}), {'submit-type': 'unsubscribe', 'reason': 2, 'comment': 'sample comment'})
        ptc2 = self.product2.find_ptc_by_request(response2.wsgi_request)
        #self.assertNotEquals(ptc2.pk, ptc2.pk)
        self.assertEquals(ptc1.status, models.PTC_STATUS_BOUGHT)
        self.assertEquals(ptc2.status, models.PTC_STATUS_CANCELLED)

        response = self.client.get(reverse('account_logout'))
        user = response.wsgi_request.user
        self.assertEquals(user.is_authenticated(), False)
        response1 = self.client.post(reverse('discount:ptc-add', kwargs={'pk': self.product1.pk}), {'submit-type': 'add'})
        ptc1 = self.product1.find_ptc_by_request(response1.wsgi_request)
        response2 = self.client.post(reverse('discount:ptc-add', kwargs={'pk': self.product2.pk}), {'submit-type': 'add'})
        ptc2 = self.product2.find_ptc_by_request(response2.wsgi_request)
        self.assertEquals(ptc1.status, models.PTC_STATUS_CART)
        self.assertEquals(ptc2.status, models.PTC_STATUS_CART)


        response = self.client.post(reverse('discount:login'), {'login': 'tester', 'password': '1234567'})
        user = response.wsgi_request.user
        self.assertEquals(user.is_authenticated(), True)
        all_ptc = models.ProductToCart.objects.all()
        self.assertEquals(all_ptc.count(), 2)
        subscribed_ptc = models.ProductToCart.objects.filter(status=models.PTC_STATUS_SUBSCRIBED)
        self.assertEquals(subscribed_ptc.count(), 0)
        cart_ptc = models.ProductToCart.objects.filter(status=models.PTC_STATUS_CART)
        self.assertEquals(cart_ptc.count(), 0)
        bought_ptc = models.ProductToCart.objects.filter(status=models.PTC_STATUS_BOUGHT)
        self.assertEquals(bought_ptc.count(), 1)
        bought_ptc = models.ProductToCart.objects.filter(status=models.PTC_STATUS_CANCELLED)
        self.assertEquals(bought_ptc.count(), 1)
        user_ptc = models.ProductToCart.objects.filter(user=user)
        self.assertEquals(user_ptc.count(), 2)

    def test_user_can_bring_back_cancelled_action(self):
        response = self.client.post(reverse('discount:signup'), {'username': 'tester', 'email': 'tester@tester.ru',
                                                         'password1':'1234567',
                                                         'password2':'1234567',
                                                         })
        self.assertEquals(self.product1.status, models.STATUS_PUBLISHED)
        self.assertEquals(self.product2.status, models.STATUS_PUBLISHED)
        response = self.client.post(reverse('discount:ptc-subscribe', kwargs={'pk': self.product1.pk}), {'submit-type': 'subscribe'})
        ptc = self.product1.find_ptc_by_request(response.wsgi_request)
        self.assertEquals(ptc.status, models.PTC_STATUS_SUBSCRIBED)
        response = self.client.post(reverse('discount:ptc-subscribe', kwargs={'pk': self.product1.pk}), {'submit-type': 'unsubscribe', 'reason': 2, 'comment': 'sample comment'})
        ptc = self.product1.find_ptc_by_request(response.wsgi_request)
        self.assertEquals(ptc.status, models.PTC_STATUS_CANCELLED)
        response = self.client.post(reverse('discount:ptc-subscribe', kwargs={'pk': self.product1.pk}), {'submit-type': 'subscribe'})
        ptc = self.product1.find_ptc_by_request(response.wsgi_request)
        self.assertEquals(ptc.status, models.PTC_STATUS_SUBSCRIBED)

    def test_user_can_use_instant_ptc(self):
        response = self.client.post(reverse('discount:ptc-subscribe', kwargs={'pk': self.product1.pk}), {'submit-type': 'first_subscribe'})
        ptc1 = self.product1.find_ptc_by_request(response.wsgi_request)
        response = self.client.post(reverse('discount:ptc-subscribe', kwargs={'pk': self.product2.pk}), {'submit-type': 'first_subscribe'})
        ptc2 = self.product2.find_ptc_by_request(response.wsgi_request)
        all_ptc = models.ProductToCart.objects.all()
        self.assertEquals(all_ptc.count(), 1)
        ptc2 = ptc2.saved_version
        self.assertEquals(ptc2.status, models.PTC_STATUS_INSTANT)
        response = self.client.get(reverse('discount:instant-cart-view'))
        self.assertEquals(all_ptc.count(), 1)
        response = self.client.get(reverse('discount:cart-view'))
        self.assertEquals(all_ptc.count(), 1)
        response = self.client.post(reverse('discount:cart-signup'), {'username': 'tester', 'email': 'tester@tester.ru',
                                                     'password1':'1234567',
                                                     'password2':'1234567',
                                                     })

        ptc2 = ptc2.saved_version
        self.assertEquals(ptc2.status, models.PTC_STATUS_SUBSCRIBED)
        all_ptc = models.ProductToCart.objects.all()
        self.assertEquals(all_ptc.count(), 1)

    def test_user_ptc_saved_on_logout_and_restored_on_login(self):
        response = self.client.post(reverse('discount:login'), {'login': 'alex1', 'password': 'top_secret1'})
        response1 = self.client.post(reverse('discount:ptc-add', kwargs={'pk': self.product1.pk}), {'submit-type': 'add'})
        ptc1 = self.product1.find_ptc_by_request(response1.wsgi_request)
        response2 = self.client.post(reverse('discount:ptc-add', kwargs={'pk': self.product2.pk}), {'submit-type': 'add'})
        ptc_count = models.ProductToCart.objects.all().count()
        self.assertEquals(ptc_count, 2)
        response2 = self.client.post(reverse('discount:ptc-add', kwargs={'pk': self.product2.pk}), {'submit-type': 'remove'})
        ptc_count = models.ProductToCart.objects.all().count()
        self.assertEquals(ptc_count, 1)
        response2 = self.client.post(reverse('discount:ptc-add', kwargs={'pk': self.product2.pk}), {'submit-type': 'add'})
        ptc_count = models.ProductToCart.objects.all().count()
        self.assertEquals(ptc_count, 2)
        ptc2 = self.product2.find_ptc_by_request(response2.wsgi_request)
        self.assertEquals(ptc1.status, models.PTC_STATUS_CART)
        self.assertEquals(ptc2.status, models.PTC_STATUS_CART)
        response = self.client.get(reverse('account_logout'))
        ptc1 = self.product1.find_ptc_by_request(response.wsgi_request)
        ptc2 = self.product1.find_ptc_by_request(response.wsgi_request)
        self.assertEquals(ptc1, None)
        self.assertEquals(ptc2, None)
        response = self.client.post(reverse('discount:login'), {'login': 'alex1', 'password': 'top_secret1'})
        ptc1 = self.product1.find_ptc_by_request(response.wsgi_request)
        ptc2 = self.product1.find_ptc_by_request(response.wsgi_request)
        self.assertEquals(ptc1.status, models.PTC_STATUS_CART)
        self.assertEquals(ptc2.status, models.PTC_STATUS_CART)
        ptc_count = models.ProductToCart.objects.all().count()
        self.assertEquals(ptc_count, 2)
        response = self.client.get(reverse('account_logout'))
        response1 = self.client.post(reverse('discount:ptc-add', kwargs={'pk': self.product1.pk}), {'submit-type': 'add'})
        response1 = self.client.post(reverse('discount:ptc-add', kwargs={'pk': self.product2.pk}), {'submit-type': 'add'})
        response1 = self.client.post(reverse('discount:ptc-add', kwargs={'pk': self.product3.pk}), {'submit-type': 'add'})
        ptc_count = models.ProductToCart.objects.all().count()
        self.assertEquals(ptc_count, 5)
        response = self.client.post(reverse('discount:login'), {'login': 'alex1', 'password': 'top_secret1'})
        user = response.wsgi_request.user
        ptc_count = models.ProductToCart.objects.all().count()
        self.assertEquals(ptc_count, 3)
        user_ptc_count = models.ProductToCart.objects.filter(user=user).count()
        self.assertEquals(user_ptc_count, 3)


    def test_shop_manager_cannot_subscribe_and_move_from_guest_cart(self):
        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': self.product1.pk}))
        form = page.forms['ptc-add-form-{0}'.format(self.product1.pk)]
        page = form.submit(name='add')
        ptc = models.ProductToCart.objects.all().latest('created')
        #self.renew_app()
        page = self.app.get(reverse('discount:full-login'))
        form = page.forms['login-form']
        form['login'] = self.user.username
        form['password'] = self.user_password
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        try:
            ptc = ptc.saved_version
        except:
            ptc = None
        self.assertEqual(ptc, None)

    def test_ptcs_with_code_is_not_deleted(self):
        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': self.product1.pk}))
        form = page.forms['ptc-add-form-{0}'.format(self.product1.pk)]
        page = form.submit(name='add')
        ptc = models.ProductToCart.objects.all().latest('created')
        #self.renew_app()
        page = self.app.get(reverse('discount:full-login'))
        form = page.forms['login-form']
        form['login'] = self.simple_user.username
        form['password'] = self.simple_user_password
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        ptc = ptc.saved_version
        self.assertEqual(ptc.status, models.PTC_STATUS_CART)
        self.assertEqual(ptc.user, self.simple_user)


    def test_code_is_generated_on_ptc_subscribe(self):
        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': self.product1.pk}))
        form = page.forms['ptc-add-form-{0}'.format(self.product1.pk)]
        page = form.submit(name='add')
        ptc = models.ProductToCart.objects.all().latest('created')
        #self.renew_app()
        page = self.app.get(reverse('discount:full-login'))
        form = page.forms['login-form']
        form['login'] = self.simple_user.username
        form['password'] = self.simple_user_password
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        ptc = ptc.saved_version
        self.assertEqual(ptc.status, models.PTC_STATUS_CART)
        self.assertEqual(ptc.user, self.simple_user)
        self.assertEqual(ptc.code, None)

        page = self.app.get(reverse('discount:cart-view'))
        form = page.forms['cart-form']
        page = form.submit()

        ptc = ptc.saved_version
        self.assertEqual(ptc.status, models.PTC_STATUS_SUBSCRIBED)
        self.assertEqual(ptc.user, self.simple_user)
        self.assertEqual(ptc.code, 1)

        u1 = User.objects.create_user(
            username='addisdftionaasdfldsf', email='sdfno@fdsfsd.ru', password='top_secresdft')

        self.renew_app()

        page = self.app.get(reverse('discount:full-login'))
        form = page.forms['login-form']
        form['login'] = 'addisdftionaasdfldsf'
        form['password'] = 'top_secresdft'
        page = form.submit()
        self.assertEqual(page.status_code, 302)

        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': self.product1.pk}), user=u1)
        form = page.forms['ptc-subscribe-form-{0}'.format(self.product1.pk)]
        form['submit-type'] = 'subscribe'
        page = form.submit()
        ptc = models.ProductToCart.objects.all().latest('created')
        #self.renew_app()

        ptc = ptc.saved_version
        self.assertEqual(ptc.status, models.PTC_STATUS_SUBSCRIBED)
        self.assertEqual(ptc.user, u1)
        self.assertEqual(ptc.code, 2)





class ProductVersionsTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.subscription_type = models.SubscriptionType.objects.create(title='Subscription type', period_points=1,
                                                                        max_products=3,
                                                                        price=100,
                                                                        period_type=models.SUBSCRIPTION_PERIOD_TYPE_MONTH,
                                                                        )


        models.Subscription.objects.create(start_date=self.today,
                                                               end_date=self.today + timezone.timedelta(days=30),
                                                               user=self.user,
                                                               shop=self.shop,
                                                               subscription_type=self.subscription_type,
                                                               )


        self.product1.status = models.STATUS_TO_APPROVE
        self.product2.status = models.STATUS_TO_APPROVE
        self.product3.status = models.STATUS_TO_APPROVE
        self.product1.save()
        self.product2.save()
        self.product3.save()

        self.product1.status = models.STATUS_APPROVED
        self.product2.status = models.STATUS_APPROVED
        self.product3.status = models.STATUS_APPROVED
        self.product1.save()
        self.product2.save()
        self.product3.save()

        self.product1.status = models.STATUS_PUBLISHED
        self.product2.status = models.STATUS_PUBLISHED
        self.product3.status = models.STATUS_PUBLISHED
        self.product1.save()
        self.product2.save()
        self.product3.save()

        self.color_red = models.FilterValue.objects.create(title='Красный', filter_type=models.FILTER_TYPE_COLOR)
        self.color_green = models.FilterValue.objects.create(title='Зеленый', filter_type=models.FILTER_TYPE_COLOR)

        self.dress_size_42 = models.FilterValue.objects.create(title='42', filter_type=models.FILTER_TYPE_SIZE_WOMAN)
        self.dress_size_44 = models.FilterValue.objects.create(title='44', filter_type=models.FILTER_TYPE_SIZE_WOMAN)

        self.product1.filter_values.add(self.color_green)
        models.FilterValueToProductType.objects.create(product_type=self.pt3, filter_type=models.FILTER_TYPE_COLOR)


    def test_messages_and_changes_full_cycle_test(self):
        #Купон и почта показываются относительно исходной акции, но изменения приходят относительно последней.
        with self.settings(REPEATED_LETTER_INTERVAL=0):
            messages = models.ProductMail.objects.all()
            self.assertEquals(messages.count(), 0)
            response = self.client.post(reverse('discount:login'), {'login': 'alex1', 'password': 'top_secret1'})
            user = response.wsgi_request.user
            self.assertEquals(user.is_authenticated(), True)
            all_messages = models.ProductMail.objects.all()
            self.assertEquals(all_messages.count(), 0)
            json_response = self.client.post(reverse('discount:ptc-subscribe', kwargs={'pk': self.product1.pk}), {'submit-type': 'subscribe'})
            all_messages = models.ProductMail.objects.all()
            self.assertEquals(all_messages.count(), 1)
            response = self.client.get(reverse('discount:coupon-view', kwargs={'pk': self.product1.pk, 'type': 'normal'}))
            self.assertEquals(response.status_code, 200)
            content = response.content.decode()
            self.assertEquals('added' in content, False)
            self.assertEquals('removed' in content, False)
            self.assertEquals('unchanged' in content, True)

            changed_fields = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=False)
            self.assertNotIn('status', changed_fields)
            self.assertNotIn('filter_values', changed_fields)
            self.assertNotIn('end_date', changed_fields)
            changed_fields1 = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=True)
            self.assertEquals(changed_fields, changed_fields1)

            self.product1.filter_values.remove(self.color_green)
            self.product1.filter_values.add(self.color_red)

            response = self.client.get(reverse('discount:coupon-view', kwargs={'pk': self.product1.pk, 'type': 'normal'}))
            changed_fields = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=False)
            self.assertNotIn('status', changed_fields)
            self.assertIn('filter_values', changed_fields)
            self.assertNotIn('end_date', changed_fields)
            self.assertEquals(response.status_code, 200)
            content = response.content.decode()
            self.assertEquals('added' in content, True)
            self.assertEquals('removed' in content, True)
            changed_fields1 = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=True)
            self.assertNotIn('status', changed_fields1)
            self.assertIn('filter_values', changed_fields1)
            self.assertNotIn('end_date', changed_fields1)

            messages = models.ProductMail.objects.all()
            self.assertEquals(messages.count(), 1)

            models.ProductMail.send_message_for_all_changed_products()
            messages = models.ProductMail.objects.all()
            self.assertEquals(messages.count(), 2)
            response = self.client.get(reverse('discount:coupon-view', kwargs={'pk': self.product1.pk, 'type': 'normal'}))
            self.assertEquals(response.status_code, 200)
            content = response.content.decode()
            self.assertEquals('added' in content, True)
            self.assertEquals('removed' in content, True)
            changed_fields = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=False)
            self.assertNotIn('status', changed_fields)
            self.assertNotIn('filter_values', changed_fields)
            changed_fields2 = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=True)
            self.assertEquals(changed_fields1, changed_fields2)

            self.product1.end_date += timezone.timedelta(days=1)
            self.product1.save()
            response = self.client.get(reverse('discount:coupon-view', kwargs={'pk': self.product1.pk, 'type': 'normal'}))
            changed_fields = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=False)
            self.assertNotIn('status', changed_fields)
            self.assertNotIn('filter_values', changed_fields)
            self.assertIn('end_date', changed_fields)
            self.assertEquals(response.status_code, 200)
            content = response.content.decode()
            self.assertEquals('added' in content, True)
            self.assertEquals('removed' in content, True)
            self.assertIn('Предыдущее значение', content)
            changed_fields2 = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=True)
            self.assertNotIn('status', changed_fields2)
            self.assertIn('filter_values', changed_fields2)
            self.assertIn('end_date', changed_fields2)


            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 3)
            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 3)


            self.product1.status = models.STATUS_SUSPENDED
            self.product1.end_date -= timezone.timedelta(days=1)
            self.product1.save()
            response = self.client.get(reverse('discount:coupon-view', kwargs={'pk': self.product1.pk, 'type': 'normal'}))
            changed_fields = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=False)
            self.assertIn('status', changed_fields)
            self.assertNotIn('filter_values', changed_fields)
            self.assertIn('end_date', changed_fields)
            self.assertEquals(response.status_code, 200)
            content = response.content.decode()
            self.assertEquals('added' in content, True)
            self.assertEquals('removed' in content, True)
            self.assertIn('Предыдущее значение', content)
            changed_fields1 = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=True)
            self.assertIn('status', changed_fields1)
            self.assertIn('filter_values', changed_fields1)
            self.assertNotIn('end_date', changed_fields1)


            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 4)
            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 4)


            self.product1.end_date += timezone.timedelta(days=1)
            self.product1.save()
            response = self.client.get(reverse('discount:coupon-view', kwargs={'pk': self.product1.pk, 'type': 'normal'}))
            changed_fields = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=False)
            self.assertNotIn('status', changed_fields)
            self.assertNotIn('filter_values', changed_fields)
            self.assertIn('end_date', changed_fields)
            self.assertEquals(response.status_code, 200)
            content = response.content.decode()
            self.assertEquals('added' in content, True)
            self.assertEquals('removed' in content, True)
            self.assertIn('Предыдущее значение', content)

            changed_fields1 = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=True)
            self.assertIn('status', changed_fields1)
            self.assertIn('filter_values', changed_fields1)
            self.assertIn('end_date', changed_fields1)


            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 4)
            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 4)



            self.product1.end_date += timezone.timedelta(days=1)
            self.product1.status = models.STATUS_PUBLISHED
            self.product1.save()
            response = self.client.get(reverse('discount:coupon-view', kwargs={'pk': self.product1.pk, 'type': 'normal'}))
            changed_fields = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=False)
            self.assertIn('status', changed_fields)
            self.assertNotIn('filter_values', changed_fields)
            self.assertIn('end_date', changed_fields)
            self.assertEquals(response.status_code, 200)
            content = response.content.decode()
            self.assertEquals('added' in content, True)
            self.assertEquals('removed' in content, True)
            self.assertIn('Предыдущее значение', content)

            changed_fields1 = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=True)
            self.assertNotIn('status', changed_fields1)
            self.assertIn('filter_values', changed_fields1)
            self.assertIn('end_date', changed_fields1)

            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 5)
            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 5)




            self.product1.filter_values.add(self.color_green)
            self.product1.filter_values.remove(self.color_red)
            #self.product1.save()
            response = self.client.get(reverse('discount:coupon-view', kwargs={'pk': self.product1.pk, 'type': 'normal'}))
            changed_fields = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=False)
            self.assertNotIn('status', changed_fields)
            self.assertIn('filter_values', changed_fields)
            self.assertNotIn('end_date', changed_fields)
            self.assertEquals(response.status_code, 200)
            content = response.content.decode()
            self.assertEquals('added' in content, False)
            self.assertEquals('removed' in content, False)
            self.assertIn('Предыдущее значение', content)

            changed_fields1 = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=True)
            self.assertNotIn('status', changed_fields1)
            self.assertNotIn('filter_values', changed_fields1)
            self.assertIn('end_date', changed_fields1)




            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 6)
            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 6)


            self.product1.end_date = self.product2.end_date
            self.product1.save()
            response = self.client.get(reverse('discount:coupon-view', kwargs={'pk': self.product1.pk, 'type': 'normal'}))
            changed_fields = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=False)
            self.assertNotIn('status', changed_fields)
            self.assertNotIn('filter_values', changed_fields)
            self.assertIn('end_date', changed_fields)
            self.assertEquals(response.status_code, 200)
            content = response.content.decode()
            self.assertEquals('added' in content, False)
            self.assertEquals('removed' in content, False)
            self.assertNotIn('Предыдущее значение', content)

            changed_fields1 = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=True)
            self.assertNotIn('status', changed_fields1)
            self.assertNotIn('filter_values', changed_fields1)
            self.assertNotIn('end_date', changed_fields1)

            self.assertEquals(messages.count(), 6)
            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 7)
            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 7)

            self.product1.status = models.STATUS_FINISHED
            self.product1.save()
            response = self.client.get(reverse('discount:coupon-view', kwargs={'pk': self.product1.pk, 'type': 'normal'}))
            changed_fields = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=False)
            self.assertIn('status', changed_fields)
            self.assertNotIn('filter_values', changed_fields)
            self.assertIn('end_date', changed_fields)
            self.assertEquals(response.status_code, 200)
            content = response.content.decode()
            self.assertEquals('added' in content, False)
            self.assertEquals('removed' in content, False)
            self.assertIn('Предыдущее значение', content)

            self.assertEquals(self.product1.end_date, self.today)

            changed_fields1 = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=True)
            self.assertIn('status', changed_fields1)
            self.assertNotIn('filter_values', changed_fields1)
            self.assertIn('end_date', changed_fields1)

            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 8)
            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 8)

            self.product1.end_date += timezone.timedelta(days=-1)
            self.product1.filter_values.remove(self.color_green)
            self.product1.save()
            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 8)

            changed_fields = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=False)
            self.assertNotIn('status', changed_fields)
            self.assertIn('filter_values', changed_fields)
            self.assertIn('end_date', changed_fields)

            changed_fields1 = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=True)
            self.assertIn('status', changed_fields1)
            self.assertIn('filter_values', changed_fields1)
            self.assertIn('end_date', changed_fields1)

            models.ProductMail.send_message_for_all_changed_products()
            self.assertEquals(messages.count(), 8)
            self.product1.filter_values.add(self.color_green)

            changed_fields = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=False)
            self.assertNotIn('status', changed_fields)
            self.assertNotIn('filter_values', changed_fields)
            self.assertIn('end_date', changed_fields)

            changed_fields1 = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=True)
            self.assertIn('status', changed_fields1)
            self.assertNotIn('filter_values', changed_fields1)
            self.assertIn('end_date', changed_fields1)


    def test_messages_simultan_messages(self):
        #Купон и почта показываются относительно исходной акции, но изменения приходят относительно последней.
        with self.settings(REPEATED_LETTER_INTERVAL=0):
            messages = models.ProductMail.objects.all()
            self.assertEquals(messages.count(), 0)
            response = self.client.post(reverse('discount:login'), {'login': 'alex1', 'password': 'top_secret1'})
            user1 = response.wsgi_request.user
            self.assertEquals(user1.is_authenticated(), True)

            all_messages = models.ProductMail.objects.all()
            self.assertEquals(all_messages.count(), 0)

            json_response = self.client.post(reverse('discount:ptc-subscribe', kwargs={'pk': self.product1.pk}), {'submit-type': 'subscribe'})

            all_messages = models.ProductMail.objects.all()
            self.assertEquals(all_messages.count(), 1)
            response = self.client.get(reverse('account_logout'))
            response = self.client.post(reverse('discount:signup'), {'username': 'alex2', 'email': '119fsd1@bsdfk.ru',
                                                     'password1':'1234567',
                                                     'password2':'1234567',
                                                     }
                                 )

            user2 = response.wsgi_request.user

            json_response = self.client.post(reverse('discount:ptc-subscribe', kwargs={'pk': self.product1.pk}), {'submit-type': 'subscribe'})
            json_response = self.client.post(reverse('discount:ptc-subscribe', kwargs={'pk': self.product2.pk}), {'submit-type': 'subscribe'})
            self.assertEquals(all_messages.count(), 3)

            self.product1.filter_values.remove(self.color_green)
            self.product1.filter_values.add(self.color_red)

            response = self.client.get(reverse('discount:coupon-view', kwargs={'pk': self.product1.pk, 'type': 'normal'}))
            changed_fields = self.product1.get_changed_fields(self.simple_user, fields=models.CHECK_FIELDS, subscribed_only=False)
            self.assertNotIn('status', changed_fields)
            self.assertIn('filter_values', changed_fields)
            self.assertNotIn('end_date', changed_fields)
            self.assertEquals(response.status_code, 200)
            content = response.content.decode()
            self.assertEquals('added' in content, True)
            self.assertEquals('removed' in content, True)

            messages = models.ProductMail.objects.all()
            self.assertEquals(messages.count(), 3)
            models.ProductMail.send_message_for_all_changed_products()
            messages = models.ProductMail.objects.all()
            self.assertEquals(messages.count(), 5)
            models.ProductMail.send_message_for_all_changed_products()
            messages = models.ProductMail.objects.all()
            self.assertEquals(messages.count(), 5)


class ProductActionsFullCycle(BaseTest):
    def test_simple_category_with_correct_data(self):
        with self.settings(PAYMENT_USER_ID=self.user.pk):
            u = models.User.objects.get(username='alex')

            models.Subscription.objects.create(start_date=self.today,
                                                               end_date=self.today + timezone.timedelta(days=30),
                                                               user=u,
                                                               shop=self.shop,
                                                               subscription_type=self.subscription_type,
                                                               )
            product = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                     start_date=self.today,
                                     end_date=self.today + timezone.timedelta(days=1),
                                     code=models.Product.generate_unique_code(), product_type=self.pt3, shop=self.shop, brand=self.brand,
                                             status=models.STATUS_TO_APPROVE,
                                     )
            product.status = models.STATUS_APPROVED
            product.save()

            product.status = models.STATUS_PUBLISHED
            product.save()

            u = models.User.objects.get(username='alex')
            models.Payment.increase(self.shop, u, settings.ACTION_TYPE_CATEGORY_COST * 2)
            page = self.app.get(reverse('discount:product-actions', kwargs={'pk': product.pk}), user=u)

            form = page.forms['product-actions-form']
            form['actions-0-action_type'] = models.ACTION_TYPE_CATEGORY
            form['actions-0-start_date'] = str(self.today)
            form['actions-0-end_date'] = str(self.today + timezone.timedelta(days=1))
            form['actions-0-start'] = True
            page = form.submit()
            self.assertEquals(page.status_code, 302)
            a = models.ProductAction.objects.latest('created')
            self.assertEquals(a.status, models.ACTION_STATUS_ACTIVE)
            self.assertEquals(self.shop.points_total, settings.ACTION_TYPE_CATEGORY_COST)
            self.assertEquals(self.shop.points_free, 0)


    def test_trying_to_make_mistake(self):
        with self.settings(PAYMENT_USER_ID=self.user.pk):
            u = models.User.objects.get(username='alex')
            models.Payment.increase(self.shop, u, settings.ACTION_TYPE_CATEGORY_COST * 2 + settings.ACTION_TYPE_POPULAR_COST * 2)

            models.Subscription.objects.create(start_date=self.today,
                                                                   end_date=self.today + timezone.timedelta(days=30),
                                                                   user=u,
                                                                   shop=self.shop,
                                                                   subscription_type=self.subscription_type,
                                                                   )
            product = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                         start_date=self.today,
                                         end_date=self.today + timezone.timedelta(days=1),
                                         code=models.Product.generate_unique_code(), product_type=self.pt3, shop=self.shop, brand=self.brand,
                                         status = models.STATUS_TO_APPROVE,
                                         )

            product.status = models.STATUS_APPROVED
            product.save()

            product.status = models.STATUS_PUBLISHED
            product.save()

            product.filter_values.add(self.color_green)
            models.ProductImage.objects.create(image='image', product=product)
            #Подписки и акции проверяются не здесь


            page = self.app.get(reverse('discount:product-banners', kwargs={'pk': product.pk}), user=u)
            form = page.forms['product-banners-form']
            f = open(TEST_IMAGE_PATH, 'rb')
            form['productbanner_set-0-banner'] = ('images-0-image', f.read())
            #form['productbanner_set-0-start'] = True
            shop_comment = 'авгыгшапвгшапрвагшпврагшпрвашгп2324пваып545н'
            form['productbanner_set-0-shop_comment'] = shop_comment

            page = form.submit()

            banner = models.ProductBanner.objects.latest('created')
            self.assertEquals(banner.shop_comment, shop_comment)
            self.assertEquals(banner.status, models.BANNER_STATUS_ON_APPROVE)
            self.assertEquals(product.productbanner_set.all().count(), 1)

            banner.status = models.BANNER_STATUS_NEED_REWORK
            banner.save()
            self.assertEquals(banner.status, models.BANNER_STATUS_NEED_REWORK)

            page = self.app.get(reverse('discount:product-banners', kwargs={'pk': product.pk}), user=u)
            shop_comment1 = shop_comment + 'dsfsdf'
            form['productbanner_set-0-shop_comment'] = shop_comment
            form['productbanner_set-1-banner'] = ('images-0-image', f.read())
            page = form.submit()
            self.assertEquals(product.productbanner_set.all().count(), 2)
            for banner in product.productbanner_set.all():
                self.assertEquals(banner.status, models.BANNER_STATUS_ON_APPROVE)
                banner.status = models.BANNER_STATUS_APPROVED
                banner.save()

            page = self.app.get(reverse('discount:product-actions', kwargs={'pk': product.pk}), user=u)

            form = page.forms['product-actions-form']
            form['actions-0-action_type'] = models.ACTION_TYPE_CATEGORY
            form['actions-0-start_date'] = str(self.today + timezone.timedelta(days=-5))
            form['actions-0-end_date'] = str(self.today + timezone.timedelta(days=33))
            form['actions-0-start'] = False
            page = form.submit()
            self.assertEquals(page.status_code, 302)
            self.assertEquals(product.actions.all().count(), 1)
            for action in product.actions.all():
                self.assertEquals(action.status, models.ACTION_STATUS_PROJECT)
                self.assertEquals(action.points_spent, 0)
                self.assertEquals(action.end_date, product.end_date)
                self.assertEquals(action.start_date, product.start_date)

            page = self.app.get(reverse('discount:product-actions', kwargs={'pk': product.pk}), user=u)
            form = page.forms['product-actions-form']
            form['actions-0-start'] = True
            form['actions-0-end_date'] = str(self.today + timezone.timedelta(days=1))
            page = form.submit()
            self.assertEquals(page.status_code, 302)
            self.assertEquals(product.actions.all().count(), 1)
            for action in product.actions.all():
                self.assertEquals(action.status, models.ACTION_STATUS_ACTIVE)
                self.assertEquals(action.points_spent, settings.ACTION_TYPE_CATEGORY_COST)
                self.assertEquals(action.points_blocked, settings.ACTION_TYPE_CATEGORY_COST)
                self.assertEquals(action.end_date, self.today + timezone.timedelta(days=1))
                self.assertEquals(action.start_date, product.start_date)

            shop = product.shop
            self.assertEquals(shop.points_blocked, settings.ACTION_TYPE_CATEGORY_COST)
            self.assertEquals(shop.points_free, settings.ACTION_TYPE_POPULAR_COST * 2)
            self.assertEquals(shop.points_total, settings.ACTION_TYPE_POPULAR_COST * 2 + settings.ACTION_TYPE_CATEGORY_COST)

            self.assertEquals(shop.points_blocked, product.points_blocked)

            page = self.app.get(reverse('discount:product-actions', kwargs={'pk': product.pk}), user=u)


            form = page.forms['product-actions-form']
            form['actions-0-end_date'] = str(self.today + timezone.timedelta(days=-1))
            page = form.submit()
            self.assertEquals(page.status_code, 200)

            form = page.forms['product-actions-form']
            form['actions-0-end_date'] = str(self.today)
            page = form.submit()
            self.assertEquals(page.status_code, 302)

            self.assertEquals(shop.points_blocked, 0)
            self.assertEquals(shop.points_free, settings.ACTION_TYPE_POPULAR_COST * 2 + settings.ACTION_TYPE_CATEGORY_COST)
            self.assertEquals(shop.points_total, shop.points_free)

            page = self.app.get(reverse('discount:product-actions', kwargs={'pk': product.pk}), user=u)
            form = page.forms['product-actions-form']
            form['actions-1-action_type'] = models.ACTION_TYPE_POPULAR
            form['actions-1-start_date'] = str(self.today + timezone.timedelta(days=-5))
            form['actions-1-end_date'] = str(self.today + timezone.timedelta(days=33))
            form['actions-1-start'] = True

            page = form.submit()
            self.assertEquals(page.status_code, 200)



            form = page.forms['product-actions-form']
            form['actions-1-action_type'] = models.ACTION_TYPE_POPULAR
            form['actions-1-start_date'] = str(self.today + timezone.timedelta(days=-5))
            form['actions-1-end_date'] = str(self.today + timezone.timedelta(days=33))
            form['actions-1-banner'] = str(banner.pk)
            form['actions-1-start'] = True
            form['actions-0-end_date'] = str(self.today + timezone.timedelta(days=1))

            page = form.submit()
            self.assertEquals(page.status_code, 302)

            self.assertEquals(shop.points_blocked, settings.ACTION_TYPE_CATEGORY_COST + settings.ACTION_TYPE_POPULAR_COST)
            self.assertEquals(shop.points_free, 0)
            self.assertEquals(shop.points_total, settings.ACTION_TYPE_POPULAR_COST + settings.ACTION_TYPE_CATEGORY_COST)

            for action in product.actions.all():
                self.assertEquals(action.status, models.ACTION_STATUS_ACTIVE)
                self.assertGreater(action.points_spent, 0)
                self.assertEquals(action.points_blocked, action.points_spent)
                self.assertEquals(action.end_date, self.today + timezone.timedelta(days=1))
                self.assertEquals(action.start_date, product.start_date)

            page = self.app.get(reverse('discount:product-actions', kwargs={'pk': product.pk}), user=u)
            form = page.forms['product-actions-form']
            form['actions-1-start_date'] = str(self.today + timezone.timedelta(days=1))
            form['actions-0-start_date'] = str(self.today + timezone.timedelta(days=-1))
            page = form.submit()
            self.assertEquals(page.status_code, 302) #Сохранит, но поменять не даст
            self.assertEquals(shop.points_blocked, settings.ACTION_TYPE_CATEGORY_COST + settings.ACTION_TYPE_POPULAR_COST)
            self.assertEquals(shop.points_free, 0)
            self.assertEquals(shop.points_total, settings.ACTION_TYPE_POPULAR_COST + settings.ACTION_TYPE_CATEGORY_COST)
            for action in product.actions.all():
                self.assertEquals(action.start_date, self.today)
                self.assertEquals(action.status, models.ACTION_STATUS_ACTIVE)

            page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=u)
            form = page.forms['product-create-form']
            page = form.submit(name='to-suspend')
            self.assertEquals(page.status_code, 302)
            for action in product.actions.all():
                self.assertEquals(action.start_date, self.today)
                self.assertEquals(action.status, models.ACTION_STATUS_PAUSED)


            page = self.app.get(reverse('discount:product-actions', kwargs={'pk': product.pk}), user=u)
            form = page.forms['product-actions-form']
            form['actions-1-start_date'] = str(self.today + timezone.timedelta(days=1))
            form['actions-0-start_date'] = str(self.today + timezone.timedelta(days=-1))
            page = form.submit()
            self.assertEquals(page.status_code, 302) #Сохранит, но поменять не даст
            self.assertEquals(shop.points_blocked, settings.ACTION_TYPE_CATEGORY_COST + settings.ACTION_TYPE_POPULAR_COST)
            self.assertEquals(shop.points_free, 0)
            self.assertEquals(shop.points_total, settings.ACTION_TYPE_POPULAR_COST + settings.ACTION_TYPE_CATEGORY_COST)



            page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=u)
            form = page.forms['product-create-form']
            page = form.submit(name='to-publish')
            self.assertEquals(page.status_code, 302)
            for action in product.actions.all():
                self.assertEquals(action.start_date, self.today)
                self.assertEquals(action.status, models.ACTION_STATUS_ACTIVE)
            self.assertEquals(shop.points_blocked, settings.ACTION_TYPE_CATEGORY_COST + settings.ACTION_TYPE_POPULAR_COST)
            self.assertEquals(shop.points_free, 0)
            self.assertEquals(shop.points_total, settings.ACTION_TYPE_POPULAR_COST + settings.ACTION_TYPE_CATEGORY_COST)

            page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=u)
            form = page.forms['product-create-form']
            page = form.submit(name='to-finish')
            self.assertEquals(page.status_code, 302)
            for action in product.actions.all():
                self.assertEquals(action.start_date, self.today)
                self.assertEquals(action.end_date, self.today)
                self.assertEquals(action.status, models.ACTION_STATUS_FINISHED)
            self.assertEquals(shop.points_blocked, 0)
            self.assertEquals(shop.points_free, settings.ACTION_TYPE_POPULAR_COST + settings.ACTION_TYPE_CATEGORY_COST)
            self.assertEquals(shop.points_total, shop.points_free)


class StartDateTest(BaseTest):
    def setUp(self):
        super().setUp()
        settings.START_DATE = self.today + timezone.timedelta(days=30)

    def test_product_cannot_start_before_start_date(self):
        u = models.User.objects.get(username='alex')
        models.Payment.increase(self.shop, u, settings.ACTION_TYPE_CATEGORY_COST * 3)

        models.Subscription.objects.create(start_date=self.today,
                                                                   end_date=settings.START_DATE + timezone.timedelta(days=15),
                                                                   user=u,
                                                                   shop=self.shop,
                                                                   subscription_type=self.subscription_type,
                                                                   )

        product = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                         start_date=self.today,
                                         end_date=self.today + timezone.timedelta(days=2),
                                         code=models.Product.generate_unique_code(), product_type=self.pt3, shop=self.shop, brand=self.brand,
                                                 status=models.STATUS_PROJECT,
                                         )
        product.filter_values.add(self.color_green)
        models.ProductImage.objects.create(image='image', product=product)

        #TODO какой-то глюк, я связываю его с ajax. Будет время - разобраться
        try:
            page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=u)
            form = page.forms['product-create-form']
            page = form.submit(name='to-approve')
        except:
            pass


        product = product.saved_version
        self.assertEquals(product.status, models.STATUS_PROJECT)

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=u)
        form = page.forms['product-create-form']
        form['start_date'] = str(settings.START_DATE)
        form['end_date'] = str(settings.START_DATE + timezone.timedelta(days=2))

        page = form.submit(name='to-approve')
        self.assertEquals(page.status_code, 302)
        product = product.saved_version
        self.assertEquals(product.status, models.STATUS_TO_APPROVE)

        product.status = models.STATUS_APPROVED
        product.save()

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=u)
        form = page.forms['product-create-form']
        page = form.submit(name='to-plan')
        self.assertEquals(page.status_code, 302)
        product = product.saved_version
        self.assertEquals(product.status, models.STATUS_READY)


        page = self.app.get(reverse('discount:product-actions', kwargs={'pk': product.pk}), user=u)

        form = page.forms['product-actions-form']
        form['actions-0-action_type'] = models.ACTION_TYPE_CATEGORY
        form['actions-0-start_date'] = str(self.today)
        form['actions-0-end_date'] = str(self.today + timezone.timedelta(days=2))
        form['actions-0-start'] = True
        page = form.submit()
        self.assertEquals(page.status_code, 200)
        self.assertEquals(product.actions.all().count(), 0)

        form['actions-0-start_date'] = str(settings.START_DATE)
        form['actions-0-end_date'] = str(settings.START_DATE + timezone.timedelta(days=2))
        page = form.submit()
        self.assertEquals(page.status_code, 302)

        for action in product.actions.all():
            self.assertEquals(action.start_date, settings.START_DATE)
            self.assertEquals(action.end_date, settings.START_DATE + timezone.timedelta(days=2))
            self.assertEquals(action.status, models.ACTION_STATUS_PLANNED)
            self.assertEquals(action.points_blocked, settings.ACTION_TYPE_CATEGORY_COST * 3)
            self.assertEquals(product.points_blocked, settings.ACTION_TYPE_CATEGORY_COST * 3)
            self.assertEquals(product.shop.points_blocked, settings.ACTION_TYPE_CATEGORY_COST * 3)
            self.assertEquals(product.shop.points_free, 0)
            self.assertEquals(product.shop.points_total, settings.ACTION_TYPE_CATEGORY_COST * 3)



class TestAllPagesAvailable(BaseTest):
    def setUp(self):
        super().setUp()
        models.Subscription.objects.create(start_date=self.today,
                                                                   end_date=settings.START_DATE + timezone.timedelta(days=45),
                                                                   user=self.user,
                                                                   shop=self.shop,
                                                                   subscription_type=self.subscription_type,
                                                                   )
        poll = Poll.objects.create(question='dsfgdsfg')
        answer = Answer.objects.create(poll=poll, body='sdhfasjfg')


    def test_discount_simple_pages_availble(self):
        simple_urls = [
        'cart-view',
        'instant-cart-view',
        'main-page',
        'shop-list',
        'full-login',
        'signup',
        'cart-login',
        'cart-signup',
        'contacts-page',
        'help-page',
        'shop-offer',
        ]

        for simple_url in simple_urls:
            su = self.user
            u = self.simple_user
            au = AnonymousUser()
            product = self.product
            self.renew_app()
            page = self.app.get(reverse('{0}:{1}'.format('discount', simple_url)))
            self.assertEquals(page.status_code, 200)


            self.renew_app()
            page = self.app.get(reverse('{0}:{1}'.format('discount', simple_url)), user=su)
            if simple_url in ['full-login', 'signup', 'cart-login', 'cart-signup']:
                self.assertEquals(page.status_code, 302)
            else:
                self.assertEquals(page.status_code, 200)

            self.renew_app()
            page = self.app.get(reverse('{0}:{1}'.format('discount', simple_url)), user=u)
            if simple_url in ['full-login', 'signup', 'cart-login', 'cart-signup']:
                self.assertEquals(page.status_code, 302)
            else:
                self.assertEquals(page.status_code, 200)

        self.product.status = models.STATUS_PUBLISHED
        self.product.save(check_status=False)


        self.renew_app()
        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEquals(page.status_code, 200)
        self.renew_app()
        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': self.product.pk}), user=su)
        self.assertEquals(page.status_code, 200)
        self.renew_app()
        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': self.product.pk}), user=u)
        self.assertEquals(page.status_code, 200)

        self.renew_app()
        page = self.app.get(reverse('discount:product-detail-code', kwargs={'code': self.product.code}))
        self.assertEquals(page.status_code, 200)
        self.renew_app()
        page = self.app.get(reverse('discount:product-detail-code', kwargs={'code': self.product.code}), user=su)
        self.assertEquals(page.status_code, 200)
        self.renew_app()
        page = self.app.get(reverse('discount:product-detail-code', kwargs={'code': self.product.code}), user=u)
        self.assertEquals(page.status_code, 200)

        self.renew_app()
        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt1.pk}))
        self.assertEquals(page.status_code, 200)
        self.renew_app()
        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt2.pk}), user=su)
        self.assertEquals(page.status_code, 200)
        self.renew_app()
        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt3.pk}), user=u)
        self.assertEquals(page.status_code, 200)

        self.renew_app()
        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt1.alias}))
        self.assertEquals(page.status_code, 200)
        self.renew_app()
        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt2.alias}), user=su)
        self.assertEquals(page.status_code, 200)
        self.renew_app()
        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt3.alias}), user=u)
        self.assertEquals(page.status_code, 200)

        self.renew_app()
        page = self.app.get(reverse('discount:product-create'))
        self.assertEquals(page.status_code, 302)

        self.renew_app()
        page = self.app.get(reverse('discount:product-create'), user=u)
        self.assertEquals(page.status_code, 302)

        self.renew_app()
        page = self.app.get(reverse('discount:product-create'), user=su)
        self.assertEquals(page.status_code, 200)


        self.renew_app()
        page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}))
        self.assertEquals(page.status_code, 302)

        self.renew_app()
        page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=u)
        self.assertEquals(page.status_code, 302)

        self.renew_app()
        page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=su)
        self.assertEquals(page.status_code, 200)









class ProductCreateButtonsTest(BaseTest):
    def setUp(self):
        super().setUp()
        subscription = models.Subscription.objects.create(start_date=self.today,
                                                                   end_date=self.today + timezone.timedelta(days=30),
                                                                   user=self.user,
                                                                   shop=self.shop,
                                                                   subscription_type=self.subscription_type,
                                                                   )

    def test_product_create_buttons(self):
        user = self.user
        product = self.product
        self.assertEquals(product.status, models.STATUS_PROJECT)
        page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-create-form']
        self.assertIn('to-approve', form.fields)
        self.assertIn('to-save', form.fields)
        self.assertIn('to-cancel', form.fields)
        self.assertNotIn('to-plan', form.fields)
        self.assertNotIn('to-publish', form.fields)
        self.assertNotIn('to-project', form.fields)
        self.assertNotIn('to-suspend', form.fields)
        self.assertNotIn('to-finish', form.fields)




        product.status = models.STATUS_TO_APPROVE
        product.save()

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-create-form']
        self.assertNotIn('to-approve', form.fields)
        self.assertNotIn('to-save', form.fields)
        self.assertNotIn('to-cancel', form.fields)
        self.assertNotIn('to-plan', form.fields)
        self.assertNotIn('to-publish', form.fields)
        self.assertNotIn('to-project', form.fields)
        self.assertNotIn('to-suspend', form.fields)
        self.assertNotIn('to-finish', form.fields)

        product.status = models.STATUS_NEED_REWORK
        product.save()

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-create-form']
        self.assertIn('to-approve', form.fields)
        self.assertIn('to-save', form.fields)
        self.assertIn('to-cancel', form.fields)
        self.assertNotIn('to-plan', form.fields)
        self.assertNotIn('to-publish', form.fields)
        self.assertNotIn('to-project', form.fields)
        self.assertNotIn('to-suspend', form.fields)
        self.assertNotIn('to-finish', form.fields)

        product.status = models.STATUS_TO_APPROVE
        product.save()
        product.status = models.STATUS_APPROVED
        product.save()

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-create-form']
        self.assertNotIn('to-approve', form.fields)
        self.assertIn('to-save', form.fields)
        self.assertIn('to-cancel', form.fields)
        self.assertIn('to-plan', form.fields)
        self.assertIn('to-publish', form.fields)
        self.assertIn('to-project', form.fields)
        self.assertNotIn('to-suspend', form.fields)
        self.assertNotIn('to-finish', form.fields)

        product.status = models.STATUS_PUBLISHED
        product.save()

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-create-form']
        self.assertNotIn('to-approve', form.fields)
        self.assertIn('to-save', form.fields)
        self.assertNotIn('to-cancel', form.fields)
        self.assertNotIn('to-plan', form.fields)
        self.assertNotIn('to-publish', form.fields)
        self.assertNotIn('to-project', form.fields)
        self.assertIn('to-suspend', form.fields)
        self.assertIn('to-finish', form.fields)

        product.status = models.STATUS_SUSPENDED
        product.save()

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-create-form']
        self.assertNotIn('to-approve', form.fields)
        self.assertIn('to-save', form.fields)
        self.assertNotIn('to-cancel', form.fields)
        self.assertNotIn('to-plan', form.fields)
        self.assertIn('to-publish', form.fields)
        self.assertNotIn('to-project', form.fields)
        self.assertNotIn('to-suspend', form.fields)
        self.assertIn('to-finish', form.fields)


        product.status = models.STATUS_READY
        product.start_date = self.today + timezone.timedelta(days=1)
        product.save(do_clean=False, check_status=False)
        self.assertEquals(product.status, models.STATUS_READY)

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-create-form']
        self.assertNotIn('to-approve', form.fields)
        self.assertIn('to-save', form.fields)
        self.assertIn('to-cancel', form.fields)
        self.assertNotIn('to-plan', form.fields)
        self.assertIn('to-publish', form.fields)
        self.assertIn('to-project', form.fields)
        self.assertNotIn('to-suspend', form.fields)
        self.assertNotIn('to-finish', form.fields)


        product.status = models.STATUS_FINISHED
        #product.start_date = self.today
        product.save(do_clean=False, check_status=False)

        page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-create-form']
        self.assertNotIn('to-approve', form.fields)
        self.assertNotIn('to-save', form.fields)
        self.assertNotIn('to-cancel', form.fields)
        self.assertNotIn('to-plan', form.fields)
        self.assertNotIn('to-publish', form.fields)
        self.assertNotIn('to-project', form.fields)
        self.assertNotIn('to-suspend', form.fields)
        self.assertNotIn('to-finish', form.fields)


class AdditionalModelChecks(BaseTest):
    def setUp(self):
        super().setUp()

    def test_cant_publish_shop_without_brands(self):

        with self.assertRaises(ValidationError):
            shop = models.Shop.objects.create(title='Магазин1', status=models.SHOP_STATUS_PROJECT, image='image.jpg')
            shop.status = models.SHOP_STATUS_PUBLISHED
            shop.save()
        models.ShopsToBrands.objects.create(shop=shop, brand=self.brand)
        shop.status = models.SHOP_STATUS_PUBLISHED
        shop.save()
        self.assertEquals(shop.status, models.SHOP_STATUS_PUBLISHED)


class LoginAndPasswordRegistrationTest(WebTest):
    def test_login_and_passw_min_length_ok(self):
        page = self.app.get(reverse('discount:signup'))
        username = 'dskjdfsldjhsdjgshdlkjghsdkfjghsdjkfdghjslk'
        username = username[:settings.ACCOUNT_USERNAME_MIN_LENGTH]
        password = 'sdfgsdfjgdksfgdfklsjhgdfksjhgdfsgdfgdfgdfs'
        password = password[:settings.ACCOUNT_PASSWORD_MIN_LENGTH]
        form = page.forms['signup-form']
        form['username'] = username
        form['password1'] = password
        form['password2'] = password
        form['email'] = 'hghdfgkdfg@gjdfkjghdfk.ru'
        page = form.submit()
        self.assertEquals(page.status_code, 302)
        users_count = models.User.objects.filter(username=username).count()
        self.assertEquals(users_count, 1)

    def test_login_min_length_violate(self):
        page = self.app.get(reverse('discount:signup'))
        username = 'dskjdfsldjhsdjgshdlkjghsdkfjghsdjkfdghjslk'
        username = username[:settings.ACCOUNT_USERNAME_MIN_LENGTH - 1]
        password = 'sdfgsdfjgdksfgdfklsjhgdfksjhgdfsgdfgdfgdfs'
        password = password[:settings.ACCOUNT_PASSWORD_MIN_LENGTH]
        form = page.forms['signup-form']
        form['username'] = username
        form['password1'] = password
        form['password2'] = password
        form['email'] = 'hghdfgkdfg@gjdfkjghdfk.ru'
        page = form.submit()
        self.assertEquals(page.status_code, 200)
        users_count = models.User.objects.filter(username=username).count()
        self.assertEquals(users_count, 0)

        username = 'dskjdfsldjhsdjgshdlkjghsdkfjghsdjkfdghjslk'
        username = username[:settings.ACCOUNT_USERNAME_MIN_LENGTH]
        form['username'] = username
        page = form.submit()
        self.assertEquals(page.status_code, 302)
        users_count = models.User.objects.filter(username=username).count()
        self.assertEquals(users_count, 1)

    def test_passw_min_length_violate(self):
        page = self.app.get(reverse('discount:signup'))
        username = 'dskjdfsldjhsdjgshdlkjghsdkfjghsdjkfdghjslk'
        username = username[:settings.ACCOUNT_USERNAME_MIN_LENGTH]
        password = 'sdfgsdfjgdksfgdfklsjhgdfksjhgdfsgdfgdfgdfs'
        password = password[:settings.ACCOUNT_PASSWORD_MIN_LENGTH - 1]
        form = page.forms['signup-form']
        form['username'] = username
        form['password1'] = password
        form['password2'] = password
        form['email'] = 'hghdfgkdfg@gjdfkjghdfk.ru'
        page = form.submit()
        self.assertEquals(page.status_code, 200)
        users_count = models.User.objects.filter(username=username).count()
        self.assertEquals(users_count, 0)

        password = 'sdfgsdfjgdksfgdfklsjhgdfksjhgdfsgdfgdfgdfs'
        password = password[:settings.ACCOUNT_PASSWORD_MIN_LENGTH]
        form['password1'] = password
        form['password2'] = password
        page = form.submit()
        self.assertEquals(page.status_code, 302)
        users_count = models.User.objects.filter(username=username).count()
        self.assertEquals(users_count, 1)

    def text_mess_in_passw_is_ok(self):
        page = self.app.get(reverse('discount:signup'))
        username = 'dskjdfsldjhsdjgshdlkjghsdkfjghsdjkfdghjslk'
        username = username[:settings.ACCOUNT_USERNAME_MIN_LENGTH]
        password = '_dsСВлШDKJFD~!@\+DDDksdsdszzz?DSFDJKfnhdsfhsdjhbj&^(&**|+_)(*&^%$#@!~{}[]/'
        form = page.forms['signup-form']
        form['username'] = username
        form['password1'] = password
        form['password2'] = password
        form['email'] = 'hghdfgkdfg@gjdfkjghdfk.ru'
        page = form.submit()
        self.assertEquals(page.status_code, 302)
        users_count = models.User.objects.filter(username=username).count()
        self.assertEquals(users_count, 1)


    def test_email_checks(self):
        page = self.app.get(reverse('discount:signup'))
        username = 'dskjdfsldjhsdjgshdlkjghsdkfjghsdjkfdghjslk'
        username = username[:settings.ACCOUNT_USERNAME_MIN_LENGTH]
        password = 'sdfgsdfjgdksfgdfklsjhgdfksjhgdfsgdfgdfgdfs'
        password = password[:settings.ACCOUNT_PASSWORD_MIN_LENGTH]
        form = page.forms['signup-form']
        form['username'] = username
        form['password1'] = password
        form['password2'] = password
        form['email'] = 'hghdfgkdfg@gjdfkjghdfk'
        page = form.submit()
        self.assertEquals(page.status_code, 200)
        users_count = models.User.objects.filter(username=username).count()
        self.assertEquals(users_count, 0)

        form['email'] = ''
        page = form.submit()
        self.assertEquals(page.status_code, 200)
        users_count = models.User.objects.filter(username=username).count()
        self.assertEquals(users_count, 0)

        form['email'] = 's@sa.ra'
        page = form.submit()
        self.assertEquals(page.status_code, 302)
        users_count = models.User.objects.filter(username=username).count()
        self.assertEquals(users_count, 1)


    def test_russian_letters_disabled(self):
        page = self.app.get(reverse('discount:signup'))
        username = 'аыввапвапваперв'
        username = username[:settings.ACCOUNT_USERNAME_MIN_LENGTH]
        password = 'sdfgsdfjgdksfgdfklsjhgdfksjhgdfsgdfgdfgdfs'
        password = password[:settings.ACCOUNT_PASSWORD_MIN_LENGTH]
        form = page.forms['signup-form']
        form['username'] = username
        form['password1'] = password
        form['password2'] = password
        form['email'] = 'hghdfgkdfg@gjdfkjghdfk.ru'
        page = form.submit()
        self.assertEquals(page.status_code, 200)
        users_count = models.User.objects.filter(username=username).count()
        self.assertEquals(users_count, 0)

    def test_digits_enabled_not_first(self):
        page = self.app.get(reverse('discount:signup'))
        username = 's12d3fsdfsdfsdf'
        username = username[:settings.ACCOUNT_USERNAME_MIN_LENGTH]
        password = 'sdfgsdfjgdksfgdfklsjhgdfksjhgdfsgdfgdfgdfs'
        password = password[:settings.ACCOUNT_PASSWORD_MIN_LENGTH]
        form = page.forms['signup-form']
        form['username'] = username
        form['password1'] = password
        form['password2'] = password
        form['email'] = 'hghdfgkdfg@gjdfkjghdfk.ru'
        page = form.submit()
        self.assertEquals(page.status_code, 302)
        users_count = models.User.objects.filter(username=username).count()
        self.assertEquals(users_count, 1)

    def test_digits_enabled_first(self):
        page = self.app.get(reverse('discount:signup'))
        username = '11234234234234234'
        username = username[:settings.ACCOUNT_USERNAME_MIN_LENGTH]
        password = 'sdfgsdfjgdksfgdfklsjhgdfksjhgdfsgdfgdfgdfs'
        password = password[:settings.ACCOUNT_PASSWORD_MIN_LENGTH]
        form = page.forms['signup-form']
        form['username'] = username
        form['password1'] = password
        form['password2'] = password
        form['email'] = 'hghdfgkdfg@gjdfkjghdfk.ru'
        page = form.submit()
        self.assertEquals(page.status_code, 302)
        users_count = models.User.objects.filter(username=username).count()
        self.assertEquals(users_count, 1)



    def test_uppercase_is_enabled(self):
        page = self.app.get(reverse('discount:signup'))
        username = 'BfdBfdXsldjkfVEF'
        username = username[:settings.ACCOUNT_USERNAME_MIN_LENGTH]
        password = 'sdfgsdfjgdksfgdfklsjhgdfksjhgdfsgdfgdfgdfs'
        password = password[:settings.ACCOUNT_PASSWORD_MIN_LENGTH]
        form = page.forms['signup-form']
        form['username'] = username
        form['password1'] = password
        form['password2'] = password
        form['email'] = 'hghdfgkdfg@gjdfkjghdfk.ru'
        page = form.submit()
        self.assertEquals(page.status_code, 302)
        users_count = models.User.objects.filter(username=username).count()
        self.assertEquals(users_count, 1)

    def test_spec_symb_is_enabled_but_not_first(self):
        page = self.app.get(reverse('discount:signup'))
        username = '_fsdk-_fhsdkfsdkfjh'
        username = username[:settings.ACCOUNT_USERNAME_MIN_LENGTH]
        password = 'sdfgsdfjgdksfgdfklsjhgdfksjhgdfsgdfgdfgdfs'
        password = password[:settings.ACCOUNT_PASSWORD_MIN_LENGTH]
        form = page.forms['signup-form']
        form['username'] = username
        form['password1'] = password
        form['password2'] = password
        form['email'] = 'hghdfgkdfg@gjdfkjghdfk.ru'
        page = form.submit()
        self.assertEquals(page.status_code, 200)
        users_count = models.User.objects.filter(username=username).count()
        self.assertEquals(users_count, 0)

        username = 'd-_.fhsdkfsdkfjh'
        form['username'] = username
        page = form.submit()
        self.assertEquals(page.status_code, 302)
        users_count = models.User.objects.filter(username=username).count()
        self.assertEquals(users_count, 1)


class ProductChangerTest(BaseTest):
    def setUp(self):
        super().setUp()
        user = self.user
        shop = self.shop
        models.Subscription.objects.create(start_date=self.today,
                                                           end_date=self.today + timezone.timedelta(days=30),
                                                           user=user,
                                                           shop=shop,
                                                           subscription_type=self.subscription_type,
                                                           )



        product = self.product1
        product.status = models.STATUS_PUBLISHED
        product.save(check_status=False)


    def test_full_cycle_product_changer_test(self):
        user = self.user
        product = self.product1
        product_image = models.ProductImage.objects.create(product=product, image='sdfasgsdfgsdfgsdfg')
        path = TEST_IMAGE_PATH
        f = open(path, 'rb')


        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']
        form['images-1-image'] = ('images-0-image', f.read())
        title = 'dsfgdsfgsd5e56ydhgfh'
        body = 'dsdsfsdfsdffgddfsgsfgsd5e56ydhgfh'
        form['title'] = title
        form['body'] = body
        page = form.submit(name='confirm')
        self.assertEquals(page.status_code, 302)

        changer = models.ProductChanger.objects.get(product=product)
        self.assertEquals(changer.status, models.STATUS_TO_APPROVE)

        changer.status = models.STATUS_APPROVED
        changer.save()

        product = product.saved_version

        self.assertEquals(product.title, title)
        self.assertEquals(product.body, body)

        self.assertEquals(product.images.all().count(), 2)
        image_names = product.images.all().values_list('image', flat=True)
        self.assertIn('sdfasgsdfgsdfgsdfg', image_names)

        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']
        self.assertEquals(product.productchanger_set.all().count(), 2)
        f = open(path, 'rb')
        form['images-0-image'] = ('images-0-image', f.read())
        f = open(path, 'rb')
        form['images-1-image'] = ('images-1-image', f.read())
        f = open(path, 'rb')
        form['images-2-image'] = ('images-2-image', f.read())
        page = form.submit(name='confirm')
        self.assertEquals(page.status_code, 302)
        self.assertEquals(product.images.all().count(), 2)

        changer = models.ProductChanger.objects.get(product=product, status=models.STATUS_TO_APPROVE)
        changer.status = models.STATUS_APPROVED
        changer.save()

        self.assertEquals(product.images.all().count(), 3)

        image_names = product.images.all().values_list('image', flat=True)
        self.assertNotIn(models.Product.generate_unique_code(), image_names)

        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']
        page = form.submit(name='confirm')
        changer = models.ProductChanger.objects.get(product=product, status=models.STATUS_TO_APPROVE)
        changer.status = models.STATUS_APPROVED
        changer.save()

        new_image_names = product.images.all().values_list('image', flat=True)
        self.assertEquals(sorted(new_image_names), sorted(image_names))
        self.assertEquals(product.productchanger_set.all().count(), 3)


        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']
        form['images-0-DELETE'] = True
        page = form.submit(name='confirm')

        changer = models.ProductChanger.objects.get(product=product, status=models.STATUS_TO_APPROVE)
        changer.status = models.STATUS_APPROVED
        changer.save()
        self.assertEquals(product.images.all().count(), 2)
        self.assertEquals(product.productchanger_set.all().count(), 4)

        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']
        page = form.submit(name='delete')
        self.assertEquals(product.productchanger_set.all().count(), 4)

        product = product.saved_version
        self.assertEquals(product.title, title)
        self.assertEquals(product.body, body)

        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']
        form['images-0-DELETE'] = True
        page = form.submit(name='confirm')

        changer = models.ProductChanger.objects.get(product=product, status=models.STATUS_TO_APPROVE)
        changer.status = models.STATUS_NEED_REWORK
        changer.save()
        self.assertEquals(product.images.all().count(), 2)
        self.assertEquals(product.productchanger_set.all().count(), 5)

        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']
        page = form.submit(name='confirm')
        changer = models.ProductChanger.objects.get(product=product, status=models.STATUS_TO_APPROVE)
        changer.status = models.STATUS_APPROVED
        changer.save()

        self.assertEquals(product.images.all().count(), 1)
        self.assertEquals(product.productchanger_set.all().count(), 5)

    def test_product_changer_condition(self):
        product = self.product1
        #product.status = models.STATUS_PUBLISHED
        #product.save(check_status=False)
        user = self.user

        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']
        form['conditions-0-condition'] = 'gdfsgjdsflkgh4t93hilsrgdfsg'
        page = form.submit(name='confirm')
        self.assertEquals(page.status_code, 302)

        changer = models.ProductChanger.objects.get(product=product, status=models.STATUS_TO_APPROVE)
        changer.status = models.STATUS_APPROVED
        changer.save()

        conditions = product.conditions.all().values_list('condition', flat=True)
        self.assertEquals(len(conditions), 1)

        self.assertEquals(conditions[0], 'gdfsgjdsflkgh4t93hilsrgdfsg')

        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']
        form['conditions-0-condition'] = 'gdfsgjdsflkgh4t93hilsrgdfsg'
        form['conditions-1-condition'] = 'sdfgsdghodasghdyfusgkdfsgjhdfs'
        page = form.submit(name='confirm')
        self.assertEquals(page.status_code, 302)

        changer = models.ProductChanger.objects.get(product=product, status=models.STATUS_TO_APPROVE)
        changer.status = models.STATUS_APPROVED
        changer.save()

        conditions = product.conditions.all().values_list('condition', flat=True)

        self.assertIn('gdfsgjdsflkgh4t93hilsrgdfsg', conditions)
        self.assertIn('sdfgsdghodasghdyfusgkdfsgjhdfs', conditions)
        self.assertEquals(len(conditions), 2)


        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']
        form['conditions-0-condition'] = ''
        form['conditions-1-condition'] = 'sdfgsdghodasghdyfusgkdfsgjhdfs'
        page = form.submit(name='confirm')
        self.assertEquals(page.status_code, 302)

        changer = models.ProductChanger.objects.get(product=product, status=models.STATUS_TO_APPROVE)
        changer.status = models.STATUS_APPROVED
        changer.save()

        conditions = product.conditions.all().values_list('condition', flat=True)

        self.assertNotIn('gdfsgjdsflkgh4t93hilsrgdfsg', conditions)
        self.assertIn('sdfgsdghodasghdyfusgkdfsgjhdfs', conditions)
        self.assertEquals(len(conditions), 1)


    def test_product_changer_link(self):
        product = self.product1

        #product.status = models.STATUS_PUBLISHED
        product.save(check_status=False)
        user = self.user

        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']
        form['link'] = 'yandex.ru'
        page = form.submit(name='confirm')
        self.assertEquals(page.status_code, 302)

        changer = models.ProductChanger.objects.get(product=product, status=models.STATUS_TO_APPROVE)
        changer.status = models.STATUS_APPROVED
        changer.save()

        product = product.saved_version

        self.assertEquals(product.link, 'yandex.ru')

        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']
        form['link'] = 'ya.ru'
        page = form.submit(name='confirm')
        self.assertEquals(page.status_code, 302)

        changer = models.ProductChanger.objects.get(product=product, status=models.STATUS_TO_APPROVE)
        changer.status = models.STATUS_APPROVED
        changer.save()

        product = product.saved_version

        self.assertEquals(product.link, 'ya.ru')

        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']
        form['link'] = ''
        page = form.submit(name='confirm')
        self.assertEquals(page.status_code, 302)

        changer = models.ProductChanger.objects.get(product=product, status=models.STATUS_TO_APPROVE)
        changer.status = models.STATUS_APPROVED
        changer.save()

        product = product.saved_version

        self.assertEquals(product.link, '')

    def test_product_changer_prices(self):
        product = self.product1

        #product.status = models.STATUS_PUBLISHED
        product.save(check_status=False)
        user = self.user

        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']
        form['stock_price'] = str(100)
        form['normal_price'] = str(200)
        page = form.submit(name='confirm')
        self.assertEquals(page.status_code, 302)

        changer = models.ProductChanger.objects.get(product=product, status=models.STATUS_TO_APPROVE)
        changer.status = models.STATUS_APPROVED
        changer.save()

        product = product.saved_version

        self.assertEquals(product.stock_price, 100)
        self.assertEquals(product.normal_price, 200)


        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']

        page = form.submit(name='confirm')
        self.assertEquals(page.status_code, 302)

        changer = models.ProductChanger.objects.get(product=product, status=models.STATUS_TO_APPROVE)
        changer.status = models.STATUS_APPROVED
        changer.save()

        product = product.saved_version

        self.assertEquals(product.stock_price, 100)
        self.assertEquals(product.normal_price, 200)


        page = self.app.get(reverse('discount:product-change', kwargs={'pk': product.pk}), user=user)
        form = page.forms['product-change-form']
        form['stock_price'] = str(300)
        form['normal_price'] = str(600)
        page = form.submit(name='confirm')
        self.assertEquals(page.status_code, 302)

        changer = models.ProductChanger.objects.get(product=product, status=models.STATUS_TO_APPROVE)
        changer.status = models.STATUS_APPROVED
        changer.save()

        product = product.saved_version

        self.assertEquals(product.stock_price, 300)
        self.assertEquals(product.normal_price, 600)




class ActionDaysViewCheck(BaseTest):
    def test_can_send_empty_form(self):
        user = self.user
        page = self.app.get(reverse('discount:action-days'), user=user)
        form = page.forms['action-days-form']
        page = form.submit()
        self.assertEquals(page.status_code, 200)
        start_date = self.today
        end_date = start_date + timezone.timedelta(days=14)
        start_date = format(start_date, '%d.%m.%Y')
        end_date = format(end_date, '%d.%m.%Y')
        form = page.forms['action-days-form']
        self.assertEquals(form['start_date'].value, start_date)
        self.assertEquals(form['end_date'].value, end_date)


class ProductListTests(BaseTest):
    def setUp(self):
        super().setUp()
        self.subscription_type.max_products = 10
        self.subscription_type.save()
        models.Subscription.objects.create(start_date=self.today,
                                                           end_date=self.today + timezone.timedelta(days=30),
                                                           user=self.user,
                                                           shop=self.shop,
                                                           subscription_type=self.subscription_type,
                                                           )
        self.product1.status = models.STATUS_PUBLISHED
        self.product1.save(check_status=False, do_clean=False)


        self.product2.status = models.STATUS_FINISHED
        self.product2.save(check_status=False, do_clean=False)



        self.brand2 = models.Brand.objects.create(title='Бренд2')
        self.shop2 = models.Shop.objects.create(title='Магазин2', status=models.SHOP_STATUS_PROJECT, image=models.Product.generate_unique_code())
        models.ShopsToBrands.objects.create(shop=self.shop2, brand=self.brand2)
        self.shop2.status = models.SHOP_STATUS_PUBLISHED
        self.shop2.save()
        self.user2 = User.objects.create_user(
                username='alex1dfgdfsg', email='aldsfgdfgex1@alex.ru', password='top_secret1')

        models.ShopsToUsers.objects.create(shop=self.shop2, user=self.user2, confirmed=True)

        self.product21 = Product.objects.create(title='Tdsfgedsfgst123123', body='Test', normal_price=500, stock_price=250,
                                     start_date=self.today,
                                     end_date=self.today + timezone.timedelta(days=5),
                                     code=models.Product.generate_unique_code(), product_type=self.pt3, shop=self.shop2, brand=self.brand2,
                                     )

        self.product22 = Product.objects.create(title='Tedsfgdsfgsdfgs123123t', body='Test', normal_price=500, stock_price=250,
                                     start_date=self.today,
                                     end_date=self.today + timezone.timedelta(days=5),
                                     code=models.Product.generate_unique_code(), product_type=self.pt3, shop=self.shop2, brand=self.brand2,
                                     )

    def test_shop_manager_can_see_only_all_his_products_in_shop_list(self):


        page = self.app.get(reverse('discount:product-list-shop'), user=self.user)
        shop_products = models.Product.objects.filter(shop=self.user.get_shop)
        for p in shop_products:
            self.assertIn(p.title, page)
        not_shop_products = models.Product.objects.exclude(shop=self.user.get_shop)
        for p in not_shop_products:
            self.assertNotIn(p.title, page)

        self.renew_app()

        page = self.app.get(reverse('discount:product-list-shop'), user=self.user2)
        shop_products = models.Product.objects.filter(shop=self.user2.get_shop)
        for p in shop_products:
            self.assertIn(p.title, page)
        not_shop_products = models.Product.objects.exclude(shop=self.user2.get_shop)
        for p in not_shop_products:
            self.assertNotIn(p.title, page)

    def test_tatamo_user_can_see_all_products(self):
        user = self.user
        profile = user.profile
        profile.role = models.USER_ROLE_TATAMO_MANAGER
        profile.save()
        page = self.app.get(reverse('discount:product-list-tatamo'), user=user)
        all_products = models.Product.objects.all()
        for p in all_products:
            self.assertIn(p.title, page)

    def test_guest_and_shop_user_can_see_the_same_and_no_mess_in_categs(self):


        pt11 = ProductType.objects.create(title='level11', parent=self.pt0, alias='test_alias_11')
        pt21 = ProductType.objects.create(title='level21', parent=pt11, alias='test_alias_21')
        pt31 = ProductType.objects.create(title='level31', parent=pt21, alias='test_alias_31')



        product31 = Product.objects.create(title='sdfgdsf56456346', body='Test', normal_price=500, stock_price=250,
                                     start_date=self.today,
                                     end_date=self.today + timezone.timedelta(days=5),
                                     code=models.Product.generate_unique_code(), product_type=pt31, shop=self.shop, brand=self.brand,
                                     )

        product32 = Product.objects.create(title='dsgfse54twhgdfghdgfhd', body='Test', normal_price=500, stock_price=250,
                                     start_date=self.today,
                                     end_date=self.today + timezone.timedelta(days=5),
                                     code=models.Product.generate_unique_code(), product_type=pt31, shop=self.shop, brand=self.brand,
                                     )

        self.product1.status = models.STATUS_PUBLISHED
        self.product1.title = 'fsdlkjhgf597h8r7ehgo8dfgd58h7'
        self.product1.save(do_clean=False, check_status=False)

        self.product2.status = models.STATUS_TO_APPROVE
        self.product2.title = 'gijrgw9854g9sd8ghosidfilg'
        self.product2.save(do_clean=False, check_status=False)

        self.product3.status = models.STATUS_PROJECT
        self.product3.title = 'gdfskbg5ygh87548gbrbgsdf'
        self.product3.save(do_clean=False, check_status=False)

        self.product4.status = models.STATUS_APPROVED
        self.product4.title = 'dsfgsdgddfshgffskbg5ygh8754dfghddfghfgh8gbrbgfghsdf'
        self.product4.save(do_clean=False, check_status=False)

        self.product5.status = models.STATUS_FINISHED
        self.product5.title = 'sgfh65ehhfdgjrtjgfyhjgh'
        self.product5.save(do_clean=False, check_status=False)

        product31.status = models.STATUS_PUBLISHED
        product31.save(do_clean=False, check_status=False)

        product32.status = models.STATUS_PUBLISHED
        product32.save(do_clean=False, check_status=False)



        page = self.app.get(reverse('discount:product-list', kwargs={'alias': pt31.pk}))
        self.assertIn(product31.title, page)
        self.assertIn(product32.title, page)
        self.assertNotIn(self.product1.title, page)
        self.assertNotIn(self.product2.title, page)
        self.assertNotIn(self.product3.title, page)
        self.assertNotIn(self.product4.title, page)
        self.assertNotIn(self.product4.title, page)

        self.renew_app()
        page = self.app.get(reverse('discount:product-list', kwargs={'alias': pt31.pk}), user=self.user)
        self.assertIn(product31.title, page)
        self.assertIn(product32.title, page)
        self.assertNotIn(self.product1.title, page)
        self.assertNotIn(self.product2.title, page)
        self.assertNotIn(self.product3.title, page)
        self.assertNotIn(self.product4.title, page)
        self.assertNotIn(self.product4.title, page)

        self.renew_app()
        page = self.app.get(reverse('discount:product-list', kwargs={'alias': pt21.pk}), user=self.user)
        self.assertIn(product31.title, page)
        self.assertIn(product32.title, page)
        self.assertNotIn(self.product1.title, page)
        self.assertNotIn(self.product2.title, page)
        self.assertNotIn(self.product3.title, page)
        self.assertNotIn(self.product4.title, page)
        self.assertNotIn(self.product4.title, page)

        self.renew_app()
        page = self.app.get(reverse('discount:product-list', kwargs={'alias': pt11.pk}), user=self.user)
        self.assertIn(product31.title, page)
        self.assertIn(product32.title, page)
        self.assertNotIn(self.product1.title, page)
        self.assertNotIn(self.product2.title, page)
        self.assertNotIn(self.product3.title, page)
        self.assertNotIn(self.product4.title, page)
        self.assertNotIn(self.product4.title, page)

        self.renew_app()
        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt1.pk}), user=self.user)
        self.assertNotIn(product31.title, page)
        self.assertNotIn(product32.title, page)
        self.assertIn(self.product1.title, page)
        self.assertNotIn(self.product2.title, page)
        self.assertNotIn(self.product3.title, page)
        self.assertNotIn(self.product4.title, page)
        self.assertNotIn(self.product4.title, page)

        self.renew_app()
        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt3.pk}))
        self.assertNotIn(product31.title, page)
        self.assertNotIn(product32.title, page)
        self.assertIn(self.product1.title, page)
        self.assertNotIn(self.product2.title, page)
        self.assertNotIn(self.product3.title, page)
        self.assertNotIn(self.product4.title, page)
        self.assertNotIn(self.product4.title, page)




    def test_shop_brand_price_category_discount_category_product_type_color_size_status_filters_works_fine(self):
        brand1= models.Brand.objects.create(title='Бренд11')
        brand2= models.Brand.objects.create(title='Бренд21')
        shop1 = models.Shop.objects.create(title='Магазин1', status=models.SHOP_STATUS_PROJECT, image=models.Product.generate_unique_code())
        shop2 = models.Shop.objects.create(title='Магазин2', status=models.SHOP_STATUS_PROJECT, image=models.Product.generate_unique_code())
        models.ShopsToBrands.objects.create(shop=self.shop, brand=self.brand)
        models.ShopsToBrands.objects.create(shop=shop1, brand=brand1)
        models.ShopsToBrands.objects.create(shop=shop2, brand=brand2)
        shop1.status = models.SHOP_STATUS_PUBLISHED
        self.shop.save()

        shop2.status = models.SHOP_STATUS_PUBLISHED
        self.shop.save()



        pt31 = ProductType.objects.create(title='level31', parent=self.pt2, alias='test_alias_31')


        self.product1.filter_values.add(self.color_green)
        models.FilterValueToProductType.objects.create(product_type=self.pt1, filter_type=models.FILTER_TYPE_COLOR)
        models.FilterValueToProductType.objects.create(product_type=self.pt2, filter_type=models.FILTER_TYPE_COLOR)
        models.FilterValueToProductType.objects.create(product_type=self.pt3, filter_type=models.FILTER_TYPE_COLOR)


        models.Subscription.objects.create(start_date=self.today,
                                                           end_date=self.today + timezone.timedelta(days=30),
                                                           user=self.simple_user,
                                                           shop=shop1,
                                                           subscription_type=self.subscription_type,
                                                           )


        models.Subscription.objects.create(start_date=self.today,
                                                           end_date=self.today + timezone.timedelta(days=30),
                                                           user=self.simple_user,
                                                           shop=shop2,
                                                           subscription_type=self.subscription_type,
                                                           )

        product31 = Product.objects.create(title='Test', body='Test', normal_price=10000, stock_price=9000,
                                     start_date=self.today,
                                     end_date=self.today + timezone.timedelta(days=5),
                                     code=models.Product.generate_unique_code(), product_type=pt31, shop=shop1, brand=brand1,
                                     )

        product32 = Product.objects.create(title='Test', body='Test', normal_price=500, stock_price=250,
                                     start_date=self.today,
                                     end_date=self.today + timezone.timedelta(days=5),
                                     code=models.Product.generate_unique_code(), product_type=pt31, shop=shop2, brand=brand2,
                                     )


        models.FilterValueToProductType.objects.create(product_type=self.pt1, filter_type=models.FILTER_TYPE_SIZE_WOMAN)
        models.FilterValueToProductType.objects.create(product_type=self.pt2, filter_type=models.FILTER_TYPE_SIZE_WOMAN)
        models.FilterValueToProductType.objects.create(product_type=self.pt3, filter_type=models.FILTER_TYPE_SIZE_WOMAN)

        product31.status = models.STATUS_PUBLISHED
        product31.title = 'dsfghy4w5yhshgfhdfghdgfh'
        product31.save(do_clean=False, check_status=False)

        product32.status = models.STATUS_PUBLISHED
        product32.title = 'fdgh56eh35hrthe56y356jututyut'
        product32.save(do_clean=False, check_status=False)


        self.product1.status = models.STATUS_PUBLISHED
        self.product1.title = 'fsdlkjhgf597h8r7ehgo8dfgd58h7'
        self.product1.save(do_clean=False, check_status=False)

        self.product2.status = models.STATUS_PUBLISHED
        self.product2.title = 'gijrgw9854g9sd8ghosidfilg'
        self.product2.save(do_clean=False, check_status=False)

        self.product3.status = models.STATUS_PUBLISHED
        self.product3.title = 'gdfskbg5ygh87548gbrbgsdf'
        self.product3.save(do_clean=False, check_status=False)

        self.product4.status = models.STATUS_PUBLISHED
        self.product4.title = 'dsfgsdgddfshgffskbg5ygh8754dfghddfghfgh8gbrbgfghsdf'
        self.product4.save(do_clean=False, check_status=False)

        self.product5.status = models.STATUS_PUBLISHED
        self.product5.title = 'sgfh65ehhfdgjrtjgfyhjgh'
        self.product5.save(do_clean=False, check_status=False)

        self.product2.filter_values.add(self.color_green)
        self.product3.filter_values.add(self.color_green)

        self.product4.filter_values.add(self.color_red)
        self.product5.filter_values.add(self.color_red)

        product31.filter_values.add(self.color_green)
        product31.filter_values.add(self.color_red)

        product32.filter_values.add(self.color_green)
        product32.filter_values.add(self.color_red)

        self.product2.filter_values.add(self.dress_size_42)
        self.product3.filter_values.add(self.dress_size_42)
        self.product4.filter_values.add(self.dress_size_42)
        self.product5.filter_values.add(self.dress_size_42)

        product31.filter_values.add(self.dress_size_42)
        product31.filter_values.add(self.dress_size_44)

        product32.filter_values.add(self.dress_size_42)
        product32.filter_values.add(self.dress_size_44)


        self.renew_app()
        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt2.pk}))
        self.assertIn(product31.title, page)
        self.assertIn(product32.title, page)
        self.assertIn(self.product1.title, page)
        self.assertIn(self.product2.title, page)
        self.assertIn(self.product3.title, page)
        self.assertIn(self.product4.title, page)
        self.assertIn(self.product5.title, page)

        form = page.forms['product_list_filter_form']
        form.fields['brand'][0].checked = True
        brand_pk = form.fields['brand'][0]._value
        brand = models.Brand.objects.get(pk=brand_pk)
        page = form.submit()
        products = models.Product.objects.filter(brand=brand, status=models.STATUS_PUBLISHED)
        self.assertEquals(products.count(), 5)
        for product in products.all():
            self.assertIn(product.title, page)

        products = models.Product.objects.filter(status=models.STATUS_PUBLISHED).exclude(brand=brand)
        self.assertEquals(products.count(), 2)
        for product in products.all():
            self.assertNotIn(product.title, page)

        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt2.pk}))
        form = page.forms['product_list_filter_form']
        form.fields['colors'][0].checked = True
        color_pk = form.fields['colors'][0]._value
        color = models.FilterValue.objects.get(pk=color_pk)
        page = form.submit()

        products = models.Product.objects.filter(filter_values=color, status=models.STATUS_PUBLISHED).distinct()
        count1 = products.count()
        #self.assertEquals(, 5)
        for product in products.all():
            self.assertIn(product.title, page)

        products = models.Product.objects.filter(status=models.STATUS_PUBLISHED).exclude(filter_values=color).distinct()
        count2 = products.count()

        for product in products.all():
            self.assertNotIn(product.title, page)

        self.assertEquals(count1 + count2, 7)
        self.assertGreater(count1, 0)
        self.assertGreater(count2, 0)


        form.fields['colors'][1].checked = True
        page = form.submit()
        self.assertIn(product31.title, page)
        self.assertIn(product32.title, page)
        self.assertIn(self.product1.title, page)
        self.assertIn(self.product2.title, page)
        self.assertIn(self.product3.title, page)
        self.assertIn(self.product4.title, page)
        self.assertIn(self.product5.title, page)


        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt2.pk}))
        form = page.forms['product_list_filter_form']
        form.fields['sizes_woman'][0].checked = True
        size_pk = form.fields['sizes_woman'][0]._value
        size = models.FilterValue.objects.get(pk=size_pk)
        page = form.submit()

        products = models.Product.objects.filter(filter_values=size, status=models.STATUS_PUBLISHED).distinct()
        count1 = products.count()
        #self.assertEquals(, 5)
        for product in products.all():
            self.assertIn(product.title, page)

        products = models.Product.objects.filter(status=models.STATUS_PUBLISHED).exclude(filter_values=size).distinct()
        count2 = products.count()

        for product in products.all():
            self.assertNotIn(product.title, page)

        self.assertEquals(count1 + count2, 7)
        self.assertGreater(count1, 0)
        self.assertGreater(count2, 0)

        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt2.pk}))
        form = page.forms['product_list_filter_form']
        form.fields['shop'][0].checked = True
        shop_pk = form.fields['shop'][0]._value
        shop = models.Shop.objects.get(pk=shop_pk)
        page = form.submit()

        products = models.Product.objects.filter(shop=shop, status=models.STATUS_PUBLISHED).distinct()
        count1 = products.count()
        #self.assertEquals(, 5)
        for product in products.all():
            self.assertIn(product.title, page)

        products = models.Product.objects.filter(status=models.STATUS_PUBLISHED).exclude(shop=shop).distinct()
        count2 = products.count()

        for product in products.all():
            self.assertNotIn(product.title, page)

        self.assertEquals(count1 + count2, 7)
        self.assertGreater(count1, 0)
        self.assertGreater(count2, 0)


        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt2.pk}))
        form = page.forms['product_list_filter_form']
        form.fields['product_type'][0].checked = True
        product_type_pk = form.fields['product_type'][0]._value
        product_type = models.ProductType.objects.get(pk=product_type_pk)
        page = form.submit()

        products = models.Product.objects.filter(product_type=product_type, status=models.STATUS_PUBLISHED).distinct()
        count1 = products.count()
        #self.assertEquals(, 5)
        for product in products.all():
            self.assertIn(product.title, page)

        products = models.Product.objects.filter(status=models.STATUS_PUBLISHED).exclude(product_type=product_type).distinct()
        count2 = products.count()

        for product in products.all():
            self.assertNotIn(product.title, page)

        self.assertEquals(count1 + count2, 7)
        self.assertGreater(count1, 0)
        self.assertGreater(count2, 0)


        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt2.pk}))
        form = page.forms['product_list_filter_form']
        form.fields['product_type'][0].checked = True
        form.fields['product_type'][1].checked = True
        page = form.submit()

        products = models.Product.objects.filter(status=models.STATUS_PUBLISHED).distinct()
        count = products.count()
        #self.assertEquals(, 5)
        for product in products.all():
            self.assertIn(product.title, page)
        self.assertEquals(count, 7)

        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt2.pk}))
        form = page.forms['product_list_filter_form']
        form.fields['product_type'][0].checked = False
        form.fields['product_type'][1].checked = False
        page = form.submit()

        products = models.Product.objects.filter(status=models.STATUS_PUBLISHED).distinct()
        count = products.count()
        #self.assertEquals(, 5)
        for product in products.all():
            self.assertIn(product.title, page)
        self.assertEquals(count, 7)


        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt2.pk}))
        form = page.forms['product_list_filter_form']
        form.fields['price_category'][0].checked = True
        price_category = form.fields['price_category'][0]._value
        page = form.submit()

        products = models.Product.objects.filter(price_category=price_category, status=models.STATUS_PUBLISHED).distinct()
        count1 = products.count()
        #self.assertEquals(, 5)
        for product in products.all():
            self.assertIn(product.title, page)

        products = models.Product.objects.filter(status=models.STATUS_PUBLISHED).exclude(price_category=price_category).distinct()
        count2 = products.count()

        for product in products.all():
            self.assertNotIn(product.title, page)

        self.assertEquals(count1 + count2, 7)
        self.assertGreater(count1, 0)
        self.assertGreater(count2, 0)


        page = self.app.get(reverse('discount:product-list', kwargs={'alias': self.pt2.pk}))
        form = page.forms['product_list_filter_form']
        form.fields['discount_category'][0].checked = True
        discount_category = form.fields['discount_category'][0]._value
        page = form.submit()

        products = models.Product.objects.filter(discount_category=discount_category, status=models.STATUS_PUBLISHED).distinct()
        count1 = products.count()
        #self.assertEquals(, 5)
        for product in products.all():
            self.assertIn(product.title, page)

        products = models.Product.objects.filter(status=models.STATUS_PUBLISHED).exclude(discount_category=discount_category).distinct()
        count2 = products.count()

        for product in products.all():
            self.assertNotIn(product.title, page)

        self.assertEquals(count1 + count2, 7)
        self.assertGreater(count1, 0)
        self.assertGreater(count2, 0)
        
        self.product1.status = models.STATUS_SUSPENDED
        self.product1.save(do_clean=False, check_status=False)

        self.renew_app()
        page = self.app.get(reverse('discount:product-list-shop'), user=self.user)
        form = page.forms['product_list_filter_form']
        form.fields['status'][0].checked = True
        status = form.fields['status'][0]._value
        page = form.submit()

        products = models.Product.objects.filter(status=status, shop=self.user.get_shop).distinct()
        count1 = products.count()
        #self.assertEquals(, 5)
        for product in products.all():
            self.assertIn(product.title, page)

        products = models.Product.objects.filter(shop=self.user.get_shop).exclude(status=status).distinct()
        count2 = products.count()

        for product in products.all():
            self.assertNotIn(product.title, page)

        self.assertEquals(count1 + count2, 6)
        self.assertGreater(count1, 0)
        self.assertGreater(count2, 0)




class ProductTatamoManagerApproveTest(BaseTest):

    def test_tatamo_manager_can_use_form_and_simple_user_cant(self):
        tatamo_user = self.simple_user
        profile = tatamo_user.profile
        profile.role = models.USER_ROLE_TATAMO_MANAGER
        profile.save()

        product1 = self.product1
        product2 = self.product2

        product1.status = models.STATUS_TO_APPROVE
        product1.save(check_status=False, do_clean=False)

        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': product1.pk}), user=self.user)
        self.assertNotIn('product-tatamo-manager-approve-form-{0}'.format(product1.pk), page.forms)

        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': product1.pk}))
        self.assertNotIn('product-tatamo-manager-approve-form-{0}'.format(product1.pk), page.forms)

        self.renew_app()
        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': product1.pk}), user=tatamo_user)
        form = page.forms['product-tatamo-manager-approve-form-{0}'.format(product1.pk)]
        form['tatamo_comment'] = 'dfgjkhdfgkdkfgdf'
        form['status'] = str(models.STATUS_NEED_REWORK)
        page = form.submit()
        product1 = product1.saved_version
        self.assertEquals(page.status_code, 302)
        self.assertEquals(product1.status, models.STATUS_NEED_REWORK)
        self.assertEquals(product1.tatamo_comment, 'dfgjkhdfgkdkfgdf')

        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': product2.pk}), user=tatamo_user)
        self.assertNotIn('product-tatamo-manager-approve-form-{0}'.format(product2.pk), page.forms)

        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': product1.pk}), user=tatamo_user)
        self.assertNotIn('product-tatamo-manager-approve-form-{0}'.format(product1.pk), page.forms)

        product1.status = models.STATUS_TO_APPROVE
        product1.save(do_clean=False, check_status=False)

        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': product1.pk}), user=tatamo_user)
        form = page.forms['product-tatamo-manager-approve-form-{0}'.format(product1.pk)]
        form['status'] = str(models.STATUS_APPROVED)
        page = form.submit()
        product1 = product1.saved_version
        self.assertEquals(page.status_code, 302)
        self.assertEquals(product1.status, models.STATUS_APPROVED)
        self.assertEquals(product1.tatamo_comment, 'dfgjkhdfgkdkfgdf')




class TestBrandNameIsUnique(BaseTest):
    def test_brand_name_is_unique(self):
        brand1 = models.Brand.objects.create(title='Test brand')
        with self.assertRaises(ValidationError):
            brand2 = models.Brand.objects.create(title='Test brand')

        with self.assertRaises(ValidationError):
            brand2 = models.Brand.objects.create(title='test Brand')


class TestAbstractTitleMixin(BaseTest):
    def test_brand_title_strip(self):
        brand1 = models.Brand.objects.create(title='   Test brand  ')
        self.assertEquals(brand1.title, 'Test brand')


    def test_shop_title_strip(self):
        shop = models.Shop.objects.create(title='   Магазин1    ', status=models.SHOP_STATUS_PROJECT, image=models.Product.generate_unique_code())
        self.assertEquals(shop.title, 'Магазин1')

    def test_product_title_strip(self):
        product = Product.objects.create(title='       Test        ', body='Test', normal_price=500, stock_price=250,
                                     start_date=self.today,
                                     end_date=self.today + timezone.timedelta(days=5),
                                     code=models.Product.generate_unique_code(), product_type=self.pt3, shop=self.shop, brand=self.brand,
                                     )
        self.assertEquals(product.title, 'Test')



class TestAdminMonitorAndMail(BaseTest):
    def setUp(self):
        super().setUp()
        self.admin = User.objects.create_user(
                username='alesdfgx', email='alex@sdgalex.ru', password='tsdfgop_secret')
        profile = self.admin.profile
        profile.role = models.USER_ROLE_TATAMO_MANAGER
        profile.save()

    def test_admin_monitor_product(self):
        product = self.product1
        product.status = models.STATUS_PUBLISHED
        product.save(do_clean=False, check_status=False)

        user = self.admin
        page = self.app.get(reverse('discount:monitor'), user=user)
        self.assertNotIn(product.title, page)

        product.status = models.STATUS_TO_APPROVE
        product.save(do_clean=False, check_status=False)

        user = self.admin
        page = self.app.get(reverse('discount:monitor'), user=user)
        self.assertIn(product.title, page)


    def test_admin_monitor_shop(self):
        shop = models.Shop.objects.create(title='21sdghdfsdfgdfgsd', image='sdgdfsgdfg')
        user = self.admin
        page = self.app.get(reverse('discount:monitor'), user=user)
        self.assertNotIn(shop.title, page)

        shop.status = models.SHOP_STATUS_TO_APPROVE
        shop.save(do_clean=False, check_status=False)

        user = self.admin
        page = self.app.get(reverse('discount:monitor'), user=user)
        self.assertIn(shop.title, page)


    def test_admin_monitor_banner(self):
        banner = models.ProductBanner.objects.create(product=self.product1, banner='sdfsdgdfgsdf', shop_comment='sdfgdfga543', status=models.BANNER_STATUS_NEED_REWORK)
        user = self.admin
        page = self.app.get(reverse('discount:monitor'), user=user)
        self.assertNotIn(str(banner), page)

        banner.status = models.BANNER_STATUS_ON_APPROVE
        banner.save()

        user = self.admin
        page = self.app.get(reverse('discount:monitor'), user=user)
        self.assertIn(str(banner), page)


    def test_admin_monitor_contact_form(self):
        contact_form = ContactForm.objects.create(name='fgsdfg', email='sdfsdf@sdgkh.ru', body='sdfsdfgdfg')
        user = self.admin
        page = self.app.get(reverse('discount:monitor'), user=user)
        self.assertIn(str(contact_form), page)

        contact_form.status = STATUS_CHECKED
        contact_form.save()

        user = self.admin
        page = self.app.get(reverse('discount:monitor'), user=user)
        self.assertNotIn(str(contact_form), page)

    def test_admin_monitor_changer(self):
        changer = models.ProductChanger.objects.create(product=self.product,
                                                       body='123123',
                                                       status=models.STATUS_PROJECT,
                                                       brand=self.brand,
                                                       product_type=self.pt3,
                                                       normal_price=100,
                                                       stock_price=20,
                                                       )
        user = self.admin
        page = self.app.get(reverse('discount:monitor'), user=user)
        self.assertNotIn(str(changer), page)

        changer.status = models.STATUS_TO_APPROVE
        changer.save()

        user = self.admin
        page = self.app.get(reverse('discount:monitor'), user=user)
        self.assertIn(str(changer), page)


    def test_admin_mail_no_repeated_mail(self):
        user = self.admin
        product = self.product1
        product.status = models.STATUS_TO_APPROVE
        product.save(do_clean=False, check_status=False)

        shop = models.Shop.objects.create(title='21sdghdfsdfgdfgsd', image='sdgdfsgdfg')
        shop.status = models.SHOP_STATUS_TO_APPROVE
        shop.save(do_clean=False, check_status=False)

        banner = models.ProductBanner.objects.create(product=self.product1, banner='sdfsdgdfgsdf', shop_comment='sdfgdfga543', status=models.BANNER_STATUS_ON_APPROVE)

        contact_form = ContactForm.objects.create(name='fgsdfg', email='sdfsdf@sdgkh.ru', body='sdfsdfgdfg')

        changer = models.ProductChanger.objects.create(product=self.product,
                                                       body='123123',
                                                       status=models.STATUS_PROJECT,
                                                       brand=self.brand,
                                                       product_type=self.pt3,
                                                       normal_price=100,
                                                       stock_price=20,
                                                       )
        changer.status = models.STATUS_TO_APPROVE
        changer.save()



        message = tasks._admin_monitor()
        self.assertEquals(message, 'Акций: 1\n Баннеров: 1\n Магазинов: 1\n Заявок: 1\n Контактных форм: 1')

        message = tasks._admin_monitor()
        self.assertEquals(message, None)

        message = tasks._admin_monitor()
        self.assertEquals(message, None)

        product2 = self.product2
        product2.status = models.STATUS_TO_APPROVE
        product2.save(do_clean=False, check_status=False)

        product.body += 'fsdfsdf'
        product.save(do_clean=False, check_status=False)

        message = tasks._admin_monitor()
        self.assertEquals(message, 'Акций: 2\n Баннеров: 1\n Магазинов: 1\n Заявок: 1\n Контактных форм: 1')

        message = tasks._admin_monitor()
        self.assertEquals(message, None)

        message = tasks._admin_monitor()
        self.assertEquals(message, None)


class TestProductShopBannerImageThumbs(BaseTest):
    def setUp(self):
        super().setUp()
        save_path = os.path.join(settings.MEDIA_ROOT, 'discount_product')
        self.storage = FileSystemStorage(save_path)

    def test_product_image(self):
        u = models.User.objects.get(username='alex')
        product = self.product1


        page = self.app.get(reverse('discount:product-update', kwargs={'pk': product.pk}), user=u)
        form = page.forms['product-create-form']
        path = TEST_IMAGE_PATH
        f = open(path, 'rb')
        form['images-0-image'] = ('images-0-image', f.read())
        models.FilterValueToProductType.objects.filter(product_type=self.pt1).delete()
        page = form.submit(name='to-save')
        self.assertEquals(page.status_code, 302)

        save_path = os.path.join(settings.MEDIA_ROOT, 'discount_product')
        storage = FileSystemStorage(save_path)
        image = product.images.latest('created').image

        for key in settings.PRODUCT_THUMB_SETTINGS:
            thumb_path = os.path.split(getattr(image, key))
            thumb_path = os.path.join(key, thumb_path[-1])
            self.assertTrue(storage.exists(thumb_path))

    def test_shop_image(self):
        u = models.User.objects.get(username='alex')
        shop = self.shop

        page = self.app.get(reverse('discount:shop-update', kwargs={'pk': shop.pk}), user=u)
        form = page.forms['shop-create-form']
        path = TEST_IMAGE_PATH
        f = open(path, 'rb')
        form['image'] = ('image', f.read())
        page = form.submit(name='to-save')
        self.assertEquals(page.status_code, 302)

        save_path = os.path.join(settings.MEDIA_ROOT, 'discount_shop')
        storage = FileSystemStorage(save_path)
        shop = shop.saved_version
        image = shop.image

        for key in settings.SHOP_THUMB_SETTINGS:
            thumb_path = os.path.split(getattr(image, key))
            thumb_path = os.path.join(key, thumb_path[-1])
            self.assertTrue(storage.exists(thumb_path))

    def test_banner_image(self):
        u = models.User.objects.get(username='alex')
        product = self.product1

        page = self.app.get(reverse('discount:product-banners', kwargs={'pk': product.pk}), user=u)
        form = page.forms['product-banners-form']
        f = open(TEST_IMAGE_PATH, 'rb')
        form['productbanner_set-0-banner'] = ('images-0-image', f.read())
        #form['productbanner_set-0-start'] = True
        shop_comment = 'авгыгшапвгшапрвагшпврагшпрвашгп2324пваып545н'
        form['productbanner_set-0-shop_comment'] = shop_comment

        page = form.submit()

        banner = models.ProductBanner.objects.latest('created')

        save_path = os.path.join(settings.MEDIA_ROOT, 'discount_product_banner')
        storage = FileSystemStorage(save_path)
        image = banner.banner

        for key in settings.PRODUCT_BANNER_THUMB_SETTINGS:
            thumb_path = os.path.split(getattr(image, key))
            thumb_path = os.path.join(key, thumb_path[-1])
            self.assertTrue(storage.exists(thumb_path))


class TestSubsribedToProductView(BaseTest):
    def setUp(self):
        super().setUp()
        self.user1 = User.objects.create_user(
                username='aledfjghfjx1', email='alfdsgfhjgdfex@alex.ru', password='top_secret', first_name='dsfgdsfg5y5647685678567')
        self.user2 = User.objects.create_user(
                username='gsdfalex1', email='alfdsgdfdsfgex@alex.ru', password='top_secret', first_name='dfghs56he567h6767')
        self.user3 = User.objects.create_user(
                username='gsdfaldfsdfgsgex1', email='alfdsgsdgfdsdfgfdsfgex@alex.ru', password='top_secret', first_name='g5wtrghehtyhrtyjrtyj')
        self.user4 = User.objects.create_user(
                username='gsdfsdfgaldfsgex1', email='alfdsgssfddgfdfdsfgex@alex.ru', password='top_secret', first_name='dfh56ehe556hwhdfghdfghdfgh')
        self.user5 = User.objects.create_user(
                username='gsdsfgdfaldfsgex1', email='alfsdfgdsgsdgfdfdsfgex@alex.ru', password='top_secret', first_name='56y356h56eh56htherhrt')
        self.user6 = User.objects.create_user(
                username='gsdfaldfsgndgfex1', email='alfddfghsgsdgfdfdsfgex@alex.ru', password='top_secret', first_name='rwtyw54y4y3y34y54y')

        models.Subscription.objects.create(start_date=self.today,
                                                           end_date=self.today + timezone.timedelta(days=30),
                                                           user=self.user,
                                                           shop=self.user.get_shop,
                                                           subscription_type=self.subscription_type,
                                                           )
        self.product.status = models.STATUS_PUBLISHED
        self.product.save(do_clean=False, check_status=False)

    def test_cart_action(self):

        product = self.product

        user = self.user

        ptc1 = models.ProductToCart.objects.create(user=self.user1, product=product, status=models.PTC_STATUS_CART)
        ptc2 = models.ProductToCart.objects.create(user=self.user2, product=product, status=models.PTC_STATUS_CART)

        page = self.app.get(reverse('discount:cart_to_product', kwargs={'pk': product.pk}), user=user)
        self.assertIn(self.user1.first_name, page)
        self.assertIn(self.user2.first_name, page)
        self.assertNotIn(self.user3.first_name, page)
        self.assertNotIn(self.user4.first_name, page)
        self.assertNotIn(self.user5.first_name, page)
        self.assertNotIn(self.user6.first_name, page)

    def test_subscribed_action(self):

        product = self.product

        user = self.user

        ptc1 = models.ProductToCart.objects.create(user=self.user3, product=product, status=models.PTC_STATUS_SUBSCRIBED)
        ptc2 = models.ProductToCart.objects.create(user=self.user4, product=product, status=models.PTC_STATUS_SUBSCRIBED)

        page = self.app.get(reverse('discount:subscribed_to_product', kwargs={'pk': product.pk}), user=user)
        self.assertNotIn(self.user1.first_name, page)
        self.assertNotIn(self.user2.first_name, page)
        self.assertIn(self.user3.first_name, page)
        self.assertIn(self.user4.first_name, page)
        self.assertNotIn(self.user5.first_name, page)
        self.assertNotIn(self.user6.first_name, page)

    def test_bought_action(self):

        product = self.product

        user = self.user

        ptc1 = models.ProductToCart.objects.create(user=self.user5, product=product, status=models.PTC_STATUS_BOUGHT)
        ptc2 = models.ProductToCart.objects.create(user=self.user6, product=product, status=models.PTC_STATUS_BOUGHT)

        page = self.app.get(reverse('discount:bought_to_product', kwargs={'pk': product.pk}), user=user)
        self.assertNotIn(self.user1.first_name, page)
        self.assertNotIn(self.user2.first_name, page)
        self.assertNotIn(self.user3.first_name, page)
        self.assertNotIn(self.user4.first_name, page)
        self.assertIn(self.user5.first_name, page)
        self.assertIn(self.user6.first_name, page)

class AccountTests(BaseTest):
    def test_discount_change_password(self):
        u = self.user
        page = self.app.get(reverse('discount:change-password'), user=u)
        form = page.forms['password_change']
        form['oldpassword'] = self.user_password
        old_password = self.user_password
        password = 'fkdjshaf847f4'
        form['password1'] = password
        form['password2'] = password
        page = form.submit().follow()
        u = models.User.objects.get(pk=u.pk)
        self.assertNotEquals(u.password, old_password)
        self.assertIn('Информация о пользователе', page)

        page = self.app.get(reverse('account_logout'), user=u).follow()

        self.renew_app()
        page = self.app.get(reverse('discount:full-login'))
        form = page.forms['login-form']

        form['login'] = u.username
        form['password'] = password
        page = form.submit().follow()
        u = models.User.objects.get(pk=u.pk)
        self.assertIn('Информация о пользователе', page)


class ProductTypeTest(BaseTest):
    def test_filter_values_to_product_type_applied_to_childs_only(self):
        pt0 = self.pt0
        pt1 = self.pt1
        pt2 = self.pt2
        pt3 = self.pt3

        models.FilterValueToProductType.objects.all().delete()

        pt11 = ProductType.objects.create(title='level11', parent=self.pt0, alias='test_alias_11')
        pt21 = ProductType.objects.create(title='level21', parent=pt11, alias='test_alias_21')
        pt31 = ProductType.objects.create(title='level31', parent=pt21, alias='test_alias_31')

        models.FilterValueToProductType.objects.create(product_type=pt1, filter_type=models.FILTER_TYPE_SIZE_CHILDS)
        #pt1.save()

        self.assertEqual(pt1.filtervaluetoproducttype_set.all().count(), 1)
        self.assertEqual(pt2.filtervaluetoproducttype_set.all().count(), 1)
        self.assertEqual(pt3.filtervaluetoproducttype_set.all().count(), 1)
        self.assertEqual(pt0.filtervaluetoproducttype_set.all().count(), 0)
        self.assertEqual(pt11.filtervaluetoproducttype_set.all().count(), 0)
        self.assertEqual(pt21.filtervaluetoproducttype_set.all().count(), 0)
        self.assertEqual(pt31.filtervaluetoproducttype_set.all().count(), 0)

        models.FilterValueToProductType.objects.create(product_type=pt21, filter_type=models.FILTER_TYPE_SIZE_WOMAN)
        #pt21.save()

        self.assertEqual(pt1.filtervaluetoproducttype_set.all().count(), 1)
        self.assertEqual(pt2.filtervaluetoproducttype_set.all().count(), 1)
        self.assertEqual(pt3.filtervaluetoproducttype_set.all().count(), 1)
        self.assertEqual(pt0.filtervaluetoproducttype_set.all().count(), 0)
        self.assertEqual(pt11.filtervaluetoproducttype_set.all().count(), 0)
        self.assertEqual(pt21.filtervaluetoproducttype_set.all().count(), 1)
        self.assertEqual(pt31.filtervaluetoproducttype_set.all().count(), 0)

        pt21.share_filter_params = False
        #pt21.save()

        self.assertEqual(pt1.filtervaluetoproducttype_set.all().count(), 1)
        self.assertEqual(pt2.filtervaluetoproducttype_set.all().count(), 1)
        self.assertEqual(pt3.filtervaluetoproducttype_set.all().count(), 1)
        self.assertEqual(pt0.filtervaluetoproducttype_set.all().count(), 0)
        self.assertEqual(pt11.filtervaluetoproducttype_set.all().count(), 0)
        self.assertEqual(pt21.filtervaluetoproducttype_set.all().count(), 1)
        self.assertEqual(pt31.filtervaluetoproducttype_set.all().count(), 0)

from discount import tasks
class TasksTests(BaseTest):
    def test_start_ready_products(self):
        self.subscription_type.max_products = 2
        self.subscription_type.save()
        models.Subscription.objects.create(start_date=self.today,
                                                           end_date=self.today + timezone.timedelta(days=30),
                                                           user=self.user,
                                                           shop=self.shop,
                                                           subscription_type=self.subscription_type,
                                                           )

        self.product1.status = models.STATUS_READY
        self.product2.status = models.STATUS_PUBLISHED
        self.product3.status = models.STATUS_READY
        self.product1.start_date = self.today
        self.product1.end_date = self.today
        self.product2.start_date = self.today
        self.product2.end_date = self.today
        self.product3.start_date = self.today + timezone.timedelta(days=1)
        self.product3.end_date = self.today + timezone.timedelta(days=1)


        self.product1.save(check_status=False, do_clean=False)
        self.product2.save(check_status=False, do_clean=False)
        self.product3.save(check_status=False, do_clean=False)

        self.assertEqual(self.product1.status, models.STATUS_READY)
        self.assertEqual(self.product2.status, models.STATUS_PUBLISHED)
        self.assertEqual(self.product3.status, models.STATUS_READY)

        tasks._start_ready_products()

        p1 = self.product1.saved_version
        p2 = self.product2.saved_version
        p3 = self.product3.saved_version

        self.assertEqual(p1.status, models.STATUS_PUBLISHED)
        self.assertEqual(p2.status, models.STATUS_PUBLISHED)
        self.assertEqual(p3.status, models.STATUS_READY)

    def test_suspend_expired_products(self):
        p1 = self.product1
        p2 = self.product2
        p3 = self.product3
        p4 = self.product4

        p1.start_date = self.today - timezone.timedelta(days=5)
        p2.start_date = self.today - timezone.timedelta(days=1)

        p1.end_date = self.today - timezone.timedelta(days=2)
        p2.end_date = self.today - timezone.timedelta(days=1)

        p3.start_date = self.today - timezone.timedelta(days=2)
        p3.end_date = self.today + timezone.timedelta(days=5)
        p3.status = models.STATUS_PUBLISHED
        p3.save(do_clean=False, check_status=False)

        p4.start_date = self.today + timezone.timedelta(days=2)
        p4.end_date = self.today + timezone.timedelta(days=5)
        p4.status = models.STATUS_READY
        p4.save(do_clean=False, check_status=False)


        p1.status = models.STATUS_PUBLISHED
        p1.save(check_status=False, do_clean=False)
        p2.save(check_status=False, do_clean=False)

        rows = models.Product.objects.filter(pk=p2.pk).update(status=models.STATUS_READY)
        self.assertEqual(rows, 1)
        p2 = p2.saved_version
        self.assertEqual(p1.status, models.STATUS_PUBLISHED)
        self.assertEqual(p2.status, models.STATUS_READY)

        message = tasks._suspend_expired_products()
        self.assertIn('1', message)

        p1 = p1.saved_version
        p2 = p2.saved_version
        p3 = p3.saved_version
        p4 = p4.saved_version

        self.assertEqual(p1.status, models.STATUS_SUSPENDED)
        self.assertEqual(p2.status, models.STATUS_NEED_REWORK)
        self.assertEqual(p3.status, models.STATUS_PUBLISHED)
        self.assertEqual(p4.status, models.STATUS_READY)

    def test_save_product_storages(self):
        p = self.product
        pt = p.product_type
        s = p.shop
        b = p.brand

        self.assertIn(p.pk, pt.all_products_pks) #3
        self.assertIn(p.pk, pt.parent.all_products_pks) #2
        self.assertIn(p.pk, pt.parent.parent.all_products_pks) #1
        self.assertIn(p.pk, pt.parent.parent.parent.all_products_pks) #0

        self.assertIn(p.pk, b.all_products_pks)
        self.assertIn(p.pk, s.all_products_pks)

        models.ProductType.objects.all().update(all_products_pks='[]')
        models.Brand.objects.all().update(all_products_pks='[]')
        models.Shop.objects.all().update(all_products_pks='[]')
        pt = pt.saved_version
        b = b.saved_version
        s = s.saved_version

        self.assertNotIn(p.pk, pt.all_products_pks) #3
        self.assertNotIn(p.pk, pt.parent.all_products_pks) #2
        self.assertNotIn(p.pk, pt.parent.parent.all_products_pks) #1
        self.assertNotIn(p.pk, pt.parent.parent.parent.all_products_pks) #0

        self.assertNotIn(p.pk, b.all_products_pks)
        self.assertNotIn(p.pk, s.all_products_pks)

        tasks._save_product_storages()

        pt = pt.saved_version
        b = b.saved_version
        s = s.saved_version

        self.assertIn(p.pk, pt.all_products_pks) #3
        self.assertIn(p.pk, pt.parent.all_products_pks) #2
        self.assertIn(p.pk, pt.parent.parent.all_products_pks) #1
        self.assertIn(p.pk, pt.parent.parent.parent.all_products_pks) #0

        self.assertIn(p.pk, b.all_products_pks)
        self.assertIn(p.pk, s.all_products_pks)

class ShopMethodsAdditionalTests(BaseTest):
    def test_shop_show_link(self):
        s = self.shop

        s.site = 'test.ru'
        s.save()
        self.assertEqual(s.show_link, True)

        s.site = 'www.test.ru'
        s.save()
        self.assertEqual(s.show_link, True)

        s.site = 'http://www.test.ru'
        s.save()
        self.assertEqual(s.show_link, True)

        s.site = 'https://www.test.ru'
        s.save()
        self.assertEqual(s.show_link, True)

        s.site = ''
        s.save()
        self.assertEqual(s.show_link, False)

        s.site = 'test.ru, test1.ru'
        s.save()
        self.assertEqual(s.show_link, False)

        s.site = 'test.ru,test1.ru'
        s.save()
        self.assertEqual(s.show_link, False)

        s.site = 'test.ru;test1.ru'
        s.save()
        self.assertEqual(s.show_link, False)

        s.site = 'test.ru test1.ru'
        s.save()
        self.assertEqual(s.show_link, False)

    def test_site_attr_is_stripped(self):
        s = self.shop
        s.site = '      test.ru    '
        s.save()
        self.assertEqual(s.site, 'test.ru')



class HelperTests(BaseTest):
    def test_get_link_test(self):
        link = ''
        link = helper.get_link(link)
        self.assertEqual(link, '')

        link = 'test.ru'
        link = helper.get_link(link)
        self.assertEqual(link, 'http://test.ru')

        link = 'http://test.ru'
        link = helper.get_link(link)
        self.assertEqual(link, 'http://test.ru')

        link = 'https://test.ru'
        link = helper.get_link(link)
        self.assertEqual(link, 'https://test.ru')

        link = 'https://test.ru, ag.ru'
        link = helper.get_link(link)
        self.assertEqual(link, 'https://test.ru, ag.ru')

        link = 'https://test.ru,ag.ru'
        link = helper.get_link(link)
        self.assertEqual(link, 'https://test.ru,ag.ru')

        link = 'https://test.ru;ag.ru'
        link = helper.get_link(link)
        self.assertEqual(link, 'https://test.ru;ag.ru')

        link = 'https://test.ru; ag.ru '
        link = helper.get_link(link)
        self.assertEqual(link, 'https://test.ru; ag.ru')

        link = 'https://test.ru ag.ru '
        link = helper.get_link(link)
        self.assertEqual(link, 'https://test.ru ag.ru')


class ProductStorageElemsTests(BaseTest):
    def test_change_product_type_is_ok(self):
        p = self.product1
        now_pt = p.product_type

        pt11 = ProductType.objects.create(title='level11', parent=self.pt0, alias='test_alias_11')
        pt21 = ProductType.objects.create(title='level21', parent=pt11, alias='test_alias_21')
        new_pt = ProductType.objects.create(title='level31', parent=pt21, alias='test_alias_31')

        self.assertIn(p.pk, now_pt.all_products_pks) #3
        self.assertIn(p.pk, now_pt.parent.all_products_pks) #2
        self.assertIn(p.pk, now_pt.parent.parent.all_products_pks) #1
        self.assertIn(p.pk, now_pt.parent.parent.parent.all_products_pks) #0


        p.product_type = new_pt
        p.save()
        now_pt = now_pt.saved_version
        new_pt = new_pt.saved_version
        self.assertIn(p.pk, new_pt.all_products_pks) #3
        self.assertIn(p.pk, new_pt.parent.all_products_pks) #2
        self.assertIn(p.pk, new_pt.parent.parent.all_products_pks) #1
        self.assertIn(p.pk, new_pt.parent.parent.parent.all_products_pks) #0

        self.assertNotIn(p.pk, now_pt.all_products_pks) #3
        self.assertNotIn(p.pk, now_pt.parent.all_products_pks) #2
        self.assertNotIn(p.pk, now_pt.parent.parent.all_products_pks) #1
        self.assertIn(p.pk, now_pt.parent.parent.parent.all_products_pks) #0


    def test_change_brand_is_ok(self):
        p = self.product1
        now_brand = p.brand

        new_brand = models.Brand.objects.create(title='Бреdfhdfhfgdhнд12345')
        models.ShopsToBrands.objects.create(shop=self.shop, brand=new_brand)


        self.assertIn(p.pk, now_brand.all_products_pks)


        p.brand = new_brand
        p.save()
        now_brand = now_brand.saved_version
        new_brand = new_brand.saved_version
        self.assertIn(p.pk, new_brand.all_products_pks)

        self.assertNotIn(p.pk, now_brand.all_products_pks)

    def test_change_shop_is_ok(self):
        p = self.product1
        now_shop = p.shop

        new_shop = models.Shop.objects.create(title='Магазиdsfgdfgн1', status=models.SHOP_STATUS_PROJECT, image=models.Product.generate_unique_code())
        models.ShopsToBrands.objects.create(shop=new_shop, brand=self.brand)
        new_shop.status = models.SHOP_STATUS_PUBLISHED
        new_shop.save()

        self.assertIn(p.pk, now_shop.all_products_pks)

        p.shop = new_shop
        p.save()
        now_shop = now_shop.saved_version
        new_shop = new_shop.saved_version
        self.assertIn(p.pk, new_shop.all_products_pks)

        self.assertNotIn(p.pk, now_shop.all_products_pks)

class PromoCodeTests(BaseTest):
    def setUp(self):
        super().setUp()
        models.Subscription.objects.create(start_date=self.today,
                                                               end_date=self.today + timezone.timedelta(days=30),
                                                               user=self.user,
                                                               shop=self.shop,
                                                               subscription_type=self.subscription_type,
                                                               )

    def test_unique_promocode_with_postfix_works_fine(self):
        p = self.product1
        p.status = models.STATUS_PUBLISHED
        p.save(check_status=False)
        self.assertEqual(p.status, models.STATUS_PUBLISHED)
        u = self.simple_user

        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': self.product1.pk}), user=u)
        form = page.forms['ptc-subscribe-form-{0}'.format(p.pk)]
        form['submit-type'] = 'subscribe'
        page = form.submit()
        ptc = p.find_ptc_by_user(user=u)
        self.assertEqual(ptc.status, models.PTC_STATUS_SUBSCRIBED)
        self.assertEqual(ptc.promocode, '{0}-00000{1}'.format(p.code, ptc.code))
        page = self.app.get(reverse('discount:coupon-view', kwargs={'pk': p.pk, 'type': 'normal'}))
        self.assertIn(ptc.promocode, page)

    def test_unique_promocode_without_postfix_works_fine(self):
        p = self.product1
        p.status = models.STATUS_PUBLISHED
        p.use_code_postfix = False
        p.save(check_status=False)
        self.assertEqual(p.status, models.STATUS_PUBLISHED)
        u = self.simple_user

        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': self.product1.pk}), user=u)
        form = page.forms['ptc-subscribe-form-{0}'.format(p.pk)]
        form['submit-type'] = 'subscribe'
        page = form.submit()
        ptc = p.find_ptc_by_user(user=u)
        self.assertEqual(ptc.status, models.PTC_STATUS_SUBSCRIBED)
        self.assertEqual(ptc.promocode, p.code)
        page = self.app.get(reverse('discount:coupon-view', kwargs={'pk': p.pk, 'type': 'normal'}))
        self.assertIn(ptc.promocode, page)
        self.assertNotIn('-000001', page)


    def test_not_unique_promocode_with_postfix_works_fine(self):
        p = self.product1
        p.status = models.STATUS_PUBLISHED
        p.use_simple_code = True
        p.simple_code = 'sdfsdfsdfasdf1TZ'
        p.save(check_status=False)
        self.assertEqual(p.status, models.STATUS_PUBLISHED)
        u = self.simple_user

        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': self.product1.pk}), user=u)
        form = page.forms['ptc-subscribe-form-{0}'.format(p.pk)]
        form['submit-type'] = 'subscribe'
        page = form.submit()
        ptc = p.find_ptc_by_user(user=u)
        self.assertEqual(ptc.status, models.PTC_STATUS_SUBSCRIBED)
        self.assertEqual(ptc.promocode, '{0}-00000{1}'.format(p.simple_code, ptc.code))
        page = self.app.get(reverse('discount:coupon-view', kwargs={'pk': p.pk, 'type': 'normal'}))
        self.assertIn(ptc.promocode, page)


    def test_not_unique_promocode_without_postfix_works_fine(self):
        p = self.product1
        p.status = models.STATUS_PUBLISHED
        p.use_simple_code = True
        p.use_code_postfix = False
        p.simple_code = 'sdfsdfsdfasdf1TZ'
        p.save(check_status=False)
        self.assertEqual(p.status, models.STATUS_PUBLISHED)
        u = self.simple_user

        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': self.product1.pk}), user=u)
        form = page.forms['ptc-subscribe-form-{0}'.format(p.pk)]
        form['submit-type'] = 'subscribe'
        page = form.submit()
        ptc = p.find_ptc_by_user(user=u)
        self.assertEqual(ptc.status, models.PTC_STATUS_SUBSCRIBED)
        self.assertEqual(ptc.promocode, p.simple_code)
        page = self.app.get(reverse('discount:coupon-view', kwargs={'pk': p.pk, 'type': 'normal'}))
        self.assertIn(ptc.promocode, page)
        self.assertNotIn('-000001', page)

class WidgetsTests(BaseTest):
    def test_get_product_stats_for_period_no_cart(self):
        models.Subscription.objects.create(start_date=self.today,
                                                           end_date=self.today + timezone.timedelta(days=30),
                                                           user=self.user,
                                                           shop=self.shop,
                                                           subscription_type=self.subscription_type,
                                                           )

        p = self.product
        u = self.simple_user

        u1 = User.objects.create_user(
                username='asdfgdsfgl3434ex', email='asdfg43t34lex@alex.ru', password='dfsgdfg545454g')

        p.status = models.STATUS_PUBLISHED
        p.save(check_status=False, do_clean=False)


        page = self.app.post(reverse('discount:product-stat-save', kwargs={'pk': p.pk}), user=u)
        page = self.app.post(reverse('discount:product-stat-save', kwargs={'pk': p.pk}), user=u)

        self.renew_app()

        page = self.app.post(reverse('discount:product-stat-save', kwargs={'pk': p.pk}), user=u1)
        page = self.app.post(reverse('discount:product-stat-save', kwargs={'pk': p.pk}), user=u1)
        page = self.app.post(reverse('discount:product-stat-save', kwargs={'pk': p.pk}), user=u1)



        s = self.client.session
        s["expire_date"] = '2050-12-05'
        s["session_key"] = 'dfh463656356356'
        s.save()
        response = self.client.post(reverse('discount:product-stat-save', kwargs={'pk': p.pk}))
        response = self.client.post(reverse('discount:product-stat-save', kwargs={'pk': p.pk}))


        s = self.client.session
        s["expire_date"] = '2050-12-05'
        s["session_key"] = 'fhdfh635653567567'
        s.save()
        response = self.client.post(reverse('discount:product-stat-save', kwargs={'pk': p.pk}))
        ps = models.ProductStat.objects.filter(product=p).latest('created')
        ps.session_key = 'asg5w54gw45g45g'
        ps.save()
        #page = self.app.get(reverse('discount:product-detail', kwargs={'pk': p.pk}), user=u)
        #form = page.forms['ptc-subscribe-form-{0}'.format(p.pk)]
        #form['submit-type'] = 'subscribe'
        #page = form.submit()

        context = {
            'product': p,
            'start_date': self.today,
            'end_date': self.today,
        }

        res = discount_tags.get_product_stats_for_period(context, 'all_visits')
        self.assertEqual(res, 8)

        res = discount_tags.get_product_stats_for_period(context, 'user_visits')
        self.assertEqual(res, 5)

        res = discount_tags.get_product_stats_for_period(context, 'guest_visits')
        self.assertEqual(res, 3)

        res = discount_tags.get_product_stats_for_period(context, 'all_unique_visits')
        self.assertEqual(res, 4)

        res = discount_tags.get_product_stats_for_period(context, 'user_unique_visits')
        self.assertEqual(res, 2)

        res = discount_tags.get_product_stats_for_period(context, 'guest_unique_visits')
        self.assertEqual(res, 2)

        res = discount_tags.get_product_stats_for_period(context, 'carts')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'subscriptions')
        self.assertEqual(res, 0)


        context = {
                'product': p,
                'start_date': self.today + timezone.timedelta(days=1),
                'end_date': self.today + timezone.timedelta(days=1),
            }

        res = discount_tags.get_product_stats_for_period(context, 'all_visits')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'user_visits')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'guest_visits')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'all_unique_visits')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'user_unique_visits')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'guest_unique_visits')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'carts')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'subscriptions')
        self.assertEqual(res, 0)


        context = {
            'product': p,
            'start_date': self.today - timezone.timedelta(days=1),
            'end_date': self.today - timezone.timedelta(days=1),
        }

        res = discount_tags.get_product_stats_for_period(context, 'all_visits')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'user_visits')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'guest_visits')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'all_unique_visits')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'user_unique_visits')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'guest_unique_visits')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'carts')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'subscriptions')
        self.assertEqual(res, 0)



    def test_get_product_stats_for_period_cart(self):
        models.Subscription.objects.create(start_date=self.today,
                                                           end_date=self.today + timezone.timedelta(days=30),
                                                           user=self.user,
                                                           shop=self.shop,
                                                           subscription_type=self.subscription_type,
                                                           )

        p = self.product
        u = self.simple_user

        u1 = User.objects.create_user(
                username='asdfgdsfgl3434ex', email='asdfg43t34lex@alex.ru', password='dfsgdfg545454g')

        p.status = models.STATUS_PUBLISHED
        p.save(check_status=False, do_clean=False)

        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': p.pk}), user=u)
        form = page.forms['ptc-subscribe-form-{0}'.format(p.pk)]
        form['submit-type'] = 'subscribe'
        page = form.submit()

        self.renew_app()

        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': p.pk}), user=u1)
        form = page.forms['ptc-subscribe-form-{0}'.format(p.pk)]
        form['submit-type'] = 'add'
        page = form.submit()

        self.renew_app()

        page = self.app.get(reverse('discount:product-detail', kwargs={'pk': p.pk}))
        form = page.forms['ptc-subscribe-form-{0}'.format(p.pk)]
        form['submit-type'] = 'add'
        page = form.submit()

        context = {
            'product': p,
            'start_date': self.today,
            'end_date': self.today,
        }


        res = discount_tags.get_product_stats_for_period(context, 'carts')
        self.assertEqual(res, 2)

        res = discount_tags.get_product_stats_for_period(context, 'subscriptions')
        self.assertEqual(res, 1)

        context = {
            'product': p,
            'start_date': self.today - timezone.timedelta(days=1),
            'end_date': self.today - timezone.timedelta(days=1),
        }


        res = discount_tags.get_product_stats_for_period(context, 'carts')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'subscriptions')
        self.assertEqual(res, 0)

        context = {
            'product': p,
            'start_date': self.today + timezone.timedelta(days=1),
            'end_date': self.today + timezone.timedelta(days=1),
        }


        res = discount_tags.get_product_stats_for_period(context, 'carts')
        self.assertEqual(res, 0)

        res = discount_tags.get_product_stats_for_period(context, 'subscriptions')
        self.assertEqual(res, 0)



