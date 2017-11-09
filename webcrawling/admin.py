# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import Notice
from models import Hits

admin.site.register(Notice)
admin.site.register(Hits)

