from django.conf.urls import patterns, url

from polls import views

urlpatterns = patterns('',
    url(r'^poll/(?P<pk>\d+)$', views.PollView.as_view(), name='poll-view'),
    #url(r'^vote/(?P<pk>\d+)$', views.VoteView.as_view(), name='vote-view'), #'discount/product/product_detail.html'
    )