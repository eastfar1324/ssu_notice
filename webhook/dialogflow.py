import os.path
import sys
import json
try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai


class DialogFlow:
    def __init__(self):
        self.dialog = apiai.ApiAI('9e2f805b26a44df3955374bb8278e848')

    def get_speech_request(self, request):
        json_request = json.loads((request.body).decode('utf-8'))
        return json_request['content']

    def get_speech_response(self, speech_request):
        request = self.dialog.text_request()
        request.lang = 'en'
        request.query = speech_request

        response = request.getresponse()
        json_response = json.loads(response.read().decode('utf-8'))
        return json_response["result"]["fulfillment"]["speech"]
