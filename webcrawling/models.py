from django.db import models


class Notification(models.Model):
    title = models.TextField()
    url = models.TextField()
    date = models.DateField()
    hits = models.IntegerField()
    category = models.CharField(max_length=16)
    owner = models.CharField(max_length=24)

    def __str__(self):
        return self.title
