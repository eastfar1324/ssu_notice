from django.conf.urls import url
import main

urlpatterns = [
    url(r'^$', main.webhook),
]