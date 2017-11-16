from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url('webhook', include('webhook.urls')),
    url('crawl', include('webcrawling.urls')),
    url('kakao', include('kakao.urls')),
    url('visualize', views.index),
    url(r'^admin/', include(admin.site.urls)),
]