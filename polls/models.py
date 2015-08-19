from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Poll(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    question = models.CharField(max_length=300)

class Answer(models.Model):
    class Meta:
        ordering = ['weight']
    poll = models.ForeignKey(Poll)
    body = models.CharField(max_length=300)
    weight = models.PositiveIntegerField(default=0, blank=True)

    def __str__(self):
        return self.body


class Vote(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    session_key = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    poll = models.ForeignKey(Poll)
    answer = models.ForeignKey(Answer)
