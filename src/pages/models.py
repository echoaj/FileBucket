from django.db import models


# Create your models here.
class Info(models.Model):
    text = models.TextField(blank=True, null=True, default="")