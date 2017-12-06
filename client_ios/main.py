# -*- coding: utf-8 -*-
from django.http import JsonResponse
from ssu_notice.common import *
from ssu_notice.db import DB
from ssu_notice.dialogflow import DialogFlow
import logging


def index(request):
    dialog_request = request.GET.get('speech')
    DialogFlow()  # initialize DialogFlow
    json_obj_response = DialogFlow.response_json_obj(dialog_request)

    dialog_response, result = '', []
    intent_name = get(json_obj_response, ['result', 'metadata', 'intentName'])
    notices = DB.get_notices(intent_name, get(json_obj_response, ['result', 'parameters']))

    if not notices:
        dialog_response += get(json_obj_response, ['result', 'fulfillment', 'speech'])
    else:
        dialog_response += '"%s"에 대한 결과에요.' % get(json_obj_response, ['result', 'resolvedQuery'])
        for notice in notices:
            result.append({
                "title": notice.title.encode('utf-8', 'ignore'),
                "url": notice.url
            })

    return JsonResponse({
        'dialog_response': dialog_response,
        'result': result
    })
