"""
Django settings for kulik project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'prq!u1o6nl3@1zj3php74k7zprrscbt93=%g^97grwkcozj8q)'

# SECURITY WARNING: don't run with debug turned on in production!


ALLOWED_HOSTS = ['127.0.0.1', 'tatamo.ru', '46.36.222.4', '46.4.104.50', 'www.tatamo.ru']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'allauth',
    'allauth.account',
    'contact_form',
    'multi_image_upload',
    #'rest_framework',
    'discount',
    #'kombu',

    #'reversion',
    'polls',
    'compressor',
)


"""
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}
"""

MIDDLEWARE_CLASSES = (

     #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'discount.middleware.DiscountUpdateCacheMiddleware',    #cache
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'discount.middleware.DiscountAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'discount.middleware.DiscountFetchFromCacheMiddleware', #cache


)

#APPEND_SLASH = False

SESSION_SAVE_EVERY_REQUEST = True




ROOT_URLCONF = 'kulik.urls'

WSGI_APPLICATION = 'kulik.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'discount',
        'USER': 'kulik',
        'PASSWORD': '1234567',
       'HOST': '127.0.0.1',
       'PORT': '5432',
        'CONN_MAX_AGE': 30,
        },


#    'default123': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
}




# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


#DATETIME_FORMAT = 'N'






AUTHENTICATION_BACKENDS = (
    'discount.backends.DiscountBackend',
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",

    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",

)

SITE_ID = '1'   #???????????????????????????
#X_FRAME_OPTIONS = 'SAMEORIGIN'

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'  # URL для медии в шаблонах


SERVER_EMAIL = 'admin@tatamo.ru'

#allauth
LOGIN_REDIRECT_URLNAME = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_MIN_LENGTH = 5
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 30
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_PASSWORD_MIN_LENGTH = 6
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = ""
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False

#
STATICFILES_FINDERS = (
                        "django.contrib.staticfiles.finders.FileSystemFinder",
                        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
                        'compressor.finders.CompressorFinder',
)









PRODUCT_THUMB_SETTINGS = {'thumb66': (66, 88), 'thumb180': (180, 240),'thumb120': (120, 160), 'thumb204': (204, 272),
                  'thumb1080':(1080, 1440), 'thumb300': (300, 400) }


PRODUCT_BANNER_THUMB_SETTINGS = {'thumb360': (360, 200), 'thumb90': (90, 50), 'thumb180': (180, 100)}

ADMINS = (('Alex Poleha', 'admin_info@tatamo.ru'),)

SHOP_THUMB_SETTINGS = {'thumb100': (100, 100), 'thumb300': (300, 300)}


GENERAL_CONDITIONS = [
    'Распечатанный купон необходимо предъявлять в магазине для получения скидки.',
    'Информацию по условиям акции вы можете уточнить по телефону магазина.',
    'Компания Татамо не продает товар и не несет ответственность за качество товара, а лишь информирует о скидках'
]

#Pagination

PAGINATE_BY_PRODUCT_LIST = 30
PAGINATE_BY_PRODUCT_DETAIL = 30 #comments
#PAGINATE_BY_CART_VIEW = 150
PAGINATE_BY_SHOP_DETAIL = 30
PAGINATE_BY_SHOP_LIST = 30

REPEATED_LETTER_INTERVAL = 60 * 60 * 3
DAYS_TO_ADD_EVERY_MONTH = 3
PAYMENT_USER_ID = 1



DEFAULT_FROM_EMAIL = 'Tatamo.ru <admin@tatamo.ru>'
SITE_URL = 'http://tatamo.ru'


#from datetime import timedelta
#celery
#http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
INSTALLED_APPS += ("celery", )
CELERY_TIMEZONE = 'Europe/Moscow'




#INSTALLED_APPS += ("markitup", )
#JQUERY_URL = None
#MARKITUP_FILTER = ('markdown.markdown', {'safe_mode': False})

#SILKY_PYTHON_PROFILER = True

#SILKY_DYNAMIC_PROFILING = [{
#    'module': 'discount.views',
#    'function': 'ProductList.get'
#}]


TEMPLATES = [{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'discount/templates/discount')],
        'OPTIONS': {
        #    'loaders': [
        #            'django.template.loaders.filesystem.Loader',
        #            'django.template.loaders.app_directories.Loader',
        #    ],

                'context_processors': [
         # Required by allauth template tags
        "django.contrib.auth.context_processors.auth",
        #'django.template.context_processors.debug',
        "django.template.context_processors.request", #делает объект request достпным в шаблонах
        # allauth specific context processors
        "allauth.account.context_processors.account",
        "discount.context_processors.debug",
        "django.core.context_processors.media",
        "django.core.context_processors.static",
        #"allauth.socialaccount.context_processors.socialaccount",
        #"kulik.context_processors.get_current_path",   1191 DELETE
                ],

        },
    }]



import socket

try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'localhost'


    CACHES = {
        'default': {
            'BACKEND': 'discount.backends.DiscountMemcachedCacheCacheBackend',
            'LOCATION': '127.0.0.1:11211',
        }
    }


if HOSTNAME in ['localhost', 'ubuntu']:
    DEBUG = True
    TEMPLATE_DEBUG = True
    DISCOUNT_CACHE_ENABLED = False

else:
    DEBUG = False
    TEMPLATE_DEBUG = False
    DISCOUNT_CACHE_ENABLED = True



DISCOUNT_FULL_PAGE_CACHE_DURATION = 60 * 60
DISCOUNT_SAVE_PRODUCT_STAT = True


DEBUG_TOOLBAR = False


if DEBUG_TOOLBAR:

    DEBUG = True

    TEMPLATE_DEBUG = False

    INSTALLED_APPS += ('debug_toolbar',)

    DEBUG_TOOLBAR_PATCH_SETTINGS = True
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]

    INTERNAL_IPS = ['127.0.0.1', '46.36.222.4']

    MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES




if DISCOUNT_CACHE_ENABLED:

    TEMPLATES[0]['OPTIONS']['loaders'] = [
            ('django.template.loaders.cached.Loader',
                  [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
            ],
                ),
        ]
else:
       TEMPLATES[0]['OPTIONS']['loaders'] = [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
        ]



ACTION_TYPE_POPULAR_COST = 800
ACTION_TYPE_CATEGORY_COST = 500

REPEATED_FREE_SUBSCRIPTION_INTERVAL = 30


MAX_POPULAR_COUNT = 3
MAX_CATEGORY_COUNT = 5

#MAX_LOCK_TIME = 5

ALIAS_MEN = 'men'
ALIAS_WOMEN = 'women'
ALIAS_CHILDREN = 'children'
ALIAS_SHOES = 'shoes'
ALIAS_BEAUTY = 'beauty'
ALIAS_HOME = 'home'
ALIAS_JEWELRY = 'jewelry'
ALIAS_TOYS = 'toys'
ALIAS_ACCESSORIES = 'accessories'
ALIAS_SPORT = 'sport'
ALIAS_ALL = 'all'
ALIAS_FAMILY_LOOK = 'family_look'


#from django.utils import timezone
from datetime import date


START_DATE = date(year=2015, month=8, day=1)


SHOW_EMPTY_CATEGORIES = False
SHOW_PREPARED_PRODUCTS = False
from datetime import timedelta


INSTALLED_APPS += ("djcelery", )

# redis server address
BROKER_URL = 'redis://localhost:6379/0'
# store task results in redis
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# task result life time until they will be deleted
CELERY_TASK_RESULT_EXPIRES = 7 * 86400  # 7 days
# needed for worker monitoring
CELERY_SEND_EVENTS = True
# where to store periodic tasks (needed for scheduler)
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

# add following lines to the end of settings.py
import djcelery
djcelery.setup_loader()



#START_DATE = date(year=2015, month=7, day=1)


COMPRESS_ENABLED = True