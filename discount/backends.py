from django.conf import settings
from django.contrib.auth.models import User, check_password
from discount.models import Product, Shop

class DiscountBackend:
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    Use the login name, and a hash of the password. For example:

    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'sha1$4e987$afbcf42e21bd417fb71db8c66b321e9fc33051de'
    """

    def authenticate(self, username=None, password=None):
       pass

    """
    def authenticate(self, username=None, password=None):
        login_valid = (settings.ADMIN_LOGIN == username)
        pwd_valid = check_password(password, settings.ADMIN_PASSWORD)
        if login_valid and pwd_valid:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user. Note that we can set password
                # to anything, because it won't be checked; the password
                # from settings.py will.
                user = User(username=username, password='get from settings.py')
                user.is_staff = True
                user.is_superuser = True
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
    """
    #TODO not used
    """
    def has_perm(self, user_obj, perm, obj=None):
        if perm == 'discount.edit_shop_products':
        #Мы попадаем сюда только если прошли все предыдущие проверки
            if not user_obj.is_authenticated():
                return False

            shop = user_obj.get_shop()
            if shop is None:
                return False

            if obj is None:
                return True

            if isinstance(obj, Product):
                shop = obj.shop
            elif isinstance(obj, Shop):
                shop = obj
            else:
                return False

            if user_obj in shop.users.all(): #and user_obj.has_perm(perm):
                return True
            else:
                return False
        return True
    """

from django.core.cache.backends.db import DatabaseCache


class DiscountCacheBackendMixin:
    def get(self, key, default=None, version=None):
        if settings.DISCOUNT_CACHE_ENABLED:
            return super().get(key, default=None, version=None)
        else:
            return None

    def set(self, key, value, timeout=settings.DISCOUNT_FULL_PAGE_CACHE_DURATION, version=None):
        if settings.DISCOUNT_CACHE_ENABLED:
            return super().set(key, value, timeout, version=None)
        else:
            return



class DiscountDBCacheBackend(DiscountCacheBackendMixin, DatabaseCache):
    pass

from django.core.cache.backends.memcached import MemcachedCache
class DiscountMemcachedCacheCacheBackend(DiscountCacheBackendMixin, MemcachedCache):
    pass