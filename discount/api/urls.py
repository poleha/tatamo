from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from discount.api import views
urlpatterns = patterns('products.api.views',
    url(r'products/$', views.ProductListCreateAPIView.as_view(), name='product-list'),
    #url(r'^$', 'api_root'),
    )

urlpatterns = format_suffix_patterns(urlpatterns)