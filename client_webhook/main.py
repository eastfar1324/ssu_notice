# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from ssu_notice.common import *
from ssu_notice.dialogflow import DialogFlow


@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        json_obj_request = make_json_object(request)
        webhook_response = DialogFlow.response_webhook(json_obj_request)
        return webhook_response
    else:
        return HttpResponse('You are questing by ' + request.method + ' method')
