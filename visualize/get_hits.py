# -*- coding: utf-8 -*-
from django.db import connection
from ssu_notice.common import korea_timestamp
from django.http import JsonResponse
import numpy


def get_deviation(hits_increase, degree):
    deviation = 0.0
    for hits in hits_increase:
        deviation += (hits[0] ** degree - hits[1]) ** 2
    return deviation


def regression(hits_increase):
    degrees = numpy.linspace(0.0, 0.5, num=1000)
    low = [0, get_deviation(hits_increase, degrees[0])]
    high = [len(degrees)-1, get_deviation(hits_increase, degrees[len(degrees)-1])]
    mid = []

    while abs(low[0] - high[0]) > 1:
        mid_index = (low[0] + high[0]) // 2
        mid = [mid_index, get_deviation(hits_increase, degrees[mid_index])]

        if low[1] < mid[1] < high[1]:
            high = mid
        elif low[1] > mid[1] > high[1]:
            low = mid
        else:
            left = [mid_index-1, get_deviation(hits_increase, degrees[mid_index-1])]
            right = [mid_index+1, get_deviation(hits_increase, degrees[mid_index+1])]

            if left[1] < right[1]:
                high = mid
            else:
                low = mid

    return degrees[mid[0]]


def get(request):
    notice_id = request.GET.get('notice_id')
    assert notice_id
    notice_id = int(notice_id)

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

    hits_increase = []
    hits_increase_temp = []

    first_timestamp = korea_timestamp(rows[0][0])
    for row in rows:
        row_time = korea_timestamp(row[0])
        row_hits = int(row[1])
        hits_increase.append((row_time, row_hits,))
        hits_increase_temp.append((row_time - first_timestamp, row_hits,))

    degree = regression(hits_increase_temp)

    return JsonResponse({
        'hits_increase': hits_increase,
        'degree': degree
    })
