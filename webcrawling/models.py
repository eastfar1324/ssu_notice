# -*- coding: utf-8 -*-
from django.db import models
from ssu_notice.common import Hangul


class Notice(models.Model):
    id = models.AutoField(primary_key=True)
    categories = models.TextField()
    title = models.TextField()
    initials = models.TextField()
    url = models.TextField()
    owner = models.TextField()
    date = models.DateField()
    hits = models.PositiveIntegerField()
    exponent = models.FloatField(default=0.0)

    @classmethod
    def create(cls, title, url, date, hits, categories, owner):
        return cls(
            title=unicode(title),
            initials=Hangul().hangul2initials(unicode(title)),
            url=url,
            date=date,
            hits=hits,
            categories=unicode(categories),
            owner=unicode(owner)
        )

    def __unicode__(self):
        return u'[%s]%s / %s / %s ' % (self.categories, self.title, self.owner, self.date)

    def __eq__(self, other):
        return self.__unicode__() == other.__unicode__()


class Hits(models.Model):
    id = models.AutoField(primary_key=True)
    notice_id = models.PositiveIntegerField()
    time = models.DateTimeField(auto_now_add=True)
    hits = models.PositiveIntegerField()
