from django.contrib import admin
from discount import models
from discount.forms import ProductAdminForm, ProductImageBaseFormset
#import reversion
from django.db.models import Q

class ProductImageAdmin(admin.ModelAdmin):
    pass


class ProductImagesInline(admin.TabularInline):
    model = models.ProductImage
    extra = 3
    formset = ProductImageBaseFormset


class ProductActionsInline(admin.TabularInline):
    model = models.ProductAction
    extra = 3
    #formset = ProductImageBaseFormset


class ProductBannersInline(admin.TabularInline):
    model = models.ProductBanner
    extra = 3



class FilterValueAdmin(admin.ModelAdmin):
    list_filter = ['filter_type', 'title']
    #search_fields = ['title']

class ProductConditionInline(admin.TabularInline):
    model = models.ProductCondition
    extra = 3

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    class Media:
        css = {
             'all': ('discount/css/admin/product.css',)
        }
    inlines = (ProductImagesInline, ProductConditionInline, ProductActionsInline, ProductBannersInline)
    list_filter = ['status', 'shop', 'brand', 'filter_values', 'product_type', 'ad']
    readonly_fields = ('created', 'edited', 'hashed')
    search_fields = ['title']
    form = ProductAdminForm
    fieldsets = (
        (None, {
            'fields': (('start_date', 'end_date', 'normal_price', 'stock_price'),)
        }),
        (None, {
            'fields': (('user', 'shop', 'product_type'),)
        }),
        (None, {
            'fields': (('status', 'start_after_approve'),)
        }),
        (None, {
            'fields': (('title', 'brand', 'link'), 'body', )
        }),
        (None, {
            'fields': (('code', 'use_code_postfix'), ('simple_code', 'use_simple_code'))
        }),
        ('Техническая информация', {
            'fields': (('percent', 'price_category', 'discount_category', 'ad', 'hashed'), ('created', 'edited', 'publish_time'))
        }),
        ('Комментарии', {
            'fields': (('shop_comment', 'tatamo_comment'),)
        }),
    )


class ProductChangerImagesInline(admin.TabularInline):
    model = models.ProductChangerImage
    extra = 3



class ProductChangerAdmin(admin.ModelAdmin):
    inlines = [ProductChangerImagesInline]
    list_filter = ['status', 'product__shop', 'product']
    search_fields = ['title']




class ProductTypeFilterValuesInline(admin.TabularInline):
    model = models.FilterValueToProductType
    extra = 3




class ProductTypeAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_filter = ['level', 'has_childs']
    inlines = [ProductTypeFilterValuesInline]



class ShopUsersInline(admin.TabularInline):
    verbose_name = 'Пользователь'
    verbose_name_plural = 'Пользователи'
    model = models.ShopsToUsers
    exclude = ()
    extra = 1

class ShopBrandsInline(admin.TabularInline):
    verbose_name = 'Бренд'
    verbose_name_plural = 'Бренды'
    model = models.ShopsToBrands
    exclude = ()
    extra = 5


class ShopPhonesInline(admin.TabularInline):
    verbose_name = 'Телефон'
    verbose_name_plural = 'Телефоны'
    model = models.ShopPhone
    exclude = ()
    extra = 5


class ShopSubscriptionsInline(admin.TabularInline):
    model = models.Subscription
    exclude = ()
    extra = 5


class ProductBannerAdmin(admin.ModelAdmin):
    list_filter = ['status', 'product__shop', 'product']


class AddBrandsListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Добавление брендов'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'add_brand'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('filled', 'Заполнено'),
            ('empty', 'Пусто'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'filled':
            return queryset.filter(add_brands__regex=r'^(?!\s*$).+')
        if self.value() == 'empty':
            return queryset.filter(~Q(add_brands__regex=r'^(?!\s*$).+'))





class ShopAdmin(admin.ModelAdmin):
    model = models.Shop
    inlines = [ShopUsersInline, ShopBrandsInline, ShopPhonesInline, ShopSubscriptionsInline]
    list_filter = ['status', AddBrandsListFilter]
    search_fields = ['title']




class ProductToCart(admin.TabularInline):
    verbose_name = 'Акция'
    verbose_name_plural = 'Акции'
    model = models.ProductToCart
    exclude = ()
    extra = 5


class SubscriptionAdmin(admin.ModelAdmin):
    model = models.Subscription
    list_filter = ['shop', 'status']



class PaymentAdmin(admin.ModelAdmin):
    model = models.Payment
    list_filter = ['created', 'operation', 'shop']

class ModelHistoryAdmin(admin.ModelAdmin):
    model = models.ModelHistory
    list_filter = ['cls']


"""
class CarpProductsInline(admin.TabularInline):
    verbose_name = 'Бренд'
    verbose_name_plural = 'Бренды'
    model = models.ShopsToBrands
    exclude = ()
    extra = 5

class CartAdmin(admin.ModelAdmin):
    model = models.Cart
    inlines = [CarpProductsInline]
"""

#admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.ProductType, ProductTypeAdmin)
admin.site.register(models.Shop, ShopAdmin)
admin.site.register(models.Comment)
admin.site.register(models.ShopType)
admin.site.register(models.Brand)
admin.site.register(models.FilterValue, FilterValueAdmin)
#admin.site.register(models.Color)

admin.site.register(models.UserProfile)
admin.site.register(models.ProductToCart)
admin.site.register(models.ProductMail)
admin.site.register(models.ProductImage, ProductImageAdmin)
#admin.site.register(models.History)
#admin.site.register(models.ProductHistory)
admin.site.register(models.ModelHistory, ModelHistoryAdmin)
admin.site.register(models.Payment, PaymentAdmin)
#admin.site.register(models.ShopAccount)
#admin.site.register(models.ProductAccount)
admin.site.register(models.SubscriptionType)
admin.site.register(models.Subscription, SubscriptionAdmin)
admin.site.register(models.ProductAction)
admin.site.register(models.ProductBanner, ProductBannerAdmin)
admin.site.register(models.ProductChanger, ProductChangerAdmin)
admin.site.register(models.FilterValueToProductType)
admin.site.register(models.ProductStat)
#admin.site.register(models.Lock)