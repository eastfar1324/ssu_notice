from django.db import models


class Notification(models.Model):
    name = models.TextField()
    category = models.CharField(max_length=16)
    date = models.DateField()
    hits = models.IntegerField()
    owner = models.CharField(max_length=24)
