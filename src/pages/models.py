from django.db import models


# Create your models here.
class Info(models.Model):
    text = models.TextField(blank=True, null=True, default="")
    # upload_to determines the file s3 will download to
    file = models.FileField(blank=True, null=True)
    file_location = models.TextField(blank=True, null=True, default="")
