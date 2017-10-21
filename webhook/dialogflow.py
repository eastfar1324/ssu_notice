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
    def get_speech_request(json_request):
        return json_request['result']['resolvedQuery']

    @staticmethod
    def get_speech_response(json_request):
        return json_request["result"]["fulfillment"]["speech"]

    @staticmethod
    def get_webhook_response(speech_response):
        return {
            "speech": speech_response,
            "displayText": speech_response,
            "data": {},
            "contextOut": [],
            "source": "ssu-notice"
        }
