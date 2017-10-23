from django.conf.urls import url
from . import main

urlpatterns = [
    url('keyboard', main.keyboard),
    url('message',  main.message),
]