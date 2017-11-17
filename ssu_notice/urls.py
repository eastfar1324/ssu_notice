from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url('webhook', include('webhook.urls')),
    url('crawl', include('webcrawling.urls')),
    url('kakao', include('kakao.urls')),
    url('visualize', include('visualize.urls')),
    url(r'^admin/', include(admin.site.urls)),
]