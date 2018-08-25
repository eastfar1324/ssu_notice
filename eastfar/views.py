# -*- coding: utf-8 -*-
from django.shortcuts import render
from client_kakao.models import Request
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def index(request):
    requests = Request.objects.all().order_by('-id')[:50]
    return render(request, 'requests.html', {'requests': requests})
