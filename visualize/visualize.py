# -*- coding: utf-8 -*-
from django.db import connection
from django.shortcuts import render
from webcrawling.models import Notice
from django.core.serializers.json import DjangoJSONEncoder
import sys
import json
from ssu_notice.common import korea_timestamp
from ssu_notice.common import get_parameter_int


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


def get_axis_info():
    with connection.cursor() as cursor:
        cursor.execute(
            ' select ' +
            '    min(time) as time_min, ' +
            '    max(time) as time_max, ' +
            '    max(hits) as hits_max  ' +
            ' FROM ' +
            '    webcrawling_hits '
        )
        row = cursor.fetchone()

    return {
        'time_min': korea_timestamp(row[0]),
        'time_max': korea_timestamp(row[1]),
        'hits_max': row[2],
    }


def index(request):
    days_min = get_parameter_int(request, 'days_min', 3)
    num = get_parameter_int(request, 'num', 100)

    notices = get_notices(recorded_more_than_days_of=days_min, num=num)
    axis_info = get_axis_info()

    context = {
        'notices': json.dumps(notices, cls=DjangoJSONEncoder, ensure_ascii=False),
        'axis_info': json.dumps(axis_info, cls=DjangoJSONEncoder, ensure_ascii=False),
        'days_min': days_min,
        'num': len(notices)
    }
    return render(request, 'visualize.html', context)
