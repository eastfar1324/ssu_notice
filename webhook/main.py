from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from dialogflow import DialogFlow
import logging

@csrf_exempt
def index(request):
    dialogflow = DialogFlow()

    if request.method == 'POST':
        json_request = dialogflow.get_json(request)
        speech_response = dialogflow.get_speech_response(json_request)
        webhook_response = dialogflow.get_webhook_response(speech_response)

        return HttpResponse(
            JsonResponse(webhook_response),
            content_type="application/json; charset=utf-8",
        )
    elif request.method == 'GET':
        return HttpResponse('Please request by POST')
    else:
        return HttpResponse('You are questing by ' + request.method + ' method')