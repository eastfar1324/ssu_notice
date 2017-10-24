# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ssu_notice.common import make_json_object
from webhook.dialogflow import DialogFlow
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from ssu_notice.common import get
import json
import logging


def keyboard(request):
    return JsonResponse({
        'type': 'text'
    })


@csrf_exempt
def message(request):
    json_obj_request = make_json_object(request)
    dialog_request = get(json_obj_request, ['content'])
    json_obj_response = DialogFlow.dialog_response(dialog_request)

    dialog_response = get(json_obj_response, ['result', 'fulfillment', 'speech'])

    result = None
    try:
        url_validator = URLValidator()
        url_validator(dialog_response)

        notices = json.loads(get(json_obj_response, ['result', 'contexts', 0, 'parameters', 'notices']))
        number = int(get(json_obj_response, ['result', 'parameters', 'number']).encode('utf-8'))

        title = notices[number-1]['fields']['title']
    except ValidationError:
        result = {
            'message': {
                'text': dialog_response
            }
        }
    except IndexError:
        result = {
            'message': {
                'text': 'Give me the right number.'
            }
        }
    else:
        result = {
            'message': {
                "message_button": {
                    "label": title,
                    "url": dialog_response
                }
            }
        }
    finally:
        return JsonResponse(result)