# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers
from ssu_notice.common import get
from ssu_notice.common import make_json_object
from ssu_notice.db import DB
import os.path
import sys

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
        intent_name = get(json_obj_request, ['queryResult', 'intent', 'displayName'])
        payload = {}

        if intent_name != 'link':  # 초기 요청에 대한 처리
            notices = DB.get_notices(intent_name, get(json_obj_request, ['queryResult', 'parameters']))

            fulfillment_text = ("'%s'에 대한 결과에요." if notices else "'%s'에 대한 결과를 찾을 수 없어요.") % get(json_obj_request, ['queryResult', 'queryText'])
            payload['notices'] = serializers.serialize('json', notices)
        else:  # 특정 공지사항 url 요청에 대한 처리
            requested_title = get(json_obj_request, ['queryResult', 'queryText'])
            requested_notice = DB.get_notice(requested_title)

            fulfillment_text = requested_title
            if requested_notice:
                payload['url'] = requested_notice.url

        return HttpResponse(
            JsonResponse({
                'fulfillmentText': fulfillment_text,
                'payload': payload,
                'source': 'http://ssu-notice.appspot.com'
            }),
            content_type='application/json; charset=utf-8',
        )
