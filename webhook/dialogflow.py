# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers
from ssu_notice.common import get
from ssu_notice.common import make_json_object
from ssu_notice.db import DB
import os.path
import sys
import json
import logging

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

reload(sys)
sys.setdefaultencoding('utf-8')


class DialogFlow:
    dialog = apiai.ApiAI('9e2f805b26a44df3955374bb8278e848')

    def __init__(self):
        pass

    @staticmethod
    def dialog_response(dialog_request):
        request = DialogFlow.dialog.text_request()
        request.query = dialog_request
        request.lang = 'ko-KR'

        response = request.getresponse()
        json_obj_response = make_json_object(response)

        return json_obj_response

    @staticmethod
    def get_webhook_response(json_obj_request):
        intent_name = get(json_obj_request, ['result', 'metadata', 'intentName'])

        result = ''
        if intent_name == 'list-detail':
            notices = json.loads(get(json_obj_request, ['result', 'contexts', 0, 'parameters', 'notices']))
            number = int(get(json_obj_request, ['result', 'parameters', 'number']).encode('utf-8'))

            result = notices[number-1]['fields']['url']
            return HttpResponse(
                JsonResponse({
                    "speech": result,
                    "displayText": result,
                    "data": {},
                    "contextOut": [],
                    "source": "ssu-notice"
                }),
                content_type="application/json; charset=utf-8",
            )
        else:
            notices, service_message = DB.get_notices(intent_name, get(json_obj_request, ['result', 'parameters']))

            if not notices:
                result += get(json_obj_request, ['result', 'fulfillment', 'speech'])
            else:
                result += service_message
                for i in range(len(notices)):
                    result += '%d : %s\n\n' % (i+1, notices[i].title.encode('utf-8', 'ignore'))
                result += 'Please let me know the number you want to check : '

            context = get(json_obj_request, ['result', 'contexts', 0])
            context['parameters']['notices'] = serializers.serialize('json', notices)
            return HttpResponse(
                JsonResponse({
                    "speech": result,
                    "displayText": result,
                    "data": {},
                    "contextOut": [context],
                    "source": "ssu-notice"
                }),
                content_type="application/json; charset=utf-8",
            )
