# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ssu_notice.common import get
from ssu_notice.common import make_json_object
from ssu_notice.dialogflow import DialogFlow
from models import Request
from models import Unknown
import logging
import json


def keyboard(request):
    return JsonResponse({
        'type': 'text'
    })


@csrf_exempt
def message(request):
    json_obj_request = make_json_object(request)
    speech_request = get(json_obj_request, ['content'])
    logging.debug(speech_request)

    DialogFlow()
    json_obj_response = DialogFlow.response_json_obj(speech_request)
    intent_name = get(json_obj_response, ['result', 'metadata', 'intentName'])
    speech_response = get(json_obj_response, ['result', 'fulfillment', 'speech'])

    if intent_name != 'link':
        user_key = get(json_obj_request, ['user_key'])
        Request.create(user_key, speech_request).save()

    result = {
        'message': {
            'text': speech_response
        },
        "keyboard": {
            "type": "text"
        }
    }

    if 'notice' in intent_name:
        notices = json.loads(get(json_obj_response, ['result', 'contexts', 0, 'parameters', 'notices']))
        result['keyboard'] = {
            "type": "buttons",
            "buttons": [notice['fields']['title'] for notice in notices]
        }
    elif intent_name == 'link':
        url = get(json_obj_response, ['result', 'fulfillment', 'displayText'])
        result['message']['message_button'] = {
            "label": '보러가기',
            "url": url
        }
    elif intent_name == 'Default Fallback Intent':
        unknown = Unknown.objects.filter(speech_request=speech_request).first()

        if unknown is None:
            Unknown.create(speech_request).save()
        else:
            unknown.count += 1
            unknown.save(update_fields=['count'])

            if unknown.speech_response is not None:
                result['message']['text'] = unknown.speech_response

    return JsonResponse(result)
