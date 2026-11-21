from django.conf import settings
from django.db import models


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    sentiment = models.CharField(max_length=10)
    score = models.FloatField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
