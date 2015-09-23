from django.conf.urls import patterns, url
from discount import views
#from django.views.decorators.cache import cache_page

urlpatterns = patterns('discount.views',
    #cart
    #url(r'^cart_add/(?P<pk>\d+)/$', views.AddProductToCart.as_view(), kwargs={'action': 'add'}, name='cart-add'),
    #url(r'^cart_remove/(?P<pk>\d+)/$', views.AddProductToCart.as_view(), kwargs={'action': 'remove'}, name='cart-remove'),
    url(r'^cart/$', views.CartView.as_view(), name='cart-view'), #'discount/cart/cart_view.html'
    url(r'^instant_cart/$', views.CartView.as_view(), name='instant-cart-view', kwargs={'action': 'instant'}), #'discount/cart/cart_view.html'
    url(r'^cart_remove_from_cart/$', views.CartView.as_view(), kwargs={'action': 'remove'}, name='cart-remove-from-cart'),  #!!!!
    url(r'^cart_clear/$', views.CartView.as_view(), kwargs={'action': 'clear'}, name='cart-clear'),  #!!!
    url(r'^cart_remove_expired/$', views.CartView.as_view(), kwargs={'action': 'remove-expired'}, name='cart-remove-expired'), #!!!
    url(r'^cart_finish/$', views.CartView.as_view(), name='cart-finish', kwargs={'action': 'finish'} ),  #!!!
    #url(r'^cart/view/(?P<link>[a-zA-Z0-9_]{1,})/$', views.CartViewLink.as_view(), name='cart-view-link'), #'discount/cart/cart_view_link.html'
    #url(r'^cart/list/$', views.CartList.as_view(), name='cart-list'), #'discount/cart/cart_list.html'


    #cart-product
    url(r'^coupon/(?P<pk>\d+)/$', views.ProductCartView.as_view(), name='coupon-view', kwargs={'type': 'normal'}), #'discount/product/product_cart_view.html'   #!!!
    url(r'^c/(?P<pk>\d+)/(?P<uid>\d+)/(?P<pin>\d+)/$', views.ProductCartView.as_view(), name='qr-coupon-view', kwargs={'type': 'qr'}), #'discount/product/product_cart_view.html' #!!!
    #Одиночная акция, на которую мы уже подписаны. Попадаем с основной страницы акции. Выводит изменения даты, статуса, размеров и цветов с момента подписки.

    url(r'^product/pdf_view/(?P<pk>\d+)/$', views.SingleProductPDFView.as_view(), name='product-pdf-view'),  #!!!
    #PDF - аналог coupon-view


    url(r'^qr-code/(?P<data>[a-zA-Z0-9\-\/_\:\.]{1,})/$', views.coupon_qr_code_view, name='coupon-qr-code-view'), #!!!


    #product
    url(r'^product/detail/(?P<pk>\d+)/$', views.ProductDetail.as_view(), kwargs={'type': 'pk'}, name='product-detail'), #'discount/product/product_detail.html'
    url(r'^product/detail/(?P<code>[a-zA-Z0-9_]{1,})/$', views.ProductDetail.as_view(), kwargs={'type': 'code'}, name='product-detail-code'), #'discount/product/product_detail.html'
    url(r'^product/list/(?P<alias>[a-z0-9_]{1,})/$', views.ProductList.as_view(), name='product-list'), #'discount/product/product_list.html'
    url(r'^product/create/$', views.ProductCreate.as_view(), name='product-create'), #'discount/product/product_create.html'
    url(r'^product/update/(?P<pk>\d+)/$', views.ProductCreate.as_view(), name='product-update'), #'discount/product/product_create.html'
    url(r'^generate_product_code/$', views.GenerateProductCode.as_view(), name='generate-product-code'), #!!!

    url(r'^get_product_by_code', views.GetProductByCode.as_view(), name='get-product-by-code'), #!!!
    url(r'^left_menu/(?P<alias>[a-z0-9_]{1,})/$', views.ProductListFilterForm.as_view(), name='product-list-filter-form'), #'discount/product/_product_list_filter_form.html' #!!!

    url(r'^product/shop_list/$', views.ProductList.as_view(), name='product-list-shop', kwargs={'type': 'shop'}), #'discount/product/product_list.html' #!!!

    url(r'^left_menu_shop/$', views.ProductListFilterForm.as_view(), name='product-list-filter-form-shop', kwargs={'type': 'shop'}), #'discount/product/_product_list_filter_form.html' #!!!



    url(r'^product/code_list/$', views.ProductList.as_view(), name='product-list-code', kwargs={'type': 'code'}), #'discount/product/product_list.html' #!!!
    url(r'^left_menu_code/$', views.ProductListFilterForm.as_view(), name='product-list-filter-form-code', kwargs={'type': 'code'}), #'discount/product/_product_list_filter_form.html' #!!!

    url(r'^product/finished_code_list/$', views.ProductList.as_view(), name='product-list-finished-code', kwargs={'type': 'finished-code'}), #'discount/product/product_list.html' #!!!
    url(r'^left_menu_finished_code/$', views.ProductListFilterForm.as_view(), name='product-list-filter-form-finished-code', kwargs={'type': 'finished-code'}), #'discount/product/_product_list_filter_form.html' #!!!

    url(r'^get_available_product_types_ajax', views.GetAvailableProductTypesAjax.as_view(), name='get-available-product-types-ajax'), #!!!
    url(r'^get_available_filters_ajax', views.GetAvailableFiltersAjax.as_view(), name='get-available-filters-ajax'), #!!!


    url(r'^product/banners/(?P<pk>\d+)/$', views.ProductBannersView.as_view(),name='product-banners'), #'discount/product/product_detail.html' #!!!

    url(r'^product/start/(?P<pk>\d+)/$', views.ProductStartView.as_view(),name='product-start'), #'discount/product/product_detail.html' #!!!


    url(r'^product/change/(?P<pk>\d+)/$', views.ProductChangeView.as_view(), name='product-change'), #'discount/product/product_detail.html' #!!!
    #url(r'^product/change/update/(?P<pk>\d+)/$', views.ProductChangeView.as_view(), kwargs={'type': 'update'}, name='product-change-existing'), #'discount/product/product_detail.html'

    #url(r'^banner/send_to_approve/$', views.SendBannerToApproveView.as_view(), name='send-banner-to-approve'), #'discount/product/product_detail.html'
    url(r'^product/export/all/$', views.ExportProductsToCsvView.as_view(), name='product-export-all'), #'discount/product/product_list.html' #!!!

    url(r'^subscribed_to_product/(?P<pk>\d+)/$', views.SubsribedToProductView.as_view(), kwargs={'action': 'subscribed'}, name='subscribed_to_product'), #!!!
    url(r'^cart_to_product/(?P<pk>\d+)/$', views.SubsribedToProductView.as_view(), kwargs={'action': 'cart'}, name='cart_to_product'), #!!!
    url(r'^bought_to_product/(?P<pk>\d+)/$', views.SubsribedToProductView.as_view(), kwargs={'action': 'bought'}, name='bought_to_product'), #!!!

    url(r'^product_stat_save/(?P<pk>\d+)/$', views.ProductStatSaveView.as_view(), name='product-stat-save'),

    url(r'^products_stat/$', views.ProductsStatView.as_view(), name='products-stat'), #'discount/product/product_list.html' #!!!

    #product_to_cart
    #url(r'^ptc_subscribe_view/(?P<pk>\d+)/$', views.PTCSubscribe.as_view(), name='ptc-subscribe-view'),

    #url(r'^cart_actions/(?P<pk>\d+)/$', views.CartActions.as_view(), name='cart-actions'),
    url(r'^ptc_add/(?P<pk>\d+)/$', views.PtcAdd.as_view(), name='ptc-add'), #!!!
    url(r'^ptc_subscribe/(?P<pk>\d+)/$', views.PtcSubscribe.as_view(), name='ptc-subscribe'), #!!!
    url(r'^coupon_status/(?P<pk>\d+)/$', views.CouponStatus.as_view(), name='coupon-status'), #!!!


    #general
    url(r'^$', views.MainPage.as_view(), name='main-page'), #'discount/general/main_page.html'

   #shop
    url(r'^shop/detail/(?P<pk>\d+)/$', views.ShopDetail.as_view(), name='shop-detail'), #'discount/shop/shop_detail.html' #!!!
    url(r'^shop/list/$', views.ShopList.as_view(), name='shop-list'), #'discount/shop/shop_list.html'

    url(r'^shop/create/$', views.ShopCreate.as_view(), name='shop-create'), #'discount/shop/shop_list.html' #!!!
    #url(r'^shop/update/(?P<pk>\d+)/$', views.ShopUpdate.as_view(), name='shop-update'),
    url(r'^shop/update/(?P<pk>\d+)/$', views.ShopCreate.as_view(), name='shop-update'), #'discount/product/product_create.html' #!!!



    #user
    url(r'^ajax_login/$', views.DiscountLoginView.as_view(), name='login'), #'discount/user/_login.html' #!!!
    url(r'^login/$', views.DiscountFullLoginView.as_view(), name='full-login'), #'discount/user/_login.html'
    url(r'^signup/$', views.DiscountSignupView.as_view(), name='signup'), #'discount/user/_login.html'
    url(r'^cart_login/$', views.DiscountCartLoginView.as_view(), name='cart-login'),
    url(r'^cart_signup/$', views.DiscountCartSignupView.as_view(), name='cart-signup'),
    url(r'^user/$', views.UserDetail.as_view(), name='user-detail'), #'discount/user/user_detail.html' #!!!
    url(r'^shops_to_users_confirm/$', views.ShopsToUsersConfirm.as_view(), name='shops-to-users-confirm'), #'discount/user/user_detail.html' #!!!
    url(r'^change_password/$', views.ChangePasswordView.as_view(), name='change-password'), #'discount/user/_login.html' #!!!


    #static
    url(r'^contacts', views.ContactsPageView.as_view(), name='contacts-page'), #'discount/user/_login.html'
    url(r'^help', views.HelpPageView.as_view(), name='help-page'), #'discount/user/_login.html'
    url(r'^shop_offer', views.ShopOfferView.as_view(), name='shop-offer'), #'discount/user/_login.html'
    url(r'^shop_instructions', views.ShopInstructionsView.as_view(), name='shop-instructions'),



    #adm
    url(r'^tatamo_manager/$', views.TatamoManagerPageView.as_view(), name='tatamo-manager-page'),   #!!!
    url(r'^load_products/$', views.AdmLoadProductsView.as_view(), name='load-products'),   #!!!
    url(r'^monitor/$', views.AdmMonitorView.as_view(), name='monitor'),   #!!!

    url(r'^product/tatamo_list/$', views.ProductList.as_view(), name='product-list-tatamo', kwargs={'type': 'tatamo'}), #'discount/product/product_list.html' #!!!
    url(r'^left_menu_tatamo/$', views.ProductListFilterForm.as_view(), name='product-list-filter-form-tatamo', kwargs={'type': 'tatamo'}), #'discount/product/_product_list_filter_form.html' #!!!

    url(r'^product_tatamo_manager_approve/(?P<pk>\d+)/$', views.ProductTatamoManagerApproveView.as_view(), name='product-tatamo-manager-approve'),  #!!!

    url(r'^shops_monitor/$', views.AdmShopsMonitorView.as_view(), name='shops-monitor'),   #!!!

    url(r'^users_monitor/$', views.AdmUsersMonitorView.as_view(), name='users-monitor'),   #!!!

    url(r'^product_doubles_monitor/$', views.AdmProductDoublesMonitorView.as_view(), name='product-doubles-monitor'),   #!!!

    url(r'^check_products_links/$', views.AdmCheckProductsLinks.as_view(), name='check-products-links'),   #!!!


    )

