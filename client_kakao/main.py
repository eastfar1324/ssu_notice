# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ssu_notice.common import get
from ssu_notice.common import make_json_object
from ssu_notice.dialogflow import DialogFlow
from models import Request
from models import Unknown
import logging
import json


@csrf_exempt
def friend(request):
    if request.method == 'POST':
        user_key = get(make_json_object(request), ['user_key'])
        logging.info('The user(%s) now is my friend.' % user_key)
    elif request.method == 'DELETE':
        user_key = request.path.split('/')[-1]
        logging.info('The user(%s) deleted me.' % user_key)

    return HttpResponse('SUCCESS')


def keyboard(request):
    return JsonResponse({
        'type': 'text'
    })


@csrf_exempt
def message(request):
    def search(_speech_request):
        _json_obj_response = DialogFlow.response_json_obj(_speech_request)
        _speech_response = get(_json_obj_response, ['result', 'fulfillment', 'speech'])
        _notices = json.loads(get(_json_obj_response, ['result', 'contexts', 0, 'parameters', 'notices']))

        if len(_notices) > 0:
            response_keyboard = {
                "type": "buttons",
                "buttons": [_notice['fields']['title'] for _notice in _notices]
            }
        else:
            response_keyboard = {
                "type": "text"
            }

        return {
            'message': {
                'text': _speech_response
            },
            'keyboard': response_keyboard
        }

    DialogFlow()
    json_obj_request = make_json_object(request)
    user_key = get(json_obj_request, ['user_key'])
    speech_request = get(json_obj_request, ['content'])
    json_obj_response = DialogFlow.response_json_obj(speech_request)
    intent_name = get(json_obj_response, ['result', 'metadata', 'intentName'])
    speech_response = get(json_obj_response, ['result', 'fulfillment', 'speech'])
    logging.debug(speech_request)

    if intent_name != 'link' and user_key != 'K9Um4_bGWB7v':
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
        if len(notices) > 0:
            result['keyboard'] = {
                "type": "buttons",
                "buttons": [notice['fields']['title'] for notice in notices]
            }
    elif intent_name == 'link':
        try:
            url = get(json_obj_response, ['result', 'fulfillment', 'displayText'])
        except KeyError:
            unknown = Unknown.objects.filter(speech_request=speech_request).first()

            if unknown is None:
                Unknown.create(speech_request).save()
                result = search('%s 검색' % speech_request)
            else:
                unknown.count += 1
                unknown.save(update_fields=['count'])

                if unknown.speech_response is None:
                    result = search('%s 검색' % speech_request)
                else:
                    result['message']['text'] = unknown.speech_response
        else:
            result['message']['message_button'] = {
                "label": '보러가기',
                "url": url
            }
    elif intent_name == 'Default Fallback Intent':
        unknown = Unknown.objects.filter(speech_request=speech_request).first()

        if unknown is None:
            Unknown.create(speech_request).save()
            result = search('%s 검색' % speech_request)
        else:
            unknown.count += 1
            unknown.save(update_fields=['count'])

            if unknown.speech_response is None:
                result = search('%s 검색' % speech_request)
            else:
                result['message']['text'] = unknown.speech_response
    elif intent_name == 'help':
        result['message']['text'] = '이런 식으로 사용하세요.\n\n' \
                                    '<사용 예시>\n' \
                                    '공지사항\n' \
                                    '중요한 공지사항 보여줘\n' \
                                    '최근 공지사항 5개\n' \
                                    '장학 검색해줘\n' \
                                    '공지사항 7일 전부터 알려줘\n' \
                                    '오늘 공지사항\n\n' \
                                    '<사용 예시 다시 보기>\n' \
                                    '기능\n' \
                                    'help'

    return JsonResponse(result)


@csrf_exempt
def leave(request):
    user_key = request.path.split('/')[-1]
    logging.info('The user(%s) just left chat room.' % user_key)
    return HttpResponse('SUCCESS')
