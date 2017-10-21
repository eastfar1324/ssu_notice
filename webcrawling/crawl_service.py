# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from bs4 import BeautifulSoup
import requests
import logging


@csrf_exempt
def crawl(request):
    source_code = requests.get('http://www.ssu.ac.kr/web/kor/plaza_d_01')
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, 'lxml')

    notices = []
    for notice in soup.select('table.bbs-list > tbody > tr.trNotice'):
        notices.append(notice.select('td.left.bold')[0].a.string + '<br />')
    return HttpResponse(notices)


# soup.select('table.bbs-list > tbody > tr.trNotice')
'''
<tr class="trNotice">
 <td class="center bold">
  <img alt="공지" src="/html/portlet/ext/bbs/images/title_notice.gif"/>
 </td>
 <td class="left bold">
  <a href="http://www.ssu.ac.kr/web/kor/plaza_d_01;jsessionid=rS07FW80aUcSPrtaRmos2i3cH9LWX9jTHTIEkjVedjZyKiRx9Pwytth3uesYBggC?p_p_id=EXT_MIRRORBBS&amp;p_p_lifecycle=0&amp;p_p_state=normal&amp;p_p_mode=view&amp;p_p_col_id=column-1&amp;p_p_col_pos=1&amp;p_p_col_count=2&amp;_EXT_MIRRORBBS_struts_action=%2Fext%2Fmirrorbbs%2Fview_message&amp;_EXT_MIRRORBBS_sCategory=&amp;_EXT_MIRRORBBS_sTitle=&amp;_EXT_MIRRORBBS_sWriter=&amp;_EXT_MIRRORBBS_sTag=&amp;_EXT_MIRRORBBS_sContent=&amp;_EXT_MIRRORBBS_sCategory2=&amp;_EXT_MIRRORBBS_sKeyType=&amp;_EXT_MIRRORBBS_sKeyword=&amp;_EXT_MIRRORBBS_curPage=1&amp;_EXT_MIRRORBBS_messageId=14718527" style="text-decoration:none">
   2017학년도 동계방학 뉴질랜드 단기어학연수 프로그램 안내
  </a>
 </td>
 <td>
  <img alt="첨부 파일" src="/html/portlet/ext/bbs/images/ico_file.gif" style="vertical-align:middle"/>
 </td>
 <td>
  학생서비스팀
 </td>
 <td>
  2017.09.29
 </td>
 <td>
  19
 </td>
</tr>
'''