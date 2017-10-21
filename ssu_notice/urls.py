from django.conf.urls import include, url
from django.contrib import admin

from webhook.main import index
from webcrawling.crawl_service import crawl

urlpatterns = [
    url(r'^$', index),
    url(r'^crawling', crawl),
    url(r'^admin/', include(admin.site.urls)),
]