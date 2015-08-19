from django.contrib.sitemaps import Sitemap
from .models import Product, ProductType, Shop, SHOP_STATUS_PUBLISHED




class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Product.objects.get_available_products()

    def lastmod(self, obj):
        return obj.edited


class ShopSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Shop.objects.filter(status=SHOP_STATUS_PUBLISHED)

    def lastmod(self, obj):
        return obj.edited


class ProductTypeSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return ProductType.objects.filter(level__gt=0)

    def lastmod(self, obj):
        return obj.edited

class MainPageSitemap(Sitemap):
    def items(self):
        return [self]

    location = "/"
    changefreq = "daily"
    priority = 1.0

sitemaps = {
    'product_type': ProductTypeSitemap,
    'main_page': MainPageSitemap,
    'product': ProductSitemap,
    'shop' : ShopSitemap,
}