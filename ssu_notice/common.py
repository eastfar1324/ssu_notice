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
    return time.mktime(datetime.timetuple())*1000


def korea_timestamp(datetime):
    return timestamp(korea_datetime(datetime))


def get_parameter_int(request, name, default=0):
    parameter = request.GET.get(name)

    if parameter:
        return int(parameter)
    else:
        return default
