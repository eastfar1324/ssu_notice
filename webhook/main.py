# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from ssu_notice.common import *
from dialogflow import DialogFlow
import logging


@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        json_obj_request = make_json_object(request)
        webhook_response = DialogFlow.get_webhook_response(json_obj_request)
        return webhook_response
    elif request.method == 'GET':
        dialog_request = request.GET.get('speech')
        DialogFlow()
        json_obj_response = DialogFlow.dialog_response(dialog_request)
        dialog_response = get(json_obj_response, ['result', 'fulfillment', 'speech'])
        return JsonResponse({'dialog_response': dialog_response})
    else:
        return HttpResponse('You are questing by ' + request.method + ' method')
