# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers
from difflib import SequenceMatcher
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
    def response_json_obj(speech_request):  # 미확인 대화 요청에 대한 json 응답 반환
        request = DialogFlow.dialog.text_request()
        request.query = speech_request
        request.lang = 'ko-KR'

        response = request.getresponse()
        json_obj_response = make_json_object(response)

        return json_obj_response

    @staticmethod
    def response_webhook(json_obj_request):  # 공지사항 웹훅 요청에 대한 응답
        intent_name = get(json_obj_request, ['result', 'metadata', 'intentName'])

        speech, display_text, context_out = None, None, []
        if intent_name != 'link':  # 초기 요청에 대한 처리
            notices = DB.get_notices(intent_name, get(json_obj_request, ['result', 'parameters']))

            speech = ('"%s"에 대한 결과에요.' if notices else '"%s"에 대한 결과를 찾을 수 없어요.') % get(json_obj_request, ['result', 'resolvedQuery'])
            display_text = speech

            context = get(json_obj_request, ['result', 'contexts', 0])
            context['parameters']['notices'] = serializers.serialize('json', notices)
            context_out.append(context)

        else:  # 특정 공지사항 url 요청에 대한 처리
            notices = json.loads(get(json_obj_request, ['result', 'contexts', 0, 'parameters', 'notices']))
            requested_title = get(json_obj_request, ['result', 'resolvedQuery'])
            requested_notices = []
            for notice in notices:
                if SequenceMatcher(None, requested_title, notice['fields']['title']).ratio() > 0.9:
                    requested_notices.append(notice)
            speech = requested_title
            display_text = requested_notices[0]['fields']['url']

        return HttpResponse(
            JsonResponse({
                "speech": speech,
                "displayText": display_text,
                "data": {},
                "contextOut": context_out,
                "source": "ssu-notice"
            }),
            content_type="application/json; charset=utf-8",
        )
