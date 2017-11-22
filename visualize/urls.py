from django.conf.urls import url
import visualize
import get_hits


urlpatterns = [
    url('get_hits', get_hits.get),
    url('^$', visualize.index),
]
