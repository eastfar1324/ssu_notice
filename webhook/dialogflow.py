# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.http import JsonResponse
from webcrawling.models import Notice
from datetime import datetime
from django.core import serializers
from ssu_notice.common import get
from ssu_notice.common import make_json_object
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


class DialogFlow:
    dialog = apiai.ApiAI('9e2f805b26a44df3955374bb8278e848')

    def __init__(self):
        pass

    @staticmethod
    def dialog_response(dialog_request):
        request = DialogFlow.dialog.text_request()
        request.query = dialog_request

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
            notices = []

            if intent_name == '00-notices':
                notices = Notice.objects.all().order_by('-id')[:20]
            elif intent_name == '01-recent':
                how_many = get(json_obj_request, ['result', 'parameters', 'number'])
                notices = Notice.objects.all().order_by('-id')[:how_many]
            elif intent_name == '02-hits':
                notices = Notice.objects.filter(hits__gte=10000).order_by('-id')
            elif intent_name == '03-about':
                subject = get(json_obj_request, ['result', 'parameters', 'any'])
                notices = Notice.objects.filter(categories__icontains=subject).order_by('-id')
            elif intent_name == '04-date-on':
                date_on = get(json_obj_request, ['result', 'parameters', 'date'])
                year = int(date_on.split('-')[0])
                month = int(date_on.split('-')[1])
                day = int(date_on.split('-')[2])
                notices = Notice.objects.filter(date=datetime(year, month, day)).order_by('-id')
            elif intent_name == '05-date-from':
                date_from = get(json_obj_request, ['result', 'parameters', 'date'])
                notices = Notice.objects.filter(date__gte=date_from).order_by('-id')
            else:
                pass

            if not notices:
                result += get(json_obj_request, ['result', 'fulfillment', 'speech'])
            else:
                result += 'These are what you ordered!\n\n'
                for i in range(len(notices)):
                    result += '%d : %s\n\n' % ((i+1), notices[i].title.encode('utf-8', 'replace'))
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
