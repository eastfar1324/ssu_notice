# -*- coding: utf-8 -*-
from django.db import connection
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from ssu_notice.common import *
from webcrawling.models import Notice
from ssu_notice.db import DB
from webcrawling.main import regression
import sys
import logging
import traceback

reload(sys)
sys.setdefaultencoding('utf-8')


def get_full_title(notice_db):
    categories = notice_db.categories.split(' ')

    full_title = ''
    for category in categories:
        full_title += '[%s]' % category
    full_title += notice_db.title

    return full_title


def get_notices(recorded_more_than_days_of, num):
    assert(recorded_more_than_days_of >= 0 and num > 0)

    with connection.cursor() as cursor:
        cursor.execute(
            ' select ' +
            '    notice_id ' +
            ' from ' +
            '    webcrawling_hits ' +
            ' group by ' +
            '    notice_id ' +
            ' having ' +
            '    (TO_DAYS(max(time))-TO_DAYS(min(time))) > %s ' +
            ' order by ' +
            '    notice_id desc ' +
            ' limit ' +
            '    %s',
            [recorded_more_than_days_of, num]
        )
        rows = cursor.fetchall()

    notices = []
    for row in rows:
        notice_id = int(row[0])
        notice_db = Notice.objects.get(id=notice_id)

        notices.append({
            'notice_id': notice_id,
            'title': get_full_title(notice_db),
        })
    return notices


def index(request):
    days_min = get_parameter_int(request, 'days_min', 3)
    num = get_parameter_int(request, 'num', 100)

    notices = get_notices(recorded_more_than_days_of=days_min, num=num)
    axis_info = DB.get_axis_info()

    context = {
        'notices': json.dumps(notices, cls=DjangoJSONEncoder, ensure_ascii=False),
        'axis_info': json.dumps(axis_info, cls=DjangoJSONEncoder, ensure_ascii=False),
        'days_min': days_min,
        'num': len(notices)
    }
    return render(request, 'visualize.html', context)


def get_hits_increase(request):
    notice_id = request.GET.get('notice_id')
    assert notice_id
    notice_id = int(notice_id)

    hits_increase = DB.get_hits_increase(notice_id)

    exponent = Notice.objects.filter(id=notice_id).values_list('exponent', flat=True)[0]

    return JsonResponse({
        'hits_increase': hits_increase,
        'exponent': exponent
    })


def analyze_all(request):
    response = None
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                ' select ' +
                '    notice_id ' +
                ' from ' +
                '    webcrawling_hits ' +
                ' group by ' +
                '    notice_id '
            )
        rows = cursor.fetchall()

        for row in rows:
            notice_id = int(row[0])
            hits_increase_time_relative = DB.get_hits_increase(notice_id, True)
            notice_db = Notice.objects.filter(id=notice_id).first()
            notice_db.exponent = regression(hits_increase_time_relative)
            notice_db.save(update_fields=['exponent'])
    except Exception as e:
        logging.exception(e)
        response = HttpResponse(traceback.format_exc())
    else:
        response = HttpResponse('success')
    finally:
        return response
