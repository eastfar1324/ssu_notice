from django.conf.urls import include, url
from django.contrib import admin
from webhook import webhook

urlpatterns = [
    url('webhook', webhook),
    url('crawl', include('webcrawling.urls')),
    url('kakao', include('client_kakao.urls')),
    url(r'^learn', include('client_learn.urls')),
    url(r'^visualize', include('client_visualize.urls')),
    url(r'^admin/', include(admin.site.urls)),
]