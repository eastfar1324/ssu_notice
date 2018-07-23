# -*- coding: utf-8 -*-
from django.http import HttpRequest
from httplib import HTTPResponse
from pytz import UnknownTimeZoneError
import json
import pytz
import time


def make_json_object(http, method='utf-8'):
    if isinstance(http, HttpRequest):
        return json.loads(http.body.decode(method))
    elif isinstance(http, HTTPResponse):
        return json.loads(http.read().decode(method))
    else:
        pass


def get(json_object, keys):
    result = json_object
    for key in keys:
        result = result[key]
    return result


def korea_datetime(datetime_utc):
    korea_dt = None
    try:
        local_timezone = pytz.timezone('Asia/Seoul')
    except UnknownTimeZoneError:
        korea_dt = datetime_utc
    else:
        korea_dt = local_timezone.normalize(datetime_utc.replace(tzinfo=pytz.utc).astimezone(local_timezone))
        # normalize() might be unnecessary
    finally:
        return korea_dt


def timestamp(datetime):
    return time.mktime(datetime.timetuple()) * 1000


def korea_timestamp(datetime):
    return timestamp(korea_datetime(datetime))


def get_parameter_int(request, name, default=0):
    parameter = request.GET.get(name)

    if parameter:
        return int(parameter)
    else:
        return default


class Hangul:
    def __init__(self):
        self.__HANGUL_RANGE = (44032, 55203)
        self.__INITIALS_START_LETTER = 4352
        self.__INITIALS_CYCLE = 588
        self.__INITIALS_TO_CONSONANTS = {}

        initials = [u'가', u'까', u'나', u'다', u'따', u'라', u'마', u'바', u'빠', u'사', u'싸', u'아', u'자', u'짜', u'차', u'카', u'타', u'파', u'하']
        consonants = [u'ㄱ', u'ㄲ', u'ㄴ', u'ㄷ', u'ㄸ', u'ㄹ', u'ㅁ', u'ㅂ', u'ㅃ', u'ㅅ', u'ㅆ', u'ㅇ', u'ㅈ', u'ㅉ', u'ㅊ', u'ㅋ', u'ㅌ', u'ㅍ', u'ㅎ']

        for i in range(len(initials)):
            self.__INITIALS_TO_CONSONANTS[self.__initial(initials[i])] = consonants[i]

    def __is_hangul(self, char):
        return self.__HANGUL_RANGE[0] <= ord(char) <= self.__HANGUL_RANGE[1]

    def __initial(self, char):
        return unichr((ord(char) - self.__HANGUL_RANGE[0]) / self.__INITIALS_CYCLE + self.__INITIALS_START_LETTER)

    def is_initials(self, string):
        if string:
            return all(all(char in self.__INITIALS_TO_CONSONANTS.values() for char in word) for word in string.split())
        else:
            return False

    def hangul2initials(self, string):
        chars = []
        for char in string:
            if self.__is_hangul(char):
                chars.append(self.__INITIALS_TO_CONSONANTS[self.__initial(char)])
            else:
                chars.append(char)

        return u''.join(chars)
