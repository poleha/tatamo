from django.conf.urls import patterns, include, url
#from rest_framework import routers, serializers, viewsets
from django.contrib.auth.models import User

"""
url()
https://docs.djangoproject.com/en/1.7/ref/urls/
url(regex, view, kwargs=None, name=None, prefix='')
You can use the url() function, instead of a tuple, as an argument to patterns(). This is convenient if you want to specify a name without the optional extra arguments dictionary. For example:

urlpatterns = patterns('',
    url(r'^index/$', index_view, name="main-view"),
    ...
)
This function takes five arguments, most of which are optional:

url(regex, view, kwargs=None, name=None, prefix='')



include()
https://docs.djangoproject.com/en/1.7/ref/urls/#include
https://docs.djangoproject.com/en/1.7/topics/http/urls
include(module[, namespace=None, app_name=None])
include(pattern_list)
include((pattern_list, app_namespace, instance_namespace))
A function that takes a full Python import path to another URLconf module that should be “included” in this place.
Optionally, the application namespace and instance namespace where the entries will be included into can also be
specified.

include() also accepts as an argument either an iterable that returns URL patterns or a 3-tuple
containing such iterable plus the names of the application and instance namespaces.

Parameters:
module – URLconf module (or module name)
namespace (string) – Instance namespace for the URL entries being included
app_name (string) – Application namespace for the URL entries being included
pattern_list – Iterable of URL entries as returned by patterns()
app_namespace (string) – Application namespace for the URL entries being included
instance_namespace (string) – Instance namespace for the URL entries being included

application namespace - простраство имен приложения. У нескольких приложений может быть view с именем index
чтобы reverse мог их различить, например:
В kulik.urls указано
url(r'^polls/', include('polls.urls', namespace="polls")),
url(r'^posts/', include('posts.urls', namespace="posts")),

В posts.urls
url(r'^$', views.index, name='index'),
В polls.urls тоже
url(r'^$', views.index, name='index'),

Мы передаем в reverse('polls:index') или reverse('posts:index'), чтобы их различить.

instance namespace
По умолчанию = application namespace.
У приложения может быть несколько instances. Если их несколько, то текущее должно быть указано в:
"If there is a current application defined, Django finds and returns the URL resolver for that instance.
The current application can be specified as an attribute on the template context - applications that expect to
have multiple deployments should set the current_app attribute on any Context or RequestContext that is used to
render a template.
The current application can also be specified manually as an argument
to the django.core.urlresolvers.reverse() function."
то есть в объекте Context или RequestContext. Также может быть указано вручную в функции reverse().

"""

from django.contrib import admin
from kulik import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.sitemaps.views import sitemap
from discount.sitemaps import sitemaps
from django.views.decorators.cache import cache_page




urlpatterns = patterns('',


    url(r'^contact_form/', include('contact_form.urls', namespace="contact_form")),

    url(r'^admin/', include(admin.site.urls)),

    (r'^accounts/', include('allauth.urls')),


    url(r'^', include('discount.urls', namespace='discount')),
    url(r'^polls/', include('polls.urls', namespace='polls')),
    url(r'^sitemap\.xml$', cache_page(60 * 60)(sitemap), {'sitemaps': sitemaps},
    name='django.contrib.sitemaps.views.sitemap')
    #url(r'^discount/api/', include('discount.api.urls')),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #url(r'^', include(router.urls)),

    #legacy
#url(r'^markitup/', include('markitup.urls')),
#url(r'^polls/', include('polls.urls', namespace="polls")),
 #url(r'^users/', include('users.urls', namespace="users")),
#url(r'^$', views.main, name='kulik'),
  #url(r'^posts/', include('posts.urls', namespace="posts")),
    #url(r'^mixintest/', include('mixintest.urls', namespace="mixintest")),
    #url(r'^history/', include('history.urls', namespace="history")),
    #url(r'^dreams/', include('dreams.urls', namespace='dreams')),
    #url(r'^dreams/api/', include('dreams.api_urls')),

    #url(r'^tester/', include('tester.urls', namespace='tester')),


)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL,
            document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

#urlpatterns += patterns('', url(r'^silk/', include('silk.urls', namespace='silk')))