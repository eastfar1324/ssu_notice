from django.conf.urls import url
from main import *


urlpatterns = [
    url('analyze_all', analyze_all),
    url('get_hits', get_hits_increase),
    url('^$', index),
]
