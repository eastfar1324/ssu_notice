from django.conf.urls import include, url
from django.contrib import admin

from webhook.main import index
from webcrawling.test import test

urlpatterns = [
    url(r'^$', index),
    url(r'^crawling', test),
    url(r'^admin/', include(admin.site.urls)),
]