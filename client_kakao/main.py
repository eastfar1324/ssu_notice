# -*- coding: utf-8 -*-
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ssu_notice.common import get, make_json_object
from ssu_notice.dialogflow import DialogFlow
from webcrawling.models import Notice
from models import Request, Unknown
import random
import logging
import json


@csrf_exempt
def message(request):
    json_obj_request = make_json_object(request)
    user_key = get(json_obj_request, ['user_key'])
    speech_request = get(json_obj_request, ['content'])

    if speech_request == '다시 물어볼래요':
        return JsonResponse({
            'message': {
                'text': random.choice([
                    '얼마든지요.',
                    '얼마든지 물어보세요.',
                    '공지사항이라면 무엇이든 물어보세요.',
                    '네.',
                    '네. 좋아요.',
                    '언제나 환영이에요.',
                    '기다리고 있을게요.',
                    '좋아요.',
                    '좋아요. 기다리고 있을게요.',
                    '환영합니다.',
                    "'ㅈㅇ' 라고 입력하시면 중요한 공지사항만 알려드려요.",
                    "사용법이 궁금하시다면, '기능' 이라고 입력해보세요.",
                    'PC 카톡에서도 되는데, 알고 계신가요?',
                    '공지사항을 초성으로도 검색할 수 있어요.',
                    '왠지 당신은 좋은 사람 같아요.',
                    '오늘 하루도 힘내세요.'
                ])
            },
            "keyboard": {
                "type": "text"
            }
        })

    DialogFlow()
    json_obj_response = DialogFlow.response_json_obj(speech_request)
    logging.debug(json_obj_response)
    intent_name = get(json_obj_response, ['result', 'metadata', 'intentName'])
    confidence = get(json_obj_response, ['result', 'score'])
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

    if confidence < 0.5:  # ambiguous request
        result = unknown_result(user_key, speech_request)
    elif 'notice' in intent_name:  # notice request
        notices = json.loads(get(json_obj_response, ['result', 'fulfillment', 'data', 'notices']))
        if len(notices) > 0:
            result['keyboard'] = {
                "type": "buttons",
                "buttons": ['다시 물어볼래요'] + [notice['fields']['title'] for notice in notices]
            }
    elif intent_name == 'link':  # link request
        try:
            url = get(json_obj_response, ['result', 'fulfillment', 'data', 'url'])
        except (KeyError, IndexError):  # dialogflow가 검색 요청을 공지사항 link intent로 인지했을 떄
            result = unknown_result(user_key, speech_request)
        else:
            result['message']['message_button'] = {
                "label": '보러가기',
                "url": url
            }
    elif intent_name == 'Default Fallback Intent':  # search request
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
            result = unknown_result(user_key, speech_request)
    elif intent_name == 'help':  # guide request
        result['message']['text'] = '아래와 같이 물어보세요.\n\n' \
                                    '<사용예시>\n' \
                                    '공지사항 / 공지 / ㄱㅈ\n' \
                                    '중요한 공지사항 / 중요 / ㅈㅇ\n' \
                                    '장학 검색해줘 / 장학\n' \
                                    '오늘 공지\n' \
                                    '공지사항 5개 / 공지 5개 / ㄱㅈ 5\n' \
                                    '공지사항 3일전부터 알려줘\n\n' \
                                    '<사용예시 다시보기>\n' \
                                    '기능 / 안내 / 예시 / help\n\n' \
                                    '초성 검색도 가능해요.'

    return JsonResponse(result)


def unknown_result(user_key, speech_request):
    unknown = Unknown.objects.filter(speech_request=speech_request).first()

    if unknown is None:
        if user_key != 'K9Um4_bGWB7v':
            Unknown.create(speech_request).save()
        result = search('%s 검색' % speech_request)
    else:
        if user_key != 'K9Um4_bGWB7v':
            unknown.count += 1
            unknown.save(update_fields=['count'])

        if unknown.speech_response is None:
            result = search('%s 검색' % speech_request)
        else:
            result = {
                'message': {
                    'text': unknown.speech_response
                },
                "keyboard": {
                    "type": "text"
                }
            }
    return result


def search(_speech_request):
    json_obj_response = DialogFlow.response_json_obj(_speech_request)
    speech_response = get(json_obj_response, ['result', 'fulfillment', 'speech'])
    notices = json.loads(get(json_obj_response, ['result', 'fulfillment', 'data', 'notices']))

    if len(notices) > 0:
        response_keyboard = {
            "type": "buttons",
            "buttons": ['다시 물어볼래요'] + [_notice['fields']['title'] for _notice in notices]
        }
    else:
        response_keyboard = {
            "type": "text"
        }

    return {
        'message': {
            'text': speech_response
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
