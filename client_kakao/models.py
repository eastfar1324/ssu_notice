# -*- coding: utf-8 -*-
from django.db import models


class Request(models.Model):
    id = models.AutoField(primary_key=True)
    user_key = models.CharField(max_length=20, default='unknown')
    time = models.DateTimeField(auto_now_add=True)
    speech = models.TextField()

    @classmethod
    def create(cls, user_key, speech):
        return cls(
            user_key=user_key,
            speech=unicode(speech),
        )


class Unknown(models.Model):
    id = models.AutoField(primary_key=True)
    speech_request = models.TextField()
    speech_response = models.TextField(null=True)
    count = models.PositiveIntegerField()

    @classmethod
    def create(cls, speech_request):
        return cls(
            speech_request=unicode(speech_request),
            count=1,
        )
