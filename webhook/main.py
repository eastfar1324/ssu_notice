# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from ssu_notice.common import make_json_object
from dialogflow import DialogFlow
from webcrawling.models import Notice
import logging


@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        json_obj_request = make_json_object(request)

        webhook_response = DialogFlow.get_webhook_response(json_obj_request)

        return webhook_response
    elif request.method == 'GET':
        notices = Notice.objects.all()
        string = ''

        for notice in notices:
            string += str(notice) + '<p>'
        return HttpResponse(string)
    else:
        return HttpResponse('You are questing by ' + request.method + ' method')
