from django.views import generic
from discount import models
from discount import forms
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from discount.forms import ProductForm, ProductImageFormset
from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache
from discount.models import STATUS_PUBLISHED, STATUS_TO_APPROVE, STATUS_SUSPENDED, STATUS_NEED_REWORK, \
    STATUS_PROJECT, STATUS_FINISHED, STATUS_APPROVED, STATUS_READY, set_conditional_cache, get_conditional_cache
from discount import helper
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from itertools import chain
from allauth.account.views import LoginView, SignupView, PasswordChangeView
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import ttfonts
from reportlab.lib.pagesizes import A4
#from reportlab.lib.units import inch
#from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from django.conf import settings
from io import BytesIO
from django.db import transaction
from discount.models import filter_popular_products
from django.db.models import Sum, Count, IntegerField
from discount.helper import get_today, replace_newlines, get_client_ip
from django.contrib.auth.decorators import user_passes_test
#from django.utils.functional import cached_property
from django.utils.html import format_html
from django.forms import ValidationError
from discount.models import MoneyExeption
from random import shuffle
from django.shortcuts import get_object_or_404
from django.http import Http404
from contact_form.models import ContactForm, STATUS_CREATED
import csv, math, operator
from functools import reduce


def shop_manager_only_test(user):
    if user.is_shop_manager:
        return True
    else:
        return False


def shop_manager_only(login_url='/'):

    _shop_manager_only = method_decorator(user_passes_test(shop_manager_only_test, login_url=login_url))
    return _shop_manager_only


def get_product(self):
    if not hasattr(self, '_product') or not self._product:
        product_pk = self.kwargs.get('pk')
        product = get_object_or_404(models.Product, pk=product_pk)
        self._product = product
    return self._product

#****************************************************
#ProductList, LeftMenu


class ProductList(generic.ListView):
    paginate_by = settings.PAGINATE_BY_PRODUCT_LIST
    context_object_name = 'products'
    template_name = 'discount/product/product_list.html'
    model = models.Product

    def get_queryset(self):
        if not hasattr(self, 'object_list'):
            queryset = self.orig_queryset
            queryset = self.filter(queryset).distinct()
            queryset = self.order(queryset)
            #self._queryset = queryset
            self.object_list = queryset
        else:
            queryset = self.object_list
        return queryset

    def order(self, queryset):
        if queryset.count() == 0:
            return queryset
        order_by_orig = 0 if not self.form.cleaned_data.get('order_by', 0) else int(self.form.cleaned_data.get('order_by', 0))
        order_by_select = 0 if not self.form.cleaned_data.get('order_by_select', 0) else int(self.form.cleaned_data.get('order_by_select', 0))

        if order_by_orig > 0:
            order_by = order_by_orig
        elif order_by_select > 0:
            order_by = order_by_select
        else:
            return queryset.order_by('product_fields__weight')
        order_by = int(order_by)
        if order_by is not None:
            if order_by == forms.ORDER_TYPE_BY_PRICE_DEC:
                queryset = queryset.order_by('-stock_price')
            elif order_by == forms.ORDER_TYPE_BY_PRICE_INC:
                queryset = queryset.order_by('stock_price')

            elif order_by == forms.ORDER_TYPE_BY_DISCOUNT_INC:
                queryset = queryset.order_by('-percent')
            elif order_by == forms.ORDER_TYPE_BY_DISCOUNT_DEC:
                queryset = queryset.order_by('percent')

            elif order_by == forms.ORDER_TYPE_BY_POPULARITY_INC:
                queryset = queryset.annotate(cart_count=Count('cart_products')).order_by('cart_count')
                """
                queryset = queryset.extra(
                select={
                'cart_count': 'SELECT COUNT(*) FROM discount_producttocart WHERE discount_producttocart.product_id = discount_product.id'
                },
                ).extra(order_by=['cart_count'])
                """
            elif order_by == forms.ORDER_TYPE_BY_POPULARITY_DEC:
                queryset = queryset.annotate(cart_count=Count('cart_products')).order_by('cart_count')
                """
                queryset = queryset.extra(
                select={
                'cart_count': 'SELECT COUNT(*) FROM discount_producttocart WHERE discount_producttocart.product_id = discount_product.id'
                },
                ).extra(order_by=['-cart_count'])
                """

            elif order_by == forms.ORDER_TYPE_BY_NEW_INC:
                queryset = queryset.order_by('-publish_time')
            elif order_by == forms.ORDER_TYPE_BY_NEW_DEC:
                queryset = queryset.order_by('publish_time')
        return queryset


    def set_category(self, **kwargs): #TODO криво, переделать
         if not hasattr(self, 'category'):
            alias = kwargs.get('alias', None)
            try:
                product_type = models.ProductType.objects.get(alias=alias)
            except:
                product_type = None
            if product_type is None:
                try:
                    product_type = models.ProductType.objects.get(pk=alias)
                except:
                    product_type = None

            self.category = product_type

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def set_orig_queryset(self, request):
        if self.type == 'shop':
            orig_queryset = models.Product.objects.get_shop_products(request.user)
            self.orig_queryset = orig_queryset
        elif self.type == 'code':
            orig_queryset = models.Product.objects.filter_has_code(request.user)
            self.orig_queryset = orig_queryset
        elif self.type == 'finished-code':
            orig_queryset = models.Product.objects.filter_finished_has_code(request.user)
            self.orig_queryset = orig_queryset
        elif self.type == 'tatamo':
            orig_queryset = models.Product.objects.all()
            self.orig_queryset = orig_queryset
        else:
            if self.category:
                self.orig_queryset = self.category.get_available_products_with_hierarchy()
                self.orig_queryset_count = self.category.available_products_count
            else:
                raise Http404

    def prepare_choice_field(self, field_name, choices):
        if self.form:
            if self.request.method.lower() == 'post':
                enabled = list(self.field_querysets[field_name].values_list(field_name, flat=True).distinct())
                self.enabled[field_name] = list(set(enabled))
            else:
                products = self.orig_queryset
                vals = products.values(field_name).distinct()
                lst = []
                for val in vals:
                    lst.append((val[field_name], models.get_title_by_num(choices, val[field_name])))
                self.form.fields[field_name].choices = sorted(lst)
                if len(vals) < 2:
                    del self.form.fields[field_name]

    def setup(self, request, *args, **kwargs):
        self.set_category(**kwargs)
        if not hasattr(self, 'filter_params'):
            self.filter_params = []
        if not hasattr(self, 'enabled'):
            self.enabled = {}
        self.filter_params.append(('price_category', '__in', None))
        self.filter_params.append(('discount_category', '__in', None))
        self.type = kwargs.get('type', None)
        self.set_orig_queryset(request)
        if self.type == 'shop':
            if not request.user.is_shop_manager:
                self.response = HttpResponseRedirect(reverse('discount:full-login'))
                return
            else:
                #self.filter_form_class = forms.ProductListFilterShopForm
                self.filter_params.append(('status', '__in', None))
            self.category = models.ProductType.objects.get(level=0)
            #queryset = super().get_queryset()

            #self.queryset = self.get_queryset()
        elif self.type == 'tatamo':
            if not request.user.is_tatamo_manager:
                self.response = HttpResponseRedirect(reverse('discount:full-login'))
                return
            else:
                #self.filter_form_class = forms.ProductListFilterShopForm
                self.filter_params.append(('status', '__in', None))
            self.category = models.ProductType.objects.get(level=0)

        elif self.type == 'code' or self.type == 'finished-code':
            if not request.user.is_authenticated():
                self.response = HttpResponseRedirect(reverse('discount:full-login'))
                return
            self.category = models.ProductType.objects.get(level=0)
        else:
            self.type = None
        self.filter_form_class = forms.ProductListFilterForm
        #top_parent = self.category.get_top_parent()
        #self.dress_sizes_filter_available = top_parent.dress_sizes_filter_available
        #self.colors_filter_available = top_parent.colors_filter_available
        self.form = self.get_form()


        self.filter_params  += [('shop', '__in', None), ('product_type', '__in', None),
                    ('brand', '__in', None), ('title','__icontains', None)]


        for param_key, field_names in models.FILTER_PARAMS_FIELD_NAMES.items():
            field_name, field_label = field_names
            if self.category.filter_available(param_key) or self.type in ['shop', 'code', 'finished_code']:
                self.filter_params.append((field_name, '__in', 'filter_values'))
            elif self.form and field_name in self.form.fields:
                del self.form.fields[field_name]


        #if self.dress_sizes_filter_available:
        #
        #else:
        #    del self.form.fields['sizes']

        #if self.colors_filter_available:
        #    self.filter_params.append(('colors', '__in', None))
        #else:
        #    del self.form.fields['colors']


        if self.request.method.lower() == 'post':
            self.set_field_querysets()
        self.prepare_form()
        self.get_queryset()
        #queryset = self.get_queryset()
        #queryset = self.order(queryset)
        #TODO хрень, разобраться
        #self.queryset = queryset
        #self._queryset = queryset
        #self.object_list = queryset

    """
    def generate_field_querysets_cache_key(self):
        user_id = self.request.user.pk
        category_id = self.category.pk
        str_parameters = ''
        parameters = getattr(self.request, self.request.method)
        for key in parameters:
            str_parameters += "{0}-{1}".format(key, parameters[key])
        cache_key = 'field_querysets-{0}-{1}-{2}'.format(user_id, category_id, str_parameters)
        return cache_key
    """

    def set_field_querysets(self):
        #cache_key = self.generate_field_querysets_cache_key()
        #self.field_querysets = cache.get(cache_key)
        #if self.field_querysets is not None:
        #    return
        #else:
        self.field_querysets = {}
        for filter_param in self.filter_params:
            filter_param_name, postfix, real_name = filter_param
            #if real_name:
            #    filter_param_name = real_name
            value = self.form.cleaned_data.get(filter_param_name, None)
            filter_param_name = filter_param[0]
            #if value:
            queryset = self.filter(self.orig_queryset, filter_param_name)
            self.field_querysets[filter_param_name] = queryset
            #else:
            #    self.field_querysets[filter_param_name] = self.orig_queryset
        #    cache.set(cache_key, self.field_querysets, settings.DISCOUNT_CACHE_DURATION)

    #def get_filter_value(self, filter_param, postfix):
    #    if postfix == '__in':
    #        filter_value = getattr(self.request, self.request.method).getlist(filter_param, None)
    #    else:
    #        filter_value = getattr(self.request, self.request.method).get(filter_param, None)
    #    return filter_value

    def filter(self, queryset, field_name=None):
        for filter_param in self.filter_params:
            filter_param, postfix, real_name = filter_param
            if field_name is not None and filter_param == field_name:
                continue
            if real_name is None:
                real_name = filter_param
            if self.form and self.form.cleaned_data.get(filter_param, False):
                filter_param_with_postfix = real_name + postfix
                filter_value = self.form.cleaned_data[filter_param]
                flt = {filter_param_with_postfix: filter_value}
                queryset = queryset.filter(**flt).distinct()
        return queryset

    def get_form(self):
        products = self.orig_queryset
        if hasattr(self, 'orig_queryset_count'):
            count = getattr(self, 'orig_queryset_count')
        else:
            count = products.count()
        if count == 0:
            return None

        data = getattr(self.request, self.request.method).copy()
        frm = self.filter_form_class(data=data) #initial and data are different things
        if frm.is_valid():
            return frm
        else:
            return None

    def prepare_form(self):
        self.prepare_field('shop', models.Shop)
        self.prepare_field('brand', models.Brand)
        self.prepare_field('product_type', models.ProductType)


        for param_key, field_names in models.FILTER_PARAMS_FIELD_NAMES.items():
            field_name, field_label = field_names
            if self.form and field_name in self.form.fields:
                self.prepare_field(field_name, models.FilterValue)


        #self.prepare_field('sizes', models.Size)


        if self.type in ['shop', 'tatamo']:
            if self.request.user.is_shop_manager:
                self.prepare_choice_field('status', models.PRODUCT_STATUSES)
        else:
            if self.form is not None:
                del self.form.fields['status']

        self.prepare_choice_field('price_category', models.PRICE_CATEGORIES)
        self.prepare_choice_field('discount_category', models.DISCOUNT_CATEGORIES)


    def prepare_field(self, field_name, model=None):
        if self.form:
            if field_name in self.form.fields:
                #frm = self.filter_field(frm, field_name, model)
                if self.request.method.lower() == 'post':
                    self.set_enabled(field_name, model)
                else:
                    self.filter_field(field_name, model)

    def filter_field(self, field_name, model=None):
        vals = model.objects.filter(products__in=self.orig_queryset)
        queryset = self.form.fields[field_name].queryset.filter(pk__in=vals).distinct()
        #if hasattr(queryset, 'order_by_available_products_count'):
        #    queryset = queryset.order_by_available_products_count()
        #if self.type is None:
        #    pks = json.loads(self.category.available_products_pks)
        #else:
        #    pks = list(self.orig_queryset.values_list('pk', flat=True))
        #if field_name in ['shop', 'brand']:
        #    #queryset = queryset.annotate(available_products_count=Count('products'))
        #    queryset = queryset.annotate(available_products_count=Sum(
        #        Case(When(products__pk__in=pks, then=1),
        #             default=0,
        #             output_field=IntegerField(),
        #             )
        #    ))

        if field_name in ['shop', 'brand']:
            queryset = queryset.order_by('-available_products_count')
        elif field_name in ['product_type']:
            queryset = queryset.order_by('parent', 'weight', 'title')

        self.form.fields[field_name].queryset = queryset
        if queryset.count() < 2:
            del self.form.fields[field_name]
            #elif len(queryset) == 1:
            #    frm.fields[field_name].widget.attrs['class'] = 'disabled'
        return self.form

    def set_enabled(self, field_name, model=None):
        if not hasattr(self, 'enabled'):
            self.enabled = {}
        if not field_name in self.form.fields:
            return
        if field_name in self.field_querysets:
            if model:
                vals = model.objects.filter(products__in=self.field_querysets[field_name]).distinct()
                queryset = self.form.fields[field_name].queryset.filter(pk__in=vals).distinct()
            enabled = list(queryset.values_list('pk', flat=True))
            self.enabled[field_name] = enabled

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        if self.type == 'code':
            context['active_menu_item'] = 'product-list-code'
        elif self.type == 'finished-code':
            context['active_menu_item'] = 'product-list-finished-code'
        elif self.type == 'shop':
            context['active_menu_item'] = 'product-list-shop'
        context['product_list_filter_form'] = self.form
        context['category'] = self.category

        if self.type == 'shop':
            context['form_action_url'] = reverse('discount:product-list-shop')
            context['left_menu_submit_url'] = reverse('discount:product-list-filter-form-shop')
        elif self.type == 'code':
            context['form_action_url'] = reverse('discount:product-list-code')
            context['left_menu_submit_url'] = reverse('discount:product-list-filter-form-code')
        elif self.type == 'finished-code':
            context['form_action_url'] = reverse('discount:product-list-finished-code')
            context['left_menu_submit_url'] = reverse('discount:product-list-filter-form-finished-code')
        elif self.type == 'tatamo':
            context['form_action_url'] = reverse('discount:product-list-tatamo')
            context['left_menu_submit_url'] = reverse('discount:product-list-filter-form-tatamo')
        else:
            context['show_get_left_menu'] = True
            context['form_action_url'] = reverse('discount:product-list', kwargs={'alias': self.category.pk})
            context['left_menu_submit_url'] = reverse('discount:product-list-filter-form', kwargs={'alias': self.category.pk})

        show_type = int(self.request.GET.get('show_type', forms.SHOW_TYPE_GRID))
        if show_type == forms.SHOW_TYPE_LIST:
            context['list_template_name'] = 'discount/product/product_list_inner_list.html'
        else:
            context['list_template_name'] = 'discount/product/product_list_inner_grid.html'

        context['product_list_filter_form_order_by'] = forms.ProductListFilterFormOrderBy()

        return context


    def get(self, request, *args, **kwargs):
        #ptc_count = models.ProductToCart.get_full_cart_queryset(request).count()
        #response = None
        #save_cache = False
        #if models.request_with_empty_guest(request):
        #    key = helper.generate_cache_key('ProductList-' + kwargs['alias'], request, kwargs)
        #    response = cache.get(key)
        #    save_cache = True
        #if response is None:

        self.setup(request, *args, **kwargs)
        if hasattr(self, 'response'):
            return self.response
        response = super().get(request, *args, **kwargs).render()
        #    if save_cache:
        #        cache.set(key, response)
        return response


class ProductListFilterForm(ProductList):
    #template_name = 'discount/product/product_list_inner_list.html'

    def get_template_names(self):
        show_type = int(self.request.POST.get('show_type', forms.SHOW_TYPE_GRID))
        if show_type == forms.SHOW_TYPE_LIST:
            return 'discount/product/product_list_inner_list.html'
        else:
            return 'discount/product/product_list_inner_grid.html'

    def get_cache_key(self, request):
        key_list = ['category_{0}'.format(self.category.pk)]

        for k, v in request.POST.items():
            if v:
                key_list.append("{0}_{1}".format(k, v))
        key_list.sort()
        vary_on = '__'.join(key_list)
        key = 'product_list_json_response_{0}'.format(vary_on).encode('utf-8')
        return key

    def post(self, request, *args, **kwargs):
        today = get_today()
        self.set_category(**kwargs)
        enable_cache = models.request_with_empty_guest(request)
        if enable_cache:
            key = self.get_cache_key(request)
            try:
                condition = models.TatamoHistory.objects.filter(product_type=self.category).latest('created').created
            except:
                condition = today
                condition = [condition, today]
            json_response = get_conditional_cache(key, condition)
        else:
            json_response = None

        #Нужно хранить не более дня, поскольку есть поле "До окончания"

        if json_response is None:
            json_response = self.get_json_response(request, *args, **kwargs)
            if enable_cache:
                set_conditional_cache(key, json_response, condition)
        return json_response

    def get_json_response(self, request, *args, **kwargs):
        self.setup(request, *args, **kwargs)

        context = self.get_context_data(**kwargs)
        data = self.enabled
        data['amount'] = self.get_queryset().count()
        html_response = self.render_to_response(context)
        if hasattr(html_response, 'render'):
            html_response.render()
        data['html'] = html_response.content.decode('utf8')
        data['url_data'] = request.body.decode('utf8')
        json_response = JsonResponse(data)

        return json_response

#*****************************************************
#Product


class ProductDetail(generic.ListView):
    #model = models.Product
    context_object_name = 'comments'
    template_name = 'discount/product/product_detail.html'
    paginate_by = settings.PAGINATE_BY_PRODUCT_DETAIL

    #TODO криво. Страница у вас нет прав.
    def get(self, request, *args, **kwargs):
        result = super().get(self, request, *args, **kwargs)
        if self.product.status in  models.ACTIVE_STATUSES + [STATUS_SUSPENDED, STATUS_FINISHED]:
            return result
        else:
            if not request.user.has_perm_for_product(self.product):
                return HttpResponseRedirect(reverse('discount:full-login'))
            else:
                return result


    def get_queryset(self):
        slug_type = self.kwargs['type']
        if slug_type == 'pk':
            pk = self.kwargs['pk']
            product = get_object_or_404(models.Product, pk=pk)
        if slug_type == 'code':
            code = self.kwargs['code']
            product = get_object_or_404(models.Product, code=code)

        self.product = product
        return self.product.comments.all()

    #TODO перенести это все в модели
    @property
    def get_subscribed_count(self):
        #ptcs = self.product_to_cart_set(status=models.PTC_STATUS_SUBSCRIBED).all()
        #users = models.User.objects.filter(cart_products__status=models.PTC_STATUS_SUBSCRIBED,
        #                                   cart_products__product=self.product)
        #users = models.ProductToCart.objects.filter(~Q(user=None), product=self.product).count()
        users = models.ProductToCart.objects.filter(status=models.PTC_STATUS_SUBSCRIBED, product=self.product).count()
        return users

    @property
    def get_in_cart_count(self):
        users = models.ProductToCart.objects.filter(status__in=[
            models.PTC_STATUS_CART,
            models.PTC_STATUS_INSTANT,
            models.PTC_STATUS_SUSPENDED
        ], product=self.product).count()
        return users

    @property
    def get_bought_count(self):
        users = models.ProductToCart.objects.filter(status__in=[
            models.PTC_STATUS_BOUGHT,
        ], product=self.product).count()
        return users

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        if self.request.user.has_perm_for_product(self.product):
            context['users_subscribed'] = self.get_subscribed_count
            context['carts_count'] = self.get_in_cart_count
            context['bought_count'] = self.get_bought_count
        if self.request.user.is_authenticated():
            if 'comment_form' in kwargs:
                comment_form = kwargs['comment_form']
            else:
                comment_form = forms.CommentForm(user=self.request.user)
            context['comment_form'] = comment_form
        #context['comments'] = self.product.comments.all()
        context['product'] = self.product
        self.set_session_data()
        #context['add_product_to_cart_form'] = forms.AddProductToCartForm(initial={'pk': self.product.pk})
        context['show_code_form'] = forms.ShowCodeForm(initial={'product_id': self.product.pk})
        if self.request.user.is_tatamo_manager and self.product.status == models.SHOP_STATUS_TO_APPROVE:
            context['shop_tatamo_manager_approve'] = True
        context['user'] = self.request.user
        if self.request.user.has_perm_for_product(self.product):
            context['manage_url'] = self.product.get_manage_url()
            context['banners'] = self.product.productbanner_set
            context['actions'] = self.product.actions.filter(status__in=[
                models.ACTION_STATUS_ACTIVE,
                models.ACTION_STATUS_PAUSED,
                models.ACTION_STATUS_PLANNED
            ]).order_by('start_date')

            try:
                changer = models.ProductChanger.objects.get(~Q(status=models.STATUS_APPROVED), product=self.product)
            except:
                changer = None
            context['changer'] = changer

        context['active_statuses'] = (models.STATUS_PUBLISHED, models.STATUS_READY)
        context['approved_statuses'] = [models.STATUS_APPROVED, models.STATUS_SUSPENDED]
        context['changer_statuses'] = [models.STATUS_SUSPENDED, models.STATUS_PUBLISHED, models.STATUS_READY]
        context['save_product_stat'] = settings.DISCOUNT_SAVE_PRODUCT_STAT
        #context['conditions'] = settings.GENERAL_CONDITIONS

        return context


    def set_session_data(self):
        if not 'visited_products' in self.request.session:
            self.request.session['visited_products'] = []
        #if self.product in self.request.session.visited_product:
        visited_products = self.request.session['visited_products']
        while self.product.pk in visited_products:
            visited_products.remove(self.product.pk)
        visited_products.append(self.product.pk)
        if len(visited_products) > 10:
            visited_products = visited_products[-10:]
        self.request.session['visited_products'] = visited_products


    def post(self, request, *args, **kwargs):
        comment_form = forms.CommentForm(self.request.POST, user=request.user)
        pk = kwargs['pk']
        product = models.Product.objects.get(pk=pk)
        if comment_form.is_valid():
            comment_form.instance.product = product
            comment_form.save()
            return HttpResponseRedirect(reverse('discount:product-detail', kwargs={'pk': product.pk}))
        else:
            return self.render_to_response(self.get_context_data(comment_form=comment_form))


class SubsribedToProductView(generic.TemplateView):
    template_name = 'discount/product/_subscribed_to_product.html'

    product = property(get_product)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.product
        action = kwargs['action']
        if action == 'subscribed':
            ptcs = models.ProductToCart.objects.filter(product=product, status=models.PTC_STATUS_SUBSCRIBED).\
                    order_by('subscription_time')
            title = 'Подписаны на акцию'
        elif action == 'cart':
            ptcs = models.ProductToCart.objects.filter(product=product, status__in=[
                models.PTC_STATUS_CART,
                models.PTC_STATUS_INSTANT,
                models.PTC_STATUS_SUSPENDED
            ]
                                                       ).order_by('subscription_time')
            title = 'Добавили акцию в корзину'
        elif action == 'bought':
            ptcs = models.ProductToCart.objects.filter(product=product, status=models.PTC_STATUS_BOUGHT).\
                    order_by('subscription_time')
            title = 'Приобрели товар по акции'
        context['ptcs'] = ptcs
        context['title'] = title
        return context

    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))


class GenerateProductCode(generic.View):
    def post(self, request, *args, **kwargs):
        code = models.Product.generate_unique_code()
        return JsonResponse({'code': code})


class GetProductByCode(generic.View):

    def post(self, request, *args, **kwargs):
        code = request.POST['product_code']
        check_ptc = False
        if '-' in code:
            check_ptc = True
            pos = code.index('-')
            ptc_code = code[pos+1:]
            code = code[:pos]
            try:
                ptc = models.ProductToCart.objects.get(code=ptc_code)
            except:
                ptc = None
        try:
            product = models.Product.objects.get(code=code)
        except:
            product = None
        if request.is_ajax():
            if (product is not None and not check_ptc) or (check_ptc and ptc is not None and product is not None):
                return JsonResponse({'status': 1, 'message': 'Переходим на страницу акции...'})
            else:
                return JsonResponse({'status': 0, 'message': 'Акция не найдена'})
        else:
            return HttpResponseRedirect(reverse('discount:product-detail', kwargs={'pk': product.pk}))

#****************************************
#MainPage
import random
class MainPage(generic.TemplateView):
    template_name = 'discount/general/main_page.html'

    def dispatch(self, request, *args, **kwargs):

        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def get_favourite_products():
        key = 'get_favourite_products'
        favourites = cache.get(key)
        if favourites is None:
            max_count = settings.MAX_POPULAR_COUNT
            today = get_today()
            ad_products = []
            additional_products = []

            if today >= settings.START_DATE :
                products = models.Product.objects.get_available_products().filter(actions__status=models.ACTION_STATUS_ACTIVE,
                                                          actions__action_type=models.ACTION_TYPE_POPULAR)[:max_count]
            else:
                products = models.Product.objects.none()


            existing_pks = list(products.values_list('pk', flat=True))
            count = products.count()
            lack = max_count - count
            if lack > 0:
                ad_products = models.Product.objects.get_ad_products_popular().order_by('id')[:lack]
                count = ad_products.count()
                lack = max_count - count

            if lack > 0:
                additional_products = models.Product.objects.get_available_products().exclude(pk__in=existing_pks).exclude(productbanner__banner=None)
                additional_products = filter_popular_products(additional_products, lack)

            favourites = []
            for product in products:
                favourites.append(product)
            for product in ad_products:
                favourites.append(product)
            for product in additional_products:
                favourites.append(product)
            cache.set(key, favourites, 60 * 30)
        #shuffle(favourites)
        return favourites

    @staticmethod
    def get_partners():
        partners = list(models.Shop.objects.filter(status=models.SHOP_STATUS_PUBLISHED).all())
        shuffle(partners)
        return partners


    def get_context_data(self, **kwargs):
        main_categories_queryset = models.ProductType.objects.filter(level=1)
        categories = []
        """
        main_categories_queryset = main_categories_queryset.extra(
        select={
        'available_products_count': 'SELECT COUNT(*) FROM discount_product WHERE discount_product.product_type_id = discount_producttype.id AND discount_product.status=2 AND discount_product.end_date > {0}'.format(today)
        },
        )
        #main_categories_queryset = main_categories_queryset.prefetch_related('products')
        main_categories_queryset = main_categories_queryset.filter(available_products_count__gt=0)
        """
        for category in main_categories_queryset.all():
            if category.available_products_count > 0 or category.all_products.get_ad_products_category().count() > 0:
               categories.append(category)

        context = super().get_context_data(**kwargs)
        context['categories'] = categories
        context['favourite_products'] = self.get_favourite_products()
        context['partners'] = self.get_partners()
        return context



#**************************************************
#ProductCreate
class ProductCreate(generic.TemplateView):
    #model = models.Product
    #form_class = ProductForm
    template_name = 'discount/product/product_create.html'

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.model = None

    @shop_manager_only()
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def set_model(self, **kwargs):
        if 'pk' in kwargs:
            model = get_object_or_404(models.Product, pk=kwargs['pk'])
            self.model = model
        else:
            self.model = None

    def get(self, request, *args, **kwargs):
        self.set_model(**kwargs)
        user = request.user
        if user.has_perm_for_product(self.model):
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('discount:full-login'))

    def get_context_data(self, form=None, image_formset=None, condition_formset=None, related_product_formset = None, **kwargs):
        self.set_model(**kwargs)
        if 'pk' in kwargs and not form and not image_formset:
            form = forms.ProductForm(instance=self.model, user=self.request.user)
            image_formset = forms.ProductImageFormset(instance=self.model)
            condition_formset = forms.ProductConditionFormset(instance=self.model)
        context = super().get_context_data(**kwargs)


        shop = self.request.user.get_shop

        if not form is None:
            context['form'] = form
        else:
            context['form'] = ProductForm(user=self.request.user)

        if context['form'].initial_value('tatamo_comment') == None:
            del context['form'].fields['tatamo_comment']

        if image_formset is not None:
            context['image_formset'] = image_formset
        else:
            context['image_formset'] = ProductImageFormset(instance=self.model)

        if related_product_formset is not None:
            context['related_product_formset'] = image_formset
        else:
            context['related_product_formset'] = forms.RelatedProductFormset(instance=self.model, shop=shop)

        if condition_formset is not None:
            context['condition_formset'] = condition_formset
        else:
            context['condition_formset'] = forms.ProductConditionFormset(instance=self.model)

        if self.model:
            context['product'] = self.model

        if not self.model:
            status = models.STATUS_NEW
        else:
            status = self.model.saved_status

        context_buttons = []
        if self.request.user.has_perm_for_product(self.model) and not self.request.user.is_tatamo_manager:
            buttons = models.AVAILABLE_BUTTONS[status]
            for button in buttons:
                context_buttons.append(models.BUTTONS[button])
        context['buttons'] = context_buttons


        #context['display_save_button'] = self.display_save_button
        #context['display_submit_button'] = self.display_submit_button
        #context['display_suspend_button'] = self.display_suspend_button
        #context['display_stop_button'] = self.display_stop_button
        context['display_add_image_button'] = self.display_add_image_button
        context['display_generate_code_button'] = self.display_generate_code_button
        #context['display_start_button'] = self.display_start_button

        if self.model is not None:
            status_text = self.model.status_text
            context['status_text'] = status_text

        context['shop'] = self.request.user.get_shop
        if self.request.user.get_shop:
            context['shop_manage_url'] = reverse('discount:shop-update', kwargs={'pk': self.request.user.get_shop.pk})

        #context['user'] = self.request.user

        return context

    """
    @property
    def display_submit_button(self): #to-approve
        if self.model is None or self.model.status in [STATUS_NEED_REWORK, STATUS_PROJECT]:
            return True
        else:
            return False

    #@property
    #def display_to_project_button(self):
    #    if self.model is not None and self.model.status in [STATUS_NEED_REWORK, STATUS_APPROVED]:
    #        return True
    #    else:
    #        return False

    @property
    def display_stop_button(self):
        if self.model is not None and self.model.status in [STATUS_PUBLISHED, STATUS_APPROVED,
                                                            STATUS_READY, STATUS_SUSPENDED,
                                                            STATUS_NEED_REWORK, STATUS_PROJECT]:
            return True
        else:
            return False

    @property
    def display_save_button(self):
        if self.model and self.model.status in [STATUS_FINISHED, STATUS_TO_APPROVE]:
            return False
        else:
            return True

    @property
    def display_start_button(self):
        if self.model and self.model.status in [STATUS_APPROVED, STATUS_SUSPENDED]:
            return True
        else:
            return False

    @property
    def display_suspend_button(self):
        if self.model is not None and self.model.status in [STATUS_PUBLISHED, STATUS_READY]:
            return True
        else:
            return False

    @property
    def display_update_button(self):
        if self.model is not None and self.model.status in [STATUS_READY, STATUS_APPROVED, STATUS_SUSPENDED]:
            return True
        else:
            return False
    """
    @property
    def display_add_image_button(self):
        if self.model is None or  self.model.status in \
            [STATUS_PROJECT, STATUS_NEED_REWORK]:
            return True
        else:
            return False
    @property
    def display_generate_code_button(self):
        if self.model is None or self.model.status in [STATUS_PROJECT] and not self.model.use_simple_code:
            return True
        else:
            return False

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.set_model(**kwargs)
        today = get_today()
        status = models.STATUS_PROJECT
        shop = request.user.get_shop
        if self.model is not None:
            status = self.model.status
        """
        image_formset_skipped = status in [
                                            models.STATUS_READY,
                                            models.SHOP_STATUS_TO_APPROVE,
                                            models.STATUS_PUBLISHED,
                                            models.STATUS_FINISHED,
                                            models.STATUS_APPROVED,
                                            models.STATUS_SUSPENDED,
                                            models.STATUS_CANCELLED,
                ]


        """
        #if not image_formset_skipped:
        image_formset = forms.ProductImageFormset(request.POST, request.FILES, instance=self.model)
        image_formset_valid = image_formset.is_valid()
        image_formset_errors = image_formset.errors
        image_formset_non_form_errors = image_formset.non_form_errors()
        #else:
        #    image_formset = None
        #    image_formset_valid = True
        #    image_formset_errors = {}
        #    image_formset_non_form_errors = {}


        #TODO пока не использую
        condition_formset = forms.ProductConditionFormset(request.POST, instance=self.model)
        condition_formset_valid = condition_formset.is_valid()
        condition_formset_errors = condition_formset.errors
        condition_formset_non_form_errors = condition_formset.non_form_errors()

        #TODO пока не использую
        related_product_formset = forms.RelatedProductFormset(request.POST, instance=self.model, shop=shop)
        related_product_formset_valid = related_product_formset.is_valid()
        related_product_formset_errors = related_product_formset.errors
        related_product_formset_non_form_errors = related_product_formset.non_form_errors()



        if self.model is not None:
            orig_status = self.model.status
        else:
            orig_status = models.STATUS_PROJECT

        submit_type = request.POST.get('submit-type', None)
        if not submit_type:
            if 'to-approve' in request.POST:
                submit_type = 'to-approve'
            elif 'to-cancel' in request.POST:
                submit_type = 'to-cancel'
            elif 'to-project' in request.POST:
                submit_type = 'to-project'
            elif 'to-suspend' in request.POST:
                submit_type = 'to-suspend'
            elif 'to-publish' in request.POST:
                submit_type = 'to-publish'
            elif 'to-finish' in request.POST:
                submit_type = 'to-finish'
            elif 'to-plan' in request.POST:
                submit_type = 'to-plan'
            else:
                submit_type = 'to-save'

        new_data = {}
        if submit_type == 'to-approve':
            new_status = models.STATUS_TO_APPROVE
        elif submit_type == 'to-finish':
            new_status = models.STATUS_FINISHED
            new_data['end_date'] = today
        #elif submit_type == 'to-project':
        #    new_status = models.STATUS_PROJECT
        elif submit_type == 'to-suspend':
            new_status = models.STATUS_SUSPENDED
        elif submit_type == 'to-publish':
            new_status = models.STATUS_PUBLISHED
        elif submit_type == 'to-cancel':
            new_status = models.STATUS_CANCELLED
        elif submit_type == 'to-project':
            new_status = models.STATUS_PROJECT
        elif submit_type == 'to-plan':
            new_status = models.STATUS_READY
        else:
            new_status = orig_status

        new_data['status'] = new_status

        code = request.POST.get('code', None)
        #if code is None:
        #    code = models.Product.generate_unique_code()


        #TODO переделать на initial
        form = ProductForm(request.POST, request.FILES, instance=self.model, user=request.user, new_data=new_data)

        form_valid = form.is_valid()

        all_valid = form_valid and image_formset_valid

        if self.request.is_ajax():
            if not all_valid:
                return JsonResponse({'form_errors': form.errors, 'form_non_field_errors': form.non_field_errors(),
                                     'image_formset_form_errors': image_formset_errors, 'image_formset_non_form_errors': image_formset_non_form_errors,'form_valid': False})
            else:
                return JsonResponse({'form_valid': True})

        if all_valid and not self.request.is_ajax():
            product = form.save(commit=False)
            product.shop = request.user.get_shop #TODO хрень, переделать
            product.code = code #TODO хрень, переделать
            if not product.code:
                product.code = models.Product.generate_unique_code()

            product.save()
            #form.save_m2m()

            for param_key, field_names in models.FILTER_PARAMS_FIELD_NAMES.items():
                field_name, field_label = field_names
                if field_name in form.cleaned_data:
                    for filter_value in form.cleaned_data[field_name]:
                        fvtp, created = models.Product.filter_values.through.objects.get_or_create(product=product, filtervalue=filter_value)
                        if created:
                            fvtp.save()
                    models.Product.filter_values.through.objects.filter(~Q(filtervalue__in=form.cleaned_data[field_name]), product=product, filtervalue__filter_type=param_key).delete()


            #if not image_formset_skipped:
            image_formset.instance = product #TODO скорее всего лишнее
            image_formset.save()

            condition_formset.instance = product
            condition_formset.save()

            related_product_formset.instance = product
            related_product_formset.save()

            if product.status in [models.STATUS_PUBLISHED, models.STATUS_READY]: #Для READY не надо, она сама переведется
                try:
                    with transaction.atomic():
                        product.pay()

                except models.MoneyExeption:
                    existing_product = models.Product.objects.get(pk=product.pk)
                    existing_product.apply_storage_params() #Поскольку тут задействован memcached, в транзакции не откатится
                    existing_product.clear_cache() #Поскольку тут задействован memcached, в транзакции не откатится
                    form.add_error(None, 'Недостаточно средств')
                    return self.render_to_response(self.get_context_data(form=form, image_formset=image_formset))

            return HttpResponseRedirect(reverse('discount:product-detail', kwargs={'pk': product.id}))
        else:
            return self.render_to_response(self.get_context_data(form=form, image_formset=image_formset))

#********************************************************



class PtcAdd(generic.TemplateView):
    template_name = 'discount/widgets/_ptc_add_form.html'

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, action=None, **kwargs):
        #pk = kwargs.get('pk')
        #ptc = models.ProductToCart.objects.get(pk=pk)
        context = get_ptc_add_actions_context(self.product, request=self.request, action=action)
        #action = kwargs.get('action', 'view')
        #action = self.request.POST.get('action')
        #if action == 'unsubscribe_form':
        #    context['form'] = forms.UnsubscribeForm()
        #context['action_url'] = reverse('discount:cart-actions', kwargs={'pk': self.product.pk})
        context['is_ajax'] = True
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('submit-type')
        user = request.user
        product = models.Product.objects.get(pk=kwargs.get('pk'))
        self.product = product
        ptc = product.find_ptc_by_request(request)
        if ptc is None:
            ptc = product.get_ptc(request=request)

        if action == 'add':
            ptc.status = models.PTC_STATUS_CART
            ptc.save()

        elif action == 'remove':
            ptc.delete()
            #ptc.save()


        data = {}
        count = models.ProductToCart.get_cart_queryset(request).count()
        html_response = self.render_to_response(self.get_context_data(action=action, **kwargs))
        if hasattr(html_response, 'render'):
                html_response.render()
        data['html'] = html_response.content.decode('utf8')
        data['count'] = count
        data['code_list_menu'] = models.ProductToCart.get_subscribed_count_text(user)
        data['finished_list_menu'] = models.ProductToCart.get_finished_count_text(user)
        data['status'] = 1
        json_response = JsonResponse(data)
        return json_response



class PtcSubscribe(generic.TemplateView):
    template_name = 'discount/widgets/_ptc_subscribe_form.html'


    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, pk=None, **kwargs):
        action = request.POST.get('submit-type')
        user = request.user
        product = models.Product.objects.get(pk=pk)
        self.product = product
        form = None
        ptc = product.find_ptc_by_request(request)
        if ptc is None:
            ptc = product.get_ptc(request=request)


        if user.is_authenticated():
            if action in ['first_subscribe', 'subscribe']:
                ptc.status = models.PTC_STATUS_SUBSCRIBED
                ptc.save()
                models.ProductMail.send_products_messages([product], user, subscribed=True)

            elif action in ['unsubscribe', 'unsubscribe_form_repeated']:
                form = forms.UnsubscribeForm(request.POST)
                if form.is_valid():

                    if form.cleaned_data['reason'] == '1': #Купил
                        ptc.status = models.PTC_STATUS_BOUGHT
                    else:
                        ptc.status = models.PTC_STATUS_CANCELLED
                    ptc.comment = form.cleaned_data['comment']
                    ptc.save()
                    action = None
        else:
            if action in ['first_subscribe', 'subscribe', 'subscribe_form']:
                cart_ptcs = models.ProductToCart.objects.filter(session_key=request.session.session_key, status=models.PTC_STATUS_INSTANT)
                for cart_ptc in cart_ptcs:
                    cart_ptc.delete()
                    #cart_ptc.save()
                ptc.status = models.PTC_STATUS_INSTANT
                ptc.save()
                data = {}
                data['status'] = 2
                data['redirect_to'] = reverse('discount:instant-cart-view')
                return JsonResponse(data)

        data = {}
        count = models.ProductToCart.get_cart_queryset(request).count()
        html_response = self.render_to_response(self.get_context_data(form=form, action=action, **kwargs))
        if hasattr(html_response, 'render'):
                html_response.render()
        data['html'] = html_response.content.decode('utf8')
        data['count'] = count
        data['code_list_menu'] = models.ProductToCart.get_subscribed_count_text(user)
        data['finished_list_menu'] = models.ProductToCart.get_finished_count_text(user)
        data['status'] = 1
        data['pk'] = product.pk
        json_response = JsonResponse(data)
        return json_response

    def get_context_data(self, form=None, action=None, **kwargs):
        #pk = kwargs.get('pk')
        #ptc = models.ProductToCart.objects.get(pk=pk)
        context = get_ptc_subscribe_actions_context(self.product, request=self.request)
        #action = kwargs.get('action', 'view')
        #action = self.request.POST.get('action')
        #if action == 'unsubscribe_form':
        #    context['form'] = forms.UnsubscribeForm()
        if form is not None and action in ['unsubscribe', 'unsubscribe_form_repeated']:
            context['unsubscribe_form'] = form

        if action == 'unsubscribe':
            context['action'] = 'unsubscribe_form_repeated'

        if action == 'unsubscribe_form':
            context['unsubscribe_form'] = forms.UnsubscribeForm()
            context['action'] = 'unsubscribe'

        #context['action_url'] = reverse('discount:cart-actions', kwargs={'pk': self.product.pk})
        context['is_ajax'] = True
        return context


class CartView(generic.ListView):
    template_name = 'discount/cart/cart_view.html'
    context_object_name = 'products'

    def clean_instant_ptc(self):
        if not self.action == 'instant':
            instant_ptcs = models.ProductToCart.objects.filter(session_key=self.request.session.session_key, status=models.PTC_STATUS_INSTANT)
            for instant_ptc in instant_ptcs:
                instant_ptc.status = models.PTC_STATUS_CART
                instant_ptc.save()

    def dispatch(self, request, *args, **kwargs):
        self.action = self.kwargs.get('action', 'regular')
        self.clean_instant_ptc()
        return super().dispatch(request, *args, **kwargs)


    def get_queryset(self):

        if self.action == 'instant':
            ptcs = models.ProductToCart.objects.filter(session_key=self.request.session.session_key, status=models.PTC_STATUS_INSTANT)
        else:
            ptcs = models.ProductToCart.get_cart_queryset(self.request)
        queryset = models.Product.objects.filter(cart_products__in=ptcs)
        return queryset

    def post(self, request, *args, **kwargs):

        pk = self.request.POST.get('product_id')
        user = request.user
        #return HttpResponse('Данные отправлены!')
        #context = self.get_context_data(**kwargs)

        if self.action == 'remove':
            product = models.Product.objects.get(pk=pk)
            ptc = product.find_ptc_by_request(request)
            ptc.delete()
            #ptc.save()
            available_products_count = models.ProductToCart.get_cart_queryset(request).count()
            return JsonResponse({'pk': pk, 'count': available_products_count})
        elif self.action == 'clear':
            ptcs = models.ProductToCart.get_cart_queryset(request)
            for ptc in ptcs:
                ptc.delete()
            return HttpResponseRedirect(reverse('discount:cart-view'))

        elif self.action == 'remove-expired':
            expired_ptcs = models.ProductToCart.get_expired_cart_queryset(request)
            for ptc in expired_ptcs:
                ptc.delete()
            return HttpResponseRedirect(reverse('discount:cart-view'))

        elif self.action == 'finish': #Гость не может этого


            self.form = forms.GetCodeForm(data=request.POST, user=request.user)
            if not self.form.is_valid():
                return self.render_to_response(self.get_context_data(form=self.form))
            else:
                self.form.save(request, repeated=True)
                products = self.get_queryset()
                products_to_send = []
                ptcs = models.ProductToCart.objects.filter(product__in=products, user=self.request.user)
                for ptc in ptcs:
                    ptc.status = models.PTC_STATUS_SUBSCRIBED
                    ptc.save()
                    products_to_send.append(ptc.product)

                if len(products_to_send) > 0:
                    models.ProductMail.send_products_messages(products_to_send, user, subscribed=True)
                return HttpResponseRedirect(reverse('discount:product-list-code'))


            if not hasattr(self, 'response'):
                return HttpResponseRedirect(reverse('discount:cart-view-link', kwargs={'link': self.cart.link}))
            else:
                return self.response


    def get_context_data(self, form=None, **kwargs):
        if not hasattr(self, 'object_list'):
            self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if form is not None:
            context['get_code_form'] = form
        else:
            if user.is_authenticated():
                profile = user.profile
                initial = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': profile.phone,
                'email': user.email
                }
                context['get_code_form'] = forms.GetCodeForm(initial=initial, user=user)

            else:
                form = forms.GetCodeForm(user=user)
                context['get_code_form'] = form

        if not user.is_authenticated():
            context['user_is_guest'] = True
            context['login_form'] = forms.DiscountLoginForm()
            context['signup_form'] = forms.DiscountSignupForm()
        return context




"""
class CartViewLink(generic.ListView):
    context_object_name = 'products'
    template_name = 'discount/cart/cart_view_link.html'


    def dispatch(self, request, *args, **kwargs):
        self.queryset = self.get_queryset()
        if self.queryset is None:
            return HttpResponseRedirect(reverse('discount:cart-view'))
        return super().dispatch(request, *args, **kwargs)


    def get_queryset(self):
        #user = self.request.user
        if self.queryset:
            return self.queryset
        cart = models.Cart.objects.get(link=self.kwargs.get('link'))

        self.cart = cart
        products = cart.products.all()
        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_buttons'] = self.cart.status == CART_STATUS_FINISHED
        context['cart'] = self.cart
        return context
"""

#class CartHtmlView(CartViewLink):
#    template_name = 'discount/cart/cart_html_view.html'

import qrcode

def get_qr_code_image(data):
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=4,
    border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    return img

def get_qr_code_response(data):
    img = get_qr_code_image(data)
    response = HttpResponse(content_type="image/jpg")
    img.save(response, "JPEG")
    return response

def coupon_qr_code_view(request, data):
    return get_qr_code_response(data)


class ProductCartView(generic.DetailView):
    model = models.Product
    context_object_name = 'product'
    template_name = 'discount/product/product_cart_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('type') == 'qr':
            uid = self.kwargs.get('uid')
            pin = self.kwargs.get('pin')
            pk = self.kwargs.get('pk')
            user = models.User.objects.get(pk=uid)
            product = models.Product.objects.get(pk=pk)
            ptc = product.find_ptc_by_user(user)
            if not pin == ptc.code:
                return None

            context['product'] = product


        else:
            user = self.request.user
        context['user'] = user
        return context

from reportlab.lib.utils import ImageReader
from reportlab.lib.utils import simpleSplit
from django.templatetags.static import static
import os

"""
def mySimpleSplit(*args, **kwargs)
    res = simpleSplit(*args, **kwargs)
    last = res.pop()
    res.insert(0, last)
    return res
"""

class SingleProductPDFView(generic.View):

    def draw_related(self, c, product, field_name, current_line, margin):
        #margin = 20
        line = 0
        vals = product.get_history_m2m_values(field_name, self.request.user)
        for val, status in vals:#getattr(product, field_name).all():
            line += margin
            #lines = simpleSplit(val.title, "Arial", 9, 580)

            if status == 'added':
                c.setFont("Arial-Bold", 9)
                txt = '+{0}'.format(val.title)
                margin = c.stringWidth(txt) + 5
                c.drawString(30 + line, current_line, txt)
                c.setFont("Arial", 9)
            elif status == 'removed':
                c.setFillColorRGB(*self.gray)
                txt = '-{0}'.format(val.title)
                margin = c.stringWidth(txt) + 5
                c.drawString(30 + line, current_line, txt)
                c.setFillColorRGB(*self.black)
            else:
                txt = val.title
                margin = c.stringWidth(txt) + 5
                c.drawString(30 + line, current_line, txt)
            if line >= 400:
                margin = 20
                current_line -= self.new_line
                line = 0
        return current_line

    def draw_product(self, c, product, line, user):
        gray = (107/256, 119/256, 119/256)
        self.gray = gray
        black = (0, 0, 0)
        self.black = black
        #green = (0, 1, 0)
        #self.green = green
        new_line = self.new_line
        code = product.get_code(user)
        current_line = line
        #current_line -= 20
        c.drawImage(os.path.join(self.static_path, 'images', 'logo3_hq.png'), x=230, y=current_line, width=120, height=60)
        current_line -= 30
        #p.addFont('pt_sansbold')
        c.setLineWidth(.1)
        c.line(30, current_line, 580, current_line)
        current_line -= 30
        brand_txt = str(product.brand).upper()
        c.setFont("Arial-Bold", 10)
        brand_txt_size = c.stringWidth(brand_txt)
        c.drawString(170, current_line, brand_txt)
        c.setFillColorRGB(*gray)
        c.setFont("Arial", 9)
        c.drawString(170 + brand_txt_size + 10, current_line, product.__str__())
        current_line -= new_line
        product_title_size = c.stringWidth(product.__str__())
        c.line(170, current_line, 170 + brand_txt_size + product_title_size + 10, current_line)
        current_line -= new_line
        stock_price_label_txt = 'Цена по акции: '
        stock_price_label_txt_size = c.stringWidth(stock_price_label_txt)
        c.drawString(170, current_line, stock_price_label_txt)
        stock_price_txt = '{0} руб.'.format(str(product.stock_price))
        c.setFont("Arial-Bold", 10)
        c.setFillColorRGB(*black)
        stock_price_txt_size = c.stringWidth(stock_price_txt)
        c.drawString(170 + stock_price_label_txt_size, current_line, stock_price_txt)
        c.setFillColorRGB(*gray)
        c.setFont("Arial", 9)
        c.drawString(170 + stock_price_label_txt_size + stock_price_txt_size + 10, current_line, 'Скидка: {0}%'.format(product.percent))
        current_line -= new_line
        code_label_txt = 'Промокод: '
        code_label_txt_size = c.stringWidth(code_label_txt)
        c.drawString(170, current_line, code_label_txt)
        c.setFillColorRGB(*black)
        c.drawString(170 + code_label_txt_size, current_line, code)
        c.setFillColorRGB(*gray)
        current_line -= 50
        img = ImageReader(get_qr_code_image(code)._img)
        c.drawImage(img, x=30, y=current_line)
        #Установить толщину линий(не текста)

        current_line -= new_line
        lines = simpleSplit(replace_newlines(product.body), c._fontname, c._fontsize, maxWidth=550)
        for line in lines:
            c.drawString(30, current_line, line)
            current_line -= new_line * 0.7
        current_line -= new_line * 1.5
        end_date_label_txt = 'Дата окончания акции: '
        end_date_label_txt_size = c.stringWidth(end_date_label_txt)
        c.drawString(30, current_line, end_date_label_txt)
        c.setFillColorRGB(*black)
        end_date_value = product.get_history_value('end_date', user)
        if len(end_date_value) == 1:
            c.drawString(30 + end_date_label_txt_size, current_line, end_date_value['value'].strftime("%d.%m.%Y"))
        elif len(end_date_value) == 2:
            c.drawString(30 + end_date_label_txt_size, current_line, 'Текущее значение: {0} Предыдущее значение: {1}'
                         .format(end_date_value['value'].strftime("%d.%m.%Y"),
                                 end_date_value['version_value'].strftime("%d.%m.%Y")))

        c.setFillColorRGB(*gray)
        current_line -= new_line
        status_label_txt = 'Статус: '
        c.drawString(30, current_line, status_label_txt)
        status_label_txt_size = c.stringWidth(status_label_txt)
        c.setFillColorRGB(*black)

        status_value = product.get_history_value('status', user)
        if len(status_value) == 1:
            c.drawString(30 + status_label_txt_size, current_line, status_value['value'])
        elif len(status_value) == 2:
            c.drawString(30 + status_label_txt_size, current_line, 'Текущее значение: {0} Предыдущее значение: {1}'
                         .format(status_value['value'], status_value['version_value']))

        #c.drawString(30 + status_label_txt_size, current_line, product.status_text)
        c.setFillColorRGB(*gray)
        current_line -= new_line


        for param_key, field_names in models.FILTER_PARAMS_FIELD_NAMES.items():
            field_name, field_label = field_names
            if product.product_type.filter_available(param_key):
                sizes_label_txt = '{0}: '.format(field_label)
                sizes_label_txt_size = c.stringWidth(sizes_label_txt)
                c.drawString(30, current_line, sizes_label_txt)
                c.setFillColorRGB(*black)
                current_line = self.draw_related(c, product, field_name, current_line, sizes_label_txt_size)
                c.setFillColorRGB(*gray)
                current_line -= new_line

        current_line -= new_line * 1.9


        c.setFont("Arial-Bold", 10)
        c.drawString(30, current_line, str(product.shop).upper())
        c.setFont("Arial", 9)
        c.setFillColorRGB(*gray)
        current_line -= new_line

        if product.shop.site:
            c.drawString(30, current_line, 'Сайт: {0}'.format(product.shop.site))
            current_line -= new_line

        if product.shop.custom_adress:
            c.drawString(30, current_line, 'Адрес:')
            current_line -= new_line

            adress_line = simpleSplit(replace_newlines(product.shop.custom_adress), c._fontname, c._fontsize, maxWidth=550)
            for adress in adress_line:
                c.drawString(30, current_line, adress)
                current_line -= new_line

        for phone in product.shop.phones.all():
            c.drawString(30, current_line, 'Телефон: {0}'.format(phone))
            current_line -= new_line

        if product.shop.work_time:
            c.drawString(30, current_line, 'Время работы:')
            current_line -= new_line

            work_time_line = simpleSplit(replace_newlines(product.shop.work_time), c._fontname, c._fontsize, maxWidth=550)
            for work_time in work_time_line:
                c.drawString(30, current_line, work_time)
                current_line -= new_line

        current_line -= 30

        c.setFont("Arial", 8)
        c.setFillColorRGB(*black)
        for condition in product.product_conditions:
            c.drawString(30, current_line, '> {0}'.format(condition))
            current_line -= new_line
        c.line(30, current_line, 580, current_line)

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        self.new_line = 17
        product = models.Product.objects.get(pk=pk)
        user = request.user
        #cart = product.carts.get(user=request.user)
        response = HttpResponse(content_type='application/pdf')
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        #The Canvas object is the primary interface for creating PDF files.
        #This class is the programmer’s interface to the PDF file format.
        # Methods are (or will be) provided here to do just about everything PDF can do.
        #if settings.DEBUG:
        self.static_path = os.path.join('discount', 'static', 'discount')
        #else:
        #    self.static_path = static(os.path.join('discount'))
        arial = ttfonts.TTFont('Arial', os.path.join(self.static_path, 'fonts', 'Aricyr', 'ARICYR.TTF'))
        arial_bold = ttfonts.TTFont('Arial-Bold', os.path.join(self.static_path, 'fonts', 'Aricyr', 'ARICYRB.TTF'))
        #Класс для использования ttf шрифтов
        pdfmetrics.registerFont(arial)
        pdfmetrics.registerFont(arial_bold)
        #Регистрируем этот шрифт, делая его доступным для использования. Причем он регистрируется в том модуле pdfmetrics
        c.setFont("Arial", 9)
        #Устанавливаем активный шрифт
        line = 750
        #height = 150
        self.draw_product(c, product, line, user=user)
        c.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response


#****************************************************
#Shop
class BaseShopView(generic.ListView):
    model = models.Product
    context_object_name = 'products'

    def get(self, request, *args, **kwargs):
        self.set_shop()
        return super().get(request, *args, **kwargs)

    def set_shop(self):
        if not hasattr(self, 'shop'):
            pk = self.kwargs.get('pk', None)
            self.shop = get_object_or_404(models.Shop, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        user = self.request.user
        if user.has_perm_for_shop(self.shop):
            context['edit_link'] = reverse('discount:shop-update', kwargs={'pk': self.shop.pk})
        #context['comment_form'] = forms.CommentForm(self.request.GET)
        #context['products'] = self.get_queryset()
        return context


class ShopDetail(BaseShopView):
    template_name = 'discount/shop/shop_detail.html'
    paginate_by = settings.PAGINATE_BY_SHOP_DETAIL

    def get_queryset(self):
        queryset = self.shop.products.get_available_products()
        return queryset




class ShopList(generic.ListView):
    model = models.Shop
    template_name = 'discount/shop/shop_list.html'
    context_object_name = 'shops'
    paginate_by = settings.PAGINATE_BY_SHOP_LIST

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(status=models.SHOP_STATUS_PUBLISHED)
        return queryset




class MoveCartFromGuestToUserMixin:

    def login_user_and_set_response(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        self.response = response

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        guest_ptcs = models.ProductToCart.get_cart_queryset(request)
        self.login_user_and_set_response(request, *args, **kwargs)
        if request.user.is_authenticated():
            if request.user.is_simple_user:
                for ptc in guest_ptcs:
                    ptc.user = request.user
                    ptc.status = models.PTC_STATUS_CART
                    product = ptc.product
                    user_ptc = product.find_ptc_by_user(request.user)
                    if user_ptc:
                        if user_ptc.status not in [models.PTC_STATUS_SUBSCRIBED, models.PTC_STATUS_BOUGHT,
                                                models.PTC_STATUS_CANCELLED]:
                            user_ptc.delete()
                        else:
                            ptc.delete()
                            #ptc.status = models.PTC_STATUS_SUBSCRIBED
                    if not ptc.product.is_available():
                        ptc.delete()

                    if ptc.pk: #Если не удалили
                        ptc.save()
            else:
                guest_ptcs.delete()

        return self.response


import json
class MoveCartFromGuestToUserMixinAndCartSubscribe(MoveCartFromGuestToUserMixin):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        ptcs = models.ProductToCart.get_cart_queryset(request)
        instant_ptc = models.ProductToCart.get_instant_ptc(request)
        if request.user.is_authenticated() and (ptcs.count() > 0 or instant_ptc is not None) and request.user.profile.role == models.USER_ROLE_DEFAULT:
            if instant_ptc is not None:
                instant_ptc.status = models.PTC_STATUS_SUBSCRIBED
                instant_ptc.save()
                products = [instant_ptc.product]
            else:
                for ptc in ptcs:
                    ptc.status = models.PTC_STATUS_SUBSCRIBED
                    ptc.save()
                products = models.Product.objects.filter(cart_products__in=list(ptcs))

            models.ProductMail.send_products_messages(products, request.user, subscribed=True)
            data = {}
            data['location'] = reverse('discount:product-list-code')
            content = json.dumps(data)
            self.response.content = content
        return self.response


class DiscountCartLoginView(MoveCartFromGuestToUserMixinAndCartSubscribe, LoginView):
    template_name = 'discount/user/_cart_login.html'
    form_class = forms.DiscountLoginForm

class DiscountCartSignupView(MoveCartFromGuestToUserMixinAndCartSubscribe, SignupView):
    template_name = 'discount/user/_cart_signup.html'
    form_class = forms.DiscountSignupForm

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DiscountLoginView(MoveCartFromGuestToUserMixin, LoginView):
    form_class = forms.DiscountLoginForm
    template_name = 'discount/user/_login.html'

class DiscountFullLoginView(MoveCartFromGuestToUserMixin, LoginView):
    form_class = forms.DiscountLoginForm
    template_name = 'discount/user/full_login.html'




class DiscountSignupView(MoveCartFromGuestToUserMixin, SignupView):
    template_name = 'discount/user/full_signup.html'
    form_class = forms.DiscountSignupForm

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        res = super().post(request, *args, **kwargs)
        #if request.user.is_authenticated():
            #self.cart.append_user_data(self.request)
        #if self.cart is not None:
            #profile = models.UserProfile.get_profile(request.user)
            #profile.phone = self.form.cleaned_data['phone']
            #profile.save()
        return res



#TODO доделать, разобрать
class HistoryList(generic.ListView):
    template_name = 'discount/history/history_list.html'
    context_object_name = 'history'

    def get_queryset(self):
        product_history_queryset = models.ProductHistory.objects.all()
        product_type_history_queryset = models.ProductTypeHistory.objects.all()
        result_list = list(chain(product_history_queryset, product_type_history_queryset))
        return result_list


#***********************************************
#User
class UserDetail(generic.TemplateView):
    template_name = 'discount/user/user_detail.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if not user.is_authenticated():
            return HttpResponseRedirect(reverse('discount:full-login'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, user_form=None, profile_form=None, **kwargs):
        user = self.request.user
        if not user.is_authenticated():
            raise Exception('Пользователь не найден') #По идее исключено, поскольку проверяем в dispatch
        profile = user.profile
        context = super().get_context_data(**kwargs)
        context['user'] = user
        if user_form is None:
            user_form = forms.UserForm(instance=user)
        if profile_form is None:
            profile_form = forms.ProfileForm(instance=profile)
        context['user_form'] = user_form
        context['profile_form'] = profile_form
        shopstousers = user.shopstousers_set.all()
        if shopstousers is not None:
            context['shopstousers'] = shopstousers
            #context['shop_confirmed'] = shop.confirmed(user)

        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        profile = user.profile
        if not user.is_authenticated():
            raise Exception('Пользователь не найден')
        user_form = forms.UserForm(request.POST, instance=user)
        profile_form = forms.ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect(reverse('discount:user-detail'))
        else:
            return self.render_to_response(self.get_context_data(user_form=user_form, profile_form=profile_form))



class ContactsPageView(generic.TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['active_menu_item'] = 'contacts-page'
        return context

    template_name = 'discount/static/contacts_page.html'

"""
class ConditionsPageView(generic.TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['active_menu_item'] = 'conditions-page'
        return context
    template_name = 'discount/general/conditions_page.html'
"""

class HelpPageView(generic.TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['active_menu_item'] = 'help-page'
        return context

    template_name = 'discount/static/help_page.html'


"""
class ShopBaseView(generic.TemplateView):

    def set_model(self, **kwargs):
        if 'pk' in kwargs:
            model = models.Shop.objects.get(pk=kwargs['pk'])
            self.model = model
        else:
            self.model = None

    def post(self, request, *args, **kwargs):
        #if kwargs['action'] == 'update':
        #    instance = models.Shop.objects.get(pk=)

        self.set_model(**kwargs)
        data = request.POST.copy()
        if 'to-approve' in request.POST:
            data['status'] = str(models.SHOP_STATUS_TO_APPROVE)
        elif self.model is None:
            data['status'] = str(models.SHOP_STATUS_PROJECT)
        else:
            data['status'] = self.model.status


        form = forms.ShopForm(data, request.FILES, instance=self.model)

        if form.is_valid():
            shop = form.save()
            return HttpResponseRedirect(reverse('discount:shop-detail', kwargs={'pk':shop.pk}))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if form is None:
            form = forms.ShopForm(instance=self.model)
        context['form'] = form
        if self.model is not None:
            context['action_url'] = reverse('discount:shop-update', kwargs={'pk': self.model.pk})
        else:
            context['action_url'] = reverse('discount:shop-create')
        return context

    def get(self, request, *args, **kwargs):
        self.set_model(**kwargs)
        return super().get(request, *args, **kwargs)

"""


class ShopCreate(generic.TemplateView):
    #form_class = forms.ShopForm
    template_name = 'discount/shop/shop_create.html'
    #model = models.Shop

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated():
            return HttpResponseRedirect(reverse('discount:full-login'))
        self.set_model(**kwargs)
        user_shop = user.get_shop
        if self._model is None and not user_shop is None \
                or self._model is not None and not user.has_perm_for_shop(self._model):
            if user_shop is not None:
                pk = user_shop.pk
            elif self._model is not None:
                pk = self._model.pk
            else:
                pk = None
            if pk is not None:
                return HttpResponseRedirect(reverse('discount:shop-detail', kwargs={'pk': pk}))
            else:
                return HttpResponseRedirect(reverse('discount:main-page'))
        return super().dispatch(request, *args, **kwargs)

    def set_model(self, **kwargs):
        if not hasattr(self, '_model') and 'pk' in kwargs:
            model = get_object_or_404(models.Shop, pk=kwargs['pk'])
        else:
            model = None
        self._model = model

    def post(self, request, *args, **kwargs):
        #self.set_model(**kwargs)
        today = get_today()
        if self._model is not None:
            orig_status = self._model.status
        else:
            orig_status = models.SHOP_STATUS_PROJECT

        form = forms.ShopForm(request.POST, request.FILES, user=request.user, instance=self._model)
        phone_formset = forms.ShopPhoneFormset(request.POST, instance=self._model)
        user_formset = forms.ShopUserFormset(request.POST, instance=self._model)
        form_valid = form.is_valid()
        phone_formset_valid = phone_formset.is_valid()
        user_formset_valid = user_formset.is_valid()
        if form_valid and phone_formset_valid and user_formset_valid:
            shop = form.save(commit=False)
            #submit_type = request.POST.get('submit-type', None)
            #if not submit_type:
            if 'to-approve' in request.POST:
                submit_type = 'to-approve'
            else:
                submit_type = 'to-save'
                    #product.status = orig_status
            if submit_type == 'to-approve':
                shop.status = str(models.SHOP_STATUS_TO_APPROVE)
            elif submit_type == 'to-save':
                if not shop.pk:
                    shop.status = str(models.SHOP_STATUS_PROJECT)
                #shop.end_date = today
            else:
                shop.status = orig_status
            shop.save()
            form.save_m2m()
            phone_formset = forms.ShopPhoneFormset(request.POST, instance=shop)
            if phone_formset.is_valid():
                phone_formset.save()
            user_formset = forms.ShopUserFormset(request.POST, instance=shop)
            if user_formset.is_valid():
                user_formset.save()
                try:
                    shop_to_users = models.ShopsToUsers.objects.get(shop=shop, user=request.user, confirmed=False)
                    shop_to_users.confirmed = True
                    shop_to_users.save()
                except:
                    pass

                shop_to_users = models.ShopsToUsers.objects.filter(shop=shop, user=request.user)
                if not shop_to_users:
                    models.ShopsToUsers.objects.create(user=request.user, shop=shop, confirmed=True)
                profile = request.user.profile
                if not profile.role == models.USER_ROLE_TATAMO_MANAGER:
                    profile.role = models.USER_ROLE_SHOP_MANAGER


            return HttpResponseRedirect(reverse('discount:shop-detail', kwargs={'pk':shop.pk}))
        else:
            return self.render_to_response(self.get_context_data(form=form, phone_formset=phone_formset, user_formset=user_formset))

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, form=None, phone_formset=None, user_formset=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if form is None:
            form = forms.ShopForm(user=self.request.user, instance=self._model)
        if phone_formset is None:
            phone_formset = forms.ShopPhoneFormset(instance=self._model)
        if user_formset is None:
            user_formset = forms.ShopUserFormset(instance=self._model)

        #if self._model and self._model.status == models.SHOP_STATUS_TO_APPROVE:
        #    phone_formset.forms = [phone_form for phone_form in phone_formset.forms if 'phone' in phone_form.initial]
        #    user_formset.forms = [user_formset for user_formset in user_formset.forms if 'user' in user_formset.initial]




        if self._model is not None:
            context['status_text'] = self._model.status_text
            context['shop'] = self._model
            context['brands'] = self._model.brands.all()
            context['brands_count'] = self._model.brands.all().count()

        context['form'] = form
        if form.initial_value('tatamo_comment') == None:
            del form.fields['tatamo_comment']


        context['phone_formset'] = phone_formset
        context['user_formset'] = user_formset
        context['show_save_button'] = not self._model or self._model and not self._model.status == models.SHOP_STATUS_TO_APPROVE
        context['show_submit_button'] = not self._model or self._model.status == models.SHOP_STATUS_PROJECT or self._model.status == models.SHOP_STATUS_NEED_REWORK
        if not context['show_submit_button']:
            del form.fields['shop_comment']

        if self._model and self._model.pk:
            context['user_formset_cls'] = 'users-block'
        else:
            context['user_formset_cls'] = 'hidden'
        context['logins'] = models.User.objects.all().values_list('username', flat=True)
        return context


class ShopsToUsersConfirm(generic.View):
    def post(self, request, *args, **kwargs):
        user = request.user
        shop_to_user = models.ShopsToUsers.objects.get(pk=request.POST.get('shopstouser'))
        #form = forms.ShopsToUsersConfirmForm(request.POST, instance=shop_to_user)
        form_user = shop_to_user.user
        if not user.is_authenticated() or not user == form_user :
            raise Exception('Текущий пользователь не авторизован')
        shop = shop_to_user.shop
        if 'confirm' in request.POST:
            submit_type = 'confirm'
        else:
            submit_type = 'cancel'
        if shop is not None:
            if submit_type == 'confirm':
                shop_to_user.confirmed = True
                shop_to_user.save()
            else:
                shop_to_user.delete()
        return HttpResponseRedirect(reverse('discount:user-detail'))


class BlockedDaysView(generic.TemplateView):
    template_name = 'discount/payment/blocked_money_view.html'

    @shop_manager_only()
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        shop = user.get_shop
        products = models.Product.objects.filter(shop=shop, actions__points_blocked__gt=0).distinct()
        context['products'] = products
        return context

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_shop_manager:
            return HttpResponseRedirect(reverse('discount:full-login'))
        return self.render_to_response(self.get_context_data(**kwargs))



class ShopOfferView(generic.TemplateView):
    template_name = 'discount/static/shop_offer.html'

    def dispatch(self, request, *args, **kwargs):
        request.session['shop_offer'] = True
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if not user.is_authenticated():
            return context
        context['user'] = user
        shop = user.get_shop
        if shop is not None:
            context['shop'] = shop
            has_shop_on_approve = True
        unapproved_shops = user.get_unconfirmed_shops()
        if shop is None:
            has_shop_on_approve = False
        shop_to_approve = None
        if shop is None and unapproved_shops is not None and unapproved_shops.count() > 0:
            for unapproved_shop in unapproved_shops:
                if unapproved_shop.status == models.SHOP_STATUS_TO_APPROVE:
                    has_shop_on_approve = True
                else:
                    shop_to_approve = unapproved_shop

        context['has_shop_on_approve'] = has_shop_on_approve
        context['shop_to_approve'] = shop_to_approve
        if shop:
            available_products_count = shop.products.all().count()
            if available_products_count > 0:
                context['has_products'] = True
            approved_available_products_count = shop.products.filter(status__in=[models.STATUS_READY, models.STATUS_PUBLISHED]).count()
            if approved_available_products_count > 0:
                context['has_approved_products'] = True

        return context



def get_coupon_status_context(request, product):
    url_name = request.resolver_match.url_name
    user = request.user
    if not user.is_simple_user:
        return
    code = None
    ptc = product.find_ptc_by_user(user=user, request=request)
    subscribed = ptc is not None and ptc.status == models.PTC_STATUS_SUBSCRIBED
    #show_short = url_name == 'main-page'
    show_bought = False
    if subscribed:
        code = product.get_code(user)
    elif ptc is not None and ptc.status == models.PTC_STATUS_BOUGHT:
        show_bought = True


    return {'code': code, 'product': product, 'subscribed': subscribed, 'show_bought': show_bought }


class CouponStatus(generic.TemplateView):
    template_name = 'discount/widgets/_product_coupon_status.html'

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        product = models.Product.objects.get(pk=pk)
        context = get_coupon_status_context(self.request, product)
        return context

    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))


def get_ptc_subscribe_actions_context(product, request=None, user=None):
    url_name = request.resolver_match.url_name
    if user is None and request is not None:
        user = request.user
    if not user.is_simple_user: #Подписываться может только простой пользователь
        return

    if not product.is_available():
        return
    ptc = product.find_ptc_by_request(request)

    input_cls = 'action-submit'
    action = None
    button_name = None
    #status_text = None
    action_url = reverse('discount:ptc-subscribe', kwargs={'pk': product.pk})
    code = product.get_code(user)


    #if action in ['unsubscribe_form', 'unsubscribe_form_repeated']:
    #    unsubscribe_form = forms.UnsubscribeForm()
    #    ptc_action = 'unsubscribe_form_repeated'
    #    ptc_button_name = 'Отправить'
    if ptc is None or ptc.status in [models.PTC_STATUS_CART, models.PTC_STATUS_INSTANT]:
        if url_name == 'product-detail':
            action = 'first_subscribe'
            button_name = 'Мгновенно получить промокод'


    elif ptc.status == models.PTC_STATUS_SUBSCRIBED:
        action = 'unsubscribe_form'
        button_name = 'Отменить подписку'
        #status_text = 'Вы подписаны на эту акцию'
        #unsubscribe_form = forms.UnsubscribeForm()

    elif ptc.status == models.PTC_STATUS_FINISHED_BY_SHOP:
        action = None
        button_name = None
        #status_text = None
    elif ptc.status == models.PTC_STATUS_BOUGHT:
        action = None
        button_name = None
        #status_text = 'Вы приобрели товар по этой акции'
    elif ptc.status == models.PTC_STATUS_CANCELLED:
        action = 'subscribe'
        button_name = 'Вернуть подписку'
        #status_text = 'Вы отписались от этой акции'



    return {'action_url': action_url, 'action': action,
                'button_name': button_name,
                 'product': product, 'code': code, 'input_cls': input_cls}



def get_ptc_add_actions_context(product, request=None, user=None, action=None):
        url_name = request.resolver_match.url_name
        #main_page = url_name == 'main-page' or 'main_page' in request.POST
        if user is None and request is not None:
            user = request.user
        if user.is_shop_manager:
            return

        if not product.is_available():
            return
        ptc = product.find_ptc_by_request(request)


        submit_button_name = None
        action = None
        input_cls = 'action-submit'
        block_cls = 'add-btn'
        inner_block_cls = 'action-submit-block'
        action_url = reverse('discount:ptc-add', kwargs={'pk': product.pk})


        if ptc is None or ptc.status in [models.PTC_STATUS_INSTANT]:
            submit_button_name = 'Добавить в корзину'
            input_cls += ' action-submit-input-add-product-to-cart'
            block_cls += ' action-submit-block-add-product-to-cart'
            inner_block_cls += ' inner-submit-block-add-product-to-cart'
            action = 'add'
        elif ptc.status in [models.PTC_STATUS_CART, models.PTC_STATUS_INSTANT]:
            submit_button_name = 'Удалить из корзины'
            input_cls += ' action-submit-input-remove-product-from-cart'
            block_cls += ' action-submit-block-remove-product-from-cart'
            inner_block_cls += ' inner-submit-block-remove-product-from-cart'
            action = 'remove'



        return {'action_url': action_url, 'submit_button_name': submit_button_name,
                'action': action, 'product': product, 'product': product,
                'input_cls': input_cls, 'block_cls': block_cls, 'inner_block_cls': inner_block_cls}


class RecreateProductPayments(generic.View):

    @shop_manager_only()
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        product = models.Product.objects.get(pk=pk)
        product.prepare_product_account()
        return HttpResponseRedirect(reverse('discount:product-detail', kwargs={'pk': pk}))

class ActionDaysView(generic.TemplateView):
    template_name = 'discount/product/action_days_view.html'

    @shop_manager_only()
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if 'submit' in request.GET:
            form = forms.ActionDaysForm(data=request.GET)
        else:
            form = forms.ActionDaysForm(initial=request.GET)

        return self.render_to_response(self.get_context_data(form=form))


    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = form

        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            category = form.cleaned_data.get('category')
            end_date = form.cleaned_data.get('end_date')
            action_type = int(form.cleaned_data.get('action_type'))
            days = models.get_actions_count_for_interval(action_type, start_date, end_date, category=category)
            context['days'] = days
            if action_type == models.ACTION_TYPE_POPULAR:
                context['max_actions'] = settings.MAX_POPULAR_COUNT
            elif action_type == models.ACTION_TYPE_CATEGORY:
                context['max_actions'] = settings.MAX_POPULAR_COUNT
        return context


class PaymentHistoryView(generic.TemplateView):
    template_name = 'discount/payment/payment_history.html'

    @shop_manager_only()
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        shop = user.get_shop
        today = get_today()

        data = self.request.GET.copy()
        if not 'start_date' in data:
            data['start_date'] = today + timezone.timedelta(days=-7)
        if not 'end_date' in data:
            data['end_date'] = today
        form = forms.BasePeriodForm(data=data)
        context['form'] = form

        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            ts = models.Payment.objects.filter(shop=shop, period__lte=end_date, period__gte=start_date)
            try:
                points_total = ts.aggregate(Sum('points'))['points__sum']
                if points_total is None:
                    points_total = 0
            except:
                points_total = 0

            context['payments'] = ts.order_by('-created')
            context['points_total'] = points_total
        return context

#Начнем с даты
#class PostRender(generic.View):
#    def post(self, request, *args, **kwargs):
#
#
#
#        return JsonResponse({'test': 'OK'})


class SubscriptionConfirmView(generic.TemplateView):
    template_name = 'discount/subscription/confirmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        action_type = kwargs['action_type']
        user = self.request.user
        active_subscription = user.active_subscription
        shop = user.get_shop
        shop_from_subscription = getattr(active_subscription, 'shop', None)
        if shop_from_subscription and not shop == shop_from_subscription:
            raise Exception('Ошибка валидации пользователя')

        new_subscription_pk = self.kwargs.get('pk', None)

        context['action_type'] = action_type
        context['subscription_pk'] = new_subscription_pk
        context['planned_subscription_type'] = shop.planned_subscription
        if active_subscription:
            context['active_subscription_type'] = active_subscription.subscription_type
        if new_subscription_pk:
            new_subscription_type = models.SubscriptionType.objects.get(pk=new_subscription_pk)
            context['new_subscription_type'] = new_subscription_type
            if active_subscription:
                active_subscription_unused_price = active_subscription.unused_price
            else:
                active_subscription_unused_price = 0
            to_pay = new_subscription_type.price - active_subscription_unused_price
            context['to_pay'] = to_pay

        if action_type == 'confirm-now' and to_pay > shop.points_free:
             context['show_confirm'] = False
        else:
            context['show_confirm'] = True
        return context

    @shop_manager_only()
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('discount:subscription-manage'))

        today = get_today()

        active_subscription = user.active_subscription
        shop = user.get_shop
        shop_from_subscription = getattr(active_subscription, 'shop', None)
        to_pay_confirmed = helper.to_int(request.POST.get('to-pay'))
        if shop_from_subscription and not shop == shop_from_subscription:
            raise Exception('Ошибка валидации пользователя')

        action_type = request.POST.get('action-type')
        if action_type in ['enable-autopay', 'disable-autopay']:
            if action_type == 'enable-autopay':
                active_subscription.auto_pay = True
            else:
                active_subscription.auto_pay = False
            active_subscription.save()
            return HttpResponseRedirect(reverse('discount:subscription-manage'))

        elif action_type == 'cancel-planned':
            shop.subscription_set.filter(status=models.SUBSCRIPTION_STATUS_PLANNED).delete()
            return HttpResponseRedirect(reverse('discount:subscription-manage'))

        else:
            try:
                new_subscription_type_pk = request.POST.get('subscription-pk', None)
                new_subscription_type = models.SubscriptionType.objects.get(pk=new_subscription_type_pk, available=True)

            except:
                new_subscription_type = None
            new_subscription = models.Subscription()
            new_subscription.subscription_type = new_subscription_type
            #new_subscription.user = user
            new_subscription.user = user
            new_subscription.shop = shop

            if action_type == 'confirm-now':
                if new_subscription_type.price == 0 and not shop.free_subscription_available:
                    return HttpResponseRedirect(reverse('discount:subscription-manage'))
                if active_subscription and active_subscription.subscription_type == new_subscription_type:
                    return HttpResponseRedirect(reverse('discount:subscription-manage'))

                if active_subscription is None:
                    active_subscription_unused_price = 0
                else:
                    active_subscription_unused_price = active_subscription.unused_price

                money_available = shop.points_free

                if new_subscription_type.price > 0 and new_subscription_type.price > active_subscription_unused_price: #С доплатой
                    to_pay = new_subscription_type.price - active_subscription_unused_price
                    if not to_pay == to_pay_confirmed:
                        raise MoneyExeption('Не удалось провести оплату')
                    if to_pay <= money_available:
                        try:
                            with transaction.atomic():
                                new_subscription.save()
                                models.Payment.subscription_type_pay(shop, user, to_pay, new_subscription)
                        except models.MoneyExeption:
                            raise MoneyExeption('Недостаточно средств')
                    else:
                        raise MoneyExeption('Недостаточно средств')
                elif new_subscription_type.price == 0 or active_subscription_unused_price == new_subscription_type.price:
                    pass

                new_subscription.start_date = today
                new_subscription.set_end_date()
                new_subscription.status = models.SUBSCRIPTION_STATUS_ACTIVE
                new_subscription.save()

                shop.subscription_set.filter(status=models.SUBSCRIPTION_STATUS_PLANNED).delete()

                if active_subscription:
                    active_subscription.status = models.SUBSCRIPTION_STATUS_CANCELLED
                    active_subscription.end_date = today
                    active_subscription.save()

            elif action_type == 'confirm-plan':
                start_date = active_subscription.end_date.replace(day=active_subscription.end_date.day + 1)

                active_subscription.auto_pay = False
                active_subscription.save()

                new_subscription.start_date = start_date
                new_subscription.set_end_date()
                new_subscription.status = models.SUBSCRIPTION_STATUS_PLANNED
                new_subscription.save()
        return HttpResponseRedirect(reverse('discount:subscription-manage'))


class SubscriptionManageView(generic.TemplateView):
    template_name = 'discount/subscription/manage.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if not user.is_authenticated():
            return HttpResponseRedirect(reverse('discount:full-login'))
        elif not user.is_shop_manager:
            HttpResponseRedirect(reverse('discount:shop-create'))
        else:
            return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        shop = user.get_shop
        active_subscription = shop.active_subscription
        if active_subscription:
            context['active_subscription'] = active_subscription

        planned_subscription = shop.planned_subscription
        if planned_subscription:
            context['planned_subscription'] = planned_subscription

        available_subscriptions = models.SubscriptionType.objects.filter(available=True)
        available_subscriptions_list = []
        if active_subscription:
            available_subscriptions = available_subscriptions.exclude(pk=active_subscription.subscription_type.pk)
        if planned_subscription:
            available_subscriptions = available_subscriptions.exclude(pk=planned_subscription.subscription_type.pk)

        if active_subscription or not shop.free_subscription_available:
            available_subscriptions = available_subscriptions.exclude(price=0)
            for available_subscription in available_subscriptions:
                available_subscription.additional_price = available_subscription.get_additional_price(active_subscription)
                available_subscriptions_list.append(available_subscription)
            context['available_subscriptions'] = available_subscriptions_list
        else:
            context['available_subscriptions'] = available_subscriptions

        return context


class SubscriptionTypeDetailView(generic.DetailView):
    template_name = 'discount/subscription/subscription_type_detail.html'
    model = models.SubscriptionType
    context_object_name = 'subscription_type'







class GetAvailableProductTypesAjax(generic.View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        category_id = helper.to_int(request.POST.get('category-id',0))
        product_type_id = helper.to_int(request.POST.get('type-id', 0))
        try:
            category = models.ProductType.objects.get(pk=category_id)
        except:
            category = None

        if category:
            try:
                product_type = models.ProductType.objects.get(pk=product_type_id)
                product_type_ok = product_type in category.get_all_childs()

            except:
                product_type_ok = False
                product_type = None

            pseudo_queryset = category.product_create_pseudo_queryset()

            if product_type_ok:
                frm = forms.ProductFormProductType(pseudo_queryset, initial={'product_type': product_type_id})
            else:
                frm = forms.ProductFormProductType(pseudo_queryset)
            text = frm['product_type'].__str__()
        else:
           text = forms.ProductFormProductType(queryset=models.ProductType.objects.none()).__str__()
        data['text'] = text
        #Правильнее сделать view, который будет рендерить в шаблон и отдавать эту форму . Но так веселее.
        return JsonResponse(data)


class GetAvailableFiltersAjax(generic.View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        product_type_id = helper.to_int(request.POST.get('type-id', 0))
        try:
            category = models.ProductType.objects.get(pk=product_type_id)
            #sizes = True
            #sizes = category.dress_sizes_filter_available
            #colors = category.colors_filter_available
        except:
            category = None

        for param_key, field_names in models.FILTER_PARAMS_FIELD_NAMES.items():
            field_name, field_label = field_names
            if category and category.filter_available(param_key):
                data[field_name] = True
            else:
                data[field_name] = False

        return JsonResponse(data)



"""
class GetProductTypeItem(generic.TemplateView):
    template_name = 'discount/product/_product_type_item.html'

    def get_context_data(self, **kwargs):
        form = forms.ProductTypeItemMiniForm()
"""





from django.forms.models import model_to_dict


class ProductBannersView(generic.TemplateView):
    template_name = 'discount/product/product_banners.html'

    product = property(get_product)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm_for_product(self.product):
            return HttpResponseRedirect(reverse('discount:full-login'))
        else:
            return super().dispatch(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        product = self.product
        banner_formset = forms.ProductBannerFormset(request.POST, request.FILES, instance=product)
        if banner_formset.is_valid():
            banners = banner_formset.save()
            #Отправляем все баннеры на повторное согласование
            for banner in product.productbanner_set.filter(status=models.BANNER_STATUS_NEED_REWORK):
                banner.status = models.BANNER_STATUS_ON_APPROVE
                banner.save()
            return HttpResponseRedirect(reverse('discount:product-detail', kwargs={'pk': product.pk}))
        else:
            return self.render_to_response(self.get_context_data(banner_formset, **kwargs))


    def get_context_data(self, banner_formset=None, **kwargs):
        product = self.product
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        #context['show_button_statuses'] = [models.BANNER_STATUS_NEED_REWORK, models.BANNER_STATUS_PROJECT]
        #context['approved_status'] = models.BANNER_STATUS_APPROVED
        if not banner_formset:
            banner_formset = forms.ProductBannerFormset(instance=product)
        context['banner_formset'] = banner_formset

        return context



class ProductActionsView(generic.TemplateView):
    template_name = 'discount/product/product_actions.html'

    product = property(get_product)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm_for_product(self.product):
            return HttpResponseRedirect(reverse('discount:full-login'))
        else:
            return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        product = self.product
        action_formset = forms.ProductActionFormset(request.POST, request.FILES, instance=product)
        if action_formset.is_valid():
            try:
                with transaction.atomic():
                    action_formset.save()
                    #product.prepare_product_account()

                    #product.prepare_product_account()
                    product.pay()

            except models.MoneyExeption as me:
                action_formset._non_form_errors += list(me.args)
                return self.render_to_response(self.get_context_data(action_formset, **kwargs))
            except ValidationError as ve:
                action_formset._non_form_errors += [arg for arg in ve.args if arg ]
                return self.render_to_response(self.get_context_data(action_formset, **kwargs))
            except:
                raise Exception('При сохранении произошла непредвиденная ошибка. Пожалуйста, обратитесь к поддержке')
            return HttpResponseRedirect(reverse('discount:product-detail', kwargs={'pk': product.pk}))
        else:
            return self.render_to_response(self.get_context_data(action_formset, **kwargs))


    def get_context_data(self, action_formset=None, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.product
        context['product'] = product
        if not action_formset:
            action_formset = forms.ProductActionFormset(instance=product)
        context['action_formset'] = action_formset


        return context


"""
class SendBannerToApproveView(generic.View):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        #product_pk = kwargs.get('pk')

        #post = {}
        #files = {}

        #for key, value in request.POST.items():
        #    if key[-3:] == '-id':
        #        post['id'] = value
        #    elif key[-12:] == 'shop_comment':
        #        post['shop_comment'] = value
        #    #elif key[-7:] == '-status':
        #    #    post['status_id'] = value
        #    elif key[-14:] == 'tatamo_comment':
        #        post['tatamo_comment'] = value
        #    elif key[-8:] == '-product':
        #        post['product'] = value
        #for key, value in request.FILES.items():
        #    if key[-7:] == '-banner':
        #        files['banner'] = value

        if request.POST.get('id', ''):
            product_banner = models.ProductBanner.objects.get(pk=request.POST.get('id'))
        else:
            product_banner = None
        #product = models.Product.objects.get(pk=product_pk)
        banner_form = forms.ProductBannerForm(request.POST, request.FILES, instance=product_banner)
        data = {}
        if banner_form.is_valid():
            banner = banner_form.save(commit=False)
            banner.status = models.BANNER_STATUS_ON_APPROVE
            banner.save()
            data['status'] = 1
            data['text'] = banner.pk
        else:
            data['status'] = 2




        return JsonResponse(data)

"""
import time
class ProductStartView(generic.View):

    product = property(get_product)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm_for_product(self.product):
            return HttpResponseRedirect(reverse('discount:full-login'))
        else:
            return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        product = self.product
        today = get_today()
        if not request.user.has_perm_for_product(product):
            return HttpResponseRedirect(reverse('discount:full-login'))
        if product.status in [models.STATUS_APPROVED, models.STATUS_SUSPENDED]:
            try:
                with transaction.atomic():
                    product.status = models.STATUS_PUBLISHED
                    product.save()
                    #product.prepare_product_account()
                    product.pay()
                    #product.prepare_product_account()
            except (ValidationError, MoneyExeption):
                return HttpResponseRedirect(reverse('discount:product-update', kwargs={'pk': product.pk}))
            except:
                raise Exception('При сохранении произошла непредвиденная ошибка. Пожалуйста, обратитесь к поддержке')
        return HttpResponseRedirect(reverse('discount:product-detail', kwargs={'pk': product.pk}))

class GetProductToPayView(generic.View):
    product = property(get_product)

    def post(self, request, *args, **kwargs):
        today = get_today()
        product = self.product

        to_pay = 0
        if product.status == models.STATUS_PUBLISHED:
            action_formset = forms.ProductActionFormset(request.POST, instance=product)
            if action_formset.is_valid():
                for form_data in action_formset.cleaned_data:
                        start_date = form_data.get('start_date', None)
                        end_date = form_data.get('end_date', None)
                        start = form_data.get('start', False)
                        action_type = form_data.get('action_type', None)
                        if not(start_date and end_date and action_type and start):
                            continue
                        if start_date <= today <= end_date and start and not product.day_paid(action_type, today):
                            to_pay += models.get_action_cost(action_type)
        return JsonResponse({'to_pay': to_pay})


class ProductChangeView(generic.TemplateView):
    template_name = 'discount/product/product_change.html'


    def update_related_field(self, related_field_name, key_field_name, cls):
        product = self.product
        changer = self.changer
        product_values = list(getattr(product, related_field_name).all().values_list(key_field_name, flat=True))
        changer_values = list(getattr(changer, related_field_name).all().values_list(key_field_name, flat=True))

        all_values = list(set(product_values + changer_values))

        to_add = []
        to_remove = []
        for value in all_values:
            if value in product_values and not value in changer_values:
                to_add.append(value)
            elif value not in product_values and value in changer_values:
                to_remove.append(value)

        flt = {'{0}__in'.format(key_field_name): to_remove}
        getattr(changer, related_field_name).filter(**flt).delete()
        for value in to_add:
            elem = cls()
            elem.product_changer = changer
            setattr(elem, key_field_name, value)
            elem.save()

    def get(self, request, *args, **kwargs):
        changer = self.changer
        product = self.product
        if changer.status == models.SHOP_STATUS_PROJECT:
            changer.title = product.title
            changer.product_type = product.product_type
            changer.brand = product.brand
            changer.body = product.body
            changer.normal_price = product.normal_price
            changer.stock_price = product.stock_price
            changer.link = product.link
            changer.product_shop_code = product.product_shop_code
            changer.compound = product.compound
            changer.product_type = product.product_type
            changer.save()

            self.update_related_field('images', 'image', models.ProductChangerImage)
            self.update_related_field('conditions', 'condition', models.ProductChangerCondition)


        return self.render_to_response(self.get_context_data(**kwargs))


    def dispatch(self, request, *args, **kwargs):
        product = models.Product.objects.get(pk=kwargs.get('pk'))
        self.product = product
        try:
            changer = models.ProductChanger.objects.get(~Q(status=models.STATUS_APPROVED), product=product)
        except:
            changer = models.ProductChanger(product=product)


        self.changer = changer
        self.product = product
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, form=None, image_formset=None, condition_formset=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['changer'] = self.changer
        context['product'] = self.product
        if not form:
            form = forms.ProductChangerForm(instance=self.changer, user=self.request.user)
        context['form'] = form
        if not condition_formset:
            condition_formset = forms.ProductChangerConditionFormset(instance=self.changer)
        context['condition_formset'] = condition_formset
        if not image_formset:
            image_formset = forms.ProductChangerImageFormset(instance=self.changer)
        context['image_formset'] = image_formset
        if self.changer.status in [models.STATUS_PROJECT, models.STATUS_NEED_REWORK]:
            context['send_button_available'] = True
        return context

    def post(self, request, *args, **kwargs):
        if 'confirm' in request.POST:
            form = forms.ProductChangerForm(request.POST, instance=self.changer, user=self.request.user)
            image_formset = forms.ProductChangerImageFormset(request.POST, request.FILES, instance=self.changer)
            condition_formset = forms.ProductChangerConditionFormset(request.POST, instance=self.changer)
            if form.is_valid() and image_formset.is_valid() and condition_formset.is_valid():
                changer = form.save(commit=False)
                changer.status = models.STATUS_TO_APPROVE
                changer.save()
                image_formset.save()
                condition_formset.save()

                return HttpResponseRedirect(reverse('discount:product-detail', kwargs={'pk': self.product.pk}))
            else:
                return self.render_to_response(self.get_context_data(form, image_formset))
        elif 'delete' in request.POST:
            self.changer.delete()
            return HttpResponseRedirect(reverse('discount:product-detail', kwargs={'pk': self.product.pk}))



class AdmLoadProductsView(generic.TemplateView):
    template_name = 'discount/adm/adm_load_products.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            return HttpResponseRedirect(reverse('discount:full-login'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if not form:
            form = forms.AdmLoadProductsForm()
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        form = forms.AdmLoadProductsForm(request.POST, request.FILES)
        if form.is_valid():
            user = self.request.user
            shop = form.cleaned_data.get('shop', None)
            file = form.cleaned_data['file']
            from discount.load_products import ProductLoader
            l = ProductLoader(file, user, shop)
            errors, products = l.load()
            context = self.get_context_data(**kwargs)
            context['errors'] = errors
            context['products'] = products
            context['form'] = form
            return self.render_to_response(context)
        else:
            return self.render_to_response(self.get_context_data(form=form))



class AdmMonitorView(generic.TemplateView):
    template_name = 'discount/adm/adm_monitor_view.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff and not user.is_tatamo_manager:
            return HttpResponseRedirect(reverse('discount:full-login'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = models.AdminMonitorMail.get_products_queryset().all()
        banners = models.AdminMonitorMail.get_banners_queryset().all()
        shops = models.AdminMonitorMail.get_shops_queryset().all()
        changers = models.AdminMonitorMail.get_changers_queryset().all()
        contact_forms = models.AdminMonitorMail.get_contact_forms_queryset().all()

        context['products'] = products
        context['banners'] = banners
        context['shops'] = shops
        context['changers'] = changers
        context['contact_forms'] = contact_forms
        return context


class AdmShopsMonitorView(generic.TemplateView):
    template_name = 'discount/adm/adm_shops_monitor_view.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff and not user.is_tatamo_manager:
            return HttpResponseRedirect(reverse('discount:full-login'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        shops_list = []
        shops = models.Shop.objects.exclude(pk=1).order_by('created')
        context['shops'] = shops
        return context

class ProductTatamoManagerApproveView(generic.View):
    def post(self, request, *args, **kwargs):
        product_pk = kwargs.get('pk')
        product = models.Product.objects.get(pk=product_pk)
        form = forms.ProductTatamoManagerApproveForm(request.POST)
        if form.is_valid():
            product.status = form.cleaned_data['status']
            product.tatamo_comment = form.cleaned_data['tatamo_comment']
            product.save()
        return HttpResponseRedirect(reverse('discount:monitor'))


class ShopInstructionsView(generic.TemplateView):
    template_name = 'discount/static/shop_instructions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #instructions = []
        #instructions.append(('Начало работы', '/discount/Tatamo - начало работы.pdf'))
        #context['instructions'] = instructions
        return context


class ExportProductsToCsvView(generic.View):
    def get(self, request, *args, **kwargs):
        user = request.user

        if user.is_tatamo_manager:
            products = models.Product.objects.all().order_by('created')
        elif user.is_shop_manager:
            shop = user.get_shop
            products = shop.products.all().order_by('created')
        else:
            return HttpResponseRedirect(reverse('discount:login'))



        response = HttpResponse(content_type='text/csv', charset='cp1251')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        #response['charset'] = 'cp1251'

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Ссылка', 'Обычная цена', 'Цена по акции', 'Код категории', 'Название категории', 'Дата начала', 'Дата завершения', 'Бренд', 'Название товара', 'Артикул', 'Состав', 'Ссылка на страницу товара на сайте магазина', 'Цвета', 'Размеры', 'Изображения', 'Название магазина', 'Статус акции', 'Промокод', 'Создана'])

        for product in products:
            row = []
            row.append(settings.SITE_URL + product.get_absolute_url())
            row.append(product.normal_price)
            row.append(product.stock_price)
            row.append(product.product_type.pk)
            row.append(product.product_type.create_title)
            row.append(product.start_date.strftime("%d.%m.%Y"))
            row.append(product.end_date.strftime("%d.%m.%Y"))
            row.append(product.brand)
            row.append(product.title)
            row.append(product.product_shop_code)
            row.append(product.compound)
            row.append(product.link)

            colors = []
            for color in product.filter_values.filter(Q(filter_type=models.FILTER_TYPE_COLOR)):
                colors.append(color.title)
            colors = ', '.join(colors)
            row.append(colors)

            sizes = []
            for size in product.filter_values.filter(~Q(filter_type=models.FILTER_TYPE_COLOR)):
                sizes.append(size.title)
            sizes = ', '.join(sizes)
            row.append(sizes)

            images = []
            for image in product.images.all():
                thumb = settings.SITE_URL + image.image.thumb1080
                images.append(thumb)
            images = ', '.join(images)
            row.append(images)

            row.append(product.shop)
            row.append(product.status_text)
            row.append(product.code)
            row.append(product.created)

            #row = [str(elem).encode('cp1251') for elem in row]

            writer.writerow(row)

        return response

class TatamoManagerPageView(generic.TemplateView):
    template_name = 'discount/adm/tatamo_manager_page.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        links = (   
            ('Просмотр магазинов', reverse('discount:shops-monitor')),
            ('Просмотр акций', reverse('discount:product-list-tatamo')),
            ('Информация о пользователях', reverse('discount:users-monitor')),
            ('Выгрузить все акции', reverse('discount:product-export-all')),
            ('Монитор событий', reverse('discount:monitor')),
            ('Загрузка акций по шаблону', reverse('discount:load-products')),
            ('Акции-дубликаты', reverse('discount:product-doubles-monitor')),
            ('Статистика посещаемости акций(beta) NEW!', reverse('discount:products-stat')),
            ('Проверка ссылок в акциях(beta) NEW!', reverse('discount:check-products-links')),
        )

        context['links'] = links
        return context


class AdmUsersMonitorView(generic.TemplateView):
    template_name = 'discount/adm/adm_users_monitor.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = models.User.objects.order_by('date_joined')
        context['users'] = users
        return context


from PIL import Image as PILImage
from django.contrib.auth import update_session_auth_hash
class ChangePasswordView(PasswordChangeView):
    success_url = reverse_lazy("discount:user-detail")

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        update_session_auth_hash(request, request.user)
        return response


class AdmProductDoublesMonitorView(generic.TemplateView):
    template_name = 'discount/adm/product_doubles_monitor.html'

    def get_context_data(self, **kwargs):
        import filecmp

        context = super().get_context_data(**kwargs)
        statuses = [models.STATUS_APPROVED, models.STATUS_PUBLISHED, models.STATUS_READY, models.STATUS_TO_APPROVE, models.STATUS_SUSPENDED]

        doubles_list = []

        ps = list(models.Product.objects.filter(status__in=statuses, shop__status=models.SHOP_STATUS_PUBLISHED))

        for p in ps:
            doubles = models.Product.objects.filter(
                stock_price=p.stock_price,
                normal_price=p.normal_price,
                title=p.title,
                brand=p.brand,
                status__in=statuses,
                body=p.body,
                #compound=p.compound,
                #link=p.link,
                #product_type=p.product_type,
                shop=p.shop,
            ).exclude(pk=p.pk)


            real_doubles = []
            for d in doubles:
                if d in ps:
                    ps.remove(d)
                #d_images = sorted(list(d.images.all().values_list('image', flat=True)))
                #images = sorted(list(p.images.all().values_list('image', flat=True)))

                #d_values = sorted(list(d.filter_values.all().values_list('title', flat=True)))
                #values = sorted(list(p.filter_values.all().values_list('title', flat=True)))

                eq = True
                #if not d_values == values:
                #    eq = False

                image = p.get_main_image
                d_image = d.get_main_image
                path1 = os.path.join(settings.MEDIA_ROOT, str(image))
                path2 = os.path.join(settings.MEDIA_ROOT, str(d_image))
                if not filecmp.cmp(path1, path2):
                    eq = False

                #im1 = PILImage.open(path1)
                #im2 = PILImage.open(path2)
                #if not im1.size == im2.size or not im1.info == im2.info:
                #    eq = False

                #if eq and len(d_images) == len(images):
                #    for k in range(len(images)):
                #        path1 = os.path.join(settings.MEDIA_ROOT, images[k])
                #        path2 = os.path.join(settings.MEDIA_ROOT, d_images[k])
                #        try:
                #            #im1 = open(path1, 'rb').read()
                #            #im2 = open(path1, 'rb').read()
                #            #if not im1 == im2:
                #            #    eq = False
                #            #try:
                #            im1 = PILImage.open(path1)
                #            im2 = PILImage.open(path2)
                #            #if math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, im1, im2))/len(im1)):
                #                eq = False
                #        except:
                #            eq = True
                if eq == True:
                    real_doubles.append(d)

            if real_doubles:
                real_doubles.append(p)
                doubles_list.append(real_doubles)

        context['doubles_list'] = doubles_list
        return context


class ProductStatSaveView(generic.View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if settings.DISCOUNT_SAVE_PRODUCT_STAT:
            pk = kwargs['pk']
            product = models.Product.objects.get(pk=pk)
            try:
                session_key=request.session.session_key
            except:
                session_key=''
            stat = models.ProductStat(product=product, session_key=session_key, ip=get_client_ip(request))
            user = request.user
            if user.is_authenticated():
                stat.user = user

            stat.save()
        return HttpResponse()


#PRODUCT_STAT_FORM_ORDER_BY_TOTAL_VISITS_INC = 1
#PRODUCT_STAT_FORM_ORDER_BY_TOTAL_VISITS_DEC = 2
#PRODUCT_STAT_FORM_ORDER_BY_UNREG_VISITS_INC = 3
#PRODUCT_STAT_FORM_ORDER_BY_UNREG_VISITS_DEC = 4
#PRODUCT_STAT_FORM_ORDER_BY_REG_VISITS_INC = 5
#PRODUCT_STAT_FORM_ORDER_BY_REG_VISITS_DEC = 6
#PRODUCT_STAT_FORM_ORDER_BY_TOTAL_VISITORS_INC = 7
#PRODUCT_STAT_FORM_ORDER_BY_TOTAL_VISITORS_DEC = 8
#PRODUCT_STAT_FORM_ORDER_BY_TOTAL_GUESTS_INC = 9
#PRODUCT_STAT_FORM_ORDER_BY_TOTAL_GUESTS_DEC = 10
#PRODUCT_STAT_FORM_ORDER_BY_USERS_INC = 11
#PRODUCT_STAT_FORM_ORDER_BY_USERS_DEC = 12
#PRODUCT_STAT_FORM_ORDER_BY_CARTS_INC = 13
#PRODUCT_STAT_FORM_ORDER_BY_CARTS_DEC = 14
#PRODUCT_STAT_FORM_ORDER_BY_INSTANT_CARTS_INC = 15
#PRODUCT_STAT_FORM_ORDER_BY_INSTANC_CARTS_DEC = 16
#PRODUCT_STAT_FORM_ORDER_BY_SUBSCRIPTIONS_INC = 17
#PRODUCT_STAT_FORM_ORDER_BY_SUBSCRIPTIONS_DEC = 18

class ProductsStatView(generic.ListView):
    template_name = 'discount/product/products_stat.html'
    context_object_name = 'products'
    paginate_by = 50

    def get_queryset(self, order_by=None, start_date=None, end_date=None):
        if not hasattr(self, '_queryset'):
            user = self.request.user
            if user.is_tatamo_manager:
                queryset = models.Product.objects.all()
            elif user.is_shop_manager:
                queryset = models.Product.objects.filter(shop=user.get_shop)
            else:
                queryset = None
            if queryset and order_by:
                order_by = int(order_by)
                if order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_TOTAL_VISITS_INC:
                    queryset = list(sorted(queryset, key=lambda q: q.stat_all_in_period(start_date, end_date).count()))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_TOTAL_VISITS_DEC:
                    queryset = list(reversed(sorted(queryset, key=lambda q: q.stat_all_in_period(start_date, end_date).count())))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_UNREG_VISITS_INC:
                    queryset = list(sorted(queryset, key=lambda q: q.stat_guests_in_period(start_date, end_date).count()))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_UNREG_VISITS_DEC:
                    queryset = list(reversed(sorted(queryset, key=lambda q: q.stat_guests_in_period(start_date, end_date).count())))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_REG_VISITS_INC:
                    queryset = list(sorted(queryset, key=lambda q: q.stat_users_in_period(start_date, end_date).count()))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_REG_VISITS_DEC:
                    queryset = list(reversed(sorted(queryset, key=lambda q: q.stat_users_in_period(start_date, end_date).count())))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_REG_VISITS_INC:
                    queryset = list(sorted(queryset, key=lambda q: q.stat_unique_all_in_period(start_date, end_date).count()))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_REG_VISITS_DEC:
                    queryset = list(reversed(sorted(queryset, key=lambda q: q.stat_unique_all_in_period(start_date, end_date).count())))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_TOTAL_GUESTS_INC:
                    queryset = list(sorted(queryset, key=lambda q: q.stat_unique_guests_in_period(start_date, end_date).count()))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_TOTAL_GUESTS_DEC:
                    queryset = list(reversed(sorted(queryset, key=lambda q: q.stat_unique_guests_in_period(start_date, end_date).count())))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_USERS_INC:
                    queryset = list(sorted(queryset, key=lambda q: q.stat_unique_users_in_period(start_date, end_date).count()))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_USERS_DEC:
                    queryset = list(reversed(sorted(queryset, key=lambda q: q.stat_unique_users_in_period(start_date, end_date).count())))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_CARTS_INC:
                    queryset = list(sorted(queryset, key=lambda q: q.get_normal_carts_in_period(start_date, end_date).count()))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_CARTS_DEC:
                    queryset = list(reversed(sorted(queryset, key=lambda q: q.get_normal_carts_in_period(start_date, end_date).count())))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_INSTANT_CARTS_INC:
                    queryset = list(sorted(queryset, key=lambda q: q.get_instant_carts_in_period(start_date, end_date).count()))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_INSTANC_CARTS_DEC:
                    queryset = list(reversed(sorted(queryset, key=lambda q: q.get_instant_carts_in_period(start_date, end_date).count())))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_SUBSCRIPTIONS_INC:
                    queryset = list(sorted(queryset, key=lambda q: q.get_subscriptions_in_period(start_date, end_date).count()))
                elif order_by == forms.PRODUCT_STAT_FORM_ORDER_BY_SUBSCRIPTIONS_DEC:
                    queryset = list(reversed(sorted(queryset, key=lambda q: q.get_subscriptions_in_period(start_date, end_date).count())))


            self._queryset = queryset
        return self._queryset

    #@property
    #def initials(self):
    #    return {'start_date': get_today() - timezone.timedelta(days=7), 'end_date': get_today()}

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date', None)
            end_date = form.cleaned_data.get('end_date', None)
            context['start_date'] = start_date
            context['end_date'] = end_date
            #self._queryset = self._queryset.filter(start_date__gte=start_date, end_date__gte=end_date)
        context['form'] = form
        return context

    def get(self, request, *args, **kwargs):
        start_date = None
        end_date = None
        order_by = None
        if 'submit' in request.GET:
            form = forms.ProductsStatForm(request.GET)
            if form.is_valid():
                start_date = form.cleaned_data.get('start_date', None)
                end_date = form.cleaned_data.get('end_date', None)
                order_by = form.cleaned_data.get('order_by', None)
        else:
            form = forms.ProductsStatForm()

        self.object_list = self.get_queryset(order_by, start_date, end_date)

        return self.render_to_response(self.get_context_data(form=form, **kwargs))


class AdmCheckProductsLinks(generic.TemplateView):
    template_name = 'discount/adm/check_products_links.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from urllib.request import urlretrieve

        products = []
        for p in models.Product.objects.filter(status__in=[models.STATUS_PUBLISHED, models.STATUS_READY]).exclude(link=''):
            try:
                res = urlretrieve(p.link)
                f = open(res[0])
                html = f.read()
                p.url_ok = True
                p.contains_normal_price = str(p.normal_price) in html
                p.contains_stock_price = str(p.stock_price) in html
            except:
                p.url_ok = False
                p.contains_normal_price = None
                p.contains_stock_price = None

            if not all([p.contains_normal_price, p.url_ok, not p.contains_stock_price]):
                products.append(p)


        context['products'] = products



    def get(self, request, *args, **kwargs):
        if not request.user.is_tatamo_manager:
            return HttpResponseRedirect(reverse('discount:login'))
        return super().get(request, *args, **kwargs)






