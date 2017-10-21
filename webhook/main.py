# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from dialogflow import DialogFlow
from webcrawling.models import Notice
import logging


@csrf_exempt
def index(request):
    if request.method == 'POST':
        json_request = DialogFlow.get_json(request)
        speech_response = DialogFlow.get_speech_response(json_request)
        webhook_response = DialogFlow.get_webhook_response(speech_response)

        return HttpResponse(
            JsonResponse(webhook_response),
            content_type="application/json; charset=utf-8",
        )
    elif request.method == 'GET':
        notices = Notice.objects.all()
        string = ''

        for notice in notices:
            string += str(notice) + '<p>'
        return HttpResponse(string)
    else:
        return HttpResponse('You are questing by ' + request.method + ' method')
