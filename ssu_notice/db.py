# -*- coding: utf-8 -*-
from django.db import connection
from django.db.models import Q
from datetime import datetime
from webcrawling.models import Notice
from common import *
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
            notices = Notice.objects.all().order_by('-exponent')[:10]
        elif intent_name == 'notice-04-search':
            keywords = []
            for sub_keyword in parameters['keyword'].split():
                special_character_removed = ''.join(ch for ch in sub_keyword if ch.isalnum())
                keywords.append(special_character_removed)

            condition = reduce(operator.or_, [Q(title__icontains=keyword) for keyword in keywords])
            condition |= reduce(operator.or_, [Q(categories__icontains=keyword) for keyword in keywords])

            notices = Notice.objects.filter(condition).order_by('-id')
        elif intent_name == 'notice-05-date-from':
            date_from = parameters['date']
            notices = Notice.objects.filter(date__gte=date_from).order_by('-id')
        elif intent_name == 'notice-06-date-on':
            date_on = parameters['date']
            year = int(date_on.split('-')[0])
            month = int(date_on.split('-')[1])
            day = int(date_on.split('-')[2])
            notices = Notice.objects.filter(date=datetime(year, month, day)).order_by('-id')
        elif intent_name == 'notice-07-hits':
            more_than = parameters['more_than']
            if more_than == '':
                more_than = 10000
                notices = Notice.objects.filter(hits__gte=more_than).order_by('-id')
            else:
                more_than = int(more_than)
                notices = Notice.objects.filter(hits__gte=more_than).order_by('-id')
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
