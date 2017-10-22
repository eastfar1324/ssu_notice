# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.http import JsonResponse
from webcrawling.models import Notice
from datetime import datetime
from django.core import serializers
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
    def get_json(http_request):
        return json.loads(http_request.body.decode('utf-8'))

    @staticmethod
    def get_data_from_request(json_request, keys, index=-1):
        result = json_request
        try:
            for key in keys:
                result = result[key]

            if index >= 0:
                result = result[index]
        except Exception as e:
            result = '%s (%s)' % (e.message, type(e))
        finally:
            return result

    @staticmethod
    def make_http_response(conversational_response):
        return HttpResponse(
            JsonResponse({
                "speech": conversational_response,
                "displayText": conversational_response,
                "data": {},
                "contextOut": [],
                "source": "ssu-notice"
            }),
            content_type="application/json; charset=utf-8",
        )

    @staticmethod
    def get_webhook_response(request, json_request):
        intent_name = DialogFlow.get_data_from_request(json_request, ['result', 'metadata', 'intentName'])

        result = ''
        if intent_name == 'list-detail':
            notices = json.loads(request.session['notices'])
            number = DialogFlow.get_data_from_request(json_request, ['result', 'parameters', 'number'])

            result = notices[int(number.encode('utf-8'))-1]['fields']['url']
        else:
            notices = []

            if intent_name == '00-notices':
                notices = Notice.objects.all().order_by('-id')[:20]
            elif intent_name == '01-recent':
                how_many = DialogFlow.get_data_from_request(json_request, ['result', 'parameters', 'number'])
                notices = Notice.objects.all().order_by('-id')[:how_many]
            elif intent_name == '02-hits':
                notices = Notice.objects.filter(hits__gte=10000).order_by('-id')
            elif intent_name == '03-about':
                subject = DialogFlow.get_data_from_request(json_request, ['result', 'parameters', 'any'])
                notices = Notice.objects.filter(categories__icontains=subject).order_by('-id')
            elif intent_name == '04-date-on' or intent_name == '05-date-from':
                keyword = DialogFlow.get_data_from_request(json_request, ['result', 'parameters', 'keyword'], 0)
                if keyword == 'on':
                    date_on = DialogFlow.get_data_from_request(json_request, ['result', 'parameters', 'date'])
                    year = int(date_on.split('-')[0])
                    month = int(date_on.split('-')[1])
                    day = int(date_on.split('-')[2])
                    notices = Notice.objects.filter(date=datetime(year, month, day)).order_by('-id')
                elif keyword == 'from':
                    date_from = DialogFlow.get_data_from_request(json_request, ['result', 'parameters', 'date'])
                    notices = Notice.objects.filter(date__gte=date_from).order_by('-id')
                else:
                    pass
            else:
                pass

            request.session['notices'] = serializers.serialize('json', notices)

            if not notices:
                result += DialogFlow.get_data_from_request(json_request, ['result', 'fulfillment', 'speech'])
            else:
                for i in range(len(notices)):
                    result += str(i + 1) + ' : ' + notices[i].title.encode('utf-8', 'replace')
                    if i < len(notices) - 1:
                        result += ' / '

        return DialogFlow.make_http_response(result)
