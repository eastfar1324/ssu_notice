# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db import transaction
from bs4 import BeautifulSoup
from models import Notice
from models import Hits
import traceback
import requests
import logging
import numpy
from ssu_notice.db import DB


def split_category_title(whole_title):
    whole_title = whole_title.strip()
    square_bracket_positions = []
    square_bracket_level = 0

    for i in range(len(whole_title)):
        if square_bracket_level == 0:
            if whole_title[i] == '[':
                square_bracket_positions.append(i)
                square_bracket_level += 1
            elif whole_title[i] == ' ':
                continue
            else:
                break
        else:
            if whole_title[i] == '[':
                square_bracket_level += 1
            elif whole_title[i] == ']':
                square_bracket_level -= 1
                if square_bracket_level == 0:
                    square_bracket_positions.append(i)

    categories = ''
    title = ''

    num_of_categories = len(square_bracket_positions) // 2

    if num_of_categories == 0:
        return categories, whole_title
    else:
        for i in range(num_of_categories):
            square_bracket_start = square_bracket_positions[i * 2]
            square_bracket_end = square_bracket_positions[i * 2 + 1]

            category = whole_title[square_bracket_start + 1:square_bracket_end].strip()
            if category not in categories:
                categories += category + ' '
            if i == num_of_categories - 1:
                title = whole_title[square_bracket_end + 1:].strip()

        categories = categories.strip()

        return categories, title


def get_notices_crawled():
    source_code = requests.get('http://www.ssu.ac.kr/web/kor/plaza_d_01')
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, 'lxml')

    notices = []
    for notice in soup.select('table.bbs-list > tbody > tr.trNotice'):
        (categories, title) = split_category_title(notice.contents[2].a.string)
        url = notice.contents[2].a['href']
        owner = notice.contents[4].string
        date = notice.contents[5].string.replace('.', '-')
        hits = notice.contents[6].string

        notices.append(Notice.create(title, url, date, hits, categories, owner))

    notices.reverse()
    return notices


def regression(hits_increase_time_relative):
    def get_deviation(hits_increase, degree):
        deviation = 0.0
        for hits in hits_increase:
            deviation += (hits[0] ** degree - hits[1]) ** 2
        return deviation

    degrees = numpy.linspace(0.0, 0.5, num=1000)
    low = [0, get_deviation(hits_increase_time_relative, degrees[0])]
    high = [len(degrees)-1, get_deviation(hits_increase_time_relative, degrees[len(degrees)-1])]
    mid = []

    while abs(low[0] - high[0]) > 1:
        mid_index = (low[0] + high[0]) // 2
        mid = [mid_index, get_deviation(hits_increase_time_relative, degrees[mid_index])]

        if low[1] < mid[1] < high[1]:
            high = mid
        elif low[1] > mid[1] > high[1]:
            low = mid
        else:
            left = [mid_index-1, get_deviation(hits_increase_time_relative, degrees[mid_index-1])]
            right = [mid_index+1, get_deviation(hits_increase_time_relative, degrees[mid_index+1])]

            if left[1] < right[1]:
                high = mid
            else:
                low = mid

    return degrees[mid[0]]


@csrf_exempt
def crawl(request):
    response = None
    savepoint = None
    num_new = 0

    try:
        savepoint = transaction.savepoint()

        notices_crawled = get_notices_crawled()
        if len(notices_crawled) == 0:
            raise Exception('crawling failed!')

        for notice_crawled in notices_crawled:
            notice_db = Notice.objects.filter(
                title=notice_crawled.title,
                categories=notice_crawled.categories,
                owner=notice_crawled.owner
            ).first()

            if notice_db is None:  # 새로운 공지사항
                notice_crawled.save()
                num_new += 1
                logging.info('New notice : %s' % str(notice_crawled))
            else:  # 기존에 있던 공지사항 이라면
                notice_db.hits = notice_crawled.hits
                notice_db.save(update_fields=['hits'])

                hits_db = Hits.objects.filter(notice_id=notice_db.id).first()

                if (hits_db is None and int(notice_db.hits) < 600) or hits_db is not None:
                    hits = Hits(
                        notice_id=notice_db.id,
                        hits=notice_db.hits
                    )
                    hits.save()

                    hits_increase_time_relative = DB.get_hits_increase(notice_db.id, True)
                    exponent = regression(hits_increase_time_relative)
                    notice_db.exponent = exponent
                    notice_db.save(update_fields=['exponent'])

                    num_hits = Hits.objects.filter(notice_id=notice_db.id).count()
                    if num_hits == 10 and exponent > 0.37:
                        pass  # push 보내기
    except Exception as e:
        transaction.savepoint_rollback(savepoint)

        logging.exception(e)
        response = HttpResponse(traceback.format_exc())
    else:
        transaction.savepoint_commit(savepoint)
        response_message = 'success, %d rows added' % num_new
        logging.info(response_message)
        response = HttpResponse(response_message)
    finally:
        return response
