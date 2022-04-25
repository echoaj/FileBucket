from django.db import models


# Create your models here.
class Info(models.Model):
    text = models.TextField(blank=True, null=True, default="")
    file = models.FileField(blank=True, null=True, upload_to='media')
