from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url('crawl', include('webcrawling.urls')),
    url('webhook', include('client_webhook.urls')),
    url('kakao', include('client_kakao.urls')),
    url('ios', include('client_ios.urls')),
    url(r'^visualize', include('client_visualize.urls')),
    url(r'^admin/', include(admin.site.urls)),
]