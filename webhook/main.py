from django.http import HttpResponse
from dialogflow import DialogFlow

def index(request):
    return HttpResponse(DialogFlow().get_speech_response('show me notices from yesterday'))