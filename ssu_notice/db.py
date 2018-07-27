# -*- coding: utf-8 -*-
from django.db import connection
from django.db.models import Q
from datetime import datetime
from webcrawling.models import Notice
from common import *
import datetime
from ssu_notice.common import Hangul
import operator
import logging


class DB:
    def __init__(self):
        pass

    @staticmethod
    def get_notices(intent_name, parameters):
        notices = []

        if intent_name == 'notice-01-common':
            notices = Notice.objects.all().order_by('-id')[:20]
        elif intent_name == 'notice-02-recent':
            how_many = int(parameters['how_many'])
            notices = Notice.objects.all().order_by('-id')[:how_many]
        elif intent_name == 'notice-03-important':
            notices = Notice.objects.filter(date__gt=datetime.datetime.today() - datetime.timedelta(days=90)).order_by(
                '-exponent')[:20]
            notices = sorted(notices, key=lambda notice: notice.id, reverse=True)
        elif intent_name == 'notice-04-search':
            search_keyword = parameters['keyword']
            condition = Q(initials__icontains=search_keyword) if Hangul().is_initials(search_keyword) else Q(title__icontains=search_keyword)
            notices = Notice.objects.filter(condition).order_by('-id')
        elif intent_name == 'notice-05-date-from':
            date_from = datetime.datetime.strptime(parameters['date'], '%Y-%m-%dT%H:%M:%S+00:00').date()
            notices = Notice.objects.filter(date__gte=date_from).order_by('-id')
        elif intent_name == 'notice-06-date-on':
            date_on = datetime.datetime.strptime(parameters['date'], '%Y-%m-%dT%H:%M:%S+00:00').date()
            notices = Notice.objects.filter(date=date_on).order_by('-id')
        else:
            pass

        return notices

    @staticmethod
    def get_hits_increase(notice_id, time_relative=False):
        with connection.cursor() as cursor:
            cursor.execute(
                ' select ' +
                '   time, hits ' +
                ' from ' +
                '   webcrawling_hits ' +
                ' where ' +
                '   notice_id=%s ',
                [notice_id]
            )
            rows = cursor.fetchall()

        first_timestamp = korea_timestamp(rows[0][0])
        hits_increase = []
        for row in rows:
            row_time = korea_timestamp(row[0])
            row_hits = int(row[1])

            if time_relative:
                hits_increase.append((row_time - first_timestamp, row_hits,))
            else:
                hits_increase.append((row_time, row_hits,))

        return hits_increase

    @staticmethod
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
