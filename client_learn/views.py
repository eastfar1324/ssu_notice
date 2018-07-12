# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.http import HttpResponse
from client_kakao.models import Unknown
import sys
import logging
import traceback

reload(sys)
sys.setdefaultencoding('utf-8')


def index(request):
    unknowns = Unknown.objects.filter(speech_response__isnull=True).order_by('count', '-id')
    return render(request, 'learn.html', {'unknowns': unknowns})


@csrf_exempt
def teach(request):
    unknown_id = int(request.POST.get('id'))
    speech_response = request.POST.get('speech_response')
    unknown = Unknown.objects.filter(Q(id=unknown_id) & Q(speech_response__isnull=True)).first()

    response = None
    try:
        if unknown:
            unknown.speech_response = speech_response
            unknown.save(update_fields=['speech_response'])
        else:
            raise Exception('speech_response is already learned')
    except Exception as e:
        logging.exception(e)
        response = HttpResponse(traceback.format_exc())
    else:
        response = HttpResponse('success')
    finally:
        return response
