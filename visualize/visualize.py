# -*- coding: utf-8 -*-

from django.db import connection
from django.shortcuts import render
from pytz import UnknownTimeZoneError
from webcrawling.models import Notice
import pytz
import sys
import json
from django.core.serializers.json import DjangoJSONEncoder

reload(sys)
sys.setdefaultencoding('utf-8')


def get_notice_ids():
    result = []
    with connection.cursor() as cursor:
        cursor.execute('select notice_id from webcrawling_hits group by notice_id')
        rows = cursor.fetchall()

    for row in rows:
        result.append(int(row[0]))

    return result


def get_notices(notice_ids):
    notices = []
    for notice_id in notice_ids:
        notice_db = Notice.objects.get(id=notice_id)

        with connection.cursor() as cursor:
            cursor.execute('select `time`, `hits` from webcrawling_hits where notice_id=%s', [notice_id])
            rows = cursor.fetchall()

        hits_increase = []
        for row in rows:
            hits_increase.append((korea_datetime(row[0]), int(row[1]),))

        notices.append({
            'notice_id': notice_id,
            'title': get_full_title(notice_db),
            'hits_increase': hits_increase
        })
    return notices


def get_full_title(notice_db):
    categories = notice_db.categories.split(' ')

    full_title = ''
    for category in categories:
        full_title += '[%s]' % category
    full_title += notice_db.title

    return full_title


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


def index(request):
    notice_ids = get_notice_ids()
    notices = get_notices(notice_ids)

    context = {'notices': json.dumps(notices, cls=DjangoJSONEncoder, ensure_ascii=False)}
    return render(request, 'visualize.html', context)
