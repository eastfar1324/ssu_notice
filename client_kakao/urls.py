from django.conf.urls import url
from . import main

urlpatterns = [
    url('friend', main.friend),
    url('keyboard', main.keyboard),
    url('message',  main.message),
    url('chat_room', main.leave),
]