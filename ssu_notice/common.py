# -*- coding: utf-8 -*-
from django.http import HttpRequest
from httplib import HTTPResponse
import json


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
