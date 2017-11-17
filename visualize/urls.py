from django.conf.urls import url
import visualize

urlpatterns = [
    url(r'^$', visualize.index),
]