# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models

# Create your models here.
class RaveEvent(models.Model):
    title = models.CharField(max_length=200)
    artists = models.TextField()
    location = models.TextField()
    Date = models.DateTimeField()
