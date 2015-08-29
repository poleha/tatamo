from django import forms
from discount.models import ProductType, Shop,  Brand, Comment, Product, ProductImage, PRODUCT_STATUSES
from django.forms.widgets import CheckboxSelectMultiple, DateInput
from django.forms.models import ModelForm, inlineformset_factory
from django.forms.models import BaseInlineFormSet
from allauth.account.forms import LoginForm, SignupForm
from discount.models import STATUS_PROJECT, STATUS_PUBLISHED, STATUS_APPROVED, STATUS_READY, STATUS_NEED_REWORK, STATUS_SUSPENDED, STATUS_TO_APPROVE
from discount import models
#from itertools import chain
from django.forms.widgets import CheckboxSelectMultiple, CheckboxInput, mark_safe, RadioSelect, RadioChoiceInput
import re
from django.conf import settings
from discount.helper import get_today
from django.forms import ValidationError
import datetime
#from django.forms import ModelChoiceField

#from django.utils.encoding import force_str
#from django.utils.html import conditional_escape
#from django.forms.models import ModelChoiceIterator
from django.db.models import QuerySet, Model, Q
from collections import namedtuple

def model_choice_field_with_custom_label_from_instance(form_class, label_from_instance):
    class Field(form_class):
        def label_from_instance(self, obj):
            label_method = getattr(obj, label_from_instance)
            if callable(label_method):
                return label_method()
            else:
                return label_method
    return Field


class HashedFormMixin:
    hashed = forms.CharField(max_length=40, widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hashed'].widget = forms.HiddenInput()

    def clean(self):
        super().clean()

        saved_version = self.instance.saved_version
        if saved_version:
            saved_hashed = saved_version.hashed
            now_hashed = self.cleaned_data.get('hashed', None)
            if not saved_hashed == now_hashed:
                self.add_error(None, 'Извините, данные были изменены кем-то другим. Сохранение невозможно.')


class SaveUserMixin:
    #Форма не должна иметь поля user, а модель - должна
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        #user_field = forms.ModelChoiceField(queryset=models.User.objects.filter(pk=user.pk), widget=forms.HiddenInput, required=False)
        if self.is_bound:
            instance_user = self.instance.user
            if instance_user:
                self.instance.user = instance_user
            else:
                self.instance.user = user





#class TatamoFormMixin:



from django.forms import widgets


class CheckboxChoiceInputLabelFirst(widgets.CheckboxChoiceInput):
    def render(self, name=None, value=None, attrs=None, choices=()):
        if self.id_for_label:
            label_for = format_html(' for="{0}"', self.id_for_label)
        else:
            label_for = ''
        return format_html('{1}<label{0}>{2}</label>', label_for, self.tag(), self.choice_label)


class CheckboxFieldRendererLabelFirst(widgets.CheckboxFieldRenderer):
    choice_input_class = CheckboxChoiceInputLabelFirst



class CheckboxSelectMultipleLabelFirst(CheckboxSelectMultiple):
    renderer = CheckboxFieldRendererLabelFirst

class ModelMultipleChoiceFieldLabelFirst(forms.ModelMultipleChoiceField):
    widget = CheckboxSelectMultipleLabelFirst

class ModelMultipleChoiceFieldWithCheckbox(forms.ModelMultipleChoiceField):
    widget = CheckboxSelectMultiple


ORDER_BY_NONE = 0
ORDER_TYPE_BY_PRICE_INC = 1
ORDER_TYPE_BY_PRICE_DEC = 2
ORDER_TYPE_BY_DISCOUNT_INC = 3
ORDER_TYPE_BY_DISCOUNT_DEC = 4
ORDER_TYPE_BY_POPULARITY_INC = 5
ORDER_TYPE_BY_POPULARITY_DEC = 6
ORDER_TYPE_BY_NEW_INC = 7
ORDER_TYPE_BY_NEW_DEC = 8

ORDER_TYPES = (
    (ORDER_BY_NONE, 'Упорядочить по:'),
    (ORDER_TYPE_BY_PRICE_INC, 'По цене по возрастанию'),
    (ORDER_TYPE_BY_PRICE_DEC, 'По цене по убыванию'),
    (ORDER_TYPE_BY_DISCOUNT_INC, 'По скидке по возрастанию'),
    (ORDER_TYPE_BY_DISCOUNT_DEC, 'По скидке по убыванию'),
    (ORDER_TYPE_BY_POPULARITY_INC, 'По популярности по возрастанию', ),
    (ORDER_TYPE_BY_POPULARITY_DEC, 'По популярности по убыванию'),
    (ORDER_TYPE_BY_NEW_INC, 'По новизне по возрастанию'),
    (ORDER_TYPE_BY_NEW_DEC, 'По новизне по убыванию'),
)


#ORDER_TYPES_SELECT = ((0, 'Нет'),) + ORDER_TYPES
ORDER_TYPES_SELECT = ORDER_TYPES


SHOW_TYPE_LIST = 0
SHOW_TYPE_GRID = 1
SHOW_TYPES = (
    (SHOW_TYPE_LIST, 'Список'),
    (SHOW_TYPE_GRID, 'Сетка'),


)
#HAS_CODE_NO = (0, 'Акции, код по которым не получен')
#HAS_CODE_YES = (1, 'Акции, код по которым получен')
#HAS_CODE_CHOICES = (HAS_CODE_NO, HAS_CODE_YES)

class ProductListFilterFormOrderBy(forms.Form):
    order_sep = forms.ChoiceField(choices=ORDER_TYPES_SELECT, required=False, label='Упорядочить по')


class ProductListFilterForm(forms.Form):
    #start_date = forms.DateField(required=False, widget=DateInput())
    #end_date = forms.DateField(required=False, widget=DateInput())
    title = forms.CharField(max_length=200, required=False, label='Название')
    shop = ModelMultipleChoiceFieldWithCheckbox(queryset=Shop.objects.all(), required=False,
                                                label='Магазин')
    brand = ModelMultipleChoiceFieldWithCheckbox(queryset=Brand.objects.all(), required=False,
                                                 label='Бренд')
    product_type = model_choice_field_with_custom_label_from_instance(ModelMultipleChoiceFieldWithCheckbox, 'create_title')(queryset=ProductType.objects.filter(has_childs=False),
                                                        required=False, label='Тип товара')




    #sizes = forms.ModelMultipleChoiceField(queryset=Size.objects.all(), required=False,
    #                                             label='Размеры', widget=CheckboxSelectMultipleLabelFirst())
    #min_price = forms.IntegerField(required=False, initial=1, label='Цена от')
    #max_price = forms.IntegerField(required=False, label='Цена до')
    status = forms.MultipleChoiceField(choices=PRODUCT_STATUSES, required=False, widget=CheckboxSelectMultiple(),
                                       label='Статус')
    #has_code = forms.BooleanField(required=False, label='Код получен')

    #amount = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    price_category = forms.MultipleChoiceField(choices=models.PRICE_CATEGORIES, required=False, widget=CheckboxSelectMultiple(),
                                       label='Ценовая категория')

    discount_category = forms.MultipleChoiceField(choices=models.DISCOUNT_CATEGORIES, required=False, widget=CheckboxSelectMultiple(),
                                       label='Скидка')

    order_by = forms.ChoiceField(choices=ORDER_TYPES, required=False, widget=RadioSelect())

    order_by_select = forms.ChoiceField(choices=ORDER_TYPES_SELECT, required=False, label='Упорядочить по')

    show_type = forms.ChoiceField(choices=SHOW_TYPES, required=False, widget=RadioSelect(), label='Вид показа')

    sender = forms.CharField(max_length=50, required=False)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for param_key, field_names in models.FILTER_PARAMS_FIELD_NAMES.items():
            field_name, field_label = field_names
            if param_key == models.FILTER_TYPE_COLOR:
                self.fields[field_name] =  ModelMultipleChoiceFieldWithCheckbox(queryset=models.FilterValue.objects.filter(filter_type=param_key), required=False,
                                                  label=field_label)
            else:
                self.fields[field_name] =  ModelMultipleChoiceFieldWithCheckbox(queryset=models.FilterValue.objects.filter(filter_type=param_key), required=False,
                                                  label=field_label, widget=CheckboxSelectMultipleLabelFirst())
            #TODO сделать как на продакт криейт
            #self.filter_fields.append(field_name)



class CommentForm(ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None and user.is_authenticated():
            self.fields['name'].initial = "{0} {1}".format(user.first_name, user.last_name)
            self.fields['name'].widget = forms.HiddenInput()
            self.fields['email'].initial = user.email
            self.fields['email'].widget = forms.HiddenInput()


    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']

from django.utils.html import conditional_escape, format_html
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy


#class DisabledField:



class StatusScheme(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prepare_form_instance(*args, **kwargs)


    def initial_value(self, field_name):
        try:
            value = self.initial.get(field_name, None)
            if not value:
                field = self.fields[field_name]
                value = getattr(field, 'initial', None)
        except:
            value = None
        if value is None and self.instance:
            value = getattr(self.instance, field_name, None)

        return value

    def get_value(self, field_name, default=None):
        if self.is_bound and hasattr(self, 'cleaned_data'):
            value = self.cleaned_data.get(field_name, None)
        else:
            value = self.initial_value(field_name)
            if value is None and default:
                value = default
        return value



    def prepare_form_instance(self, *args, **kwargs):
        #status = self.get_instance_status()
        disabled = self.get_disabled_fields(*args, **kwargs)
        for field in self.fields:
            if field in disabled:
                self.fields[field]._disabled = True
                if 'disabled' not in self.fields[field].widget.attrs:
                    self.fields[field].widget.attrs['disabled'] = 'disabled'
                    self.fields[field].required = False
                    self.fields[field].bound_data = lambda data, initial: initial

                if not self.get_value(field) and not field in self.exclude_from_deleting(): #Если для запрещенного поля нет значения, скроем его
                    pass
                    self.fields[field].widget = forms.HiddenInput()
                    self.fields[field].label = ''

    def exclude_from_deleting(self):
        return []


    def clean(self):
        super().clean()

        for field in self.base_fields:
            if field in self.fields and getattr(self.fields[field], '_disabled', False) is True:
                if field in self._errors:
                    del self._errors[field]
                if field in self.cleaned_data:
                    if not self.instance.pk:
                        del self.cleaned_data[field]
                        continue
                    instance_value = getattr(self.instance, field, None)
                    if instance_value is not None:
                        if isinstance(instance_value, (str, int, datetime.date, Model)):
                            self.cleaned_data[field] = instance_value
                            self.initial[field] = instance_value
                            if isinstance(instance_value, Model):
                                self.initial[field] = instance_value.pk
                        elif hasattr(type(instance_value), 'file'):
                            continue #Если это файл, то он взялся в cleaned_data из инстанс. Ничего не надо делать.
                        else:
                            try:
                                queryset = instance_value
                                self.initial[field] = queryset.values_list('pk', flat=True)
                                self.cleaned_data[field] = queryset
                            except:
                                del self.cleaned_data[field]

        efs = self.get_essential_fields()
        if efs:
            delete = True
            for field in efs:
                val = self.cleaned_data.get(field, None)
                from_instance = getattr(self.instance, field, None)
                if from_instance:
                    is_file = hasattr(from_instance, '_file')
                    if is_file:
                        val = True
                if isinstance(val, str):
                    val = re.sub("^\s+|\n|\r|\s+$", '', val) #Пустые пробелы #TODO разобрать
                if val:
                    delete = False
            if delete:
                self.cleaned_data['DELETE'] = True
                self._errors = {}
                for field in self.fields.values():
                    field.required = False




        return self.cleaned_data

    def get_essential_fields(self):
        return []

    def get_disabled_fields(self, *args, **kwargs):
        return []




class ProductInlineBaseFormset(BaseInlineFormSet): #Общий для телефона и юзера
    def __init__(self, *args, **kwargs):
        product = kwargs.get('instance', None)
        if product is not None:
            status = product.status
        else:
            status = models.STATUS_NEW
        if status in [STATUS_PUBLISHED, STATUS_TO_APPROVE, models.STATUS_SUSPENDED, models.STATUS_READY, models.STATUS_APPROVED]:
            self.extra = 0
        super().__init__(*args, **kwargs)
        #if status in [models.STATUS_TO_APPROVE, models.STATUS_PUBLISHED, models.STATUS_READY]:
        #    self.remove_disabled()

    #def remove_disabled(self):
    #    for form in self.forms:
    #        for bound_field in form:
    #            field = bound_field.field
    #            if 'disabled' not in field.widget.attrs:
    #                    field.widget.attrs['disabled'] = 'disabled'
    #                    field.required = False


class ProductInlineBaseForm(StatusScheme):
    #def get_instance_status(self):
    #    instance = self.instance
    #    if instance is not None and instance.pk:
    #        status = instance.product.status
    #    else:
    #        status = models.STATUS_PROJECT
    #    return status

    def get_disabled_fields(self, *args, instance=None,  **kwargs):
        if instance:
            status = instance.product.status
        else:
            status = models.STATUS_NEW
        if status in [STATUS_PROJECT, STATUS_NEED_REWORK, models.STATUS_NEW]:
            disabled = []
        else:
            disabled = list(self.base_fields.keys())
        return disabled




class TatamoImageClearableFileInput(forms.FileInput):
    initial_text = ''
    input_text = ugettext_lazy('Change')
    clear_checkbox_label = ugettext_lazy('Clear')

    template_with_initial = '<div class="image-initial-block">%(initial)s </div> <div class="image-input-block">%(clear_template)s<label class="image-input-label">%(input_text)s:</label> %(input)s</div>'

    #template_with_clear = '%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'

    url_markup_template = '<img src="{0}" id="{1}">' #1191

    def __init__(self, thumb_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thumb_name = thumb_name

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': '', #self.clear_checkbox_label,
        }
        template = '%(input)s'
        substitutions['input'] = super().render(name, value, attrs)

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = format_html(self.url_markup_template, getattr(value, self._thumb_name), name + '-image') #1191
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)

    """
    def render(self, name, *args, **kwargs):
        result = super().render(name, *args, **kwargs)
        if '<a' in result:
            a_index = result.index('<a')
            result = result[0:a_index+2] + ' id="' + name + '-link" ' + result[a_index+3:]
        return result
    """



class ProductImageForm(ProductInlineBaseForm):
    required_css_class = 'required'
    image = forms.ImageField(label='Изображение', widget=TatamoImageClearableFileInput(thumb_name='thumb66', attrs={'class': 'image-input'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False #Не при объявлении поля потому, что тогда не будет флажка удалить

    #def get_instance_status(self):
    #    instance = self.instance
    #    if instance is not None and instance.pk:
    #        status = instance.product.status
    #    else:
    #        status = models.STATUS_PROJECT
    #    return status

    def get_disabled_fields(self, *args, instance=None,  **kwargs):
        if instance:
            status = instance.product.status
        else:
            status = models.STATUS_NEW
        if status in [STATUS_PROJECT, STATUS_NEED_REWORK, models.STATUS_NEW]:
            disabled = []
        else:
            disabled = list(self.base_fields.keys())
            disabled.remove('weight')
        return disabled

    def get_essential_fields(self):
        return ['image']




#For admin
class ProductImageBaseFormset(ProductInlineBaseFormset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)





class ProductImageBaseFormsetWithDisabled(ProductImageBaseFormset):

    def clean(self):
        super().clean()
        form_count = 0
        if hasattr(self, 'cleaned_data'):
            for form in self.forms:
                image = form.get_value('image', None)
                delete = form.get_value('DELETE', False)
                if not delete and image:
                    form_count += 1
        if form_count < 1:
            self._non_form_errors.append('Необходимо присоединить хотя бы одно изображение')


ProductImageFormset = inlineformset_factory(Product, ProductImage, form=ProductImageForm, min_num=1, validate_min=True, extra=3, exclude=[], formset=ProductImageBaseFormsetWithDisabled)



class RelatedProductFormBaseFormset(ProductInlineBaseFormset):

    def __init__(self, *args, **kwargs):
        shop = kwargs.pop('shop')
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.fields['related_product'].queryset = shop.products.filter(status__in=models.AVAILABLE_FOR_RELATED_PRODUCTS_STATUSES).order_by('id')



class RelatedProductForm(StatusScheme):
    related_product = model_choice_field_with_custom_label_from_instance(forms.ModelChoiceField, 'title_with_pk')(queryset=models.Product.objects.none(), label='Связанная акция')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



    def get_essential_fields(self):
        return ['related_product']



RelatedProductFormset = inlineformset_factory(Product, models.RelatedProduct, max_num=3, min_num=3, exclude=['product'], fk_name='product', form=RelatedProductForm, formset=RelatedProductFormBaseFormset)







class ProductBannerBaseFormset(BaseInlineFormSet):
    pass


class ProductBannerForm(StatusScheme):
    class Meta:
        model = models.ProductBanner
        exclude = []
    banner = forms.ImageField(label='Изображение', widget=TatamoImageClearableFileInput(thumb_name='thumb180', attrs={'class': 'banner-input'}))

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, instance=instance, **kwargs)
        #self.fields['banner'].widget = TatamoImageClearableFileInput(thumb_name='thumb90')
        if not instance or instance.status in [models.BANNER_STATUS_APPROVED, models.BANNER_STATUS_ON_APPROVE] or not self.initial.get('tatamo_comment', None):
            if 'tatamo_comment' in self.fields:
                del self.fields['tatamo_comment']
        if instance and instance.status == models.BANNER_STATUS_APPROVED:
            if 'shop_comment' in self.fields:
                del self.fields['shop_comment']



    def get_essential_fields(self):
        return ['banner', 'shop_comment']


    def get_disabled_fields(self, *args, instance=None, **kwargs):
        disabled = list(self.base_fields.keys())
        disabled.remove('status')
        disabled.remove('product')
        if instance and instance.status in [models.BANNER_STATUS_APPROVED, models.BANNER_STATUS_ON_APPROVE]:
            pass
        else:
            if 'shop_comment' in disabled:
                disabled.remove('shop_comment')
            if 'banner' in disabled:
                disabled.remove('banner')
        return disabled

    #def clean(self):
    #    super().clean()
    #    status = self.get_value('status')
    #    if not status or status == models.BANNER_STATUS_PROJECT:
    #        self.cleaned_data['status'] = models.BANNER_STATUS_ON_APPROVE






ProductBannerFormset = inlineformset_factory(Product, models.ProductBanner, form=ProductBannerForm, extra=3, exclude=[], formset=ProductBannerBaseFormset)



class ProductInlineActionBaseFormset(BaseInlineFormSet):
    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, instance=instance, **kwargs)
        for form in self.forms:
            queryset = models.ProductBanner.objects.filter(product=instance, status=models.BANNER_STATUS_APPROVED)
            form.fields['banner'].queryset = queryset
            #if queryset.count() == 1:
            #    form.fields['banner'].initial = queryset.latest('created')

    def clean(self):
        super().clean()




class ProductActionForm(StatusScheme):
    class Meta:
        model = models.ProductAction
        fields = ['action_type', 'start_date', 'end_date', 'banner', 'start']
    #start = forms.BooleanField(required=False)

    def get_essential_fields(self):
        return ['start_date', 'end_date']

    #banner = forms.ModelChoiceField(queryset=models.ProductBanner.objects.none())
    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, instance=instance, **kwargs)
        #if instance and instance.pk and instance.status in [models.ACTION_STATUS_ACTIVE, models.ACTION_STATUS_PLANNED]:
        #    self.fields['start'].initial = True


    def disable_delete(self):
        if hasattr(self.fields['action_type'], '_disabled'):
            return self.fields['action_type']._disabled
        else:
            return False

    def get_disabled_fields(self, *args, instance=None, **kwargs):
        #today = get_today()
        status = self.get_value('status')
        disabled = list(self.base_fields.keys())
        if not status == models.ACTION_STATUS_FINISHED:
            disabled.remove('banner')
        if status not in [models.ACTION_STATUS_ACTIVE, models.ACTION_STATUS_FINISHED, models.ACTION_STATUS_PAUSED]:
            disabled = []

        if instance and instance.pk and instance.status in [models.ACTION_STATUS_ACTIVE, models.ACTION_STATUS_PAUSED]:
            disabled.remove('end_date')

        if instance and instance.pk and instance.status == models.ACTION_STATUS_FINISHED and self.points_spent > 0:
            pass

        return disabled


ProductActionFormset = inlineformset_factory(Product, models.ProductAction, form=ProductActionForm,
                                         extra=3, exclude=[], formset=ProductInlineActionBaseFormset)


#class ProductTypeItemMiniForm(forms.Form):
#    product_type = forms.ModelChoiceField(queryset=ProductType.objects.filter(has_childs=False))






class ProductFormProductType(forms.Form):
    product_type = model_choice_field_with_custom_label_from_instance(forms.ModelChoiceField, 'create_title')(queryset=ProductType.objects.none(),
                                                        required=True, label='Тип товара')

    def __init__(self, queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_type'].queryset = queryset

#from markitup.widgets import MarkItUpWidget
from django.utils import timezone
from discount import models
class ProductForm(HashedFormMixin, SaveUserMixin, StatusScheme):
    required_css_class = 'required'
    product_type = model_choice_field_with_custom_label_from_instance(forms.ModelChoiceField, 'create_title')(queryset=ProductType.objects.filter(has_childs=False),
                                                        required=True, label='Тип товара')
    category = forms.ModelChoiceField(queryset=ProductType.objects.filter(level=1),
                                                        required=True, label='Категория')


    #colors =  ModelMultipleChoiceFieldWithCheckbox(queryset=models.FilterValue.objects.filter(filter_type=models.FILTER_TYPE_COLOR), required=False,
    #                                          label='Цвета')
    class Meta:
        model = Product
        exclude = ['alias', 'cart_users', 'discount_category', 'price_category', 'percent', 'status', 'user']


    def exclude_from_deleting(self):
        return ['category', 'code']

    def __init__(self, *args, user=None, new_data=None, **kwargs):
        self._user = user
        self._new_data = new_data

        super().__init__(*args, user=user, **kwargs)
        self.filter_fields = []

        product_type_pk = self.initial_value('product_type')
        if product_type_pk:
            product_type = models.ProductType.objects.get(pk=product_type_pk)
            category = product_type.get_top_parent()
            if category:
                self.initial['category'] = category.pk
        #        self.fields['product_type'].queryset = models.ProductType.objects.filter(Q(parent=category) | Q(parent__parent=category))



        for param_key, field_names in models.FILTER_PARAMS_FIELD_NAMES.items():
            field_name, field_label = field_names
            #self.fields[field_name] =  ModelMultipleChoiceFieldWithCheckbox(queryset=models.FilterValue.objects.filter(filter_type=param_key), required=False,
                 #                                                               label=field_label)

            self.filter_fields.append(field_name)
            if self.instance.pk:
                self.fields[field_name].initial = self.instance.filter_values.filter(filter_type=param_key)



            #if not product_type.sizes_filter_available:
            #    self.fields['sizes'].widget = forms.HiddenInput()
            #    self.fields['sizes'].label = ''

            #if not product_type.colors_filter_available:
            #    self.fields['colors'].widget = forms.HiddenInput()
            #    self.fields['colors'].label = ''

        self.fields['shop'].label = None
        self.fields['shop'].widget = forms.HiddenInput()
        if not self.instance.pk:
            #self.fields['shop'].widget = forms.HiddenInput()
            self.fields['shop'].initial = user.get_shop

            #self.initial['shop'] = user.get_shop().pk

        #else:
        #    self.fields['shop'].initial = self.instance.shop
        self.prepare_form(user)
        if not self.initial.get('tatamo_comment', None):
            del self.fields['tatamo_comment']


    def get_disabled_fields(self, *args, instance=None, **kwargs):
        if instance:
            status = instance.status
        else:
            status = models.STATUS_NEW

        if status in [models.STATUS_NEW, STATUS_PROJECT, STATUS_NEED_REWORK]:
            disabled = ['code', 'tatamo_comment']

        elif status in [models.STATUS_APPROVED, STATUS_PUBLISHED, STATUS_SUSPENDED, STATUS_READY]:
            disabled = list(self.base_fields.keys())
            for param_key, field_names in models.FILTER_PARAMS_FIELD_NAMES.items():
                field_name, field_label = field_names
                if field_name in disabled:
                    disabled.remove(field_name)
            #disabled.remove('sizes')
            #disabled.remove('colors')
            disabled.remove('end_date')
            if status in [STATUS_READY, STATUS_APPROVED]:
                disabled.remove('start_date')
        else: #STATUS_TO_APPROVE, FINISHED, CANCELLED
            disabled = list(self.base_fields.keys())

        #if instance and instance.pk:
        #    if not instance.product_type.sizes_filter_available and not 'sizes' in disabled:
        #        disabled.append('sizes')
        #    if not instance.product_type.colors_filter_available and not 'colors' in disabled:
        #        disabled.append('colors')
        if 'hashed' in disabled:
            disabled.remove('hashed')

        return disabled


    def prepare_form(self, user):
        available_brands = Brand.objects.filter(shops=user.get_shop)
        #available_shops = user.shops.all()


        #status = self.get_instance_status()
        self.fields['brand'] = forms.ModelChoiceField(available_brands, required=True,
                                           label='Бренд')
        if 'brand' in self.get_disabled_fields(instance=self.instance):
            self.fields['brand'].widget.attrs['disabled'] = 'disabled'
            self.fields['brand'].required = False
            self.fields['brand']._disabled = True
        #self.fields['shop'] = forms.ModelChoiceField(available_shops, required=True,
        #                                   cache_choices=False, label='Магазин')
        """
        if 'shop' in self.get_disabled_fields(status):
            self.fields['shop'].widget.attrs['disabled'] = 'disabled'
            self.fields['shop'].required = False
            self.fields['shop']._disabled = True
        """

        """
        if len(available_shops) == 1:
            self.fields['shop'].initial = available_shops[0]
        """
        if len(available_brands) == 1:
            self.fields['brand'].initial = available_brands[0]

        self.fields['start_date'].initial = get_today()
        #self.fields['status'].choices = self.get_available_statuses()

    #def get_instance_status(self):
    #    if self.instance.pk:
    #        status = self.instance.status
    #    else:
    #        status = STATUS_PROJECT
    #    return status

    #def get_available_statuses(self):
    #    if self.instance.id is not None:
    #        statuses = self.instance.get_available_statuses()
    #    else:
    #        statuses = [models.get_choice_by_num(models.PRODUCT_STATUSES, models.STATUS_PROJECT),
    #                    models.get_choice_by_num(models.PRODUCT_STATUSES, models.STATUS_TO_APPROVE)]
    #    return statuses


    #status = forms.ChoiceField(label='Статус', required=False, choices=models.PRODUCT_STATUSES)
    #sizes = forms.ModelMultipleChoiceField(Size.objects.all(), required=False, widget=CheckboxSelectMultiple(),
    #                                        label='Размеры')
    #colors = forms.ModelMultipleChoiceField(models.FilterValue.objects.filter(filter_type=models.FILTER_TYPE_COLOR), required=False, widget=CheckboxSelectMultiple(),
    #                                         label='Цвета')
    start_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'class': 'date-input',}),
                                 label='Дата начала')
    end_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'class': 'date-input',}),
                               label='Дата окончания')
    #brand = forms.ModelMultipleChoiceField(queryset=Brand.objects.all(), required=False)
    #body = forms.CharField(label='Описание акции')



    def clean(self):
        super().clean()
        today = get_today()
        cleaned_data = self.cleaned_data




        #start_date = self.get_value('start_date')
        end_date = self.get_value('end_date')
        status = self.get_value('status')



        if self._new_data is not None:
            if 'status' in self._new_data:
                status = self._new_data['status']
            if 'end_date' in self._new_data:
                end_date = self._new_data['end_date']



        #if start_date == today and status == models.STATUS_READY:
        #    status = models.STATUS_PUBLISHED

        #TODO разобраться
        self.instance.status = status
        self.instance.end_date = end_date
        cleaned_data['status'] = status
        cleaned_data['end_date'] = end_date
        #if not self._changed_data:
        #    self._changed_data = []
        #self._changed_data.append('status')
        #self._changed_data.append('end_date')

        if status in [models.STATUS_PROJECT, models.STATUS_FINISHED, models.STATUS_CANCELLED, STATUS_NEED_REWORK]:
            return



        product_type = self.get_value('product_type')
        if product_type:
            category = product_type.get_top_parent()
            #if category.dress_sizes_filter_available and not self.get_value('sizes'):
            #    self.add_error('sizes', 'Для этой категории обязательно указать хотя бы один размер')

            for param_key, field_names in models.FILTER_PARAMS_FIELD_NAMES.items():
                field_name, field_label = field_names
                if category.filter_available(param_key) and not self.get_value(field_name):
                    self.add_error(field_name, 'Для этой категории обязательно указать хотя бы один {0}'.format(field_label))




for param_key, field_names in models.FILTER_PARAMS_FIELD_NAMES.items():
        field_name, field_label = field_names
        field = ModelMultipleChoiceFieldWithCheckbox(queryset=models.FilterValue.objects.filter(filter_type=param_key),
                                                     required=False, label=field_label)
        #field.widget.attrs['class'] = 'required'
        ProductForm.base_fields[field_name] = field





class AddProductToCartForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput)


class ProductAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for param_key, field_names in models.FILTER_PARAMS_FIELD_NAMES.items():
            field_name, field_label = field_names
            if self.instance.pk:
                self.fields[field_name].initial = self.instance.filter_values.filter(filter_type=param_key)

    def clean(self, *args, **kwargs):
        return super().clean(*args, **kwargs)


for param_key, field_names in models.FILTER_PARAMS_FIELD_NAMES.items():
        field_name, field_label = field_names
        field = ModelMultipleChoiceFieldWithCheckbox(queryset=models.FilterValue.objects.filter(filter_type=param_key),
                                                     required=False, label=field_label)
        #field.widget.attrs['class'] = 'required'
        ProductAdminForm.base_fields[field_name] = field


class ShowCodeForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput)

class DiscountLoginForm(LoginForm):
    required_css_class = 'required'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.fields['remember'].initial = True




class GetCodeForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None and user.is_authenticated():
            #self.fields['email'].widget = forms.HiddenInput()
            self.user = user

    first_name = forms.CharField(max_length=250, label='Имя', required=False)
    #last_name = forms.CharField(max_length=250, label='Фамилия')
    phone = forms.CharField(max_length=100, label='Телефон', required=False)
    #email = forms.EmailField(max_length=250, label='E-mail')

    def clean(self):
        super().clean()

    def save(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated():
            profile = user.profile
            save_user = False
            if self.cleaned_data['first_name'] and not user.first_name == self.cleaned_data['first_name']:
                user.first_name = self.cleaned_data['first_name']
                save_user = True
            if save_user:
                user.save()
            if self.cleaned_data['phone'] and not profile.phone == self.cleaned_data['phone']:
                profile.phone = self.cleaned_data['phone']
                profile.save()
        return user


def validate_first_is_letter(value):
    if re.search('^[a-zA-Z0-9]+', value) is None:
        raise ValidationError('Имя пользователя должно начинаться с английской буквы или цифры')

def validate_contains_russian(value):
    if re.search('[а-яА-Я]+', value) is not None:
        raise ValidationError('Имя пользователя содержит русские буквы. Допустимо использовать только английские')

def validate_username(value):
    if re.fullmatch('^[a-zA-Z0-9-_\.]*$', value) is None:
        raise ValidationError('Ошибка в имени пользователя.'
                              ' Допустимо использовать только английские буквы, цифры и символы -  _  .')


class DiscountSignupForm(SignupForm):
    required_css_class = 'required'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].validators.append(validate_first_is_letter)
        self.fields['username'].validators.append(validate_contains_russian)
        self.fields['username'].validators.append(validate_username)
        self.fields['first_name'] = forms.CharField(max_length=250, label='Имя', required=False)
        #self.fields['last_name'] = forms.CharField(max_length=250, label='Фамилия', required=False)
        self.fields['phone'] = forms.CharField(max_length=100, label='Телефон', required=False)

    def save(self, request, *args, **kwargs):
        user = super().save(request, *args, **kwargs)
        if 'phone' in self.cleaned_data:
            profile = user.profile
            profile.phone = self.cleaned_data['phone']
            profile.save()
        return user







class GetProductByCode(forms.Form):
    product_code = forms.CharField(max_length=250, label='Код акции', widget=forms.TextInput(attrs={'placeholder': 'Код акции'}))



class ProfileForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = models.UserProfile
        fields = ['phone', 'get_product_changed_messages', 'active_shop']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = kwargs.get('instance', None)
        if profile is not None:
            user = profile.user
            shops = user.get_all_shops()
            if not shops:
                if 'active_shop' in self.fields:
                    del self.fields['active_shop']
            elif shops.count() == 1:
                self.fields['active_shop'].queryset = shops
                self.fields['active_shop'].widget = forms.HiddenInput()
                self.fields['active_shop'].initial = shops[0] #Похоже, что не обязательно
                self.initial['active_shop'] = shops[0].pk
            else:
                self.fields['active_shop'].queryset = shops
                self.fields['active_shop'].required = True




class UserForm(forms.ModelForm):
    required_css_class = 'required'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #user = self.instance
        #if user is not None:
        #    profile = models.UserProfile.get_profile(user)
        #    self.fields['phone'].initial = profile.phone
        #    self.fields['get_product_changed_messages'].initial = profile.get_product_changed_messages
        self.fields['first_name'].label = 'Имя'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        #user = self.instance
        #profile = models.UserProfile.get_profile(user)
        #if not profile.phone == self.fields['phone']:
        #    profile.phone = self.cleaned_data.get('phone', '')
        #    profile.save()


    class Meta:
        model = models.User
        fields = ['first_name']

    #phone = forms.CharField(max_length=256)
    #get_product_changed_messages = forms.BooleanField()


UNSUBSCRIBE_REASONS = (
    (1, 'Купил(а)'),
    (2, 'Передумал(а)'),
)

class UnsubscribeForm(forms.Form):
    reason = forms.ChoiceField(choices=UNSUBSCRIBE_REASONS, widget=forms.RadioSelect, required=True, label='Причина')
    comment = forms.CharField(widget=forms.Textarea, required=False, label='Комментарий')
    action = forms.CharField(required=False, widget=forms.HiddenInput, max_length=50, initial='unsubscribe')




class ShopInlineBaseForm(StatusScheme):
    #def get_instance_status(self):
    #    instance = self.instance
    #    if instance is not None and instance.pk:
    #        status = instance.shop.status
    #    else:
    #        status = models.SHOP_STATUS_PROJECT
    #    return status


    def get_disabled_fields(self, *args, instance=None, **kwargs):
        if instance:
            status = instance.shop.status
        else:
            status = models.SHOP_STATUS_PROJECT
        if status == models.SHOP_STATUS_TO_APPROVE:
            disabled = list(self.base_fields.keys())
        else:
            disabled = []
        return disabled


class ShopInlineBaseFormset(BaseInlineFormSet): #Общий для телефона и юзера
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #shop = kwargs.get('instance', None)
        #if shop is not None:
        #    status = shop.status
        #    if status == models.SHOP_STATUS_TO_APPROVE:
        #        self.remove_disabled()

    #def remove_disabled(self):
    #    for form in self.forms:
    #        for bound_field in form:
    #            field = bound_field.field
    #            if 'disabled' not in field.widget.attrs:
    #                    field.widget.attrs['disabled'] = 'disabled'
    #                    field.required = False

class ShopPhoneForm(ShopInlineBaseForm):
    required_css_class = ''
    class Meta:
        model = models.ShopPhone
        fields = ['phone']

    def get_essential_fields(self):
        return ['phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False

    def clean(self):
        super().clean()
        #phone = self.cleaned_data.get('phone', None)
        #if not phone:
        #    self.cleaned_data['DELETE'] = True



ShopPhoneFormset = inlineformset_factory(Shop, models.ShopPhone, form=ShopPhoneForm,
                                         extra=3, exclude=[], formset=ShopInlineBaseFormset)




class ProductConditionForm(ProductInlineBaseForm):
    required_css_class = ''
    class Meta:
        model = models.ProductCondition
        fields = ['condition']

    def get_essential_fields(self):
        return ['condition']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['condition'].required = False

    def clean(self):
        super().clean()
        #phone = self.cleaned_data.get('phone', None)
        #if not phone:
        #    self.cleaned_data['DELETE'] = True



ProductConditionFormset = inlineformset_factory(Product, models.ProductCondition, form=ProductConditionForm,
                                         min_num=5, max_num=5, exclude=[], formset=ProductInlineBaseFormset)




from django.core.exceptions import ValidationError
class UsernameModelChoiceField(forms.ModelChoiceField):
    default_validators = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, value):
        if value is None:
            raise ValidationError('Пользователь не найден')
        return super().validate(value)

    def to_python(self, value):
        if value:
            try:
                value = models.User.objects.get(username=value)
            except:
                value = '__ERROR__'
        else:
            value = '__DELETE__'
        return value

class ShopUserForm(ShopInlineBaseForm):
    required_css_class = 'required'
    class Meta:
        model = models.ShopsToUsers
        fields = ['user', 'confirmed']

    def get_essential_fields(self):
        return ['user']

    def __init__(self, *args, **kwargs):
        #self.base_fields['confirmed'].widget = forms.HiddenInput()
        super().__init__(*args, **kwargs)
        self.fields['confirmed'].widget = forms.HiddenInput()
        self.fields['user'].required = False
        initial_user_value = self.initial_value('user')
        if initial_user_value:
            user = models.User.objects.get(pk=initial_user_value)
            self.initial['user'] = user.username

    user = UsernameModelChoiceField(queryset=models.User.objects.all(), widget=forms.TextInput(), to_field_name='username', label='Имя пользователя')

    #shop = forms.ModelChoiceField(queryset=models.Shop.objects.all(), widget=forms.TextInput(), to_field_name='username')
    def clean(self):
        super().clean()
        user = self.cleaned_data.get('user', None)
        if user == '__DELETE__':
            try:
                old_user = models.User.objects.get(username=self.initial_value('user'))
                self.cleaned_data['DELETE'] = True
                self.cleaned_data['user'] = old_user
            except:
                self.cleaned_data = {}
                self._errors = {}
                self._changed_data = []

        elif user == '__ERROR__':
            self.add_error('user', 'Пользователь не найден')

        """
        shop = self.cleaned_data.get('shop', None)
        delete = self.cleaned_data.get('DELETE', None)
        if user is not None and shop is not None:
            user_shop = user.get_shop()
            if user_shop is not None and not user_shop.pk == shop.pk and not delete:
                self.add_error('user', 'Данный пользователь уже является менеджером другого магазина')

        """



class ShopUserBaseFormset(ShopInlineBaseFormset):
    #Тут будем проверять, что пользователь указан в одной из форм. Если нет - добавляем.
    #@property
    #def current_user_present(self):
    #    user_present = False
    #    if self.forms:
    #        for form in self.forms:
    #            if form.initial_value('user') == self.user.username:
    #                user_present = True
    #                break
    #    return user_present

    #def set_current_user(self):
    #    for form in self.forms:
    #        if not form.initial_value('user'):
    #            form.initial['user'] = self.user.username
    #            form.initial['confirmed'] = True
    #            break

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #if user is not None:
        #    self.user = user
        #    if not self.is_bound and not self.current_user_present:
        #        self.set_current_user()
        #for form in self.forms:
        #    if self.forms.index(form) > 0:
        #        form.fields['user'].required = False


    def clean(self):
        super().clean()

        if hasattr(self, 'cleaned_data'):
            #user_added = False
            #for form_data in self.cleaned_data:
            #    if form_data.get('user', None) == self.user and not form_data.get('DELETE', False):
            #        user_added = True
            #if not user_added:
            #    raise ValidationError('У текущего пользователя нет прав на редактирование магазина')

            users = []
            for form_data in self.cleaned_data:
                user = form_data.get('user', None)
                delete = form_data.get('DELETE', False)
                if user is not None and not delete:
                    if user in users:
                        raise ValidationError('Один пользователь добавлен несколько раз')
                    else:
                        users.append(user)

        if hasattr(self, '_deleted_form_indexes'):
            for ind in self._deleted_form_indexes:
                self._errors[ind] = {}









ShopUserFormset = inlineformset_factory(Shop, models.ShopsToUsers, form=ShopUserForm, min_num=1, validate_min=True,
                                         extra=2, exclude=[], formset=ShopUserBaseFormset)







class ShopForm(HashedFormMixin, SaveUserMixin, StatusScheme):
    required_css_class = 'required'
    image = forms.ImageField(label='Логотип магазина', widget=TatamoImageClearableFileInput(thumb_name='thumb100', attrs={'class': 'image-input'}))


    class Meta:
        model = Shop
        exclude = ('alias', 'brands', 'users', 'region', 'area', 'street', 'house', 'building',
                   'flat', 'index', 'settlement', 'use_custom_adress', 'shop_type', 'status', 'all_products_count', 'available_products_count', 'all_products_pks', 'available_products_pks', 'user')

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        if not self.instance.pk or self.instance.brands.all().count() == 0:
            self.fields['add_brands'].required = True
        self.prepare_form_instance()

        if not self.initial.get('tatamo_comment', None):
            del self.fields['tatamo_comment']

        add_brands_required = not self.instance.pk or not self.instance.brands.exists()
        if add_brands_required:
            self.fields['add_brands'].required = True

    def clean(self):
        super().clean()
        if self.instance.pk:
            saved_version = self.instance.saved_version
            if saved_version.status == models.SHOP_STATUS_TO_APPROVE:
                self.add_error(None, 'Магазин уже на согласовании, повторная отправка невозможна')

        if self.instance.pk is None or not self.instance.brands.all().exists():
            add_brands = self.cleaned_data.get('add_brands', None)
            if not add_brands:
                self.add_error('add_brands', 'Для магазина не указано ни одного бренда. Пожалуйста, добавьте хотя бы один.')

    def get_disabled_fields(self, *args, instance=None, **kwargs):
        if instance:
            status = instance.status
        else:
            status = models.SHOP_STATUS_PROJECT

        if status == models.SHOP_STATUS_TO_APPROVE:
            disabled = list(self.base_fields.keys())
        else:
            disabled = ['tatamo_comment']

        if 'hashed' in disabled:
            disabled.remove('hashed')

        return disabled


    #def get_instance_status(self):
    #    shop = self.instance
    #    if shop is None or not shop.pk:
    #        status = models.SHOP_STATUS_PROJECT
    #    else:
    #        status = shop.status
    #    return status

"""
class ShopsToUsersConfirmForm(forms.ModelForm):
    class Meta:
        model = models.ShopsToUsers
        exclude = ['confirmed']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget = forms.HiddenInput()
"""

class BasePeriodForm(forms.Form):
    start_date = forms.DateField(label="Дата начала", widget=forms.DateInput(attrs={'class': 'date-input'}))
    end_date = forms.DateField(label="Дата окончания", widget=forms.DateInput(attrs={'class': 'date-input'}))


class ActionDaysForm(BasePeriodForm):
    category = forms.ModelChoiceField(queryset=models.ProductType.objects.filter(level=1), label='Категория', required=False)
    action_type = forms.ChoiceField(choices=models.ACTION_TYPES, label='Вид акции')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = get_today()
        if not 'start_date' in self.initial:
            self.initial['start_date'] = today
        if not 'end_date' in self.initial:
            self.initial['end_date'] = self.initial['start_date'] + timezone.timedelta(days=14)

    def clean(self):
        super().clean()

        cleaned_data = self.cleaned_data
        action_type = cleaned_data.get('action_type', None)
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date:
            if (end_date - start_date).days > 100:
                self.add_error('end_date', 'Пожалуйста, установите интервал не более 100 дней')


        category = cleaned_data.get('category', None)
        if int(action_type) == models.ACTION_TYPE_CATEGORY and category is None:
            self.add_error('category', 'Обязательное поле')

"""
class ChangeSubscriptionForm(forms.Form):
    subscription_type = forms.ModelChoiceField(queryset=models.SubscriptionType.objects.filter(available=True),
                                               widget=forms.HiddenInput())
"""


class ProductChangerForm(StatusScheme):
    class Meta:
        model = models.ProductChanger
        exclude = ['product', 'status']

    category = forms.ModelChoiceField(queryset=ProductType.objects.filter(level=1),
                                                        required=True, label='Категория')


    def exclude_from_deleting(self):
        return ['category']

    def __init__(self, *args, user=None, instance=None, **kwargs):
        super().__init__(*args, instance=instance, **kwargs)
        #self.fields['brand'].queryset = Brand.objects.filter(shops=user.get_shop)
        product_type_pk = self.initial_value('product_type')
        if product_type_pk:
            product_type = models.ProductType.objects.get(pk=product_type_pk)
            category = product_type.get_top_parent()
            if category:
                self.initial['category'] = category.pk

    def get_disabled_fields(self, *args, instance=None, **kwargs):
        if instance.status in [models.ACTION_STATUS_PROJECT, models.STATUS_NEED_REWORK]:
            disabled = ['tatamo_comment']
        else:
            disabled = list(self.base_fields.keys())

        return disabled







class ProductChangerImageBaseFormset(BaseInlineFormSet):
    image = forms.ImageField(label='Изображение', widget=TatamoImageClearableFileInput(thumb_name='thumb66', attrs={'class': 'image-input'}))
    def __init__(self, *args, **kwargs):
        changer = kwargs.get('instance', None)
        if changer is not None:
            status = changer.status
        else:
            status = models.STATUS_PROJECT
        if status in [STATUS_TO_APPROVE, STATUS_APPROVED]:
            self.extra = 0
        super().__init__(*args, **kwargs)




class ProductChangerImageForm(StatusScheme):
    required_css_class = 'required'
    image = forms.ImageField(label='Изображение', widget=TatamoImageClearableFileInput(thumb_name='thumb66', attrs={'class': 'image-input'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False #Не при объявлении поля потому, что тогда не будет флажка удалить


    def get_disabled_fields(self, *args, instance=None,  **kwargs):
        if instance:
            status = instance.product_changer.status
        else:
            status= models.STATUS_PROJECT
        if status in [STATUS_PROJECT, STATUS_NEED_REWORK]:
            disabled = []
        else:
            disabled = list(self.base_fields.keys())
        return disabled

    def get_essential_fields(self):
        return ['image']



ProductChangerImageFormset = inlineformset_factory(models.ProductChanger, models.ProductChangerImage, form=ProductChangerImageForm,  exclude=['product'], extra=3, formset=ProductChangerImageBaseFormset)




class ProductChangerConditionBaseFormset(BaseInlineFormSet):
    #image = forms.ImageField(label='Изображение', widget=TatamoImageClearableFileInput(thumb_name='thumb66', attrs={'class': 'image-input'}))
    def __init__(self, *args, **kwargs):
        changer = kwargs.get('instance', None)
        if changer is not None:
            status = changer.status
        else:
            status = models.STATUS_PROJECT
        if status in [STATUS_TO_APPROVE, STATUS_APPROVED]:
            self.extra = 0
        super().__init__(*args, **kwargs)




class ProductChangerConditionForm(StatusScheme):
    required_css_class = ''
    #image = forms.ImageField(label='Изображение', widget=TatamoImageClearableFileInput(thumb_name='thumb66', attrs={'class': 'image-input'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['image'].required = False #Не при объявлении поля потому, что тогда не будет флажка удалить


    def get_disabled_fields(self, *args, instance=None,  **kwargs):
        if instance:
            status = instance.product_changer.status
        else:
            status= models.STATUS_PROJECT
        if status in [STATUS_PROJECT, STATUS_NEED_REWORK]:
            disabled = []
        else:
            disabled = list(self.base_fields.keys())
        return disabled

    def get_essential_fields(self):
        return ['condition']



ProductChangerConditionFormset = inlineformset_factory(models.ProductChanger, models.ProductChangerCondition, form=ProductChangerConditionForm,  exclude=['product'], extra=5, formset=ProductChangerConditionBaseFormset)






class AdmLoadProductsForm(forms.Form):
    file = forms.FileField(label='Файл')
    #user = forms.ModelChoiceField(queryset=models.User.objects.filter(~Q(shops=None)))
    shop = forms.ModelChoiceField(queryset=models.Shop.objects.filter(status=models.SHOP_STATUS_PUBLISHED), required=False)


PRODUCT_ADMIN_FORM_STATUSES = (
    (models.STATUS_APPROVED, 'Согласована'),
    (models.STATUS_NEED_REWORK, 'На доработку'),

)




class ProductTatamoManagerApproveForm(forms.Form):
    tatamo_comment = forms.CharField(widget=forms.Textarea, required=False, label='Комментарий Татамо')
    status = forms.ChoiceField(required=True, label='Статус', choices=PRODUCT_ADMIN_FORM_STATUSES )



PRODUCT_STAT_FORM_ORDER_BY_TOTAL_VISITS_INC = 1
PRODUCT_STAT_FORM_ORDER_BY_TOTAL_VISITS_DEC = 2
PRODUCT_STAT_FORM_ORDER_BY_UNREG_VISITS_INC = 3
PRODUCT_STAT_FORM_ORDER_BY_UNREG_VISITS_DEC = 4
PRODUCT_STAT_FORM_ORDER_BY_REG_VISITS_INC = 5
PRODUCT_STAT_FORM_ORDER_BY_REG_VISITS_DEC = 6
PRODUCT_STAT_FORM_ORDER_BY_TOTAL_VISITORS_INC = 7
PRODUCT_STAT_FORM_ORDER_BY_TOTAL_VISITORS_DEC = 8
PRODUCT_STAT_FORM_ORDER_BY_TOTAL_GUESTS_INC = 9
PRODUCT_STAT_FORM_ORDER_BY_TOTAL_GUESTS_DEC = 10
PRODUCT_STAT_FORM_ORDER_BY_USERS_INC = 11
PRODUCT_STAT_FORM_ORDER_BY_USERS_DEC = 12
PRODUCT_STAT_FORM_ORDER_BY_CARTS_INC = 13
PRODUCT_STAT_FORM_ORDER_BY_CARTS_DEC = 14
PRODUCT_STAT_FORM_ORDER_BY_INSTANT_CARTS_INC = 15
PRODUCT_STAT_FORM_ORDER_BY_INSTANC_CARTS_DEC = 16
PRODUCT_STAT_FORM_ORDER_BY_SUBSCRIPTIONS_INC = 17
PRODUCT_STAT_FORM_ORDER_BY_SUBSCRIPTIONS_DEC = 18


PRODUCT_STAT_FORM_ORDER_BY_CHOICES = (
    (PRODUCT_STAT_FORM_ORDER_BY_TOTAL_VISITS_INC, 'Всего посещений по возрастанию'),
    (PRODUCT_STAT_FORM_ORDER_BY_TOTAL_VISITS_DEC, 'Всего посещений по убыванию'),
    (PRODUCT_STAT_FORM_ORDER_BY_UNREG_VISITS_INC, 'Посещений незарегистрированными пользователями по возрастанию'),
    (PRODUCT_STAT_FORM_ORDER_BY_UNREG_VISITS_DEC, 'Посещений незарегистрированными пользователями по убыванию'),
    (PRODUCT_STAT_FORM_ORDER_BY_REG_VISITS_INC, 'Посещений зарегистрированными пользователями по возрастанию'),
    (PRODUCT_STAT_FORM_ORDER_BY_REG_VISITS_DEC, 'Посещений зарегистрированными пользователями по убыванию'),
    (PRODUCT_STAT_FORM_ORDER_BY_TOTAL_VISITORS_INC, 'Всего посетителей по возрастанию'),
    (PRODUCT_STAT_FORM_ORDER_BY_TOTAL_VISITORS_DEC, 'Всего посетителей по убыванию'),
    (PRODUCT_STAT_FORM_ORDER_BY_TOTAL_GUESTS_INC, 'Гостей по возрастанию'),
    (PRODUCT_STAT_FORM_ORDER_BY_TOTAL_GUESTS_DEC, 'Гостей по убыванию'),
    (PRODUCT_STAT_FORM_ORDER_BY_USERS_INC, 'Пользователей по возрастанию'),
    (PRODUCT_STAT_FORM_ORDER_BY_USERS_DEC, 'Пользователей по убыванию'),
    (PRODUCT_STAT_FORM_ORDER_BY_CARTS_INC, 'Корзин по возрастанию'),
    (PRODUCT_STAT_FORM_ORDER_BY_CARTS_DEC, 'Корзин по убыванию'),
    (PRODUCT_STAT_FORM_ORDER_BY_INSTANT_CARTS_INC, 'Мгновенных корзин по возрастанию'),
    (PRODUCT_STAT_FORM_ORDER_BY_INSTANC_CARTS_DEC, 'Мгновенных корзин по убыванию'),
    (PRODUCT_STAT_FORM_ORDER_BY_SUBSCRIPTIONS_INC, 'Подписок по возрастанию'),
    (PRODUCT_STAT_FORM_ORDER_BY_SUBSCRIPTIONS_DEC, 'Подписок по убыванию'),

)

class ProductsStatForm(BasePeriodForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].required = False
        self.fields['end_date'].required = False
    order_by = forms.ChoiceField(required=False, label='Упорядочить по', choices=PRODUCT_STAT_FORM_ORDER_BY_CHOICES)