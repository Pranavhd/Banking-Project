from django.db import models

# Create your models here.


class SystemLogModel(models.Model):
    title = models.CharField(max_length=20)
    content = models.CharField(max_length=100)
