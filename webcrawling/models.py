# -*- coding: utf-8 -*-
from django.db import models

class Notice(models.Model):
    title = models.TextField()
    url = models.TextField()
    date = models.DateField()
    hits = models.IntegerField()
    categories = models.TextField()
    owner = models.TextField()

    @classmethod
    def create(cls, title, url, date, hits, categories, owner):
        return cls(
            title=unicode(title),
            url=url,
            date=date,
            hits=hits,
            categories=unicode(categories),
            owner=unicode(owner)
        )

    def __unicode__(self):
        return u'[%s]%s / %s / %s / %s' % (self.categories, self.title, self.date, self.hits, self.owner)