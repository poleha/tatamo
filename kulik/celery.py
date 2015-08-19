from __future__ import absolute_import

import os

from celery import Celery
import celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kulik.settings')

app = Celery('kulik')

from datetime import timedelta

#app.conf.update(
#CELERYBEAT_SCHEDULE = {
#    'add-every-10-seconds': {
#        'debug': 'debug_task',
#        'schedule': timedelta(seconds=10),
#        'args': (16, 16)
#    },
#},
#CELERYBEAT_SCHEDULE = {
    #'tatamo_test': {
    #    'task': 'tatamo_test',
    #    'schedule': timedelta(seconds=10),
    #},
#},
#CELERYBEAT_SCHEDULER = 'celery.beat:PersistentScheduler',
#CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
#)

CELERY_TIMEZONE = 'Europe/Moscow'

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

#from app.task import periodic_task
#@app.task
#def debug_task(self):
#    print('Request: {0!r}'.format(self.request))

#@app.task(name='tatamo_test')
#def tatamo_test():
#    print('finished')
