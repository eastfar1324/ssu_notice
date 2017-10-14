from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from dialogflow import DialogFlow
import json


@csrf_exempt
def index(request):
    dialog_flow = DialogFlow()
    if request.POST:
        json_request = dialog_flow.get_json(request)
        speech_request = dialog_flow.get_speech_request(json_request)
        webhook_response = dialog_flow.get_webhook_response(speech_request)

        return HttpResponse(
            JsonResponse(json.dump(webhook_response)),
            content_type="application/json; charset=utf-8",
        )
    else:
        return HttpResponse(
            DialogFlow().get_speech_response('show me notices from yesterday'),
            content_type="text/html; charset=utf-8",
        )
