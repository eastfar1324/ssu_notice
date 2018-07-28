# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ssu_notice.common import get
from ssu_notice.common import make_json_object
from ssu_notice.dialogflow import DialogFlow
from models import Request
from models import Unknown
from webcrawling.models import Notice
import logging
import json


@csrf_exempt
def message(request):
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
        notices = json.loads(get(json_obj_response, ['result', 'fulfillment', 'data', 'notices']))
        if len(notices) > 0:
            result['keyboard'] = {
                "type": "buttons",
                "buttons": [notice['fields']['title'] for notice in notices]
            }
    elif intent_name == 'link':
        try:
            url = get(json_obj_response, ['result', 'fulfillment', 'data', 'url'])
        except (KeyError, IndexError):  # dialogflow가 검색 요청을 공지사항 link intent로 인지했을 떄
            result = unknown_result(speech_request)
        else:
            result['message']['message_button'] = {
                "label": '보러가기',
                "url": url
            }
    elif intent_name == 'Default Fallback Intent':
        if speech_request[-3:] == '...':
            notice = Notice.objects.filter(title__icontains=speech_request[0:-3]).first()
        else:
            notice = Notice.objects.filter(title=speech_request).first()

        if notice:
            result['message'] = {
                'text': notice.title,
                'message_button': {
                    "label": '보러가기',
                    "url": notice.url
                }
            }
        else:
            result = unknown_result(speech_request)
    elif intent_name == 'help':
        result['message']['text'] = '이런 식으로 사용하세요.\n\n' \
                                    '<사용 예시>\n' \
                                    '공지사항 / 공지 / ㄱㅈ\n' \
                                    '중요한 공지사항 / 중요 / ㅈㅇ\n' \
                                    '장학 검색해줘 / 장학\n' \
                                    '오늘 공지사항\n' \
                                    '최근 공지사항 5개 보여줘\n' \
                                    '공지사항 7일 전부터 알려줘\n\n' \
                                    '<사용 예시 다시 보기>\n' \
                                    '기능 / 사용법 / 예시 / ㅇㅅ'

    return JsonResponse(result)


def unknown_result(_speech_request):
    unknown = Unknown.objects.filter(speech_request=_speech_request).first()

    if unknown is None:
        Unknown.create(_speech_request).save()
        _result = search('%s 검색' % _speech_request)
    else:
        unknown.count += 1
        unknown.save(update_fields=['count'])

        if unknown.speech_response is None:
            _result = search('%s 검색' % _speech_request)
        else:
            _result = {
                'message': {
                    'text': unknown.speech_response
                },
                "keyboard": {
                    "type": "text"
                }
            }
    return _result


def search(_speech_request):
    _json_obj_response = DialogFlow.response_json_obj(_speech_request)
    _speech_response = get(_json_obj_response, ['result', 'fulfillment', 'speech'])
    _notices = json.loads(get(_json_obj_response, ['result', 'fulfillment', 'data', 'notices']))

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


def keyboard(request):
    return JsonResponse({
        'type': 'text'
    })


@csrf_exempt
def friend(request):
    if request.method == 'POST':
        user_key = get(make_json_object(request), ['user_key'])
        logging.info('The user(%s) now is my friend.' % user_key)
    elif request.method == 'DELETE':
        user_key = request.path.split('/')[-1]
        logging.info('The user(%s) deleted me.' % user_key)

    return HttpResponse('SUCCESS')


@csrf_exempt
def leave(request):
    user_key = request.path.split('/')[-1]
    logging.info('The user(%s) just left chat room.' % user_key)
    return HttpResponse('SUCCESS')
