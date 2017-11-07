# -*- coding: utf-8 -*-
from webcrawling.models import Notice
from datetime import datetime
from django.db.models import Q


class DB:
    def __init__(self):
        pass

    @staticmethod
    def get_notices(intent_name, parameters):
        notices = []
        service_message = ''

        if intent_name == '00-notices':
            notices = Notice.objects.all().order_by('-id')[:20]
            service_message = 'These are what you ordered!\n\n'
        elif intent_name == '01-recent':
            how_many = int(parameters['how_many'])
            notices = Notice.objects.all().order_by('-id')[:how_many]
            service_message = 'These are recent %d notices!\n\n' % how_many
        elif intent_name == '02-hits':
            more_than = parameters['more_than']
            if more_than == '':
                more_than = 10000
                notices = Notice.objects.filter(hits__gte=more_than).order_by('-id')
                service_message = 'These are notices more than %d hits!\n\n' % more_than
            else:
                more_than = int(more_than)
                notices = Notice.objects.filter(hits__gte=more_than).order_by('-id')
                service_message = 'These are notices more than %d hits!\n\n' % more_than
        elif intent_name == '03-search':
            keyword = parameters['keyword']
            notices = Notice.objects.filter(Q(title__icontains=keyword) | Q(categories__icontains=keyword)).order_by('-id')
            service_message = 'These are notices about %s!\n\n' % keyword
        elif intent_name == '04-date-on':
            date_on = parameters['date']
            year = int(date_on.split('-')[0])
            month = int(date_on.split('-')[1])
            day = int(date_on.split('-')[2])
            notices = Notice.objects.filter(date=datetime(year, month, day)).order_by('-id')
            service_message = 'These are notices on %s!\n\n' % date_on
        elif intent_name == '05-date-from':
            date_from = parameters['date']
            notices = Notice.objects.filter(date__gte=date_from).order_by('-id')
            service_message = 'These are notices from %s!\n\n' % date_from
        else:
            pass

        return notices, service_message
