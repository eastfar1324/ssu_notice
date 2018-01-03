from django.conf.urls import url
from views import *


urlpatterns = [
    url('teach', teach),
    url('^$', index),
]
