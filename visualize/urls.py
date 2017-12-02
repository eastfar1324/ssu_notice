from django.conf.urls import url
import visualize


urlpatterns = [
    url('analyze_all', visualize.analyze_all),
    url('get_hits', visualize.get_hits_increase),
    url('^$', visualize.index),
]
