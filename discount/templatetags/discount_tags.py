from django import template
from django.core.urlresolvers import reverse
from django.conf import settings
from discount.models import Product
from discount.forms import GetProductByCode, DiscountLoginForm, ProductTatamoManagerApproveForm
from discount import models
from discount.views import get_ptc_add_actions_context, get_ptc_subscribe_actions_context, get_coupon_status_context
from django.utils import timezone

register = template.Library()

@register.filter(name='cut_text')
def cut_text(value, length): # Only one argument.
    """Cuts first length letters from string"""
    return value[0:length]


@register.filter(name='bool_as_yes')
def bool_as_yes(value):
    if value:
        return 'Да'
    else:
        return 'Нет'

from django.contrib.admin.helpers import AdminReadonlyField, AdminField
@register.filter(name='get_admin_field')
def get_admin_field(fieldset, field, is_first=False):
        if field in fieldset.readonly_fields:
            return AdminReadonlyField(fieldset.form, field, is_first=is_first,
                model_admin=fieldset.model_admin)
        else:
            return AdminField(fieldset.form, field, is_first=is_first)


@register.filter(name='get_item')
def get_item(dct, key):
    if hasattr(dct, 'get'): #У форм нет метода get
        res = dct.get(key, None)
    else:
        try:
            res = dct[key]
        except:
            res = None
    return res


@register.filter(name='get_attr')
def get_attr(ob, item):
    res = getattr(ob, item, None)
    if callable(res):
        return res()
    else:
        return res


#@register.filter(name='call_meth')
#def call_meth(ob, item):
#    if hasattr(ob, item):
#        res = getattr(ob, item, None)
#    return res()


@register.simple_tag()
def get_filter_param_names():
    return models.FILTER_PARAMS_FIELD_NAMES.values()



from discount.models import Breadcrumb
@register.inclusion_tag('discount/widgets/breadcrumbs.html', takes_context=True)
def breadcrumbs(context):

    request = context['request']
    url_name = request.resolver_match.url_name
    #kwargs = request.resolver_match.kwargs

    if url_name == 'main-page':
        return

    breadcrumbs_list = [Breadcrumb(title='Главная', href=reverse('discount:main-page'), type='link')]

    if url_name in ['product-list', 'product-detail', 'product-update', 'product-change',
                    'product-banners', 'product-actions']:
        if url_name == 'product-list':
            category = context.get('category', None)
        else:
            product = context.get('product', None)
            if not product: #TODO Иначе глюк в тесте...
                return
            category = product.product_type
        parents = []
        cur = category
        if category:
            while cur.parent:
                if cur.parent.level != 0:
                    parents.append(cur.parent)
                cur = cur.parent
            parents.reverse()
            parents.append(category)

        for parent in parents:
            if parent.alias:
                key = parent.alias
            else:
                key = parent.pk
            breadcrumbs_list.append(Breadcrumb(title=parent.title, href=reverse('discount:product-list', kwargs={'alias': key}), type='link'))

        if url_name == 'product-detail':
            breadcrumbs_list.append(Breadcrumb(title=product.__str__(), type='text'))

        elif url_name in ['product-update', 'product-change', 'product-banners', 'product-actions']:
            breadcrumbs_list.append(Breadcrumb(title=product.__str__(), href=reverse('discount:product-detail', kwargs={'pk': product.pk}), type='link'))
            if url_name == 'product-update':
                breadcrumbs_list.append(Breadcrumb(title="Изменить", type='text'))
            elif url_name == 'product-change':
                breadcrumbs_list.append(Breadcrumb(title="Заявка на изменение", type='text'))
            elif url_name == 'product-banners':
                breadcrumbs_list.append(Breadcrumb(title="Баннеры", type='text'))
            elif url_name == 'product-actions':
                breadcrumbs_list.append(Breadcrumb(title="Размещение на главной", type='text'))


        #breadcrumbs_list[-1].type = 'text'

    elif url_name == 'shop-create':
        breadcrumbs_list.append(Breadcrumb('Создание магазина', type='text'))

    elif url_name in ['cart-view', 'cart-view-link']:
        breadcrumbs_list.append(Breadcrumb('Просмотр корзины', type='text'))

    elif url_name == 'product-create':
        breadcrumbs_list.append(Breadcrumb('Создание акции', type='text'))

    #elif url_name == 'product-update':
    #    breadcrumbs_list.append(Breadcrumb('Создание акции', type='text'))


    elif url_name == 'shop-create':
        breadcrumbs_list.append(Breadcrumb('Регистрация магазина', type='text'))

    elif url_name == 'shop-list':
        breadcrumbs_list.append(Breadcrumb(title='Магазины', type='text'))

    elif url_name == 'user-detail':
        breadcrumbs_list.append(Breadcrumb('Информация о пользователе', type='text'))

    elif url_name == 'signup':
        breadcrumbs_list.append(Breadcrumb('Регистрация', type='text'))

    elif url_name == 'help-page':
        breadcrumbs_list.append(Breadcrumb('Как мы работаем', type='text'))


    elif url_name == 'contacts-page':
        breadcrumbs_list.append(Breadcrumb('Контакты', type='text'))

    elif url_name == 'full-login':
        breadcrumbs_list.append(Breadcrumb('Войти', type='text'))

    elif url_name == 'shop-detail':
        shop = context.get('shop')
        breadcrumbs_list.append(Breadcrumb(title='Магазины', href=reverse('discount:shop-list'), type='link'))
        breadcrumbs_list.append(Breadcrumb(title=shop, type='text'))

    elif url_name == 'product-list-shop':
        breadcrumbs_list.append(Breadcrumb(title='Акции магазина', type='text'))

    elif url_name == 'product-list-shop':
        breadcrumbs_list.append(Breadcrumb(title='Акции магазина', type='text'))

    elif url_name == 'product-list-code':
        breadcrumbs_list.append(Breadcrumb(title='Мои действующие подписки', type='text'))

    elif url_name == 'product-list-finished-code':
        breadcrumbs_list.append(Breadcrumb(title='Мои завершенные подписки', type='text'))


    elif url_name == 'blocked-funds':
        breadcrumbs_list.append(Breadcrumb(title='Заблокированные средства', type='text'))

    elif url_name == 'payment-history':
        breadcrumbs_list.append(Breadcrumb(title='История взаиморасчетов', type='text'))

    elif url_name == 'action-days':
        breadcrumbs_list.append(Breadcrumb(title='График доступности размещения на главной', type='text'))

    else:
        breadcrumbs_list = []

    return {'breadcrumbs_list': breadcrumbs_list}


@register.inclusion_tag('discount/widgets/metatags.html', takes_context=True)
def metatags(context):

    request = context['request']
    url_name = request.resolver_match.url_name
    kwargs = request.resolver_match.kwargs

    metatags_dict = {}
    metatags_dict['title'] = 'Tatamo - территория скидок'
    metatags_dict['keywords'] = 'Tatamo - территория скидок'
    metatags_dict['description'] = 'Tatamo - территория скидок'

    if url_name == 'main-page':
        pass

    elif url_name == 'product-detail':
        product = context.get('product')
        metatags_dict['title'] = 'Tatamo - территория скидок | {0}'.format(product.__str__())
        metatags_dict['keywords'] = 'Tatamo - территория скидок | {0}'.format(product.__str__())
        metatags_dict['description'] = 'Tatamo - территория скидок | {0}'.format(product.__str__())

    elif url_name == 'product-list':
        category = context.get('category', None)
        if category:
            metatags_dict['title'] = 'Tatamo - территория скидок | {0}'.format(category.title)
            metatags_dict['keywords'] = 'Tatamo - территория скидок | {0}'.format(category.title)
            metatags_dict['description'] = 'Tatamo - территория скидок | {0}'.format(category.title)

    elif url_name in ['cart-view', 'cart-pdf-view', 'cart-html-view']:
        metatags_dict['title'] = 'Tatamo - территория скидок | Корзина'
        metatags_dict['keywords'] = 'Tatamo - территория скидок | Корзина'
        metatags_dict['description'] = 'Tatamo - территория скидок | Корзина'

    elif url_name == 'signup':
        metatags_dict['title'] = 'Tatamo - территория скидок | Корзина'
        metatags_dict['keywords'] = 'Tatamo - территория скидок | Корзина'
        metatags_dict['description'] ='Tatamo - территория скидок | Корзина'

    elif url_name == 'shop-list':
        metatags_dict['title'] = 'Tatamo - территория скидок | Магазины'
        metatags_dict['keywords'] = 'Tatamo - территория скидок | Магазины'
        metatags_dict['description'] = 'Tatamo - территория скидок | Магазины'

    elif url_name == 'shop-detail':
        shop = context.get('shop')
        metatags_dict['title'] = 'Tatamo - территория скидок | {0}'.format(shop.title)
        metatags_dict['keywords'] = 'Tatamo - территория скидок | {0}'.format(shop.title)
        metatags_dict['description'] = 'Tatamo - территория скидок | {0}'.format(shop.title)

    elif url_name == 'product-create':
        metatags_dict['title'] = 'Tatamo - территория скидок | Создание акции'
        metatags_dict['keywords'] = 'Tatamo - территория скидок | Создание акции'
        metatags_dict['description'] = 'Tatamo - территория скидок | Создание акции'

    elif url_name == 'shop-create':
        metatags_dict['title'] = 'Tatamo - территория скидок | Регистрация магазина'
        metatags_dict['keywords'] = 'Tatamo - территория скидок | Регистрация магазина'
        metatags_dict['description'] = 'Tatamo - территория скидок | Регистрация магазина'

    return {'metatags_dict': metatags_dict}


@register.inclusion_tag('discount/widgets/recent_products.html', takes_context=True)
def recent_products(context):
    request = context.get('request')
    if not models.request_with_empty_guest(request):

        if not 'visited_products' in request.session:
            return {'recent_products': [], 'count': 0}
        else:
            recent_products = list(Product.objects.filter(pk__in=request.session['visited_products']))
            if 'product' in context:
                product = context.get('product')
                if product in recent_products:
                    recent_products.remove(product)
            recent_products = recent_products[-5:]
            return {'recent_products': recent_products, 'count':len(recent_products)}
    else:
        return {'recent_products': [], 'count': 0}



@register.inclusion_tag('discount/widgets/shop_balance.html', takes_context=True)
def shop_balance(context):
    user = context['request'].user
    shop = user.get_shop
    if user.is_shop_manager and shop is not None:
        #shop = list(user.shops.all())[0]
        context = {}
        context['show'] = True
        context['points_total'] = shop.points_total
        context['points_free'] = shop.points_free
        context['points_blocked'] = shop.points_blocked
        return context
    else:
        return {'show': False}



@register.inclusion_tag('discount/widgets/_coupon.html')
def get_coupon(product, user):
    #url_to_decode = settings.SITE_URL + product.get_coupon_qr_url(user)
    code = product.get_code(user)
    if code:
        qr_url = reverse('discount:coupon-qr-code-view', kwargs={'data': code})
    else:
        qr_url = ''

    return {'qr_url': qr_url, 'code': code, 'product': product, 'user': user}


@register.inclusion_tag('discount/widgets/shop_products.html', takes_context=True)
def shop_products(context):
    product = context.get('product')
    shop = product.shop
    shop_products = shop.products.get_available_products()
    shop_products = shop_products.exclude(pk=product.pk)
    shop_products = shop_products[:5]
    return {'shop_products': shop_products, 'count':len(shop_products), 'shop_url': reverse('discount:shop-detail', kwargs={'pk': shop.pk})}




@register.inclusion_tag('discount/widgets/_product_info_main.html', takes_context=True)
def product_info_main(context, product):
    request = context.get('request')
    return {'product': product, 'request': request}



@register.inclusion_tag('discount/widgets/_shop_info.html', takes_context=True)
def shop_info(context):
    if 'shop' in context:
        shop = context.get('shop')
    elif 'product' in context:
        shop = context.get('product').shop

    result_context = {'shop': shop}
    return result_context



@register.inclusion_tag('discount/widgets/product_payments.html')
def product_payments(product):
    ts = models.Payment.objects.filter(product=product).order_by('period', 'action_type')
    return {'payments': ts}



from discount.models import MenuItem
@register.inclusion_tag('discount/widgets/_main_top_menu.html', takes_context=True)
def get_main_top_menu(context):
    #user = context['request'].user
    full_menu = MenuItem.get_full_menu()
    #active_menu_item = context.get('active_menu_item', None)

    return {'full_menu': full_menu}





def get_user_top_menu_list(context):
    request = context['request']
    user = request.user
    full_menu_list = []

    url_name = request.resolver_match.url_name

    if user.is_authenticated() and not user.is_shop_manager:

        item = MenuItem(title=models.ProductToCart.get_subscribed_count_text(user), href=reverse('discount:product-list-code'))
        if url_name == 'product-list-code':
            item.cls = 'active'
        item.link_class = 'code-list-menu'
        full_menu_list.append(item)

        item = MenuItem(title=models.ProductToCart.get_finished_count_text(user), href=reverse('discount:product-list-finished-code'))
        if url_name == 'product-list-finished-code':
            item.cls = 'active'
        item.link_class = 'finished-list-menu'
        full_menu_list.append(item)

    if user.is_shop_manager:

        shop = user.get_shop
        item = MenuItem(title='Страница магазина: {0}'.format(shop.title), href=reverse('discount:shop-detail', kwargs={'pk': shop.pk }))
        full_menu_list.append(item)

        item = MenuItem(title='Управление подпиской', href=reverse('discount:subscription-manage'))
        full_menu_list.append(item)

        item = MenuItem(title='Акции магазина', href=reverse('discount:product-list-shop'))
        full_menu_list.append(item)

        item = MenuItem(title='График доступности размещения на главной', href=reverse('discount:action-days'))
        full_menu_list.append(item)

        item = MenuItem(title='Заблокированные средства', href=reverse('discount:blocked-funds'))
        full_menu_list.append(item)

        item = MenuItem(title='История взаиморасчетов', href=reverse('discount:payment-history'))
        full_menu_list.append(item)

        item = MenuItem(title='Добавить акцию', href=reverse('discount:product-create'))
        full_menu_list.append(item)

        item = MenuItem(title='Инструкции по работе с сайтом', href=reverse('discount:shop-instructions'))
        full_menu_list.append(item)
    return full_menu_list

@register.inclusion_tag('discount/widgets/_user_top_right_menu.html', takes_context=True)
def user_top_right_menu(context):
    request = context['request']
    user = request.user
    menu_list = []

    url_name = request.resolver_match.url_name

    if user.is_authenticated() and not user.is_shop_manager:
        item = MenuItem(title='Зарегистрировать магазин', href=reverse('discount:shop-create'))
        if url_name == 'shop-create':
            item.cls = 'active'
        else:
            item.cls = 'inactive'
        menu_list.append(item)

    return {'menu_list': menu_list}


@register.filter(name='empty_as_text')
def empty_as_text(val):
    if not val:
        return ''
    else:
        return val


@register.inclusion_tag('discount/widgets/_user_top_menu.html', takes_context=True)
def get_user_top_menu(context):
    user = context['request'].user
    full_menu_list = get_user_top_menu_list(context)
    return {'full_menu_list': full_menu_list, 'user': user}



@register.inclusion_tag('discount/general/_left_menu.html', takes_context=True)
def get_left_menu(context):
    category = context.get('category', None)
    #active_menu_item = context.get('active_menu_item', None)
    user = context['request'].user
    if not category: #Главная
        return
    else:
        full_menu_list = MenuItem.get_partial_menu_list(category)
    return {'full_menu_list': full_menu_list, 'user': user}

@register.inclusion_tag('discount/widgets/_top_menu.html', takes_context=True)
def get_top_menu(context):
    #active_menu_item = context.get('active_menu_item', None)
    request = context.get('request')
    menu_items = []
    url_name = request.resolver_match.url_name
    user = context['request'].user
    contacts_item = MenuItem(title='Контакты', href=reverse('discount:contacts-page'))

    #if user.is_authenticated() and not user.is_shop_manager:
    #    add_shop_item = MenuItem(title='Зарегистрировать магазин', href=reverse('discount:shop-create'))
    #    if url_name == 'shop-create':
    #        add_shop_item.cls = ' active'
    #    menu_items.append(add_shop_item)

    #conditions_item = MenuItem(title='Условия сотрудничества', href=reverse('discount:conditions-page'))
    help_item = MenuItem(title='Как мы работаем', href=reverse('discount:help-page'))

    #TODO Переделать после старта покупателей
    if context['request'].session.get('shop_offer', None) is not None:
        item = MenuItem(title='Предложение для магазинов', href=reverse('discount:shop-offer'), cls='shop-offer-menu-item')
        menu_items.append(item)

    if url_name == 'contacts-page':
        contacts_item.cls = ' active'
    #if active_menu_item == 'conditions-page':
    #    conditions_item.cls = ' active'
    if url_name == 'help-page':
        help_item.cls = ' active'

    menu_items.append(contacts_item)
    #menu_items.append(conditions_item)
    menu_items.append(help_item)

    return {'menu_items': menu_items}


@register.inclusion_tag('discount/widgets/_bottom_menu.html', takes_context=True)
def get_bottom_menu(context):
    user = context['request'].user
    active_menu_item = context.get('active_menu_item', None)
    menu_items = {}
    contacts_item = MenuItem(title='Контакты', href=reverse('discount:contacts-page'))
    #conditions_item = MenuItem(title='Условия сотрудничества', href=reverse('discount:conditions-page'))
    help_item = MenuItem(title='Как мы работаем', href=reverse('discount:help-page'))
    if context['request'].session.get('shop_offer', None):
        shop_offer_item = MenuItem(title='Предложение для магазинов', href=reverse('discount:shop-offer'))
        menu_items['shop_offer'] = shop_offer_item

    product_types = []
    product_types.append(MenuItem(title='Женщинам', href=reverse('discount:product-list', kwargs={'alias':  settings.ALIAS_WOMEN})))
    product_types.append(MenuItem(title='Мужчинам', href=reverse('discount:product-list', kwargs={'alias':  settings.ALIAS_MEN})))
    product_types.append(MenuItem(title='Детям', href=reverse('discount:product-list', kwargs={'alias':  settings.ALIAS_CHILDREN})))
    product_types.append(MenuItem(title='Обувь', href=reverse('discount:product-list', kwargs={'alias':  settings.ALIAS_SHOES})))
    product_types.append(MenuItem(title='Аксессуары', href=reverse('discount:product-list', kwargs={'alias':  settings.ALIAS_ACCESSORIES})))
    product_types.append(MenuItem(title='Игрушки', href=reverse('discount:product-list', kwargs={'alias':  settings.ALIAS_TOYS})))
    product_types.append(MenuItem(title='Красота', href=reverse('discount:product-list', kwargs={'alias':  settings.ALIAS_BEAUTY})))
    product_types.append(MenuItem(title='Спорт', href=reverse('discount:product-list', kwargs={'alias':  settings.ALIAS_SPORT})))
    product_types.append(MenuItem(title='Товары для дома', href=reverse('discount:product-list', kwargs={'alias':  settings.ALIAS_HOME})))
    product_types.append(MenuItem(title='Ювелирные изделия', href=reverse('discount:product-list', kwargs={'alias':  settings.ALIAS_JEWELRY})))
    product_types.append(MenuItem(title='Family Look', href=reverse('discount:product-list', kwargs={'alias':  settings.ALIAS_FAMILY_LOOK})))

    if not user.is_shop_manager:
        favourite = MenuItem(title='Корзина', href=reverse('discount:cart-view'))
        menu_items['favourite'] = favourite
    if user.is_authenticated():
        personal = MenuItem(title='Личная информация', href=reverse('discount:user-detail'))
        login = MenuItem(title='Выйти', href=reverse('account_logout'))
    else:
        login = MenuItem(title='Войти', href=reverse('discount:full-login'))
        personal = MenuItem(title='Личная информация', href=reverse('discount:full-login'))

    if user.is_shop_manager:
        shop_create = MenuItem(title='Зарегистрировать магазин', href=reverse('discount:shop-create'))
        menu_items['shop_create'] = shop_create


    instructions_item = MenuItem(title='Инструкции по работе с сайтом', href=reverse('discount:shop-instructions'))
    if active_menu_item == 'shop-instructions':
        instructions_item.cls = 'active'
    else:
        instructions_item.cls = 'inactive'

    if active_menu_item == 'contacts-page':
        contacts_item.cls = ' active'
    #if active_menu_item == 'conditions-page':
    #    conditions_item.cls = ' active'
    if active_menu_item == 'help-page':
        help_item.cls = ' active'

    menu_items['contacts'] = contacts_item

    menu_items['help'] = help_item
    menu_items['instructions'] = instructions_item

    #menu_items['women'] = women_item
    #menu_items['men'] = men_item
    #menu_items['child'] = child_item


    menu_items['login'] = login
    menu_items['personal'] = personal


    user_menu_items = get_user_top_menu_list(context)

    return {'menu_items': menu_items, 'user_menu_items': user_menu_items, 'product_types': product_types}


@register.inclusion_tag('discount/widgets/cart_link.html', takes_context=True)
def cart_link(context):
    request = context.get('request')
    user = request.user
    count = models.ProductToCart.get_cart_queryset(request).count()
    show = not user.is_shop_manager
    return {'product_count': count, 'show': show}


@register.inclusion_tag('discount/widgets/get_product_by_code.html')
def get_product_by_code():
    form = GetProductByCode()
    return {'form': form}



@register.inclusion_tag('discount/widgets/main_social_links.html')
def main_social_links():
    return

#PTC_STATUS_CART = 1
#PTC_STATUS_SUBSCRIBED = 2
#PTC_STATUS_FINISHED_BY_SHOP = 3
#PTC_STATUS_BOUGHT = 4
#PTC_STATUS_CANCELLED = 5
#PTC_STATUS_DELETED = 6
#PTC_STATUS_INSTANT = 7


#@register.inclusion_tag('discount/widgets/_unsubscribe_product_form.html', takes_context=True)
#def unsubscribe_form(context, product):
#    context = {}#get_ptc_actions_context(product, context.get('request'))
#    return context



@register.inclusion_tag('discount/widgets/_ptc_add_form.html', takes_context=True)
def ptc_add_form(context, product):
    context = get_ptc_add_actions_context(product, context.get('request'))
    return context


@register.inclusion_tag('discount/widgets/_ptc_subscribe_form.html', takes_context=True)
def ptc_subscribe_form(context, product):
    context = get_ptc_subscribe_actions_context(product, context.get('request'))
    return context


@register.inclusion_tag('discount/widgets/_product_coupon_status.html', takes_context=True)
def product_coupon_status(context, product):
    request = context['request']
    context = get_coupon_status_context(request, product)
    return context



@register.inclusion_tag('discount/user/_login.html', takes_context=True)
def login_form(context):
    user = context['request'].user
    if user.is_authenticated():
        return
    else:
        form = DiscountLoginForm()
        return {'form': form}

from discount.forms import AddProductToCartForm
@register.inclusion_tag('discount/widgets/cart_remove_product.html')
def cart_remove_product(pk):
    form = AddProductToCartForm(initial={'product_id': pk})
    #action_url = reverse('discount:cart-remove-from-cart')
    return {'form': form}

@register.simple_tag(takes_context=True)
def get_product_code(context, product):
    cart = context.get('cart')
    code = product.generate_full_product_code(cart)
    return code


@register.simple_tag(takes_context=True)
def get_days_left(context, product):
    user = context.get('request').user
    has_perm = user.has_perm_for_product(product)
    if product.status == models.STATUS_PUBLISHED or not has_perm:
        return product.get_days_left
    else:
        return product.status_text



@register.inclusion_tag('discount/widgets/shop_link.html')
def shop_link(shop):
    return {'shop': shop }


"""
@register.simple_tag(takes_context=True)
def product_field_changed_class(context, product, field_name, value):
    user = context.get('request').user
    version = product.get_last_sent_version(user)
    version_value = getattr(version, field_name)
    if isinstance(version_value, (str, int)):
        if not version_value == value:
            return 'changed'
        else:
            return 'unchanged'
    else:
"""


@register.inclusion_tag('discount/widgets/m2m_with_changed.html', takes_context=True)
def get_history_m2m_values(context, product, field_name):
        try:
            user = context.get('user')
        except:
            user = context.get('request').user

        values = product.get_history_m2m_values(field_name, user)

        return {'values': values}


@register.inclusion_tag('discount/widgets/_product_value_with_changed.html', takes_context=True)
def get_history_value(context, product, field_name):
        try:
            user = context.get('user')
        except:
            user = context.get('request').user

        history_value = product.get_history_value(field_name, user)

        return history_value


@register.inclusion_tag('discount/widgets/_product_tatamo_manager_approve.html', takes_context=True)
def product_tatamo_manager_approve(context, product):
        user = context.get('request').user
        if user.is_tatamo_manager:
            initial = {'tatamo_comment': product.tatamo_comment}
            form = ProductTatamoManagerApproveForm(initial=initial)
            return {'form': form, 'product': product}


"""
@register.inclusion_tag('discount/widgets/_related_actions.html', takes_context=True)
def related_actions(context, product=None):
    if not product:
        product = context.get('product', None)
    if not product:
        return

    return {'related_products': product.related_products.all()}
"""

@register.simple_tag(takes_context=True)
def get_get_parameters_exclude(context, exclude=('page',), page=None):
    request = context['request']
    params = ''
    for key in request.GET:
        if key in exclude:
            continue
        if params == '':
            params = '?'
        lst = request.GET.getlist(key)
        if len(lst) == 1:
            params +="&{0}={1}".format(key, request.GET[key])
        else:
            for item in lst:
                params +="&{0}={1}".format(key, item)
    if page is not None and page > 1:
        if params == '':
            params += '?page=' + str(page)
        elif params == '?':
            params += 'page=' + str(page)
        else:
            params += '&page=' + str(page)
    return params

#TODO Удалить шаблон
"""
@register.inclusion_tag('discount/widgets/user_menu.html', takes_context=True)
def user_menu(context):
    request = context['request']
    user_menu = []
    user = request.user
    url_name = request.resolver_match.url_name


    if user.is_authenticated() and not user.is_shop_manager:
        item = MenuItem(title='Зарегистрировать магазин', href=reverse('discount:shop-create'))
        if url_name == 'shop-create':
            item.cls = 'active'
        user_menu.append(item)
    return {'user_menu': user_menu, 'user': user}
"""
@register.filter(is_safe=True)
def label_with_classes(value, arg):

    return value.label_tag(attrs={'class': arg})

@register.filter(is_safe=True)
def field_with_classes(value, arg):
    if not 'class' in value.field.widget.attrs:
        value.field.widget.attrs['class'] = ''
    value.field.widget.attrs['class'] += arg

    return value


@register.simple_tag()
def get_timestamp():
    if settings.DEBUG:
        result = '?' + str(timezone.now().timestamp())[:10]
    else:
        result = ''
    return result


@register.simple_tag()
def get_site_url():
    result = settings.SITE_URL
    return result


"""
@register.inclusion_tag('discount/widgets/_unsubscribe_product_form.html', takes_context=True)
def unsubscribe_form(context):
    user = context['request'].user
    product = context['product']
    try:
        ptc = ProductToCart.objects.get(user=user, product=product)
    except:
        return
    if ptc.status == models.PTC_STATUS_SUBSCRIBED:
        url = reverse('discount:ptc-subscribe-view', kwargs={'pk': ptc.pk})
        return {'url': url}
    elif:
        ptc.status = models.PT

"""



"""
@register.inclusion_tag('widgets/user_block.html')
def user_block(request):
    authentificated = request.user.is_authenticated()
    if authentificated:
        user = request.user
    else:
        user = None
    return {'authentificated': authentificated,'user': user}
"""

"""
@register.inclusion_tag('widgets/comment_list.html')
def comment_list():
    comment_list = None#Comment.objects.all()
    return {'object_list': comment_list}
"""
"""

@register.simple_tag
def test_tag():
    return Comment.objects.all()
"""

@register.simple_tag(takes_context=True)
def get_product_stats_for_period(context, t):
    product = context['product']
    start_date = context.get('start_date', None)
    end_date = context.get('end_date', None)
    if t == 'all_visits':
        return product.stat_all_in_period(start_date, end_date).count()
    elif t == 'user_visits':
        return product.stat_users_in_period(start_date, end_date).count()
    elif t == 'guest_visits':
        return product.stat_guests_in_period(start_date, end_date).count()
    elif t == 'all_unique_visits':
        return product.stat_unique_all_in_period(start_date, end_date).count()
    elif t == 'user_unique_visits':
        return product.stat_unique_users_in_period(start_date, end_date).count()
    elif t == 'guest_unique_visits':
        return product.stat_unique_guests_in_period(start_date, end_date).count()
    elif t == 'carts':
        return product.get_normal_carts_in_period(start_date, end_date).count()
    elif t == 'instant_carts':
        return product.get_instant_carts_in_period(start_date, end_date).count()
    elif t == 'subscriptions':
        return product.get_subscriptions_in_period(start_date, end_date).count()


